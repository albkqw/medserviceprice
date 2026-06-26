"""Normalization CLI.

Normal run (requires canonical services to already exist):
    python -m app.normalization.runner --source kdl

Bootstrap mode (creates canonical Service records from unique raw names, then normalizes):
    python -m app.normalization.runner --source kdl --bootstrap

Bootstrap is idempotent: re-running it skips names that are already canonical services.
After bootstrap every raw_price from that source matches exactly (score=100, method=exact).
Admins can then merge near-duplicate services from different sources by adding synonyms —
the next run picks them up automatically.
"""

import asyncio
import logging
import re
import sys
import uuid

from sqlalchemy import func, select

from app.db.engine import AsyncSessionLocal
from app.models.city import City
from app.models.clinic import Clinic
from app.models.enums import ServiceCategory
from app.models.parser_source import ParserSource
from app.models.raw_price import RawPrice
from app.models.service import Service
from app.normalization import pipeline
from app.normalization.matcher import FUZZY_THRESHOLD, ServiceMatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Default category per source slug.
# Override here when a new source covers a different service type.
SOURCE_DEFAULT_CATEGORY: dict[str, ServiceCategory] = {
    "kdl": ServiceCategory.lab,
    "invitro": ServiceCategory.lab,
    "doq": ServiceCategory.doctor_visit,
}


_CITY_SUFFIX_RE = re.compile(r"\(([^)]+)\)\s*$")


async def _bootstrap_clinics(session, source: ParserSource) -> int:
    """Auto-create Clinic records for any raw_clinic_name not yet in the DB.

    Expects clinic names in the format "Clinic Name (City Name)".
    Idempotent — skips names that already exist (matched by name + city_id).
    """
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    rows = await session.execute(
        select(RawPrice.raw_clinic_name)
        .where(RawPrice.parser_source_id == source.id)
        .distinct()
    )
    raw_names: list[str] = [r[0] for r in rows.all()]

    cities_result = await session.execute(select(City))
    city_by_name: dict[str, uuid.UUID] = {
        c.name.lower(): c.id for c in cities_result.scalars().all()
    }

    created = 0
    for raw_name in raw_names:
        m = _CITY_SUFFIX_RE.search(raw_name)
        if not m:
            logger.warning("Cannot extract city from clinic name %r — skipping", raw_name)
            continue
        city_name = m.group(1).strip()
        city_id = city_by_name.get(city_name.lower())
        if city_id is None:
            logger.warning("Unknown city %r in clinic name %r — skipping", city_name, raw_name)
            continue
        await session.execute(
            pg_insert(Clinic)
            .values(id=uuid.uuid4(), name=raw_name, city_id=city_id)
            .on_conflict_do_nothing(index_elements=["name", "city_id"])
        )
        created += 1

    await session.commit()
    return created


async def _bootstrap(session, source: ParserSource) -> int:
    """Create a canonical Service for every unique raw_service_name not yet in the dictionary."""
    category = SOURCE_DEFAULT_CATEGORY.get(source.slug, ServiceCategory.lab)

    # Distinct names from unprocessed raw_prices for this source
    rows = await session.execute(
        select(RawPrice.raw_service_name)
        .where(RawPrice.parser_source_id == source.id)
        .where(RawPrice.is_processed == False)  # noqa: E712
        .distinct()
    )
    raw_names: list[str] = [r[0] for r in rows.all()]

    # Names already in services table
    existing = await session.execute(select(Service.name))
    existing_names: set[str] = {r[0] for r in existing.all()}

    created = 0
    for name in raw_names:
        if name in existing_names:
            continue
        session.add(
            Service(
                id=uuid.uuid4(),
                name=name,
                category=category,
                synonyms=[],
            )
        )
        existing_names.add(name)
        created += 1

    await session.commit()
    return created


async def run(source_slug: str, bootstrap: bool, threshold: float) -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ParserSource).where(ParserSource.slug == source_slug)
        )
        source = result.scalar_one_or_none()
        if source is None:
            print(f"ParserSource '{source_slug}' not found. Run scripts.seed first.", file=sys.stderr)
            sys.exit(1)

        if bootstrap:
            clinic_created = await _bootstrap_clinics(session, source)
            logger.info("Bootstrap clinics: created/verified %d clinic records", clinic_created)
            created = await _bootstrap(session, source)
            logger.info("Bootstrap: created %d new canonical services", created)

        # Load all active services and build in-memory index
        svc_result = await session.execute(
            select(Service).where(Service.is_active == True)  # noqa: E712
        )
        services = list(svc_result.scalars().all())
        matcher = ServiceMatcher(services, threshold=threshold)
        logger.info("Matcher index: %d canonical service names loaded", matcher.service_count)

        # Count pending raw_prices so we can show progress
        count_result = await session.execute(
            select(func.count())
            .select_from(RawPrice)
            .where(RawPrice.parser_source_id == source.id)
            .where(RawPrice.is_processed == False)  # noqa: E712
        )
        pending = count_result.scalar_one()
        logger.info("Pending raw_prices: %d", pending)

        if pending == 0:
            print("Nothing to process.")
            return

        stats = await pipeline.run(session, source.id, matcher)

    print(
        f"\nNormalization complete (source={source_slug})\n"
        f"  matched:   {stats['matched']}\n"
        f"  unmatched: {stats['unmatched']}\n"
        f"  no_clinic: {stats['no_clinic']}\n"
        f"  bad_price: {stats['bad_price']}\n"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Normalize raw_prices into prices")
    parser.add_argument("--source", required=True, help="parser_source slug, e.g. kdl")
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="Create canonical Service records from unique raw names before matching",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=FUZZY_THRESHOLD,
        help=f"Fuzzy match threshold 0-100 (default {FUZZY_THRESHOLD})",
    )
    args = parser.parse_args()
    asyncio.run(run(args.source, args.bootstrap, args.threshold))

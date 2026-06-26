import hashlib
import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.engine import AsyncSessionLocal
from app.models.parser_source import ParserSource
from app.models.raw_price import RawPrice
from app.parsers.models import ParsedItem

logger = logging.getLogger(__name__)


def _checksum(slug: str, clinic: str, service: str, price: str) -> str:
    payload = f"{slug}|{clinic}|{service}|{price}"
    return hashlib.sha256(payload.encode()).hexdigest()


async def save_items(items: list[ParsedItem], source_slug: str) -> dict[str, int]:
    """Insert new ParsedItems into raw_prices, skipping duplicates via checksum.

    Returns {"saved": N, "skipped": M}.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ParserSource).where(ParserSource.slug == source_slug)
        )
        source = result.scalar_one_or_none()
        if source is None:
            raise ValueError(
                f"ParserSource with slug '{source_slug}' not found in DB. "
                "Run the seed script first: python -m scripts.seed"
            )

        saved = 0
        skipped = 0

        for item in items:
            checksum = _checksum(
                item.parser_source_slug,
                item.raw_clinic_name,
                item.raw_service_name,
                item.raw_price,
            )
            stmt = (
                pg_insert(RawPrice)
                .values(
                    parser_source_id=source.id,
                    raw_clinic_name=item.raw_clinic_name,
                    raw_service_name=item.raw_service_name,
                    raw_price=item.raw_price,
                    raw_currency=item.raw_currency,
                    raw_duration=item.raw_duration,
                    source_url=item.source_url,
                    checksum=checksum,
                    parsed_at=item.parsed_at,
                )
                .on_conflict_do_nothing(index_elements=["checksum"])
            )
            result = await session.execute(stmt)
            if result.rowcount > 0:
                saved += 1
            else:
                skipped += 1

        source.last_parsed_at = datetime.now(UTC)
        await session.commit()

    logger.info("Saved %d new raw prices, skipped %d duplicates (source=%s)", saved, skipped, source_slug)
    return {"saved": saved, "skipped": skipped}

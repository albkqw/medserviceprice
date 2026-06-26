"""Normalization pipeline.

Reads unprocessed raw_prices, matches each service name against the canonical
Service dictionary, and either:
  - creates a Price record  (matched)
  - creates an UnmatchedService record  (unmatched)

Both outcomes mark raw_price.is_processed = True so the row is never visited twice.
"""

import logging
import uuid
from decimal import Decimal, InvalidOperation

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinic import Clinic
from app.models.enums import Currency, UnmatchedStatus
from app.models.price import Price
from app.models.raw_price import RawPrice
from app.models.unmatched_service import UnmatchedService
from app.normalization.matcher import ServiceMatcher
from app.normalization.text import parse_duration_days

logger = logging.getLogger(__name__)


async def _build_clinic_map(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Return {raw_clinic_name (lowercased) → clinic_id} for all active clinics."""
    result = await session.execute(select(Clinic).where(Clinic.is_active == True))  # noqa: E712
    return {c.name.strip().lower(): c.id for c in result.scalars().all()}


async def _fetch_batch(
    session: AsyncSession, source_id: uuid.UUID, batch_size: int
) -> list[RawPrice]:
    result = await session.execute(
        select(RawPrice)
        .where(RawPrice.parser_source_id == source_id)
        .where(RawPrice.is_processed == False)  # noqa: E712
        .limit(batch_size)
    )
    return list(result.scalars().all())


async def run(
    session: AsyncSession,
    source_id: uuid.UUID,
    matcher: ServiceMatcher,
    *,
    batch_size: int = 500,
) -> dict[str, int]:
    stats = {"matched": 0, "unmatched": 0, "no_clinic": 0, "bad_price": 0}
    clinic_map = await _build_clinic_map(session)

    while True:
        batch = await _fetch_batch(session, source_id, batch_size)
        if not batch:
            break

        processed_ids: list[uuid.UUID] = []

        for rp in batch:
            processed_ids.append(rp.id)

            # --- Resolve clinic ---
            clinic_id = clinic_map.get(rp.raw_clinic_name.strip().lower())
            if clinic_id is None:
                logger.warning("No clinic for raw_clinic_name=%r — skipping", rp.raw_clinic_name)
                stats["no_clinic"] += 1
                continue

            # --- Parse price ---
            try:
                price_kzt = Decimal(rp.raw_price)
            except InvalidOperation:
                logger.warning("Bad price value %r on raw_price %s", rp.raw_price, rp.id)
                stats["bad_price"] += 1
                continue

            # --- Match service ---
            result = matcher.match(rp.raw_service_name)

            if result.service_id:
                session.add(
                    Price(
                        clinic_id=clinic_id,
                        service_id=result.service_id,
                        raw_price_id=rp.id,
                        price_kzt=price_kzt,
                        currency=Currency.KZT,
                        duration_days=parse_duration_days(rp.raw_duration),
                        parsed_at=rp.parsed_at,
                        is_active=True,
                    )
                )
                # backfill clinic_id on the raw_price row
                rp.clinic_id = clinic_id
                stats["matched"] += 1
            else:
                # Upsert: avoid duplicates if pipeline is re-run on partially processed data
                await session.execute(
                    pg_insert(UnmatchedService)
                    .values(
                        id=uuid.uuid4(),
                        raw_price_id=rp.id,
                        raw_service_name=rp.raw_service_name,
                        parser_source_id=rp.parser_source_id,
                        suggested_service_id=result.suggested_id,
                        status=UnmatchedStatus.pending,
                    )
                    .on_conflict_do_nothing()
                )
                stats["unmatched"] += 1

        # Mark entire batch as processed in one statement
        await session.execute(
            update(RawPrice)
            .where(RawPrice.id.in_(processed_ids))
            .values(is_processed=True)
        )
        await session.commit()
        logger.info(
            "Batch done: matched=%d unmatched=%d no_clinic=%d bad_price=%d",
            stats["matched"], stats["unmatched"], stats["no_clinic"], stats["bad_price"],
        )

    return stats

"""Core job logic: parse → save → normalize.

Each call is one attempt. Retries are handled by the caller (scheduler or API).
"""

import asyncio
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select

from app.db.engine import AsyncSessionLocal
from app.models.enums import ParseRunStatus, ServiceCategory
from app.models.parse_run import ParseRun
from app.models.parser_source import ParserSource
from app.models.service import Service
from app.normalization import pipeline as norm_pipeline
from app.normalization.matcher import FUZZY_THRESHOLD, ServiceMatcher
from app.normalization.runner import SOURCE_DEFAULT_CATEGORY, _bootstrap, _bootstrap_clinics
from app.parsers.sources.doq import DoqParser
from app.parsers.sources.invitro import InvitroParser
from app.parsers.sources.kdl import KDLParser
from app.parsers.storage import save_items

logger = logging.getLogger(__name__)

_PARSERS = {
    "kdl": KDLParser,
    "invitro": InvitroParser,
    "doq": DoqParser,
}

MAX_RETRIES = 3
RETRY_DELAYS = [60, 120]  # seconds between retries (attempt 1→2, 2→3)


async def _normalize(source_slug: str) -> int:
    """Run bootstrap + normalization pipeline for a source. Returns matched count."""
    async with AsyncSessionLocal() as session:
        source_result = await session.execute(
            select(ParserSource).where(ParserSource.slug == source_slug)
        )
        source = source_result.scalar_one()

        await _bootstrap_clinics(session, source)
        await _bootstrap(session, source)

        svc_result = await session.execute(
            select(Service).where(Service.is_active == True)  # noqa: E712
        )
        services = list(svc_result.scalars().all())
        matcher = ServiceMatcher(services, threshold=FUZZY_THRESHOLD)

        stats = await norm_pipeline.run(session, source.id, matcher)
        return stats["matched"]


async def _run_once(source_slug: str, run_id: uuid.UUID, attempt: int) -> dict:
    """One parse+save+normalize attempt. Updates ParseRun in DB."""
    logger.info("[%s] attempt %d — starting", source_slug, attempt)

    parser_cls = _PARSERS.get(source_slug)
    if parser_cls is None:
        raise ValueError(f"Unknown parser slug: {source_slug!r}")

    try:
        # Parse
        parser = parser_cls()
        items = await parser.parse()
        logger.info("[%s] fetched %d items", source_slug, len(items))

        # Save
        stats = await save_items(items, source_slug)
        logger.info("[%s] saved=%d skipped=%d", source_slug, stats["saved"], stats["skipped"])

        # Normalize
        matched = await _normalize(source_slug)
        logger.info("[%s] normalized %d prices", source_slug, matched)

        result = {
            "items_saved": stats["saved"],
            "items_skipped": stats["skipped"],
            "items_normalized": matched,
        }

        async with AsyncSessionLocal() as session:
            run = await session.get(ParseRun, run_id)
            if run:
                run.status = ParseRunStatus.success
                run.finished_at = datetime.now(UTC)
                run.items_saved = result["items_saved"]
                run.items_skipped = result["items_skipped"]
                run.items_normalized = result["items_normalized"]
                await session.commit()

        return result

    except Exception as exc:
        logger.error("[%s] attempt %d failed: %s", source_slug, attempt, exc, exc_info=True)

        async with AsyncSessionLocal() as session:
            run = await session.get(ParseRun, run_id)
            if run:
                run.status = ParseRunStatus.failed
                run.finished_at = datetime.now(UTC)
                run.error_message = f"{type(exc).__name__}: {exc}"
                await session.commit()

        raise


async def run_parser(source_slug: str) -> uuid.UUID:
    """Entry point for both manual and scheduled runs.

    Creates a ParseRun record, then retries up to MAX_RETRIES times.
    Returns the run_id of the final attempt.
    """
    run_id: uuid.UUID | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        async with AsyncSessionLocal() as session:
            run = ParseRun(
                id=uuid.uuid4(),
                source_slug=source_slug,
                status=ParseRunStatus.running,
                attempt=attempt,
                started_at=datetime.now(UTC),
            )
            session.add(run)
            await session.commit()
            run_id = run.id

        try:
            await _run_once(source_slug, run_id, attempt)
            logger.info("[%s] completed successfully on attempt %d", source_slug, attempt)
            return run_id

        except Exception:
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAYS[attempt - 1]
                logger.warning(
                    "[%s] retrying in %ds (attempt %d/%d)", source_slug, delay, attempt, MAX_RETRIES
                )
                await asyncio.sleep(delay)
            else:
                logger.error("[%s] all %d attempts failed", source_slug, MAX_RETRIES)

    return run_id  # type: ignore[return-value]

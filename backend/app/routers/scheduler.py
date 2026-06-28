import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import desc, select

from app.db.engine import AsyncSessionLocal
from app.dependencies.auth import require_admin_key
from app.models.enums import ParseRunStatus
from app.models.parse_run import ParseRun
from app.scheduler.jobs import _PARSERS, run_parser
from app.scheduler.scheduler import scheduler
from app.schemas.scheduler import ParseRunResponse, ScheduledJobResponse

router = APIRouter(
    prefix="/scheduler",
    tags=["scheduler"],
    dependencies=[Depends(require_admin_key)],
)


async def _get_runs(source_slug: str | None, limit: int) -> list[ParseRunResponse]:
    async with AsyncSessionLocal() as session:
        q = select(ParseRun).order_by(desc(ParseRun.started_at)).limit(limit)
        if source_slug:
            q = q.where(ParseRun.source_slug == source_slug)
        result = await session.execute(q)
        runs = result.scalars().all()

    return [
        ParseRunResponse(
            id=r.id,
            source_slug=r.source_slug,
            status=r.status,
            attempt=r.attempt,
            started_at=r.started_at,
            finished_at=r.finished_at,
            items_saved=r.items_saved,
            items_skipped=r.items_skipped,
            items_normalized=r.items_normalized,
            error_message=r.error_message,
        )
        for r in runs
    ]


@router.get("/jobs", response_model=list[ScheduledJobResponse])
async def list_jobs() -> list[ScheduledJobResponse]:
    """List all scheduled jobs and their next run times."""
    jobs = scheduler.get_jobs()
    return [
        ScheduledJobResponse(
            id=job.id,
            name=job.name,
            next_run_time=job.next_run_time,
        )
        for job in jobs
    ]


@router.post("/run/{source_slug}", status_code=202)
async def trigger_run(source_slug: str, background_tasks: BackgroundTasks) -> dict:
    """Manually trigger a parser run in the background."""
    if source_slug not in _PARSERS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown parser: {source_slug!r}. Available: {list(_PARSERS)}",
        )
    background_tasks.add_task(run_parser, source_slug)
    return {"message": f"Parser '{source_slug}' triggered", "source_slug": source_slug}


@router.get("/runs", response_model=list[ParseRunResponse])
async def list_runs(
    source: str | None = Query(None, description="Filter by parser slug"),
    limit: int = Query(50, ge=1, le=200),
) -> list[ParseRunResponse]:
    """List recent parse runs (logs)."""
    return await _get_runs(source, limit)


@router.get("/runs/{run_id}", response_model=ParseRunResponse)
async def get_run(run_id: uuid.UUID) -> ParseRunResponse:
    """Get a specific parse run by ID."""
    async with AsyncSessionLocal() as session:
        run = await session.get(ParseRun, run_id)

    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return ParseRunResponse(
        id=run.id,
        source_slug=run.source_slug,
        status=run.status,
        attempt=run.attempt,
        started_at=run.started_at,
        finished_at=run.finished_at,
        items_saved=run.items_saved,
        items_skipped=run.items_skipped,
        items_normalized=run.items_normalized,
        error_message=run.error_message,
    )

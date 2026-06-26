import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.db.engine import engine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Liveness + DB connectivity check.

    Uses a direct engine connection rather than the session dependency
    so the health endpoint never fails due to session/transaction state.
    Always returns HTTP 200 — the 'database' field signals DB health to callers.
    """
    db_status = "ok"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Health check: database unreachable")
        db_status = "error"

    return {"status": "ok", "database": db_status}

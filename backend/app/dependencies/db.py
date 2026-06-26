from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a transactional DB session per request.

    Commits on clean exit, rolls back on any exception.
    This means services never need to call session.commit() themselves —
    the request boundary IS the transaction boundary.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

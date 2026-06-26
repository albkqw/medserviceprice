from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    # pool_size: persistent connections kept open.
    # max_overflow: extra connections allowed under peak load, closed when idle.
    pool_size=10,
    max_overflow=20,
    # Verify a connection is alive before handing it to a request.
    # Catches stale connections after DB restarts without surfacing errors to clients.
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    # Prevent SQLAlchemy from expiring attributes after commit.
    # Without this, accessing obj.field after commit triggers a lazy load,
    # which raises MissingGreenlet in an async context.
    expire_on_commit=False,
)

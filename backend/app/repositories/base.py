import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, record_id: uuid.UUID) -> ModelT | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == record_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[ModelT]:
        result = await self.session.execute(
            select(self.model).offset(offset).limit(limit)  # type: ignore[attr-defined]
        )
        return list(result.scalars().all())

    async def save(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

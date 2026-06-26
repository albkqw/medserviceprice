from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.city import City
from app.repositories.base import BaseRepository


class CityRepository(BaseRepository[City]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(City, session)

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[City]:
        result = await self.session.execute(
            select(City).order_by(City.name).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> City | None:
        result = await self.session.execute(
            select(City).where(City.slug == slug)
        )
        return result.scalar_one_or_none()

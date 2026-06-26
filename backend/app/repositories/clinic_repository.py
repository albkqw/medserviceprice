import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.city import City
from app.models.clinic import Clinic
from app.repositories.base import BaseRepository


class ClinicRepository(BaseRepository[Clinic]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Clinic, session)

    async def get_by_id_with_city(self, clinic_id: uuid.UUID) -> Clinic | None:
        result = await self.session.execute(
            select(Clinic)
            .where(Clinic.id == clinic_id)
            .where(Clinic.is_active == True)  # noqa: E712
            .options(selectinload(Clinic.city))
        )
        return result.scalar_one_or_none()

    async def get_all_with_city(
        self,
        city_slug: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Clinic]:
        stmt = (
            select(Clinic)
            .join(City, Clinic.city_id == City.id)
            .where(Clinic.is_active == True)  # noqa: E712
            .options(selectinload(Clinic.city))
            .order_by(Clinic.name)
            .offset(offset)
            .limit(limit)
        )
        if city_slug:
            stmt = stmt.where(City.slug == city_slug)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

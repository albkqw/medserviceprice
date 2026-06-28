import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.city import City
from app.models.clinic import Clinic
from app.models.price import Price
from app.models.raw_price import RawPrice
from app.models.service import Service
from app.repositories.base import BaseRepository
from app.repositories.price_repository import STALE_PRICE_DAYS


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

    async def get_services(
        self,
        clinic_id: uuid.UUID,
        limit: int = 200,
    ) -> list[Row]:
        cutoff = datetime.now(UTC) - timedelta(days=STALE_PRICE_DAYS)
        stmt = (
            select(
                Service.id.label("service_id"),
                Service.name.label("service_name"),
                Service.category,
                Price.price_kzt,
                Price.duration_days,
                Price.parsed_at,
                RawPrice.source_url,
            )
            .select_from(Price)
            .join(Service, Price.service_id == Service.id)
            .outerjoin(RawPrice, Price.raw_price_id == RawPrice.id)
            .where(Price.clinic_id == clinic_id)
            .where(Price.is_active == True)  # noqa: E712
            .where(Price.parsed_at >= cutoff)
            .order_by(Service.name.asc(), Price.price_kzt.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()

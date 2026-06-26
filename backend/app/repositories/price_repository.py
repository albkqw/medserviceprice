import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.city import City
from app.models.clinic import Clinic
from app.models.price import Price
from app.models.raw_price import RawPrice
from app.models.service import Service
from app.repositories.base import BaseRepository

STALE_PRICE_DAYS = 30


class PriceRepository(BaseRepository[Price]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Price, session)

    async def search_prices(
        self,
        service_ids: list[uuid.UUID],
        city_slug: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        limit: int = 100,
    ) -> list[Row]:
        cutoff = datetime.now(UTC) - timedelta(days=STALE_PRICE_DAYS)

        stmt = (
            select(
                Price,
                Clinic,
                City,
                Service,
                RawPrice.source_url.label("source_url"),
            )
            .join(Clinic, Price.clinic_id == Clinic.id)
            .join(City, Clinic.city_id == City.id)
            .join(Service, Price.service_id == Service.id)
            .outerjoin(RawPrice, Price.raw_price_id == RawPrice.id)
            .where(Price.service_id.in_(service_ids))
            .where(Price.is_active == True)  # noqa: E712
            .where(Price.parsed_at >= cutoff)
            .where(Clinic.is_active == True)  # noqa: E712
        )

        if city_slug:
            stmt = stmt.where(City.slug == city_slug)
        if min_price is not None:
            stmt = stmt.where(Price.price_kzt >= min_price)
        if max_price is not None:
            stmt = stmt.where(Price.price_kzt <= max_price)

        stmt = stmt.order_by(Price.price_kzt.asc()).limit(limit)

        result = await self.session.execute(stmt)
        return result.all()

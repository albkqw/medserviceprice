from sqlalchemy import Text, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ServiceCategory
from app.models.service import Service
from app.repositories.base import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Service, session)

    async def search(
        self,
        query: str | None = None,
        category: ServiceCategory | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Service]:
        stmt = select(Service).where(Service.is_active == True)  # noqa: E712

        if query:
            stmt = stmt.where(
                or_(
                    Service.name.ilike(f"%{query}%"),
                    # Cast JSONB array to text for substring search across all synonyms.
                    # Good enough for MVP; replace with to_tsvector for full-text later.
                    cast(Service.synonyms, Text).ilike(f"%{query}%"),
                )
            )

        if category:
            stmt = stmt.where(Service.category == category)

        result = await self.session.execute(
            stmt.order_by(Service.name).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

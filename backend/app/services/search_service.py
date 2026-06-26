from decimal import Decimal

from app.models.enums import ServiceCategory
from app.repositories.price_repository import PriceRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.search import (
    SearchClinicInfo,
    SearchResponse,
    SearchResultItem,
    SearchServiceInfo,
)


class SearchService:
    def __init__(
        self,
        service_repo: ServiceRepository,
        price_repo: PriceRepository,
    ) -> None:
        self.service_repo = service_repo
        self.price_repo = price_repo

    async def search(
        self,
        query: str,
        city_slug: str | None = None,
        category: ServiceCategory | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        limit: int = 50,
    ) -> SearchResponse:
        services = await self.service_repo.search(query=query, category=category)

        if not services:
            return SearchResponse(query=query, total=0, results=[])

        rows = await self.price_repo.search_prices(
            service_ids=[s.id for s in services],
            city_slug=city_slug,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
        )

        results = [
            SearchResultItem(
                service=SearchServiceInfo(
                    id=row.Service.id,
                    name=row.Service.name,
                    category=row.Service.category,
                ),
                clinic=SearchClinicInfo(
                    id=row.Clinic.id,
                    name=row.Clinic.name,
                    city=row.City.name,
                    address=row.Clinic.address,
                    phone=row.Clinic.phone,
                    working_hours=row.Clinic.working_hours,
                    website=row.Clinic.website,
                ),
                price_kzt=row.Price.price_kzt,
                duration_days=row.Price.duration_days,
                parsed_at=row.Price.parsed_at,
                source_url=row.source_url,
            )
            for row in rows
        ]

        return SearchResponse(query=query, total=len(results), results=results)

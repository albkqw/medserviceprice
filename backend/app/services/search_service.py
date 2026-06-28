from decimal import Decimal

from app.models.enums import ServiceCategory
from app.repositories.price_repository import PriceRepository
from app.schemas.search import (
    SearchClinicInfo,
    SearchResponse,
    SearchResultItem,
    SearchServiceInfo,
)


class SearchService:
    def __init__(self, price_repo: PriceRepository) -> None:
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
        rows = await self.price_repo.search_prices(
            query=query,
            city_slug=city_slug,
            category=category,
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
                    lat=row.Clinic.lat,
                    lng=row.Clinic.lng,
                ),
                price_kzt=row.Price.price_kzt,
                duration_days=row.Price.duration_days,
                parsed_at=row.Price.parsed_at,
                source_url=row.source_url,
                source_slug=row.source_slug,
            )
            for row in rows
        ]

        return SearchResponse(query=query, total=len(results), results=results)

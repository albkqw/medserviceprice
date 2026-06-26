from decimal import Decimal

from fastapi import APIRouter, Depends, Query

from app.dependencies.services import get_search_service
from app.models.enums import ServiceCategory
from app.schemas.search import SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    query: str = Query(..., min_length=2, description="Service name or synonym"),
    city_slug: str | None = Query(None, description="Filter by city, e.g. 'almaty'"),
    category: ServiceCategory | None = Query(None),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    return await service.search(
        query=query,
        city_slug=city_slug,
        category=category,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
    )

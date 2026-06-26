import uuid

from fastapi import APIRouter, Depends, Query

from app.dependencies.services import get_catalog_service
from app.models.enums import ServiceCategory
from app.schemas.service import ServiceResponse
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceResponse])
async def list_services(
    query: str | None = Query(None, description="Search by name or synonym"),
    category: ServiceCategory | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: CatalogService = Depends(get_catalog_service),
) -> list[ServiceResponse]:
    return await service.list_services(query=query, category=category, offset=offset, limit=limit)


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: uuid.UUID,
    service: CatalogService = Depends(get_catalog_service),
) -> ServiceResponse:
    return await service.get_by_id(service_id)

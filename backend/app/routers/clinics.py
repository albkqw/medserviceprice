import uuid

from fastapi import APIRouter, Depends, Query

from app.dependencies.services import get_clinic_service
from app.schemas.clinic import ClinicResponse, ClinicServiceItem
from app.services.clinic_service import ClinicService

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.get("", response_model=list[ClinicResponse])
async def list_clinics(
    city_slug: str | None = Query(None, description="Filter by city slug, e.g. 'almaty'"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ClinicService = Depends(get_clinic_service),
) -> list[ClinicResponse]:
    return await service.list_clinics(city_slug=city_slug, offset=offset, limit=limit)


@router.get("/{clinic_id}/services", response_model=list[ClinicServiceItem])
async def get_clinic_services(
    clinic_id: uuid.UUID,
    service: ClinicService = Depends(get_clinic_service),
) -> list[ClinicServiceItem]:
    return await service.get_services(clinic_id)


@router.get("/{clinic_id}", response_model=ClinicResponse)
async def get_clinic(
    clinic_id: uuid.UUID,
    service: ClinicService = Depends(get_clinic_service),
) -> ClinicResponse:
    return await service.get_by_id(clinic_id)

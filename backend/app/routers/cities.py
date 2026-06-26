from fastapi import APIRouter, Depends

from app.dependencies.services import get_city_service
from app.schemas.city import CityResponse
from app.services.city_service import CityService

router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("", response_model=list[CityResponse])
async def list_cities(
    service: CityService = Depends(get_city_service),
) -> list[CityResponse]:
    return await service.list_cities()

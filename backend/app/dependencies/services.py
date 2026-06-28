from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_async_session
from app.repositories.city_repository import CityRepository
from app.repositories.clinic_repository import ClinicRepository
from app.repositories.price_repository import PriceRepository
from app.repositories.service_repository import ServiceRepository
from app.services.catalog_service import CatalogService
from app.services.city_service import CityService
from app.services.clinic_service import ClinicService
from app.services.search_service import SearchService


def get_city_service(session: AsyncSession = Depends(get_async_session)) -> CityService:
    return CityService(CityRepository(session))


def get_clinic_service(session: AsyncSession = Depends(get_async_session)) -> ClinicService:
    return ClinicService(ClinicRepository(session))


def get_catalog_service(session: AsyncSession = Depends(get_async_session)) -> CatalogService:
    return CatalogService(ServiceRepository(session))


def get_search_service(session: AsyncSession = Depends(get_async_session)) -> SearchService:
    return SearchService(price_repo=PriceRepository(session))

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import ServiceCategory


class SearchServiceInfo(BaseModel):
    id: uuid.UUID
    name: str
    category: ServiceCategory


class SearchClinicInfo(BaseModel):
    id: uuid.UUID
    name: str
    city: str
    address: str | None
    phone: str | None
    working_hours: str | None
    website: str | None
    lat: float | None
    lng: float | None


class SearchResultItem(BaseModel):
    service: SearchServiceInfo
    clinic: SearchClinicInfo
    price_kzt: Decimal
    duration_days: int | None
    parsed_at: datetime
    source_url: str | None
    source_slug: str | None


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResultItem]

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import ServiceCategory
from app.schemas.city import CityResponse


class ClinicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    city: CityResponse
    address: str | None
    phone: str | None
    working_hours: str | None
    website: str | None
    source_url: str | None


class ClinicServiceItem(BaseModel):
    service_id: uuid.UUID
    service_name: str
    category: ServiceCategory
    price_kzt: Decimal
    duration_days: int | None
    parsed_at: datetime
    source_url: str | None

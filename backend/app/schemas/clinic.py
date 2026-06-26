import uuid

from pydantic import BaseModel, ConfigDict

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

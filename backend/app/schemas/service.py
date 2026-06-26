import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import ServiceCategory


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category: ServiceCategory
    synonyms: list[str]
    description: str | None

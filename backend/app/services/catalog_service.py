import uuid

from app.core.exceptions import NotFoundError
from app.models.enums import ServiceCategory
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import ServiceResponse


class CatalogService:
    def __init__(self, service_repo: ServiceRepository) -> None:
        self.service_repo = service_repo

    async def get_by_id(self, service_id: uuid.UUID) -> ServiceResponse:
        service = await self.service_repo.get_by_id(service_id)
        if not service:
            raise NotFoundError("Service", str(service_id))
        return ServiceResponse.model_validate(service)

    async def list_services(
        self,
        query: str | None = None,
        category: ServiceCategory | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ServiceResponse]:
        services = await self.service_repo.search(
            query=query, category=category, offset=offset, limit=limit
        )
        return [ServiceResponse.model_validate(s) for s in services]

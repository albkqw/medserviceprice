import uuid

from app.core.exceptions import NotFoundError
from app.repositories.clinic_repository import ClinicRepository
from app.schemas.clinic import ClinicResponse


class ClinicService:
    def __init__(self, clinic_repo: ClinicRepository) -> None:
        self.clinic_repo = clinic_repo

    async def get_by_id(self, clinic_id: uuid.UUID) -> ClinicResponse:
        clinic = await self.clinic_repo.get_by_id_with_city(clinic_id)
        if not clinic:
            raise NotFoundError("Clinic", str(clinic_id))
        return ClinicResponse.model_validate(clinic)

    async def list_clinics(
        self,
        city_slug: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ClinicResponse]:
        clinics = await self.clinic_repo.get_all_with_city(
            city_slug=city_slug, offset=offset, limit=limit
        )
        return [ClinicResponse.model_validate(c) for c in clinics]

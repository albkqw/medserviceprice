from app.repositories.city_repository import CityRepository
from app.schemas.city import CityResponse


class CityService:
    def __init__(self, city_repo: CityRepository) -> None:
        self.city_repo = city_repo

    async def list_cities(self) -> list[CityResponse]:
        cities = await self.city_repo.get_all()
        return [CityResponse.model_validate(city) for city in cities]

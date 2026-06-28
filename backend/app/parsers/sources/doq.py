import logging
from datetime import UTC, datetime

from app.parsers.base import BaseParser
from app.parsers.http_client import HttpClient
from app.parsers.models import ParsedItem

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.doq.kz/api/v1"

# DOQ city_id → our city display name
_CITY_MAP: dict[int, str] = {
    3: "Алматы",
    1: "Астана",
    5: "Шымкент",
}

# DOQ city_id → city slug used in doq.kz URLs (/doctors/{city_slug}/{service_slug})
_CITY_SLUG_MAP: dict[int, str] = {
    3: "almaty",
    1: "astana",
    5: "shymkent",
}


async def _fetch_all(client: HttpClient, url: str) -> list[dict]:
    """Paginate through all pages of a DOQ list endpoint."""
    results = []
    next_url: str | None = url
    while next_url:
        data = await client.get_json(next_url)
        results.extend(data.get("results", []))
        next_url = data.get("next")
    return results


class DoqParser(BaseParser):
    """Fetches doctor visit prices from doq.kz JSON API.

    Fetches all active doctor-services once, deduplicates by (clinic_branch, service)
    keeping the lowest price, then resolves names via pre-loaded reference data.
    Only includes branches whose city is one of our target cities.
    """

    source_slug = "doq"

    async def parse(self) -> list[ParsedItem]:
        items: list[ParsedItem] = []
        parsed_at = datetime.now(UTC)

        async with HttpClient(delay=0.5) as client:
            logger.info("Loading services index...")
            raw_services = await _fetch_all(client, f"{_BASE_URL}/services/?limit=100")
            service_map: dict[int, str] = {s["id"]: s["name"] for s in raw_services}
            # service_id → slug used in doq.kz URLs (/doctors/{city}/{service_slug})
            service_slug_map: dict[int, str] = {s["id"]: s["slug"] for s in raw_services}
            logger.info("Loaded %d services", len(service_map))

            logger.info("Loading clinic-branches index...")
            raw_branches = await _fetch_all(client, f"{_BASE_URL}/clinic-branches/?limit=100")
            # Only keep branches in our target cities
            branch_map: dict[int, dict] = {
                b["id"]: b for b in raw_branches
                if b.get("city") in _CITY_MAP
            }
            logger.info(
                "Loaded %d clinic branches in target cities (of %d total)",
                len(branch_map), len(raw_branches),
            )

            logger.info("Fetching all active doctor-services...")
            # key=(branch_id, service_id) → lowest price
            best: dict[tuple[int, int], tuple[int, dict]] = {}

            next_url: str | None = f"{_BASE_URL}/doctor-services/?is_active=true&limit=100"
            total_fetched = 0
            while next_url:
                data = await client.get_json(next_url)
                for rec in data.get("results", []):
                    branch_id = rec.get("clinic_branch")
                    service_id = rec.get("service")
                    price = rec.get("price")
                    if not price or price <= 0:
                        continue
                    if branch_id not in branch_map:
                        continue
                    key = (branch_id, service_id)
                    existing = best.get(key)
                    if existing is None or price < existing[0]:
                        best[key] = (price, rec)
                total_fetched += len(data.get("results", []))
                next_url = data.get("next")

            logger.info(
                "Fetched %d total records → %d unique (branch, service) pairs with price",
                total_fetched, len(best),
            )

            for (branch_id, service_id), (price, _) in best.items():
                service_name = service_map.get(service_id)
                branch = branch_map.get(branch_id)
                if not service_name or not branch:
                    continue

                city_name = _CITY_MAP[branch["city"]]
                city_slug = _CITY_SLUG_MAP[branch["city"]]
                service_slug = service_slug_map.get(service_id, "")
                # Link to service search page — shows all doctors offering this service
                # in the city with prices. DOQ's own links use this pattern.
                source_url = f"https://doq.kz/doctors/{city_slug}/{service_slug}"

                items.append(
                    ParsedItem(
                        parser_source_slug=self.source_slug,
                        raw_clinic_name=f"{branch['name']} ({city_name})",
                        raw_service_name=service_name,
                        raw_price=str(price),
                        raw_currency="KZT",
                        raw_duration=None,
                        source_url=source_url,
                        parsed_at=parsed_at,
                    )
                )

        logger.info("DoQ total: %d items", len(items))
        return items

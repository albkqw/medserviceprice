import asyncio
import logging
from datetime import UTC, datetime

from app.parsers.base import BaseParser
from app.parsers.http_client import HttpClient
from app.parsers.models import ParsedItem

logger = logging.getLogger(__name__)

_BASE_API = "https://kdlolymp.kz/api/analysis"
_ANALYSIS_URL = "https://kdlolymp.kz/services/{slug}"

# city_id → display name used as raw_clinic_name
_CITIES: dict[int, str] = {
    136: "Алматы",
    98: "Астана",
    21: "Шымкент",
}


class KDLParser(BaseParser):
    """Fetches prices from the KDL (Olymp lab) JSON API.

    The API requires city_id to return prices; without it the price field is null.
    Pagination is controlled by the `page` query param; an empty `data` array signals the end.
    """

    source_slug = "kdl"

    async def parse(self) -> list[ParsedItem]:
        items: list[ParsedItem] = []
        parsed_at = datetime.now(UTC)

        async with HttpClient(delay=0.5) as client:
            for city_id, city_name in _CITIES.items():
                clinic_name = f"KDL {city_name}"
                page = 1
                city_total = 0

                while True:
                    url = f"{_BASE_API}?lang=ru-RU&city_id={city_id}&page={page}"
                    data = await client.get_json(url)
                    analyses = data.get("data", [])

                    if not analyses:
                        break

                    for entry in analyses:
                        price_data = entry.get("price")
                        if not price_data or price_data.get("price") is None:
                            continue

                        title = (entry.get("translation") or {}).get("title", "").strip()
                        if not title:
                            continue

                        slug = entry.get("slug") or str(entry["id"])
                        raw_price = str(int(price_data["price"]))

                        min_dur = price_data.get("min_duration")
                        max_dur = price_data.get("max_duration")
                        if min_dur is not None and max_dur is not None:
                            raw_duration = (
                                f"{min_dur} дней" if min_dur == max_dur else f"{min_dur}-{max_dur} дней"
                            )
                        else:
                            raw_duration = None

                        items.append(
                            ParsedItem(
                                parser_source_slug=self.source_slug,
                                raw_clinic_name=clinic_name,
                                raw_service_name=title,
                                raw_price=raw_price,
                                raw_currency="KZT",
                                raw_duration=raw_duration,
                                source_url=_ANALYSIS_URL.format(slug=slug),
                                parsed_at=parsed_at,
                            )
                        )
                        city_total += 1

                    logger.info("KDL %s page %d: %d analyses", city_name, page, len(analyses))
                    page += 1

                logger.info("KDL %s: %d items total", city_name, city_total)

        return items

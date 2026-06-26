import logging
import re
from datetime import UTC, datetime

from bs4 import BeautifulSoup

from app.parsers.base import BaseParser
from app.parsers.http_client import HttpClient
from app.parsers.models import ParsedItem

logger = logging.getLogger(__name__)

_BASE_URL = "https://invitro.kz"
_CATALOG_URL = "https://invitro.kz/analizes/for-doctors/{city}/"

_CITIES: dict[str, str] = {
    "almaty": "Алматы",
    "astana": "Астана",
    "shymkent": "Шымкент",
}


def _parse_price(text: str) -> str | None:
    digits = re.sub(r"[^\d]", "", text)
    return digits if digits else None


def _parse_duration(item_div) -> str | None:
    """Extract duration from the first add-list-item (time icon block)."""
    add_items = item_div.select("div.analyzes-item__add--list-item")
    for block in add_items:
        img = block.find("img")
        if img and "time.svg" in img.get("src", ""):
            span = block.find("span")
            if span:
                return span.get_text(strip=True)
    return None


class InvitroParser(BaseParser):
    """Fetches prices from invitro.kz by parsing server-rendered HTML pages."""

    source_slug = "invitro"

    async def parse(self) -> list[ParsedItem]:
        items: list[ParsedItem] = []
        parsed_at = datetime.now(UTC)

        async with HttpClient(delay=1.0) as client:
            for city_slug, city_name in _CITIES.items():
                clinic_name = f"ИНВИТРО {city_name}"
                url = _CATALOG_URL.format(city=city_slug)

                try:
                    html = await client.get_html(url)
                except Exception as exc:
                    logger.error("Failed to fetch %s: %s", url, exc)
                    continue

                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("div.analyzes-list.item_card")

                city_total = 0
                for card in cards:
                    title_tag = card.select_one("div.analyzes-item__title a")
                    price_tag = card.select_one("div.analyzes-item__total--sum")

                    if not title_tag or not price_tag:
                        continue

                    name = title_tag.get_text(strip=True)
                    href = title_tag.get("href", "")
                    source_url = _BASE_URL + href if href.startswith("/") else href

                    raw_price = _parse_price(price_tag.get_text())
                    if not raw_price or not name:
                        continue

                    duration = _parse_duration(card)

                    items.append(
                        ParsedItem(
                            parser_source_slug=self.source_slug,
                            raw_clinic_name=clinic_name,
                            raw_service_name=name,
                            raw_price=raw_price,
                            raw_currency="KZT",
                            raw_duration=duration,
                            source_url=source_url,
                            parsed_at=parsed_at,
                        )
                    )
                    city_total += 1

                logger.info("Invitro %s: %d items", city_name, city_total)

        return items

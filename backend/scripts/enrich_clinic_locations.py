"""Populate lat/lng (and address/phone) for all clinics.

Sources:
  - DOQ branches: lat/lng/address/phones fetched directly from api.doq.kz
  - KDL / Invitro: city-center coordinates (they are aggregated per city, no branch data)

Run from the backend/ directory:
    python -m scripts.enrich_clinic_locations
"""

import asyncio
import json
import logging
import urllib.request

from sqlalchemy import select, update

from app.db.engine import AsyncSessionLocal
from app.models.city import City
from app.models.clinic import Clinic

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# DOQ city_id → display name (matches how DOQ parser builds raw_clinic_name)
# ---------------------------------------------------------------------------
_DOQ_CITY_MAP: dict[int, str] = {
    3: "Алматы",
    1: "Астана",
    5: "Шымкент",
}

# ---------------------------------------------------------------------------
# City-center fallback coordinates for KDL / Invitro (aggregated per-city labs)
# ---------------------------------------------------------------------------
_CITY_CENTERS: dict[str, tuple[float, float]] = {
    "Алматы":  (43.2381, 76.8819),
    "Астана":  (51.1694, 71.4492),
    "Шымкент": (42.3000, 69.5903),
}


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "MedServicePrice/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _fetch_all_doq(endpoint: str) -> list[dict]:
    results = []
    next_url: str | None = endpoint
    while next_url:
        data = _fetch_json(next_url)
        results.extend(data.get("results", []))
        next_url = data.get("next")
    return results


def _build_doq_location_map() -> dict[str, dict]:
    """Build {clinic_name_as_stored_in_db → {lat, lng, address, phone}} from DOQ API."""
    logger.info("Fetching DOQ clinic branches…")
    branches = _fetch_all_doq("https://api.doq.kz/api/v1/clinic-branches/?limit=100")
    logger.info("Fetched %d DOQ branches", len(branches))

    location_map: dict[str, dict] = {}
    for b in branches:
        city_id = b.get("city")
        if city_id not in _DOQ_CITY_MAP:
            continue
        city_display = _DOQ_CITY_MAP[city_id]
        # Must match exactly how DoqParser builds raw_clinic_name:
        # f"{branch['name']} ({city_name})"
        key = f"{b['name']} ({city_display})"

        loc = b.get("location") or {}
        phones = b.get("phones") or []

        location_map[key] = {
            "lat": loc.get("lat"),
            "lng": loc.get("lng"),
            "address": b.get("address") or None,
            "phone": phones[0] if phones else None,
        }
    logger.info("Built location map with %d DOQ entries", len(location_map))
    return location_map


async def main() -> None:
    doq_map = _build_doq_location_map()

    async with AsyncSessionLocal() as session:
        # Load all clinics with their city names
        result = await session.execute(
            select(Clinic, City.name.label("city_name"))
            .join(City, Clinic.city_id == City.id)
            .where(Clinic.is_active == True)  # noqa: E712
        )
        rows = result.all()
        logger.info("Loaded %d clinics from DB", len(rows))

        updated = 0
        skipped = 0

        for clinic, city_name in rows:
            # Try DOQ location map first (exact name match)
            loc = doq_map.get(clinic.name)

            if loc and loc["lat"] is not None:
                # DOQ branch: we have precise coordinates + address + phone
                if clinic.lat != loc["lat"] or clinic.lng != loc["lng"]:
                    await session.execute(
                        update(Clinic)
                        .where(Clinic.id == clinic.id)
                        .values(
                            lat=loc["lat"],
                            lng=loc["lng"],
                            address=loc["address"] or clinic.address,
                            phone=loc["phone"] or clinic.phone,
                        )
                    )
                    updated += 1
            elif clinic.lat is None:
                # KDL / Invitro / anything without coordinates:
                # fall back to city-center so the clinic still appears on map
                center = _CITY_CENTERS.get(city_name)
                if center:
                    await session.execute(
                        update(Clinic)
                        .where(Clinic.id == clinic.id)
                        .values(lat=center[0], lng=center[1])
                    )
                    updated += 1
                else:
                    skipped += 1
            else:
                skipped += 1

        await session.commit()

    logger.info("Done — updated %d, skipped %d", updated, skipped)


if __name__ == "__main__":
    asyncio.run(main())

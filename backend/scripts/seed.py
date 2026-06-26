"""One-time seed script: inserts reference data needed before parsers can run.

Run from the backend/ directory:
    python -m scripts.seed

Idempotent — re-running is safe (ON CONFLICT DO NOTHING).
"""

import asyncio
import uuid

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.engine import AsyncSessionLocal
from app.models.city import City
from app.models.clinic import Clinic
from app.models.parser_source import ParserSource

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

_CITIES = [
    {"name": "Алматы", "slug": "almaty"},
    {"name": "Астана", "slug": "astana"},
    {"name": "Шымкент", "slug": "shymkent"},
]

_PARSER_SOURCES = [
    {
        "slug": "kdl",
        "name": "KDL Олимп",
        "base_url": "https://kdlolymp.kz",
        "is_active": True,
    },
    {
        "slug": "invitro",
        "name": "ИНВИТРО",
        "base_url": "https://invitro.kz",
        "is_active": True,
    },
    {
        "slug": "doq",
        "name": "DOQ.kz",
        "base_url": "https://doq.kz",
        "is_active": True,
    },
]

_INVITRO_CLINICS = {
    "almaty": {
        "name": "ИНВИТРО Алматы",
        "website": "https://invitro.kz",
        "source_url": "https://invitro.kz/analizes/for-doctors/almaty/",
    },
    "astana": {
        "name": "ИНВИТРО Астана",
        "website": "https://invitro.kz",
        "source_url": "https://invitro.kz/analizes/for-doctors/astana/",
    },
    "shymkent": {
        "name": "ИНВИТРО Шымкент",
        "website": "https://invitro.kz",
        "source_url": "https://invitro.kz/analizes/for-doctors/shymkent/",
    },
}

# KDL has one branch per city.  Keyed by city slug.
_KDL_CLINICS = {
    "almaty": {
        "name": "KDL Алматы",
        "website": "https://kdlolymp.kz",
        "source_url": "https://kdlolymp.kz/ru/analizy",
    },
    "astana": {
        "name": "KDL Астана",
        "website": "https://kdlolymp.kz",
        "source_url": "https://kdlolymp.kz/ru/analizy",
    },
    "shymkent": {
        "name": "KDL Шымкент",
        "website": "https://kdlolymp.kz",
        "source_url": "https://kdlolymp.kz/ru/analizy",
    },
}


async def main() -> None:
    async with AsyncSessionLocal() as session:
        # 1. Cities
        for row in _CITIES:
            await session.execute(
                pg_insert(City)
                .values(id=uuid.uuid4(), **row)
                .on_conflict_do_nothing(index_elements=["slug"])
            )
        await session.flush()

        # 2. ParserSources
        for row in _PARSER_SOURCES:
            await session.execute(
                pg_insert(ParserSource)
                .values(id=uuid.uuid4(), **row)
                .on_conflict_do_nothing(index_elements=["slug"])
            )
        await session.flush()

        # 3. Clinics (one KDL branch per city)
        from sqlalchemy import select

        cities_result = await session.execute(select(City))
        city_by_slug = {c.slug: c for c in cities_result.scalars().all()}

        for clinics_dict in (_KDL_CLINICS, _INVITRO_CLINICS):
            for city_slug, clinic_data in clinics_dict.items():
                city = city_by_slug.get(city_slug)
                if city is None:
                    print(f"Warning: city '{city_slug}' not found, skipping clinic")
                    continue
                await session.execute(
                    pg_insert(Clinic)
                    .values(id=uuid.uuid4(), city_id=city.id, **clinic_data)
                    .on_conflict_do_nothing(index_elements=["name", "city_id"])
                )

        await session.commit()

    print("Seed complete.")
    for c in _CITIES:
        print(f"  City: {c['name']} ({c['slug']})")
    for s in _PARSER_SOURCES:
        print(f"  ParserSource: {s['slug']} — {s['name']}")
    for clinics_dict in (_KDL_CLINICS, _INVITRO_CLINICS):
        for city_slug, clinic in clinics_dict.items():
            print(f"  Clinic: {clinic['name']} ({city_slug})")


if __name__ == "__main__":
    asyncio.run(main())

from fastapi import APIRouter

from app.routers import cities, clinics, health, search, services

# All v1 routes live under /api/v1.
# When v2 arrives, create app/api/v2/ and register a separate router in main.py.
router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(cities.router)
router.include_router(clinics.router)
router.include_router(services.router)
router.include_router(search.router)

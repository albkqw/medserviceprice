from fastapi import APIRouter

from app.routers import health

# All v1 routes live under /api/v1.
# When v2 arrives, create app/api/v2/ and register a separate router in main.py.
router = APIRouter(prefix="/api/v1")

router.include_router(health.router)

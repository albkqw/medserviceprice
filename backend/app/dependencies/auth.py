from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings

_api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


def require_admin_key(key: str | None = Security(_api_key_header)) -> None:
    if not key or key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing X-Admin-Key header")

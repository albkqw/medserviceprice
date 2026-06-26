import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MedServicePrice/1.0; +https://medserviceprice.kz)",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "ru-RU,ru;q=0.9",
}


class HttpClient:
    """Async HTTP client with retry and polite rate limiting.

    Use as an async context manager so the underlying connection pool
    is shared across all requests in a single parser run.
    """

    def __init__(self, delay: float = 0.5, retries: int = 3) -> None:
        self._delay = delay
        self._retries = retries
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "HttpClient":
        self._client = httpx.AsyncClient(headers=_HEADERS, timeout=30.0, follow_redirects=True)
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def get_json(self, url: str) -> Any:
        assert self._client is not None, "HttpClient must be used as an async context manager"
        last_exc: Exception | None = None
        for attempt in range(self._retries):
            try:
                resp = await self._client.get(url)
                resp.raise_for_status()
                await asyncio.sleep(self._delay)
                return resp.json()
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                last_exc = exc
                wait = self._delay * 2**attempt
                logger.warning("GET %s attempt %d failed: %s — retrying in %.1fs", url, attempt + 1, exc, wait)
                await asyncio.sleep(wait)
        raise RuntimeError(f"Failed to fetch {url} after {self._retries} attempts") from last_exc

    async def get_html(self, url: str) -> str:
        assert self._client is not None, "HttpClient must be used as an async context manager"
        last_exc: Exception | None = None
        for attempt in range(self._retries):
            try:
                resp = await self._client.get(url)
                resp.raise_for_status()
                await asyncio.sleep(self._delay)
                return resp.text
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                last_exc = exc
                wait = self._delay * 2**attempt
                logger.warning("GET %s attempt %d failed: %s — retrying in %.1fs", url, attempt + 1, exc, wait)
                await asyncio.sleep(wait)
        raise RuntimeError(f"Failed to fetch {url} after {self._retries} attempts") from last_exc

from abc import ABC, abstractmethod

from app.parsers.models import ParsedItem


class BaseParser(ABC):
    """All parsers inherit from this. Each subclass sets `source_slug` and
    implements `parse()` which returns a flat list of ParsedItems."""

    source_slug: str  # must match parser_sources.slug in DB

    @abstractmethod
    async def parse(self) -> list[ParsedItem]:
        """Fetch all pages and return extracted price items."""
        ...

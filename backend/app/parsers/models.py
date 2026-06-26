from datetime import datetime

from pydantic import BaseModel


class ParsedItem(BaseModel):
    """One price entry as extracted by a parser, before any normalization."""

    parser_source_slug: str
    raw_clinic_name: str
    raw_service_name: str
    raw_price: str
    raw_currency: str | None = None
    raw_duration: str | None = None
    source_url: str
    parsed_at: datetime

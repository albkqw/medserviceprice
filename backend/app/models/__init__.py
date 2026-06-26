# Import all models so they register on Base.metadata before Alembic inspects it.
# Every new model file must be added here.
from app.models.city import City
from app.models.clinic import Clinic
from app.models.enums import Currency, ParseRunStatus, ServiceCategory, UnmatchedStatus
from app.models.parse_run import ParseRun
from app.models.parser_source import ParserSource
from app.models.price import Price
from app.models.raw_price import RawPrice
from app.models.service import Service
from app.models.unmatched_service import UnmatchedService

__all__ = [
    "City",
    "Clinic",
    "Currency",
    "ParseRun",
    "ParseRunStatus",
    "ParserSource",
    "Price",
    "RawPrice",
    "Service",
    "ServiceCategory",
    "UnmatchedService",
    "UnmatchedStatus",
]

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ParseRunStatus


class ParseRunResponse(BaseModel):
    id: uuid.UUID
    source_slug: str
    status: ParseRunStatus
    attempt: int
    started_at: datetime
    finished_at: datetime | None
    items_saved: int | None
    items_skipped: int | None
    items_normalized: int | None
    error_message: str | None


class ScheduledJobResponse(BaseModel):
    id: str
    name: str
    next_run_time: datetime | None

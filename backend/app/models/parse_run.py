import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ParseRunStatus


class ParseRun(Base):
    __tablename__ = "parse_runs"
    __table_args__ = (
        Index("ix_parse_run_source_started", "source_slug", "started_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_slug: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[ParseRunStatus] = mapped_column(
        SAEnum(ParseRunStatus, name="parse_run_status", create_type=True),
        nullable=False,
        default=ParseRunStatus.running,
    )
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    items_saved: Mapped[int | None] = mapped_column(Integer, nullable=True)
    items_skipped: Mapped[int | None] = mapped_column(Integer, nullable=True)
    items_normalized: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<ParseRun source={self.source_slug!r} status={self.status} attempt={self.attempt}>"

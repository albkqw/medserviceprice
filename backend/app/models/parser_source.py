import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ParserSource(Base, TimestampMixin):
    __tablename__ = "parser_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Stable code-level identifier. Used in checksum computation — never rename a live slug.
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    last_parsed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    raw_prices: Mapped[list["RawPrice"]] = relationship(back_populates="parser_source")
    unmatched_services: Mapped[list["UnmatchedService"]] = relationship(back_populates="parser_source")

    def __repr__(self) -> str:
        return f"<ParserSource slug={self.slug!r}>"

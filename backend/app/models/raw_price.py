import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RawPrice(Base):
    __tablename__ = "raw_prices"
    __table_args__ = (
        Index("ix_raw_price_parser_parsed_at", "parser_source_id", "parsed_at"),
        Index("ix_raw_price_is_processed", "is_processed"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    parser_source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parser_sources.id", ondelete="RESTRICT"), nullable=False
    )
    # Nullable: resolved at parse time if possible; left null if clinic is not yet known.
    clinic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id", ondelete="SET NULL"), nullable=True
    )
    raw_clinic_name: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_service_name: Mapped[str] = mapped_column(String(500), nullable=False)
    raw_price: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    raw_duration: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    # SHA-256 of (parser_slug + raw_clinic_name + raw_service_name + raw_price).
    # UNIQUE constraint makes this the deduplication guard — no SELECT needed before INSERT.
    checksum: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    parsed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_processed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parser_source: Mapped["ParserSource"] = relationship(back_populates="raw_prices")
    clinic: Mapped["Clinic | None"] = relationship(back_populates="raw_prices")
    price: Mapped["Price | None"] = relationship(back_populates="raw_price", uselist=False)
    unmatched_service: Mapped["UnmatchedService | None"] = relationship(
        back_populates="raw_price", uselist=False
    )

    def __repr__(self) -> str:
        return f"<RawPrice id={self.id} service={self.raw_service_name!r}>"

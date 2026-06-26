import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import UnmatchedStatus


class UnmatchedService(Base, TimestampMixin):
    __tablename__ = "unmatched_services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    raw_price_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_prices.id", ondelete="CASCADE"), nullable=False
    )
    raw_service_name: Mapped[str] = mapped_column(String(500), nullable=False)
    parser_source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parser_sources.id", ondelete="RESTRICT"), nullable=False
    )
    # Set by a normalizer (fuzzy match, AI, etc.) as a suggestion for human review.
    suggested_service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[UnmatchedStatus] = mapped_column(
        SAEnum(UnmatchedStatus, name="unmatched_status", create_type=True),
        nullable=False,
        default=UnmatchedStatus.pending,
        server_default="pending",
    )

    raw_price: Mapped["RawPrice"] = relationship(back_populates="unmatched_service")
    parser_source: Mapped["ParserSource"] = relationship(back_populates="unmatched_services")
    suggested_service: Mapped["Service | None"] = relationship(
        back_populates="unmatched_services",
        foreign_keys=[suggested_service_id],
    )

    def __repr__(self) -> str:
        return f"<UnmatchedService id={self.id} status={self.status} name={self.raw_service_name!r}>"

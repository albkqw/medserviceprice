import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Index, Integer, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import Currency


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (
        # Search: "show me all clinics offering service X, active prices only, sorted by price"
        Index("ix_price_service_active_kzt", "service_id", "is_active", "price_kzt"),
        # Lookup: "all active prices for clinic Y"
        Index("ix_price_clinic_service_active", "clinic_id", "service_id", "is_active"),
        # Staleness filter: "exclude prices older than 30 days"
        Index("ix_price_parsed_at", "parsed_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    # Nullable: allows manually entered prices with no raw source.
    raw_price_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_prices.id", ondelete="SET NULL"), nullable=True
    )
    price_kzt: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[Currency] = mapped_column(
        SAEnum(Currency, name="currency", create_type=True),
        nullable=False,
        default=Currency.KZT,
        server_default="KZT",
    )
    duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parsed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    clinic: Mapped["Clinic"] = relationship(back_populates="prices")
    service: Mapped["Service"] = relationship(back_populates="prices")
    raw_price: Mapped["RawPrice | None"] = relationship(back_populates="price")

    def __repr__(self) -> str:
        return f"<Price id={self.id} price_kzt={self.price_kzt} active={self.is_active}>"

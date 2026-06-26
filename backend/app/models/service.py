import uuid

from sqlalchemy import Boolean, Enum as SAEnum, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import ServiceCategory


class Service(Base, TimestampMixin):
    __tablename__ = "services"
    __table_args__ = (
        # GIN index lets PostgreSQL search inside the JSONB synonyms array efficiently.
        Index("ix_service_synonyms_gin", "synonyms", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    category: Mapped[ServiceCategory] = mapped_column(
        SAEnum(ServiceCategory, name="service_category", create_type=True),
        nullable=False,
    )
    synonyms: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    prices: Mapped[list["Price"]] = relationship(back_populates="service")
    unmatched_services: Mapped[list["UnmatchedService"]] = relationship(
        back_populates="suggested_service",
        foreign_keys="UnmatchedService.suggested_service_id",
    )

    def __repr__(self) -> str:
        return f"<Service id={self.id} name={self.name!r}>"

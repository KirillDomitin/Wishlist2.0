import enum
import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ReservationStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"


class ItemReadModel(Base):
    """Local read-model of wishlist items, kept in sync via stream:wishlist_items."""

    __tablename__ = "item_read_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    wishlist_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    target_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    image_urls: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)

    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation", back_populates="item"
    )


class Reservation(Base, TimestampMixin):
    __tablename__ = "reservations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("item_read_models.id"),
        nullable=False,
        index=True,
    )
    reserver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus), nullable=False, default=ReservationStatus.active
    )

    item: Mapped["ItemReadModel"] = relationship("ItemReadModel", back_populates="reservations")

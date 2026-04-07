import secrets
import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Wishlist(Base, TimestampMixin):
    __tablename__ = "wishlists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    share_token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        default=lambda: secrets.token_urlsafe(16),
    )
    surprise_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    items: Mapped[list["WishlistItem"]] = relationship(
        "WishlistItem", back_populates="wishlist", cascade="all, delete-orphan"
    )


class WishlistItem(Base, TimestampMixin):
    __tablename__ = "wishlist_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    wishlist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wishlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    target_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    reserved_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    wishlist: Mapped["Wishlist"] = relationship("Wishlist", back_populates="items")

    @property
    def is_fully_reserved(self) -> bool:
        return self.reserved_count >= self.target_quantity

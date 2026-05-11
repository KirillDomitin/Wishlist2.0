import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ── Item schemas ─────────────────────────────────────────────────────────────

class WishlistItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    url: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    image_urls: list[str] = Field(default_factory=list)
    target_quantity: int = Field(default=1, ge=1)
    priority: int = Field(default=0, ge=0, le=2)


class WishlistItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    url: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    image_urls: list[str] | None = None
    target_quantity: int | None = Field(default=None, ge=1)
    priority: int | None = Field(default=None, ge=0, le=2)


class WishlistItemResponse(BaseModel):
    id: uuid.UUID
    wishlist_id: uuid.UUID
    title: str
    description: str | None
    url: str | None
    price: Decimal | None
    image_urls: list[str]
    target_quantity: int
    reserved_count: int
    is_fully_reserved: bool
    priority: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_masked(cls, item: object) -> "WishlistItemResponse":
        """Returns item without reserver identity (surprise mode for owner).
        reserved_count and is_fully_reserved are preserved so the owner can
        still see which gifts are taken."""
        return cls.model_validate(item)


# ── Wishlist schemas ──────────────────────────────────────────────────────────

class WishlistCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    is_public: bool = True
    surprise_mode: bool = False
    event_date: date | None = None


class WishlistUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    is_public: bool | None = None
    surprise_mode: bool | None = None
    event_date: date | None = None


class WishlistSummaryResponse(BaseModel):
    """Returned in list — no items to keep payload small."""
    id: uuid.UUID
    title: str
    is_public: bool
    share_token: str
    surprise_mode: bool
    event_date: date | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WishlistDetailResponse(BaseModel):
    """Returned for single wishlist — includes items."""
    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    is_public: bool
    share_token: str
    surprise_mode: bool
    event_date: date | None
    items: list[WishlistItemResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminWishlistResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    is_public: bool
    surprise_mode: bool
    event_date: date | None
    item_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
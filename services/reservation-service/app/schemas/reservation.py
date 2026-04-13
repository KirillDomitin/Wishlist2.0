import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.reservation import ReservationStatus


class ReservationCreate(BaseModel):
    item_id: uuid.UUID
    quantity: int = Field(default=1, ge=1)


class ItemReservationInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: uuid.UUID
    reserver_id: uuid.UUID
    quantity: int


class ItemSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    price: Decimal | None
    image_urls: list[str]
    target_quantity: int


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    item_id: uuid.UUID
    reserver_id: uuid.UUID
    quantity: int
    status: ReservationStatus
    item: ItemSummary | None = None

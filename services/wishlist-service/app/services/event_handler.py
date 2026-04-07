import uuid

from app.core.database import AsyncSessionLocal
from app.repositories.item_repository import WishlistItemRepository


async def handle_reservation_event(event_type: str, data: dict[str, str]) -> None:
    """Consumes events from reservation-service and updates reserved_count."""
    item_id = uuid.UUID(data["item_id"])
    quantity = int(data.get("quantity", "1"))

    async with AsyncSessionLocal() as session:
        repo = WishlistItemRepository(session)
        if event_type == "reservation.created":
            await repo.increment_reserved_count(item_id, quantity)
        elif event_type == "reservation.cancelled":
            await repo.decrement_reserved_count(item_id, quantity)

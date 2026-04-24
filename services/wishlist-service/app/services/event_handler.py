import uuid

from app.core.database import AsyncSessionLocal
from app.repositories.item_repository import WishlistItemRepository


async def handle_reservation_event(event_type: str, data: dict[str, str]) -> None:
    """Process reservation lifecycle events and update item reserved counts.

    Handles ``reservation.created`` (increments) and ``reservation.cancelled``
    (decrements) to keep ``WishlistItem.reserved_count`` in sync with the
    reservation service.

    Args:
        event_type: One of ``reservation.created``, ``reservation.cancelled``.
        data: Event payload fields as string key-value pairs.
    """
    item_id = uuid.UUID(data["item_id"])
    quantity = int(data.get("quantity", "1"))

    async with AsyncSessionLocal() as session:
        repo = WishlistItemRepository(session)
        if event_type == "reservation.created":
            await repo.increment_reserved_count(item_id, quantity)
        elif event_type == "reservation.cancelled":
            await repo.decrement_reserved_count(item_id, quantity)

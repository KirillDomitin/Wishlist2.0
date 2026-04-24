import uuid
from decimal import Decimal

from app.core.database import AsyncSessionLocal
from app.repositories.reservation_repository import ItemReadModelRepository


async def handle_wishlist_item_event(event_type: str, data: dict[str, str]) -> None:
    """Process item lifecycle events from the wishlist service.

    Handles ``item.created`` and ``item.deleted`` to keep the local
    ItemReadModel in sync with wishlist-service data.

    Args:
        event_type: One of ``item.created``, ``item.deleted``.
        data: Event payload fields as string key-value pairs.
    """
    async with AsyncSessionLocal() as session:
        repo = ItemReadModelRepository(session)

        if event_type == "item.created":
            raw_price = data.get("price")
            raw_image_urls = data.get("image_urls", "")
            image_urls = [u for u in raw_image_urls.split(",") if u] if raw_image_urls else []
            raw_owner_id = data.get("owner_id")
            await repo.upsert(
                item_id=uuid.UUID(data["item_id"]),
                wishlist_id=uuid.UUID(data["wishlist_id"]),
                target_quantity=int(data.get("target_quantity", "1")),
                title=data.get("title", ""),
                price=Decimal(raw_price) if raw_price else None,
                image_urls=image_urls,
                owner_id=uuid.UUID(raw_owner_id) if raw_owner_id else None,
                surprise_mode=data.get("surprise_mode", "False").lower() == "true",
            )

        elif event_type == "item.deleted":
            await repo.mark_deleted(uuid.UUID(data["item_id"]))

import uuid
from decimal import Decimal

from app.core.database import AsyncSessionLocal
from app.repositories.reservation_repository import ItemReadModelRepository


async def handle_wishlist_item_event(event_type: str, data: dict[str, str]) -> None:
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

        elif event_type == "item.updated":
            target_quantity = data.get("target_quantity")
            if target_quantity is not None:
                item = await repo.get(uuid.UUID(data["item_id"]))
                if item:
                    item.target_quantity = int(target_quantity)
                    await session.commit()

        elif event_type == "item.deleted":
            await repo.mark_deleted(uuid.UUID(data["item_id"]))

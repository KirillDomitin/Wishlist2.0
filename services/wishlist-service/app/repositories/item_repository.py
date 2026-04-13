import uuid
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wishlist import WishlistItem


class WishlistItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, item_id: uuid.UUID) -> WishlistItem | None:
        result = await self._session.execute(
            select(WishlistItem).where(WishlistItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        wishlist_id: uuid.UUID,
        title: str,
        description: str | None,
        url: str | None,
        price: Decimal | None,
        image_urls: list[str],
        target_quantity: int,
    ) -> WishlistItem:
        item = WishlistItem(
            wishlist_id=wishlist_id,
            title=title,
            description=description,
            url=url,
            price=price,
            image_urls=image_urls,
            target_quantity=target_quantity,
        )
        self._session.add(item)
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def update(self, item: WishlistItem, data: dict) -> WishlistItem:
        for field, value in data.items():
            if value is not None:
                setattr(item, field, value)
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def delete(self, item: WishlistItem) -> None:
        await self._session.delete(item)
        await self._session.commit()

    async def increment_reserved_count(
        self, item_id: uuid.UUID, quantity: int
    ) -> None:
        await self._session.execute(
            update(WishlistItem)
            .where(WishlistItem.id == item_id)
            .values(reserved_count=WishlistItem.reserved_count + quantity)
        )
        await self._session.commit()

    async def decrement_reserved_count(
        self, item_id: uuid.UUID, quantity: int
    ) -> None:
        await self._session.execute(
            update(WishlistItem)
            .where(WishlistItem.id == item_id)
            .values(
                reserved_count=WishlistItem.reserved_count - quantity
            )
        )
        await self._session.commit()

import uuid
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wishlist import WishlistItem


class WishlistItemRepository:
    """Repository for WishlistItem persistence operations.

    Args:
        session: Active async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, item_id: uuid.UUID) -> WishlistItem | None:
        """Fetch a wishlist item by primary key.

        Args:
            item_id: Item primary key.

        Returns:
            The matching WishlistItem, or ``None`` if not found.
        """
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
        priority: int = 0,
    ) -> WishlistItem:
        """Persist a new wishlist item and return the created instance.

        Args:
            wishlist_id: Parent wishlist ID.
            title: Item display name.
            description: Optional free-text description.
            url: Optional link to the item.
            price: Optional price value.
            image_urls: Ordered list of image URL paths.
            target_quantity: Maximum number of reservations allowed.
            priority: Sort priority; higher values appear first.

        Returns:
            The newly created WishlistItem instance.
        """
        item = WishlistItem(
            wishlist_id=wishlist_id,
            title=title,
            description=description,
            url=url,
            price=price,
            image_urls=image_urls,
            target_quantity=target_quantity,
            priority=priority,
        )
        self._session.add(item)
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def update(self, item: WishlistItem, data: dict) -> WishlistItem:
        """Apply a partial update to a wishlist item and persist the changes.

        Args:
            item: The WishlistItem instance to update.
            data: Mapping of field names to new values; ``None`` values are skipped.

        Returns:
            The updated WishlistItem instance.
        """
        for field, value in data.items():
            if value is not None:
                setattr(item, field, value)
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def delete(self, item: WishlistItem) -> None:
        """Delete a wishlist item from the database.

        Args:
            item: The WishlistItem instance to delete.
        """
        await self._session.delete(item)
        await self._session.commit()

    async def increment_reserved_count(
        self, item_id: uuid.UUID, quantity: int
    ) -> None:
        """Increment an item's reserved_count by the given quantity.

        Args:
            item_id: Item primary key.
            quantity: Amount to add to the current reserved count.
        """
        await self._session.execute(
            update(WishlistItem)
            .where(WishlistItem.id == item_id)
            .values(reserved_count=WishlistItem.reserved_count + quantity)
        )
        await self._session.commit()

    async def decrement_reserved_count(
        self, item_id: uuid.UUID, quantity: int
    ) -> None:
        """Decrement an item's reserved_count by the given quantity.

        Args:
            item_id: Item primary key.
            quantity: Amount to subtract from the current reserved count.
        """
        await self._session.execute(
            update(WishlistItem)
            .where(WishlistItem.id == item_id)
            .values(
                reserved_count=WishlistItem.reserved_count - quantity
            )
        )
        await self._session.commit()

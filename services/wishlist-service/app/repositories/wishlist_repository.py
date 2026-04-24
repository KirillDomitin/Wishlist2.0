import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.wishlist import Wishlist


class WishlistRepository:
    """Repository for Wishlist persistence operations.

    Args:
        session: Active async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, wishlist_id: uuid.UUID) -> Wishlist | None:
        """Fetch a wishlist by primary key (without items).

        Args:
            wishlist_id: Wishlist primary key.

        Returns:
            The matching Wishlist, or ``None`` if not found.
        """
        result = await self._session.execute(
            select(Wishlist).where(Wishlist.id == wishlist_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_items(self, wishlist_id: uuid.UUID) -> Wishlist | None:
        """Fetch a wishlist by primary key with items eager-loaded.

        Args:
            wishlist_id: Wishlist primary key.

        Returns:
            The matching Wishlist with ``items`` loaded, or ``None`` if not found.
        """
        result = await self._session.execute(
            select(Wishlist)
            .options(selectinload(Wishlist.items))
            .where(Wishlist.id == wishlist_id)
        )
        return result.scalar_one_or_none()

    async def get_by_share_token(self, token: str) -> Wishlist | None:
        """Fetch a wishlist by its public share token with items eager-loaded.

        Args:
            token: Unique share token string.

        Returns:
            The matching Wishlist with ``items`` loaded, or ``None`` if not found.
        """
        result = await self._session.execute(
            select(Wishlist)
            .options(selectinload(Wishlist.items))
            .where(Wishlist.share_token == token)
        )
        return result.scalar_one_or_none()

    async def get_all_by_owner(self, owner_id: uuid.UUID) -> list[Wishlist]:
        """Return all wishlists belonging to an owner.

        Args:
            owner_id: Owner user ID.

        Returns:
            List of Wishlist instances (items not loaded).
        """
        result = await self._session.execute(
            select(Wishlist).where(Wishlist.owner_id == owner_id)
        )
        return list(result.scalars().all())

    async def create(
        self,
        owner_id: uuid.UUID,
        title: str,
        is_public: bool,
        surprise_mode: bool,
        event_date: date | None = None,
    ) -> Wishlist:
        """Persist a new wishlist and return the created instance.

        Args:
            owner_id: Owner user ID.
            title: Wishlist display title.
            is_public: Whether the wishlist is publicly visible.
            surprise_mode: Whether reserver identities are hidden from the owner.
            event_date: Optional target date for the event.

        Returns:
            The newly created Wishlist instance.
        """
        wishlist = Wishlist(
            owner_id=owner_id,
            title=title,
            is_public=is_public,
            surprise_mode=surprise_mode,
            event_date=event_date,
        )
        self._session.add(wishlist)
        await self._session.commit()
        await self._session.refresh(wishlist)
        return wishlist

    async def update(self, wishlist: Wishlist, data: dict) -> Wishlist:
        """Apply a partial update to a wishlist and persist the changes.

        Args:
            wishlist: The Wishlist instance to update.
            data: Mapping of field names to new values; ``None`` values are skipped.

        Returns:
            The updated Wishlist instance.
        """
        for field, value in data.items():
            if value is not None:
                setattr(wishlist, field, value)
        await self._session.commit()
        await self._session.refresh(wishlist)
        return wishlist

    async def delete(self, wishlist: Wishlist) -> None:
        """Delete a wishlist and all its items from the database.

        Args:
            wishlist: The Wishlist instance to delete.
        """
        await self._session.delete(wishlist)
        await self._session.commit()

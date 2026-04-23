import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.wishlist import Wishlist


class WishlistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, wishlist_id: uuid.UUID) -> Wishlist | None:
        result = await self._session.execute(
            select(Wishlist).where(Wishlist.id == wishlist_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_items(self, wishlist_id: uuid.UUID) -> Wishlist | None:
        result = await self._session.execute(
            select(Wishlist)
            .options(selectinload(Wishlist.items))
            .where(Wishlist.id == wishlist_id)
        )
        return result.scalar_one_or_none()

    async def get_by_share_token(self, token: str) -> Wishlist | None:
        result = await self._session.execute(
            select(Wishlist)
            .options(selectinload(Wishlist.items))
            .where(Wishlist.share_token == token)
        )
        return result.scalar_one_or_none()

    async def get_all_by_owner(self, owner_id: uuid.UUID) -> list[Wishlist]:
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
        for field, value in data.items():
            if value is not None:
                setattr(wishlist, field, value)
        await self._session.commit()
        await self._session.refresh(wishlist)
        return wishlist

    async def delete(self, wishlist: Wishlist) -> None:
        await self._session.delete(wishlist)
        await self._session.commit()

import uuid

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.streams import StreamProducer
from app.repositories.item_repository import WishlistItemRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.wishlist import (
    WishlistCreate,
    WishlistDetailResponse,
    WishlistItemCreate,
    WishlistItemResponse,
    WishlistItemUpdate,
    WishlistSummaryResponse,
    WishlistUpdate,
)

_STREAM_WISHLIST_ITEMS = "stream:wishlist_items"


class WishlistService:
    """Business logic for managing wishlists and their items.

    Args:
        session: Active async database session.
        redis: Active Redis client used for event publishing.
    """

    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self._repo = WishlistRepository(session)
        self._item_repo = WishlistItemRepository(session)
        self._producer = StreamProducer(redis, _STREAM_WISHLIST_ITEMS)

    # ── Wishlists ─────────────────────────────────────────────────────────────

    async def create(
        self, owner_id: uuid.UUID, data: WishlistCreate
    ) -> WishlistSummaryResponse:
        """Create a new wishlist for the given owner.

        Args:
            owner_id: ID of the user creating the wishlist.
            data: Wishlist creation payload.

        Returns:
            Summary response schema for the created wishlist.
        """
        wishlist = await self._repo.create(
            owner_id=owner_id,
            title=data.title,
            is_public=data.is_public,
            surprise_mode=data.surprise_mode,
            event_date=data.event_date,
        )
        return WishlistSummaryResponse.model_validate(wishlist)

    async def list_my(self, owner_id: uuid.UUID) -> list[WishlistSummaryResponse]:
        """Return summary responses for all wishlists owned by the user.

        Args:
            owner_id: Owner user ID.

        Returns:
            List of wishlist summary response schemas.
        """
        wishlists = await self._repo.get_all_by_owner(owner_id)
        return [WishlistSummaryResponse.model_validate(w) for w in wishlists]

    async def get_detail(
        self, wishlist_id: uuid.UUID, owner_id: uuid.UUID
    ) -> WishlistDetailResponse:
        """Return the full detail of a wishlist, enforcing owner-only access.

        In surprise mode, item details visible to the owner are masked.

        Args:
            wishlist_id: Wishlist primary key.
            owner_id: ID of the requesting user; must match the wishlist owner.

        Returns:
            Detailed wishlist response schema including items.

        Raises:
            NotFoundError: If the wishlist does not exist.
            ForbiddenError: If the requesting user is not the owner.
        """
        wishlist = await self._repo.get_by_id_with_items(wishlist_id)
        if not wishlist:
            raise NotFoundError("Wishlist not found")
        if wishlist.owner_id != owner_id:
            raise ForbiddenError()

        items = [
            WishlistItemResponse.from_orm_masked(item)
            if wishlist.surprise_mode
            else WishlistItemResponse.model_validate(item)
            for item in wishlist.items
        ]
        return WishlistDetailResponse(
            **{
                k: getattr(wishlist, k)
                for k in ("id", "owner_id", "title", "is_public",
                          "share_token", "surprise_mode", "event_date", "created_at")
            },
            items=items,
        )

    async def get_by_share_token(self, token: str) -> WishlistDetailResponse:
        """Return the public view of a wishlist identified by its share token.

        Args:
            token: Unique share token string.

        Returns:
            Detailed wishlist response schema including items.

        Raises:
            NotFoundError: If no wishlist matches the token.
        """
        wishlist = await self._repo.get_by_share_token(token)
        if not wishlist:
            raise NotFoundError("Wishlist not found")

        items = [WishlistItemResponse.model_validate(item) for item in wishlist.items]
        return WishlistDetailResponse(
            **{
                k: getattr(wishlist, k)
                for k in ("id", "owner_id", "title", "is_public",
                          "share_token", "surprise_mode", "event_date", "created_at")
            },
            items=items,
        )

    async def update(
        self, wishlist_id: uuid.UUID, owner_id: uuid.UUID, data: WishlistUpdate
    ) -> WishlistSummaryResponse:
        """Apply a partial update to a wishlist, enforcing owner-only access.

        Args:
            wishlist_id: Wishlist primary key.
            owner_id: ID of the requesting user; must match the wishlist owner.
            data: Fields to update; ``None`` fields are ignored.

        Returns:
            Updated wishlist summary response schema.

        Raises:
            NotFoundError: If the wishlist does not exist.
            ForbiddenError: If the requesting user is not the owner.
        """
        wishlist = await self._repo.get_by_id(wishlist_id)
        if not wishlist:
            raise NotFoundError("Wishlist not found")
        if wishlist.owner_id != owner_id:
            raise ForbiddenError()
        wishlist = await self._repo.update(
            wishlist, data.model_dump(exclude_none=True)
        )
        return WishlistSummaryResponse.model_validate(wishlist)

    async def delete(self, wishlist_id: uuid.UUID, owner_id: uuid.UUID) -> None:
        """Delete a wishlist, enforcing owner-only access.

        Args:
            wishlist_id: Wishlist primary key.
            owner_id: ID of the requesting user; must match the wishlist owner.

        Raises:
            NotFoundError: If the wishlist does not exist.
            ForbiddenError: If the requesting user is not the owner.
        """
        wishlist = await self._repo.get_by_id(wishlist_id)
        if not wishlist:
            raise NotFoundError("Wishlist not found")
        if wishlist.owner_id != owner_id:
            raise ForbiddenError()
        await self._repo.delete(wishlist)

    # ── Items ─────────────────────────────────────────────────────────────────

    async def add_item(
        self, wishlist_id: uuid.UUID, owner_id: uuid.UUID, data: WishlistItemCreate
    ) -> WishlistItemResponse:
        """Add a new item to a wishlist and publish an ``item.created`` event.

        Args:
            wishlist_id: Parent wishlist ID.
            owner_id: ID of the requesting user; must match the wishlist owner.
            data: Item creation payload.

        Returns:
            Response schema for the created item.

        Raises:
            NotFoundError: If the wishlist does not exist.
            ForbiddenError: If the requesting user is not the owner.
        """
        wishlist = await self._repo.get_by_id(wishlist_id)
        if not wishlist:
            raise NotFoundError("Wishlist not found")
        if wishlist.owner_id != owner_id:
            raise ForbiddenError()

        item = await self._item_repo.create(
            wishlist_id=wishlist_id,
            title=data.title,
            description=data.description,
            url=data.url,
            price=data.price,
            image_urls=data.image_urls,
            target_quantity=data.target_quantity,
            priority=data.priority,
        )
        await self._producer.publish(
            "item.created",
            {
                "item_id": str(item.id),
                "wishlist_id": str(wishlist_id),
                "owner_id": str(owner_id),
                "surprise_mode": str(wishlist.surprise_mode),
                "target_quantity": str(item.target_quantity),
                "title": item.title,
                "price": str(item.price) if item.price is not None else "",
                "image_urls": ",".join(item.image_urls),
            },
        )
        return WishlistItemResponse.model_validate(item)

    async def update_item(
        self,
        wishlist_id: uuid.UUID,
        item_id: uuid.UUID,
        owner_id: uuid.UUID,
        data: WishlistItemUpdate,
    ) -> WishlistItemResponse:
        """Apply a partial update to a wishlist item, enforcing owner-only access.

        Args:
            wishlist_id: Parent wishlist ID.
            item_id: Item primary key.
            owner_id: ID of the requesting user; must match the wishlist owner.
            data: Fields to update; ``None`` fields are ignored.

        Returns:
            Updated item response schema.

        Raises:
            NotFoundError: If the wishlist or item does not exist.
            ForbiddenError: If the requesting user is not the owner.
        """
        wishlist = await self._repo.get_by_id(wishlist_id)
        if not wishlist:
            raise NotFoundError("Wishlist not found")
        if wishlist.owner_id != owner_id:
            raise ForbiddenError()

        item = await self._item_repo.get_by_id(item_id)
        if not item or item.wishlist_id != wishlist_id:
            raise NotFoundError("Item not found")

        item = await self._item_repo.update(item, data.model_dump(exclude_none=True))
        return WishlistItemResponse.model_validate(item)

    async def delete_item(
        self, wishlist_id: uuid.UUID, item_id: uuid.UUID, owner_id: uuid.UUID
    ) -> None:
        """Delete a wishlist item and publish an ``item.deleted`` event.

        Args:
            wishlist_id: Parent wishlist ID.
            item_id: Item primary key.
            owner_id: ID of the requesting user; must match the wishlist owner.

        Raises:
            NotFoundError: If the wishlist or item does not exist.
            ForbiddenError: If the requesting user is not the owner.
        """
        wishlist = await self._repo.get_by_id(wishlist_id)
        if not wishlist:
            raise NotFoundError("Wishlist not found")
        if wishlist.owner_id != owner_id:
            raise ForbiddenError()

        item = await self._item_repo.get_by_id(item_id)
        if not item or item.wishlist_id != wishlist_id:
            raise NotFoundError("Item not found")

        await self._item_repo.delete(item)
        await self._producer.publish("item.deleted", {"item_id": str(item_id)})

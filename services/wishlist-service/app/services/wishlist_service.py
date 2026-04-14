import uuid

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.streams import StreamProducer
from app.repositories.item_repository import WishlistItemRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.wishlist import (
    ScrapedItemData,
    WishlistCreate,
    WishlistDetailResponse,
    WishlistItemCreate,
    WishlistItemResponse,
    WishlistItemUpdate,
    WishlistSummaryResponse,
    WishlistUpdate,
)
from app.services.meta_scraper import fetch_url_meta

_STREAM_WISHLIST_ITEMS = "stream:wishlist_items"


class WishlistService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self._repo = WishlistRepository(session)
        self._item_repo = WishlistItemRepository(session)
        self._producer = StreamProducer(redis, _STREAM_WISHLIST_ITEMS)

    # ── Wishlists ─────────────────────────────────────────────────────────────

    async def create(
        self, owner_id: uuid.UUID, data: WishlistCreate
    ) -> WishlistSummaryResponse:
        wishlist = await self._repo.create(
            owner_id=owner_id,
            title=data.title,
            is_public=data.is_public,
            surprise_mode=data.surprise_mode,
        )
        return WishlistSummaryResponse.model_validate(wishlist)

    async def list_my(self, owner_id: uuid.UUID) -> list[WishlistSummaryResponse]:
        wishlists = await self._repo.get_all_by_owner(owner_id)
        return [WishlistSummaryResponse.model_validate(w) for w in wishlists]

    async def get_detail(
        self, wishlist_id: uuid.UUID, owner_id: uuid.UUID
    ) -> WishlistDetailResponse:
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
                          "share_token", "surprise_mode", "created_at")
            },
            items=items,
        )

    async def get_by_share_token(self, token: str) -> WishlistDetailResponse:
        wishlist = await self._repo.get_by_share_token(token)
        if not wishlist:
            raise NotFoundError("Wishlist not found")

        items = [WishlistItemResponse.model_validate(item) for item in wishlist.items]
        return WishlistDetailResponse(
            **{
                k: getattr(wishlist, k)
                for k in ("id", "owner_id", "title", "is_public",
                          "share_token", "surprise_mode", "created_at")
            },
            items=items,
        )

    async def update(
        self, wishlist_id: uuid.UUID, owner_id: uuid.UUID, data: WishlistUpdate
    ) -> WishlistSummaryResponse:
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

    async def scrape_url(self, url: str) -> ScrapedItemData:
        data = await fetch_url_meta(url)
        return ScrapedItemData(
            title=data.get("title"),
            price=data.get("price"),
            image_url=data.get("image_url"),
        )

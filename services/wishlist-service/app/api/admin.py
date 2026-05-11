import uuid
from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.exceptions import NotFoundError
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.wishlist import AdminWishlistResponse

router = APIRouter(prefix="/api/wishlists/admin", dependencies=[Depends(require_admin)])


class AdminWishlistUpdateRequest(BaseModel):
    title: str | None = None
    is_public: bool | None = None
    surprise_mode: bool | None = None
    event_date: date | None = None


@router.get("/wishlists", response_model=list[AdminWishlistResponse])
async def list_all_wishlists(db: AsyncSession = Depends(get_db)) -> list[AdminWishlistResponse]:
    rows = await WishlistRepository(db).get_all_with_stats()
    return [
        AdminWishlistResponse(
            id=wishlist.id,
            owner_id=wishlist.owner_id,
            title=wishlist.title,
            is_public=wishlist.is_public,
            surprise_mode=wishlist.surprise_mode,
            event_date=wishlist.event_date,
            item_count=item_count,
            created_at=wishlist.created_at,
        )
        for wishlist, item_count in rows
    ]


@router.patch("/wishlists/{wishlist_id}", response_model=AdminWishlistResponse)
async def update_wishlist(
    wishlist_id: uuid.UUID,
    data: AdminWishlistUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> AdminWishlistResponse:
    repo = WishlistRepository(db)
    wishlist = await repo.get_by_id(wishlist_id)
    if not wishlist:
        raise NotFoundError("Wishlist not found")
    updated = await repo.update(wishlist, data.model_dump(exclude_none=True))
    rows = await repo.get_all_with_stats()
    item_count = next((cnt for wl, cnt in rows if wl.id == updated.id), 0)
    return AdminWishlistResponse(
        id=updated.id,
        owner_id=updated.owner_id,
        title=updated.title,
        is_public=updated.is_public,
        surprise_mode=updated.surprise_mode,
        event_date=updated.event_date,
        item_count=item_count,
        created_at=updated.created_at,
    )

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.core.redis_client import get_redis
from app.schemas.wishlist import (
    WishlistCreate,
    WishlistDetailResponse,
    WishlistItemCreate,
    WishlistItemResponse,
    WishlistItemUpdate,
    WishlistSummaryResponse,
    WishlistUpdate,
)
from app.services.wishlist_service import WishlistService

router = APIRouter(prefix="/api/wishlists")


def _svc(db: AsyncSession = Depends(get_db)) -> WishlistService:
    return WishlistService(db, get_redis())


# ── Shared (public, no auth) ──────────────────────────────────────────────────

@router.get("/shared/{token}", response_model=WishlistDetailResponse)
async def get_shared(token: str, svc: WishlistService = Depends(_svc)) -> WishlistDetailResponse:
    """Return the public view of a wishlist by its share token."""
    return await svc.get_by_share_token(token)


# ── My wishlists ──────────────────────────────────────────────────────────────

@router.get("/", response_model=list[WishlistSummaryResponse])
async def list_my(
    user_id: str = Depends(get_current_user_id),
    svc: WishlistService = Depends(_svc),
) -> list[WishlistSummaryResponse]:
    """List all wishlists belonging to the authenticated user."""
    return await svc.list_my(uuid.UUID(user_id))


@router.post("/", response_model=WishlistSummaryResponse, status_code=201)
async def create(
    data: WishlistCreate,
    user_id: str = Depends(get_current_user_id),
    svc: WishlistService = Depends(_svc),
) -> WishlistSummaryResponse:
    """Create a new wishlist for the authenticated user."""
    return await svc.create(uuid.UUID(user_id), data)


@router.get("/{wishlist_id}", response_model=WishlistDetailResponse)
async def get_detail(
    wishlist_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    svc: WishlistService = Depends(_svc),
) -> WishlistDetailResponse:
    """Return the full detail of a wishlist owned by the authenticated user."""
    return await svc.get_detail(wishlist_id, uuid.UUID(user_id))


@router.patch("/{wishlist_id}", response_model=WishlistSummaryResponse)
async def update(
    wishlist_id: uuid.UUID,
    data: WishlistUpdate,
    user_id: str = Depends(get_current_user_id),
    svc: WishlistService = Depends(_svc),
) -> WishlistSummaryResponse:
    """Apply a partial update to a wishlist owned by the authenticated user."""
    return await svc.update(wishlist_id, uuid.UUID(user_id), data)


@router.delete("/{wishlist_id}", status_code=204)
async def delete(
    wishlist_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    svc: WishlistService = Depends(_svc),
) -> None:
    """Delete a wishlist owned by the authenticated user."""
    await svc.delete(wishlist_id, uuid.UUID(user_id))


# ── Items ─────────────────────────────────────────────────────────────────────

@router.post("/{wishlist_id}/items", response_model=WishlistItemResponse, status_code=201)
async def add_item(
    wishlist_id: uuid.UUID,
    data: WishlistItemCreate,
    user_id: str = Depends(get_current_user_id),
    svc: WishlistService = Depends(_svc),
) -> WishlistItemResponse:
    """Add a new item to a wishlist owned by the authenticated user."""
    return await svc.add_item(wishlist_id, uuid.UUID(user_id), data)


@router.patch("/{wishlist_id}/items/{item_id}", response_model=WishlistItemResponse)
async def update_item(
    wishlist_id: uuid.UUID,
    item_id: uuid.UUID,
    data: WishlistItemUpdate,
    user_id: str = Depends(get_current_user_id),
    svc: WishlistService = Depends(_svc),
) -> WishlistItemResponse:
    """Apply a partial update to an item in a wishlist owned by the authenticated user."""
    return await svc.update_item(wishlist_id, item_id, uuid.UUID(user_id), data)


@router.delete("/{wishlist_id}/items/{item_id}", status_code=204)
async def delete_item(
    wishlist_id: uuid.UUID,
    item_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    svc: WishlistService = Depends(_svc),
) -> None:
    """Delete an item from a wishlist owned by the authenticated user."""
    await svc.delete_item(wishlist_id, item_id, uuid.UUID(user_id))

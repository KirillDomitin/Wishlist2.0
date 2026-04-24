import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.core.redis_client import get_redis
from app.schemas.reservation import ItemReservationInfo, ReservationCreate, ReservationResponse
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/api/reservations")


def _svc(db: AsyncSession = Depends(get_db)) -> ReservationService:
    return ReservationService(db, get_redis())


@router.get("/", response_model=list[ReservationResponse])
async def list_my(
    user_id: str = Depends(get_current_user_id),
    svc: ReservationService = Depends(_svc),
) -> list[ReservationResponse]:
    """List all reservations belonging to the authenticated user."""
    return await svc.list_my(uuid.UUID(user_id))


@router.post("/", response_model=ReservationResponse, status_code=201)
async def create(
    data: ReservationCreate,
    user_id: str = Depends(get_current_user_id),
    svc: ReservationService = Depends(_svc),
) -> ReservationResponse:
    """Create a new reservation for the specified item."""
    return await svc.create(uuid.UUID(user_id), data)


@router.delete("/{reservation_id}", status_code=204)
async def cancel(
    reservation_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    svc: ReservationService = Depends(_svc),
) -> None:
    """Cancel an active reservation owned by the authenticated user."""
    await svc.cancel(reservation_id, uuid.UUID(user_id))


@router.get("/wishlist/{wishlist_id}", response_model=list[ItemReservationInfo])
async def list_for_wishlist(
    wishlist_id: uuid.UUID,
    _user_id: str = Depends(get_current_user_id),
    svc: ReservationService = Depends(_svc),
) -> list[ItemReservationInfo]:
    """List active reservations for all items in the specified wishlist."""
    return await svc.list_for_wishlist(wishlist_id)

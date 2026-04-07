import uuid

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.streams import StreamProducer
from app.repositories.reservation_repository import (
    ItemReadModelRepository,
    ReservationRepository,
)
from app.schemas.reservation import ItemReservationInfo, ReservationCreate, ReservationResponse

_STREAM_RESERVATIONS = "stream:reservations"


class ReservationService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self._item_repo = ItemReadModelRepository(session)
        self._repo = ReservationRepository(session)
        self._producer = StreamProducer(redis, _STREAM_RESERVATIONS)

    async def create(
        self, reserver_id: uuid.UUID, data: ReservationCreate
    ) -> ReservationResponse:
        item = await self._item_repo.get(data.item_id)
        if item is None or item.is_deleted:
            raise NotFoundError("Item not found")

        active_count = await self._item_repo.get_active_reserved_count(data.item_id)
        if active_count + data.quantity > item.target_quantity:
            raise ConflictError(
                f"Only {item.target_quantity - active_count} slot(s) available"
            )

        reservation = await self._repo.create(data.item_id, reserver_id, data.quantity)

        await self._producer.publish(
            "reservation.created",
            {
                "item_id": str(data.item_id),
                "wishlist_id": str(item.wishlist_id),
                "quantity": str(data.quantity),
            },
        )

        return ReservationResponse.model_validate(reservation)

    async def cancel(
        self, reservation_id: uuid.UUID, reserver_id: uuid.UUID
    ) -> ReservationResponse:
        reservation = await self._repo.get(reservation_id)
        if reservation is None:
            raise NotFoundError("Reservation not found")
        if reservation.reserver_id != reserver_id:
            raise ForbiddenError()
        if reservation.status.value == "cancelled":
            raise ConflictError("Reservation already cancelled")

        item = await self._item_repo.get(reservation.item_id)
        reservation = await self._repo.cancel(reservation)

        await self._producer.publish(
            "reservation.cancelled",
            {
                "item_id": str(reservation.item_id),
                "wishlist_id": str(item.wishlist_id) if item else "",
                "quantity": str(reservation.quantity),
            },
        )

        return ReservationResponse.model_validate(reservation)

    async def list_my(self, reserver_id: uuid.UUID) -> list[ReservationResponse]:
        reservations = await self._repo.list_by_reserver(reserver_id)
        return [ReservationResponse.model_validate(r) for r in reservations]

    async def list_for_wishlist(self, wishlist_id: uuid.UUID) -> list[ItemReservationInfo]:
        reservations = await self._repo.list_active_for_wishlist(wishlist_id)
        return [ItemReservationInfo.model_validate(r) for r in reservations]

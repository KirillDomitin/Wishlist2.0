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
    """Business logic for creating, cancelling, and querying reservations.

    Args:
        session: Active async database session.
        redis: Active Redis client used for event publishing.
    """

    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self._item_repo = ItemReadModelRepository(session)
        self._repo = ReservationRepository(session)
        self._producer = StreamProducer(redis, _STREAM_RESERVATIONS)

    async def create(
        self, reserver_id: uuid.UUID, data: ReservationCreate
    ) -> ReservationResponse:
        """Create a reservation after validating availability and ownership.

        Args:
            reserver_id: ID of the user making the reservation.
            data: Reservation creation payload.

        Returns:
            The created reservation response schema.

        Raises:
            NotFoundError: If the item does not exist or has been deleted.
            ForbiddenError: If the user tries to reserve their own item.
            ConflictError: If requested quantity exceeds available slots.
        """
        item = await self._item_repo.get(data.item_id)
        if item is None or item.is_deleted:
            raise NotFoundError("Item not found")

        if item.owner_id is not None and item.owner_id == reserver_id:
            raise ForbiddenError("Cannot reserve your own item")

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
                "owner_id": str(item.owner_id) if item.owner_id else "",
                "reserver_id": str(reserver_id),
                "item_title": item.title,
                "surprise_mode": str(item.surprise_mode),
                "quantity": str(data.quantity),
            },
        )

        return ReservationResponse.model_validate(reservation)

    async def cancel(
        self, reservation_id: uuid.UUID, reserver_id: uuid.UUID
    ) -> ReservationResponse:
        """Cancel an active reservation owned by the requesting user.

        Args:
            reservation_id: ID of the reservation to cancel.
            reserver_id: ID of the user requesting cancellation.

        Returns:
            The updated reservation response schema.

        Raises:
            NotFoundError: If the reservation does not exist.
            ForbiddenError: If the user does not own the reservation.
            ConflictError: If the reservation is already cancelled.
        """
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
                "owner_id": str(item.owner_id) if item and item.owner_id else "",
                "reserver_id": str(reserver_id),
                "item_title": item.title if item else "",
                "surprise_mode": str(item.surprise_mode) if item else "False",
                "quantity": str(reservation.quantity),
            },
        )

        return ReservationResponse.model_validate(reservation)

    async def list_my(self, reserver_id: uuid.UUID) -> list[ReservationResponse]:
        """Return all reservations belonging to a user.

        Args:
            reserver_id: User ID of the reserver.

        Returns:
            List of reservation response schemas.
        """
        reservations = await self._repo.list_by_reserver(reserver_id)
        return [ReservationResponse.model_validate(r) for r in reservations]

    async def list_for_wishlist(self, wishlist_id: uuid.UUID) -> list[ItemReservationInfo]:
        """Return active reservations for all items in a wishlist.

        Args:
            wishlist_id: Parent wishlist ID.

        Returns:
            List of item reservation info schemas.
        """
        reservations = await self._repo.list_active_for_wishlist(wishlist_id)
        return [ItemReservationInfo.model_validate(r) for r in reservations]

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.reservation import ItemReadModel, Reservation, ReservationStatus


class ItemReadModelRepository:
    """Read-model repository for wishlist items cached in the reservation service.

    Args:
        session: Active async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(
        self,
        item_id: uuid.UUID,
        wishlist_id: uuid.UUID,
        target_quantity: int,
        title: str = "",
        price: Decimal | None = None,
        image_urls: list[str] | None = None,
        owner_id: uuid.UUID | None = None,
        surprise_mode: bool = False,
    ) -> None:
        """Insert a new item read-model or update the existing one.

        Args:
            item_id: Item primary key.
            wishlist_id: Parent wishlist ID.
            target_quantity: Maximum number of reservations allowed.
            title: Item display name.
            price: Item price, or ``None`` if not set.
            image_urls: Ordered list of image URL paths.
            owner_id: Wishlist owner user ID.
            surprise_mode: Whether the wishlist is in surprise mode.
        """
        result = await self._session.get(ItemReadModel, item_id)
        if result is None:
            self._session.add(
                ItemReadModel(
                    id=item_id,
                    wishlist_id=wishlist_id,
                    owner_id=owner_id,
                    surprise_mode=surprise_mode,
                    target_quantity=target_quantity,
                    title=title,
                    price=price,
                    image_urls=image_urls or [],
                )
            )
        else:
            result.wishlist_id = wishlist_id
            result.owner_id = owner_id
            result.surprise_mode = surprise_mode
            result.target_quantity = target_quantity
            result.is_deleted = False
            result.title = title
            result.price = price
            result.image_urls = image_urls or []
        await self._session.commit()

    async def mark_deleted(self, item_id: uuid.UUID) -> None:
        """Soft-delete an item read-model by ID.

        Args:
            item_id: Item primary key.
        """
        item = await self._session.get(ItemReadModel, item_id)
        if item:
            item.is_deleted = True
            await self._session.commit()

    async def get(self, item_id: uuid.UUID) -> ItemReadModel | None:
        """Fetch an item read-model by ID.

        Args:
            item_id: Item primary key.

        Returns:
            The matching ItemReadModel, or ``None`` if not found.
        """
        return await self._session.get(ItemReadModel, item_id)

    async def get_active_reserved_count(self, item_id: uuid.UUID) -> int:
        """Return the sum of quantities across all active reservations for an item.

        Args:
            item_id: Item primary key.

        Returns:
            Total reserved quantity; 0 if no active reservations exist.
        """
        result = await self._session.execute(
            select(func.coalesce(func.sum(Reservation.quantity), 0)).where(
                Reservation.item_id == item_id,
                Reservation.status == ReservationStatus.active,
            )
        )
        return int(result.scalar())


class ReservationRepository:
    """Repository for Reservation persistence operations.

    Args:
        session: Active async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, item_id: uuid.UUID, reserver_id: uuid.UUID, quantity: int
    ) -> Reservation:
        """Persist a new active reservation and return it.

        Args:
            item_id: ID of the reserved item.
            reserver_id: ID of the user making the reservation.
            quantity: Number of slots to reserve.

        Returns:
            The newly created Reservation instance.
        """
        reservation = Reservation(
            item_id=item_id,
            reserver_id=reserver_id,
            quantity=quantity,
        )
        self._session.add(reservation)
        await self._session.commit()
        await self._session.refresh(reservation)
        return reservation

    async def get(self, reservation_id: uuid.UUID) -> Reservation | None:
        """Fetch a reservation by primary key.

        Args:
            reservation_id: Reservation primary key.

        Returns:
            The matching Reservation, or ``None`` if not found.
        """
        return await self._session.get(Reservation, reservation_id)

    async def cancel(self, reservation: Reservation) -> Reservation:
        """Mark a reservation as cancelled and persist the change.

        Args:
            reservation: The Reservation instance to cancel.

        Returns:
            The updated Reservation instance.
        """
        reservation.status = ReservationStatus.cancelled
        await self._session.commit()
        await self._session.refresh(reservation)
        return reservation

    async def list_active_for_wishlist(self, wishlist_id: uuid.UUID) -> list[Reservation]:
        """Return all active reservations for items belonging to a wishlist.

        Args:
            wishlist_id: Parent wishlist ID.

        Returns:
            List of active Reservation instances.
        """
        result = await self._session.execute(
            select(Reservation)
            .join(ItemReadModel, Reservation.item_id == ItemReadModel.id)
            .where(
                ItemReadModel.wishlist_id == wishlist_id,
                Reservation.status == ReservationStatus.active,
            )
        )
        return list(result.scalars().all())

    async def list_by_reserver(self, reserver_id: uuid.UUID) -> list[Reservation]:
        """Return all reservations made by a user, with item data eager-loaded.

        Args:
            reserver_id: User ID of the reserver.

        Returns:
            List of Reservation instances with ``item`` relationship loaded.
        """
        result = await self._session.execute(
            select(Reservation)
            .options(selectinload(Reservation.item))
            .where(Reservation.reserver_id == reserver_id)
        )
        return list(result.scalars().all())

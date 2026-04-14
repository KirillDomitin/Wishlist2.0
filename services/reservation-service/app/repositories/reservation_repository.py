import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.reservation import ItemReadModel, Reservation, ReservationStatus


class ItemReadModelRepository:
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
        item = await self._session.get(ItemReadModel, item_id)
        if item:
            item.is_deleted = True
            await self._session.commit()

    async def get(self, item_id: uuid.UUID) -> ItemReadModel | None:
        return await self._session.get(ItemReadModel, item_id)

    async def get_active_reserved_count(self, item_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.coalesce(func.sum(Reservation.quantity), 0)).where(
                Reservation.item_id == item_id,
                Reservation.status == ReservationStatus.active,
            )
        )
        return int(result.scalar())


class ReservationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, item_id: uuid.UUID, reserver_id: uuid.UUID, quantity: int
    ) -> Reservation:
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
        return await self._session.get(Reservation, reservation_id)

    async def cancel(self, reservation: Reservation) -> Reservation:
        reservation.status = ReservationStatus.cancelled
        await self._session.commit()
        await self._session.refresh(reservation)
        return reservation

    async def list_active_for_wishlist(self, wishlist_id: uuid.UUID) -> list[Reservation]:
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
        result = await self._session.execute(
            select(Reservation)
            .options(selectinload(Reservation.item))
            .where(Reservation.reserver_id == reserver_id)
        )
        return list(result.scalars().all())

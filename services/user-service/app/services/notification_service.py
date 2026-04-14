import uuid
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.repositories.user_repository import UserRepository


async def _get_user_info(user_id: str) -> tuple[str, str] | None:
    """Returns (email, name) for a given user_id string, or None if not found."""
    try:
        uid = uuid.UUID(user_id)
    except (ValueError, AttributeError):
        return None
    async with AsyncSessionLocal() as session:
        user = await UserRepository(session).get_by_id(uid)
        if user is None:
            return None
        return user.email, user.name


async def _send_email(to_email: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    smtp_user = settings.SMTP_USER or settings.SMTP_FROM
    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=smtp_user,
        password=settings.SMTP_PASSWORD,
        use_tls=settings.SMTP_USE_SSL,
        start_tls=not settings.SMTP_USE_SSL,
    )


async def handle_reservation_event(event_type: str, data: dict[str, str]) -> None:
    owner_id = data.get("owner_id", "")
    reserver_id = data.get("reserver_id", "")
    item_title = data.get("item_title", "подарок")
    surprise_mode = data.get("surprise_mode", "False").lower() == "true"

    if not owner_id:
        return

    owner = await _get_user_info(owner_id)
    if owner is None:
        return
    owner_email, owner_name = owner

    if event_type == "reservation.created":
        if not surprise_mode and reserver_id:
            reserver = await _get_user_info(reserver_id)
            reserver_name = reserver[1] if reserver else "Кто-то"
        else:
            reserver_name = "Кто-то"

        subject = f'"{item_title}" забронирован'
        body = (
            f"Привет, {owner_name}!\n\n"
            f'{reserver_name} забронировал(а) «{item_title}» из вашего вишлиста.\n\n'
            "Удачи с подарком!"
        )

    elif event_type == "reservation.cancelled":
        if not surprise_mode and reserver_id:
            reserver = await _get_user_info(reserver_id)
            reserver_name = reserver[1] if reserver else "Кто-то"
        else:
            reserver_name = "Кто-то"

        subject = f'Бронь «{item_title}» отменена'
        body = (
            f"Привет, {owner_name}!\n\n"
            f'{reserver_name} отменил(а) бронь «{item_title}» из вашего вишлиста.\n\n'
            "Возможно, кто-то другой успеет забронировать!"
        )

    else:
        return

    await _send_email(owner_email, subject, body)

import uuid
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.repositories.user_repository import UserRepository

_BASE_HTML = """\
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{subject}</title>
</head>
<body style="margin:0;padding:0;background:#fdf4ff;font-family:'Inter',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#fdf4ff;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="100%" style="max-width:520px;border-radius:20px;overflow:hidden;
               box-shadow:0 20px 60px rgba(147,51,234,0.12);">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#9333ea 0%,#ec4899 100%);
                       padding:32px 40px;text-align:center;">
              <div style="font-size:26px;letter-spacing:2px;">🎁</div>
              <div style="margin-top:8px;font-size:22px;font-weight:700;
                          color:#ffffff;letter-spacing:0.5px;">Wishlist</div>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#ffffff;padding:36px 40px;">
              {body_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#fdf4ff;padding:20px 40px;text-align:center;
                       border-top:1px solid #f3e8ff;">
              <p style="margin:0;font-size:12px;color:#a78bfa;">
                Это автоматическое письмо — отвечать на него не нужно.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

_CREATED_BODY = """\
<p style="margin:0 0 6px;font-size:16px;font-weight:600;color:#1f2937;">
  Привет, {owner_name}!
</p>
<p style="margin:0 0 24px;font-size:14px;color:#6b7280;">
  Хорошие новости — кто-то заинтересовался вашим вишлистом&nbsp;🎉
</p>

<table width="100%" cellpadding="0" cellspacing="0"
       style="background:linear-gradient(135deg,#fdf4ff,#fce7f3);
              border:1px solid #f3e8ff;border-radius:14px;margin-bottom:24px;">
  <tr>
    <td style="padding:20px 24px;">
      <p style="margin:0 0 4px;font-size:11px;font-weight:600;text-transform:uppercase;
                letter-spacing:1px;color:#a78bfa;">Подарок</p>
      <p style="margin:0;font-size:17px;font-weight:700;color:#7c3aed;">
        {item_title}
      </p>
    </td>
  </tr>
</table>

<p style="margin:0 0 6px;font-size:14px;color:#374151;">
  <span style="font-weight:600;color:#9333ea;">{reserver_name}</span>
  забронировал(а) этот подарок из вашего вишлиста.
</p>
<p style="margin:0;font-size:14px;color:#6b7280;">Удачи с подарком! 🥳</p>
"""

_CANCELLED_BODY = """\
<p style="margin:0 0 6px;font-size:16px;font-weight:600;color:#1f2937;">
  Привет, {owner_name}!
</p>
<p style="margin:0 0 24px;font-size:14px;color:#6b7280;">
  Бронь на один из ваших подарков была отменена.
</p>

<table width="100%" cellpadding="0" cellspacing="0"
       style="background:linear-gradient(135deg,#fdf4ff,#fce7f3);
              border:1px solid #f3e8ff;border-radius:14px;margin-bottom:24px;">
  <tr>
    <td style="padding:20px 24px;">
      <p style="margin:0 0 4px;font-size:11px;font-weight:600;text-transform:uppercase;
                letter-spacing:1px;color:#a78bfa;">Подарок</p>
      <p style="margin:0;font-size:17px;font-weight:700;color:#7c3aed;">
        {item_title}
      </p>
    </td>
  </tr>
</table>

<p style="margin:0 0 6px;font-size:14px;color:#374151;">
  <span style="font-weight:600;color:#9333ea;">{reserver_name}</span>
  отменил(а) бронь.
</p>
<p style="margin:0;font-size:14px;color:#6b7280;">
  Возможно, кто-то другой успеет забронировать&nbsp;🤞
</p>
"""


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


async def _send_email(to_email: str, subject: str, html: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content("Это письмо в формате HTML. Откройте его в почтовом клиенте с поддержкой HTML.")
    msg.add_alternative(html, subtype="html")

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
    """Process reservation lifecycle events and email the wishlist owner.

    Handles ``reservation.created`` and ``reservation.cancelled``. Skips
    silently if owner is missing or the event type is unrecognised.

    Args:
        event_type: One of ``reservation.created``, ``reservation.cancelled``.
        data: Event payload fields as string key-value pairs.
    """
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

    if not surprise_mode and reserver_id:
        reserver = await _get_user_info(reserver_id)
        reserver_name = reserver[1] if reserver else "Кто-то"
    else:
        reserver_name = "Кто-то"

    if event_type == "reservation.created":
        subject = f'"{item_title}" забронирован 🎁'
        body_html = _CREATED_BODY.format(
            owner_name=owner_name,
            item_title=item_title,
            reserver_name=reserver_name,
        )
    elif event_type == "reservation.cancelled":
        subject = f'Бронь «{item_title}» отменена'
        body_html = _CANCELLED_BODY.format(
            owner_name=owner_name,
            item_title=item_title,
            reserver_name=reserver_name,
        )
    else:
        return

    html = _BASE_HTML.format(subject=subject, body_html=body_html)
    await _send_email(owner_email, subject, html)

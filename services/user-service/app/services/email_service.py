from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings


async def send_verification_email(to_email: str, code: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = "Код подтверждения регистрации"
    msg.set_content(
        f"Ваш код подтверждения: {code}\n\n"
        "Код действителен 15 минут.\n"
        "Если вы не регистрировались — просто проигнорируйте это письмо."
    )

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )

from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings

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
          <tr>
            <td style="background:linear-gradient(135deg,#9333ea 0%,#ec4899 100%);
                       padding:32px 40px;text-align:center;">
              <div style="font-size:26px;letter-spacing:2px;">🎁</div>
              <div style="margin-top:8px;font-size:22px;font-weight:700;
                          color:#ffffff;letter-spacing:0.5px;">Wishlist</div>
            </td>
          </tr>
          <tr>
            <td style="background:#ffffff;padding:36px 40px;">
              {body_html}
            </td>
          </tr>
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

_VERIFICATION_BODY = """\
<p style="margin:0 0 6px;font-size:16px;font-weight:600;color:#1f2937;">
  Подтвердите email
</p>
<p style="margin:0 0 24px;font-size:14px;color:#6b7280;">
  Введите код ниже, чтобы завершить регистрацию. Код действует&nbsp;15&nbsp;минут.
</p>
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:linear-gradient(135deg,#fdf4ff,#fce7f3);
              border:1px solid #f3e8ff;border-radius:14px;margin-bottom:24px;">
  <tr>
    <td style="padding:20px 24px;text-align:center;">
      <p style="margin:0 0 4px;font-size:11px;font-weight:600;text-transform:uppercase;
                letter-spacing:1px;color:#a78bfa;">Код подтверждения</p>
      <p style="margin:0;font-size:36px;font-weight:800;color:#7c3aed;letter-spacing:8px;">
        {code}
      </p>
    </td>
  </tr>
</table>
<p style="margin:0;font-size:13px;color:#9ca3af;">
  Если вы не регистрировались — просто проигнорируйте это письмо.
</p>
"""

_RESET_BODY = """\
<p style="margin:0 0 6px;font-size:16px;font-weight:600;color:#1f2937;">
  Сброс пароля
</p>
<p style="margin:0 0 24px;font-size:14px;color:#6b7280;">
  Мы получили запрос на сброс пароля для вашего аккаунта.
  Ссылка действует&nbsp;15&nbsp;минут.
</p>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
  <tr>
    <td align="center">
      <a href="{reset_url}"
         style="display:inline-block;padding:14px 32px;
                background:linear-gradient(135deg,#9333ea 0%,#ec4899 100%);
                color:#ffffff;font-size:15px;font-weight:700;
                text-decoration:none;border-radius:14px;
                box-shadow:0 4px 15px rgba(147,51,234,0.35);">
        Сбросить пароль
      </a>
    </td>
  </tr>
</table>
<p style="margin:0 0 8px;font-size:13px;color:#6b7280;">
  Или вставьте ссылку вручную:
</p>
<p style="margin:0;font-size:12px;color:#a78bfa;word-break:break-all;">
  {reset_url}
</p>
<p style="margin:16px 0 0;font-size:13px;color:#9ca3af;">
  Если вы не запрашивали сброс пароля — просто проигнорируйте это письмо.
</p>
"""


async def _send(to_email: str, subject: str, body_html: str) -> None:
    html = _BASE_HTML.format(subject=subject, body_html=body_html)
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


async def send_verification_email(to_email: str, code: str) -> None:
    """Send an HTML email containing the 6-digit email verification code.

    Args:
        to_email: Recipient email address.
        code: 6-digit verification code.
    """
    body_html = _VERIFICATION_BODY.format(code=code)
    await _send(to_email, "Код подтверждения регистрации", body_html)


async def send_password_reset_email(to_email: str, token: str) -> None:
    """Send an HTML email containing the password-reset link.

    Args:
        to_email: Recipient email address.
        token: Opaque URL-safe token embedded in the reset link.
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    body_html = _RESET_BODY.format(reset_url=reset_url)
    await _send(to_email, "Сброс пароля — Wishlist", body_html)

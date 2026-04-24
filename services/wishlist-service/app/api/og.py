import html as _html

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.redis_client import get_redis
from app.services.wishlist_service import WishlistService

router = APIRouter(prefix="/api/og")


def _svc(db: AsyncSession = Depends(get_db)) -> WishlistService:
    return WishlistService(db, get_redis())


def _build_html(title: str, description: str, image_url: str, page_url: str) -> str:
    t = _html.escape(title)
    d = _html.escape(description[:200])
    i = _html.escape(image_url)
    u = _html.escape(page_url)
    img_tags = (
        f'  <meta property="og:image" content="{i}">\n'
        f'  <meta name="twitter:image" content="{i}">'
        if i else ""
    )
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>{t} — Wishlist</title>
  <meta property="og:type" content="website">
  <meta property="og:url" content="{u}">
  <meta property="og:title" content="{t}">
  <meta property="og:description" content="{d}">
{img_tags}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{t}">
  <meta name="twitter:description" content="{d}">
</head>
<body><a href="{u}">{t}</a></body>
</html>"""


@router.get("/shared/{token}", response_class=HTMLResponse)
async def og_shared(token: str, svc: WishlistService = Depends(_svc)) -> HTMLResponse:
    """Return an HTML page with Open Graph meta tags for the shared wishlist.

    Used by Telegram and other link-preview crawlers to render rich previews.
    Falls back to generic metadata if the token is invalid.
    """
    try:
        wishlist = await svc.get_by_share_token(token)
    except NotFoundError:
        return HTMLResponse(
            _build_html("Wishlist", "Список желаний", "", settings.APP_BASE_URL)
        )

    if wishlist.items:
        names = [item.title for item in wishlist.items[:3]]
        description = ", ".join(names)
        if (extra := len(wishlist.items) - 3) > 0:
            description += f" и ещё {extra}"
    else:
        description = "Список желаний"

    image_url = ""
    for item in wishlist.items:
        if item.image_urls:
            raw = item.image_urls[0]
            image_url = raw if raw.startswith("http") else f"{settings.APP_BASE_URL}{raw}"
            break

    return HTMLResponse(
        _build_html(
            wishlist.title,
            description,
            image_url,
            f"{settings.APP_BASE_URL}/shared/{token}",
        )
    )

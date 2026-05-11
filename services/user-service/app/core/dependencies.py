from fastapi import Header

from app.core.exceptions import ForbiddenError, UnauthorizedError


async def get_current_user_id(x_user_id: str = Header(...)) -> str:
    """Extract the authenticated user ID from the X-User-Id request header.

    This header is injected by the Nginx gateway after JWT verification.

    Args:
        x_user_id: Value of the ``X-User-Id`` header.

    Returns:
        The user ID string.

    Raises:
        UnauthorizedError: If the header is missing or empty.
    """
    if not x_user_id:
        raise UnauthorizedError()
    return x_user_id


async def require_admin(x_user_is_admin: str = Header(default="false")) -> None:
    """Raise 403 if the request does not come from an admin user.

    The ``X-User-Is-Admin`` header is injected by the Nginx gateway after JWT verification.

    Raises:
        ForbiddenError: If the header is not ``"true"``.
    """
    if x_user_is_admin != "true":
        raise ForbiddenError()

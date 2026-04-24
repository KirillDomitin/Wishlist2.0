from fastapi import Header

from app.core.exceptions import UnauthorizedError


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

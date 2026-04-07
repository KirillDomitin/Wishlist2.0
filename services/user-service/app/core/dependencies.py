from fastapi import Header

from app.core.exceptions import UnauthorizedError


async def get_current_user_id(x_user_id: str = Header(...)) -> str:
    if not x_user_id:
        raise UnauthorizedError()
    return x_user_id

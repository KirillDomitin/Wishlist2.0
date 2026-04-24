from fastapi import APIRouter, Request, Response

from app.core.exceptions import UnauthorizedError
from app.core.jwt import decode_access_token

router = APIRouter()


@router.get("/internal/verify")
async def verify_token(request: Request) -> Response:
    """Verify a Bearer JWT and return the user ID in the X-User-Id response header.

    Called by the Nginx gateway to authenticate upstream requests.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedError()

    token = auth_header.removeprefix("Bearer ")
    user_id = decode_access_token(token)

    return Response(status_code=200, headers={"X-User-Id": user_id})

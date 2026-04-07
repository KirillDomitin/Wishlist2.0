from fastapi import APIRouter, Request, Response

from app.core.exceptions import UnauthorizedError
from app.core.jwt import decode_access_token

router = APIRouter()


@router.get("/internal/verify")
async def verify_token(request: Request) -> Response:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise UnauthorizedError()

    token = auth_header.removeprefix("Bearer ")
    user_id = decode_access_token(token)

    return Response(status_code=200, headers={"X-User-Id": user_id})

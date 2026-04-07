import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users")


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    return await UserService(db).get_by_id(uuid.UUID(user_id))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    _caller_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    return await UserService(db).get_by_id(user_id)

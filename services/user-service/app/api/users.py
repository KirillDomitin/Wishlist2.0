import uuid

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.core.redis_client import get_redis
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users")


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Return the profile of the authenticated user."""
    return await UserService(db).get_by_id(uuid.UUID(user_id))


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> UserResponse:
    """Update the authenticated user's name and/or password."""
    return await UserService(db, redis).update_me(uuid.UUID(user_id), data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    _caller_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Return the public profile of a user by ID."""
    return await UserService(db).get_by_id(user_id)

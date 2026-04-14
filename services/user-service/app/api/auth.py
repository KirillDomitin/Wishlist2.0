from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.schemas.user import (
    LogoutRequest,
    RefreshRequest,
    RegisterInitiateResponse,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    VerifyEmailRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users")


@router.post("/register", response_model=RegisterInitiateResponse, status_code=200)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> RegisterInitiateResponse:
    return await UserService(db, redis).initiate_register(data)


@router.post("/verify-email", response_model=TokenResponse, status_code=201)
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> TokenResponse:
    return await UserService(db, redis).verify_email(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> TokenResponse:
    return await UserService(db, redis).login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> TokenResponse:
    return await UserService(db, redis).refresh(data.refresh_token)


@router.post("/logout", status_code=204)
async def logout(
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> None:
    await UserService(db, redis).logout(data.refresh_token)

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.schemas.user import (
    ForgotPasswordRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterInitiateResponse,
    ResetPasswordRequest,
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
    """Initiate user registration by sending a verification code to the provided email."""
    return await UserService(db, redis).initiate_register(data)


@router.post("/verify-email", response_model=TokenResponse, status_code=201)
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> TokenResponse:
    """Verify the email code and complete account creation, returning a token pair."""
    return await UserService(db, redis).verify_email(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> TokenResponse:
    """Authenticate a user with email and password, returning a token pair."""
    return await UserService(db, redis).login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> TokenResponse:
    """Rotate a refresh token and return a new access/refresh token pair."""
    return await UserService(db, redis).refresh(data.refresh_token)


@router.post("/logout", status_code=204)
async def logout(
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> None:
    """Revoke the provided refresh token, ending the session."""
    await UserService(db, redis).logout(data.refresh_token)


@router.post("/forgot-password", status_code=204)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> None:
    """Send a password-reset link to the provided email address if it is registered."""
    await UserService(db, redis).forgot_password(data)


@router.post("/reset-password", status_code=204)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> None:
    """Reset the user's password using the token received by email."""
    await UserService(db, redis).reset_password(data)

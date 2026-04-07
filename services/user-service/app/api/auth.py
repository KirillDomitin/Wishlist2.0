from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import TokenResponse, UserRegisterRequest, UserLoginRequest, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users")


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    return await UserService(db).register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await UserService(db).login(data)

import uuid

from passlib.context import CryptContext
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.core.token_store import revoke_refresh_token, store_refresh_token, validate_and_rotate
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session: AsyncSession, redis: Redis | None = None) -> None:
        self._repo = UserRepository(session)
        self._redis = redis

    async def register(self, data: UserRegisterRequest) -> TokenResponse:
        if await self._repo.get_by_email(data.email):
            raise ConflictError("Email already registered")
        password_hash = _pwd_context.hash(data.password)
        user = await self._repo.create(data.email, password_hash, data.name)
        user_id = str(user.id)
        refresh_token, jti = create_refresh_token(user_id)
        await store_refresh_token(self._redis, jti, user_id)
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=refresh_token,
        )

    async def login(self, data: UserLoginRequest) -> TokenResponse:
        user = await self._repo.get_by_email(data.email)
        if not user or not _pwd_context.verify(data.password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")
        user_id = str(user.id)
        refresh_token, jti = create_refresh_token(user_id)
        await store_refresh_token(self._redis, jti, user_id)
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=refresh_token,
        )

    async def refresh(self, token: str) -> TokenResponse:
        user_id, jti = decode_refresh_token(token)
        valid = await validate_and_rotate(self._redis, jti, user_id)
        if not valid:
            raise UnauthorizedError("Refresh token is invalid or already used")
        new_refresh_token, new_jti = create_refresh_token(user_id)
        await store_refresh_token(self._redis, new_jti, user_id)
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=new_refresh_token,
        )

    async def logout(self, token: str) -> None:
        user_id, jti = decode_refresh_token(token)
        await revoke_refresh_token(self._redis, jti)

    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserResponse.model_validate(user)

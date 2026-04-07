import uuid

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.jwt import create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def register(self, data: UserRegisterRequest) -> UserResponse:
        if await self._repo.get_by_email(data.email):
            raise ConflictError("Email already registered")
        password_hash = _pwd_context.hash(data.password)
        user = await self._repo.create(data.email, password_hash, data.name)
        return UserResponse.model_validate(user)

    async def login(self, data: UserLoginRequest) -> TokenResponse:
        user = await self._repo.get_by_email(data.email)
        if not user or not _pwd_context.verify(data.password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")
        return TokenResponse(access_token=create_access_token(str(user.id)))

    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserResponse.model_validate(user)

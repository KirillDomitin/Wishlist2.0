import json
import random
import secrets
import string
import uuid

from passlib.context import CryptContext
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.core.token_store import revoke_refresh_token, store_refresh_token, validate_and_rotate
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    ForgotPasswordRequest,
    RegisterInitiateResponse,
    ResetPasswordRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
    VerifyEmailRequest,
)
from app.services.email_service import send_password_reset_email, send_verification_email

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_PENDING_REG_TTL = 900  # 15 minutes


class UserService:
    """Business logic for user registration, authentication, and profile management.

    Args:
        session: Active async database session.
        redis: Active Redis client, required for token storage and temporary codes.
    """

    def __init__(self, session: AsyncSession, redis: Redis | None = None) -> None:
        self._repo = UserRepository(session)
        self._redis = redis

    async def initiate_register(self, data: UserRegisterRequest) -> RegisterInitiateResponse:
        """Begin registration by sending a verification code to the user's email.

        Args:
            data: Registration payload containing email, password, and name.

        Returns:
            A response message confirming the code was sent.

        Raises:
            ConflictError: If the email address is already registered.
        """
        if await self._repo.get_by_email(data.email):
            raise ConflictError("Email already registered")

        code = "".join(random.choices(string.digits, k=6))
        password_hash = _pwd_context.hash(data.password)

        pending = json.dumps({
            "email": data.email,
            "password_hash": password_hash,
            "name": data.name,
            "code": code,
        })
        await self._redis.setex(f"pending_reg:{data.email}", _PENDING_REG_TTL, pending)

        await send_verification_email(data.email, code)

        return RegisterInitiateResponse(message="Код подтверждения отправлен на email")

    async def verify_email(self, data: VerifyEmailRequest) -> TokenResponse:
        """Verify the email code, create the user account, and return tokens.

        Args:
            data: Payload containing email and the 6-digit verification code.

        Returns:
            Access and refresh token pair.

        Raises:
            NotFoundError: If the pending registration has expired.
            UnauthorizedError: If the verification code is incorrect.
            ConflictError: If the email was registered between initiation and verification.
        """
        raw = await self._redis.get(f"pending_reg:{data.email}")
        if not raw:
            raise NotFoundError("Код истёк или не найден. Зарегистрируйтесь заново.")

        pending = json.loads(raw)
        if pending["code"] != data.code:
            raise UnauthorizedError("Неверный код подтверждения")

        if await self._repo.get_by_email(data.email):
            raise ConflictError("Email already registered")

        user = await self._repo.create(pending["email"], pending["password_hash"], pending["name"])
        await self._redis.delete(f"pending_reg:{data.email}")

        user_id = str(user.id)
        refresh_token, jti = create_refresh_token(user_id)
        await store_refresh_token(self._redis, jti, user_id)
        return TokenResponse(
            access_token=create_access_token(user_id, is_admin=user.is_admin),
            refresh_token=refresh_token,
        )

    async def login(self, data: UserLoginRequest) -> TokenResponse:
        """Authenticate a user and return a new token pair.

        Args:
            data: Login payload containing email and password.

        Returns:
            Access and refresh token pair.

        Raises:
            UnauthorizedError: If credentials are invalid.
        """
        user = await self._repo.get_by_email(data.email)
        if not user or not _pwd_context.verify(data.password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")
        user_id = str(user.id)
        refresh_token, jti = create_refresh_token(user_id)
        await store_refresh_token(self._redis, jti, user_id)
        return TokenResponse(
            access_token=create_access_token(user_id, is_admin=user.is_admin),
            refresh_token=refresh_token,
        )

    async def refresh(self, token: str) -> TokenResponse:
        """Rotate a refresh token and issue a new access/refresh token pair.

        Args:
            token: Current refresh token string.

        Returns:
            New access and refresh token pair.

        Raises:
            UnauthorizedError: If the token is invalid, expired, or already used.
        """
        user_id, jti = decode_refresh_token(token)
        valid = await validate_and_rotate(self._redis, jti, user_id)
        if not valid:
            raise UnauthorizedError("Refresh token is invalid or already used")
        user = await self._repo.get_by_id(uuid.UUID(user_id))
        is_admin = user.is_admin if user else False
        new_refresh_token, new_jti = create_refresh_token(user_id)
        await store_refresh_token(self._redis, new_jti, user_id)
        return TokenResponse(
            access_token=create_access_token(user_id, is_admin=is_admin),
            refresh_token=new_refresh_token,
        )

    async def logout(self, token: str) -> None:
        """Revoke the given refresh token, preventing further use.

        Args:
            token: Refresh token string to revoke.
        """
        user_id, jti = decode_refresh_token(token)
        await revoke_refresh_token(self._redis, jti)

    async def get_by_id(self, user_id: uuid.UUID) -> UserResponse:
        """Fetch a user by primary key and return a response schema.

        Args:
            user_id: User primary key.

        Returns:
            User response schema.

        Raises:
            NotFoundError: If the user does not exist.
        """
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserResponse.model_validate(user)

    async def forgot_password(self, data: ForgotPasswordRequest) -> None:
        """Initiate a password reset flow by emailing a reset link.

        If the email is not registered the request silently succeeds to avoid
        revealing whether an account exists.

        Args:
            data: Payload containing the user's email address.
        """
        user = await self._repo.get_by_email(data.email)
        if not user:
            return  # silent — don't reveal whether email is registered
        token = secrets.token_urlsafe(32)
        await self._redis.setex(f"reset_pwd:{token}", _PENDING_REG_TTL, str(user.id))
        await send_password_reset_email(data.email, token)

    async def reset_password(self, data: ResetPasswordRequest) -> None:
        """Set a new password using a valid password-reset token.

        Args:
            data: Payload containing the reset token and new password.

        Raises:
            NotFoundError: If the reset token is invalid or has expired.
        """
        raw = await self._redis.get(f"reset_pwd:{data.token}")
        if not raw:
            raise NotFoundError("Ссылка недействительна или истекла")
        user_id = uuid.UUID(raw.decode() if isinstance(raw, bytes) else raw)
        password_hash = _pwd_context.hash(data.new_password)
        await self._repo.update(user_id, password_hash=password_hash)
        await self._redis.delete(f"reset_pwd:{data.token}")

    async def update_me(self, user_id: uuid.UUID, data: UserUpdateRequest) -> UserResponse:
        """Update the authenticated user's name and/or password.

        Args:
            user_id: ID of the user to update.
            data: Update payload; ``new_password`` requires ``current_password``.

        Returns:
            Updated user response schema.

        Raises:
            NotFoundError: If the user does not exist.
            UnauthorizedError: If current password is missing or incorrect.
        """
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        password_hash: str | None = None
        if data.new_password:
            if not data.current_password:
                raise UnauthorizedError("Требуется текущий пароль")
            if not _pwd_context.verify(data.current_password, user.password_hash):
                raise UnauthorizedError("Неверный текущий пароль")
            password_hash = _pwd_context.hash(data.new_password)
        updated = await self._repo.update(user_id, name=data.name, password_hash=password_hash)
        return UserResponse.model_validate(updated)

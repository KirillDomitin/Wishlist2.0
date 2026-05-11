import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedError


def create_access_token(user_id: str, is_admin: bool = False) -> str:
    """Create a signed JWT access token for the given user.

    Args:
        user_id: User primary key as a string.
        is_admin: Whether the user has admin privileges.

    Returns:
        Encoded JWT string.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire, "type": "access", "is_admin": is_admin}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """Create a signed JWT refresh token with a unique JTI claim.

    Args:
        user_id: User primary key as a string.

    Returns:
        A ``(token, jti)`` tuple where *jti* is used as the Redis key.
    """
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    payload = {"sub": user_id, "exp": expire, "type": "refresh", "jti": jti}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, jti


def decode_access_token(token: str) -> tuple[str, bool]:
    """Decode and validate a JWT access token.

    Args:
        token: Encoded JWT string.

    Returns:
        A ``(user_id, is_admin)`` tuple.

    Raises:
        UnauthorizedError: If the token is invalid, expired, or has the wrong type.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            raise UnauthorizedError()
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError()
        is_admin: bool = bool(payload.get("is_admin", False))
        return user_id, is_admin
    except JWTError:
        raise UnauthorizedError()


def decode_refresh_token(token: str) -> tuple[str, str]:
    """Decode and validate a JWT refresh token.

    Args:
        token: Encoded JWT string.

    Returns:
        A ``(user_id, jti)`` tuple.

    Raises:
        UnauthorizedError: If the token is invalid, expired, or has the wrong type.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise UnauthorizedError()
        user_id: str | None = payload.get("sub")
        jti: str | None = payload.get("jti")
        if not user_id or not jti:
            raise UnauthorizedError()
        return user_id, jti
    except JWTError:
        raise UnauthorizedError()

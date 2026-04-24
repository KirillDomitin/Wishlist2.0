from redis.asyncio import Redis

from app.core.config import settings

_REFRESH_TTL = settings.JWT_REFRESH_EXPIRE_DAYS * 86400  # seconds


def _active_key(jti: str) -> str:
    return f"refresh:active:{jti}"


def _blacklist_key(jti: str) -> str:
    return f"refresh:blacklist:{jti}"


async def store_refresh_token(redis: Redis, jti: str, user_id: str) -> None:
    """Store an active refresh token JTI in Redis.

    Args:
        redis: Active Redis client.
        jti: JWT ID claim used as the Redis key suffix.
        user_id: User ID associated with the token.
    """
    await redis.set(_active_key(jti), user_id, ex=_REFRESH_TTL)


async def validate_and_rotate(
    redis: Redis, jti: str, user_id: str
) -> bool:
    """Atomically validate a refresh token JTI and move it to the blacklist.

    Checks that the JTI is active and not blacklisted, then deletes the active
    key and writes a blacklist entry to prevent reuse.

    Args:
        redis: Active Redis client.
        jti: JWT ID claim to validate.
        user_id: Expected user ID stored under this JTI.

    Returns:
        ``True`` if the token was valid and rotated; ``False`` otherwise.
    """
    blacklisted = await redis.exists(_blacklist_key(jti))
    if blacklisted:
        return False

    stored_user = await redis.getdel(_active_key(jti))
    if stored_user != user_id:
        return False

    await redis.set(_blacklist_key(jti), "1", ex=_REFRESH_TTL)
    return True


async def revoke_refresh_token(redis: Redis, jti: str) -> None:
    """Revoke a refresh token by deleting the active key and blacklisting the JTI.

    Args:
        redis: Active Redis client.
        jti: JWT ID claim to revoke.
    """
    await redis.delete(_active_key(jti))
    await redis.set(_blacklist_key(jti), "1", ex=_REFRESH_TTL)

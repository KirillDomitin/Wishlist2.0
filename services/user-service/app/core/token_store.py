from redis.asyncio import Redis

from app.core.config import settings

_REFRESH_TTL = settings.JWT_REFRESH_EXPIRE_DAYS * 86400  # seconds


def _active_key(jti: str) -> str:
    return f"refresh:active:{jti}"


def _blacklist_key(jti: str) -> str:
    return f"refresh:blacklist:{jti}"


async def store_refresh_token(redis: Redis, jti: str, user_id: str) -> None:
    await redis.set(_active_key(jti), user_id, ex=_REFRESH_TTL)


async def validate_and_rotate(
    redis: Redis, jti: str, user_id: str
) -> bool:
    """
    Atomically checks that jti is active and not blacklisted,
    then moves it to the blacklist. Returns False if invalid.
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
    await redis.delete(_active_key(jti))
    await redis.set(_blacklist_key(jti), "1", ex=_REFRESH_TTL)

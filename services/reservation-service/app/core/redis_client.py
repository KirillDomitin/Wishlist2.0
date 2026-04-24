from redis.asyncio import Redis
from redis.asyncio import from_url

from app.core.config import settings

_redis: Redis | None = None


async def init_redis() -> None:
    """Initialize the global Redis connection from settings."""
    global _redis
    _redis = await from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis() -> None:
    """Close the global Redis connection if open."""
    if _redis is not None:
        await _redis.aclose()


def get_redis() -> Redis:
    """Return the initialized Redis instance.

    Returns:
        The active Redis client.

    Raises:
        RuntimeError: If called before ``init_redis()``.
    """
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    return _redis

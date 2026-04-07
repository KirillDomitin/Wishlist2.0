from redis.asyncio import Redis
from redis.asyncio import from_url

from app.core.config import settings

_redis: Redis | None = None


async def init_redis() -> None:
    global _redis
    _redis = await from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis() -> None:
    if _redis is not None:
        await _redis.aclose()


def get_redis() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    return _redis

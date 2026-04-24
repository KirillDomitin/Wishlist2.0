import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.reservations import router as reservations_router
from app.core.redis_client import close_redis, get_redis, init_redis
from app.core.streams import StreamConsumer
from app.services.event_handler import handle_wishlist_item_event

_STREAM_WISHLIST_ITEMS = "stream:wishlist_items"
_CONSUMER_GROUP = "reservation-service"
_CONSUMER_NAME = "reservation-consumer-1"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize Redis and the wishlist-items stream consumer on startup; clean up on shutdown."""
    await init_redis()

    consumer = StreamConsumer(
        redis=get_redis(),
        stream_name=_STREAM_WISHLIST_ITEMS,
        group_name=_CONSUMER_GROUP,
        consumer_name=_CONSUMER_NAME,
    )
    task = asyncio.create_task(consumer.consume(handle_wishlist_item_event))

    yield

    task.cancel()
    await close_redis()


app = FastAPI(title="Reservation Service", version="1.0.0", lifespan=lifespan)

app.include_router(reservations_router)

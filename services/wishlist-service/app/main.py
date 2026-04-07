import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.wishlists import router as wishlists_router
from app.core.redis_client import close_redis, get_redis, init_redis
from app.core.streams import StreamConsumer
from app.services.event_handler import handle_reservation_event

_STREAM_RESERVATIONS = "stream:reservations"
_CONSUMER_GROUP = "wishlist-service"
_CONSUMER_NAME = "wishlist-consumer-1"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_redis()

    consumer = StreamConsumer(
        redis=get_redis(),
        stream_name=_STREAM_RESERVATIONS,
        group_name=_CONSUMER_GROUP,
        consumer_name=_CONSUMER_NAME,
    )
    task = asyncio.create_task(consumer.consume(handle_reservation_event))

    yield

    task.cancel()
    await close_redis()


app = FastAPI(title="Wishlist Service", version="1.0.0", lifespan=lifespan)

app.include_router(wishlists_router)

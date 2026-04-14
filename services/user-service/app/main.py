import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.internal import router as internal_router
from app.api.users import router as users_router
from app.core.redis_client import close_redis, get_redis, init_redis
from app.core.streams import StreamConsumer
from app.services.notification_service import handle_reservation_event


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_redis()
    consumer = StreamConsumer(
        redis=get_redis(),
        stream_name="stream:reservations",
        group_name="user-service-notifications",
        consumer_name="user-service-1",
    )
    task = asyncio.create_task(consumer.consume(handle_reservation_event))
    yield
    task.cancel()
    await close_redis()


app = FastAPI(title="User Service", version="1.0.0", lifespan=lifespan)

app.include_router(internal_router)
app.include_router(auth_router)
app.include_router(users_router)

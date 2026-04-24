import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from redis.asyncio import Redis


class StreamProducer:
    """Publishes events to a Redis Stream.

    Args:
        redis: Active Redis client.
        stream_name: Target Redis stream key.
    """

    def __init__(self, redis: Redis, stream_name: str) -> None:
        self._redis = redis
        self._stream_name = stream_name

    async def publish(self, event_type: str, data: dict[str, Any]) -> str:
        """Append an event to the stream.

        Args:
            event_type: Logical event identifier (e.g. ``reservation.created``).
            data: Payload fields; all values are serialized to strings.

        Returns:
            The Redis message ID assigned to the appended entry.
        """
        payload = {"event_type": event_type} | {k: str(v) for k, v in data.items()}
        msg_id: str = await self._redis.xadd(self._stream_name, payload)
        return msg_id


class StreamConsumer:
    """Reads events from a Redis Stream consumer group.

    Args:
        redis: Active Redis client.
        stream_name: Source Redis stream key.
        group_name: Consumer group name; created automatically if absent.
        consumer_name: Unique name for this consumer instance.
    """

    def __init__(
        self,
        redis: Redis,
        stream_name: str,
        group_name: str,
        consumer_name: str,
    ) -> None:
        self._redis = redis
        self._stream_name = stream_name
        self._group_name = group_name
        self._consumer_name = consumer_name

    async def _ensure_group(self) -> None:
        try:
            await self._redis.xgroup_create(
                self._stream_name, self._group_name, id="0", mkstream=True
            )
        except Exception:
            pass  # Group already exists

    async def consume(
        self,
        handler: Callable[[str, dict[str, str]], Coroutine[Any, Any, None]],
        batch_size: int = 10,
        block_ms: int = 2000,
    ) -> None:
        """Poll the stream and dispatch messages to *handler* in a loop.

        Runs until the enclosing asyncio task is cancelled. Successfully
        processed messages are acknowledged; failed messages stay pending
        and will be retried on the next restart.

        Args:
            handler: Async callable that receives ``(event_type, fields)``.
            batch_size: Maximum messages to read per poll.
            block_ms: Milliseconds to block waiting for new messages.
        """
        await self._ensure_group()
        while True:
            try:
                results = await self._redis.xreadgroup(
                    groupname=self._group_name,
                    consumername=self._consumer_name,
                    streams={self._stream_name: ">"},
                    count=batch_size,
                    block=block_ms,
                )
                if not results:
                    continue
                for _, messages in results:
                    for msg_id, fields in messages:
                        try:
                            event_type: str = fields.pop("event_type", "")
                            await handler(event_type, fields)
                            await self._redis.xack(
                                self._stream_name, self._group_name, msg_id
                            )
                        except Exception:
                            pass  # Message stays pending; retried on restart
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)

import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator

from pydantic import BaseModel, Field
from redis.asyncio import Redis


class AtlasMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    user: str
    destination: str
    msg: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_redis_dict(self) -> dict:
        """Convert the message to a dictionary for Redis Stream storage."""
        return {
            "id": self.id,
            "source": self.source,
            "user": self.user,
            "destination": self.destination,
            "msg": self.msg,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_redis_dict(cls, data: dict) -> "AtlasMessage":
        """Create an AtlasMessage from a Redis Stream dictionary."""
        # Redis returns bytes for keys and values, so we need to decode them
        decoded_data = {
            k.decode("utf-8") if isinstance(k, bytes) else k: v.decode("utf-8") if isinstance(v, bytes) else v
            for k, v in data.items()
        }
        return cls(**decoded_data)


class RedisManager:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)

    async def send_message(self, message: AtlasMessage):
        """Send a message to the target agent's stream."""
        stream_key = f"agent:stream:{message.destination}"
        await self.redis.xadd(stream_key, message.to_redis_dict())

    async def listen(self, agent_name: str) -> AsyncGenerator[AtlasMessage, None]:
        """Listen for messages on the agent's stream."""
        stream_key = f"agent:stream:{agent_name}"
        last_id = "$"  # Start listening for new messages only

        while True:
            # XREAD block=0 means wait indefinitely
            streams = await self.redis.xread({stream_key: last_id}, count=1, block=0)
            if not streams:
                continue

            for _, messages in streams:
                for msg_id, data in messages:
                    last_id = msg_id
                    yield AtlasMessage.from_redis_dict(data)

    async def close(self):
        """Close the Redis connection."""
        await self.redis.aclose()

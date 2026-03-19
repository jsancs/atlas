import asyncio
import pytest
from atlas.messaging import AtlasMessage, RedisManager
from fakeredis.aioredis import FakeRedis


@pytest.fixture
def mock_redis():
    return FakeRedis()


def test_atlas_message_serialization():
    message = AtlasMessage(
        source="agent-a", user="user-1", destination="agent-b", msg="hello world"
    )

    redis_dict = message.to_redis_dict()
    assert redis_dict["source"] == "agent-a"
    assert redis_dict["user"] == "user-1"
    assert redis_dict["destination"] == "agent-b"
    assert redis_dict["msg"] == "hello world"
    assert isinstance(redis_dict["timestamp"], str)

    new_message = AtlasMessage.from_redis_dict(redis_dict)
    assert new_message.id == message.id
    assert new_message.source == message.source
    assert new_message.timestamp == message.timestamp


@pytest.mark.asyncio
async def test_redis_manager_send_receive(mock_redis, monkeypatch):
    # Patch Redis.from_url to return our FakeRedis instance
    monkeypatch.setattr("atlas.messaging.Redis.from_url", lambda url: mock_redis)

    manager = RedisManager("redis://localhost")
    message = AtlasMessage(
        source="sender", user="user", destination="receiver", msg="test message"
    )

    # In a real test we'd need to run listen() in a task because it blocks
    # But since we're using FakeRedis, we can just check if XADD worked
    await manager.send_message(message)

    stream_key = f"agent:stream:{message.destination}"
    stream_data = await mock_redis.xread({stream_key: 0})

    assert len(stream_data) == 1
    _, messages = stream_data[0]
    assert len(messages) == 1
    _, data = messages[0]

    received_message = AtlasMessage.from_redis_dict(data)
    assert received_message.msg == "test message"

    await manager.close()


@pytest.mark.asyncio
async def test_redis_manager_listen(mock_redis, monkeypatch):
    monkeypatch.setattr("atlas.messaging.Redis.from_url", lambda url: mock_redis)

    manager = RedisManager("redis://localhost")
    agent_name = "test-agent"
    message = AtlasMessage(
        source="sender", user="user", destination=agent_name, msg="hello listener"
    )

    async def send_later():
        await asyncio.sleep(0.1)
        await manager.send_message(message)

    # Start sending message in the background
    asyncio.create_task(send_later())

    # Listen for the message
    received = None
    try:
        # Use wait_for to avoid hanging forever if the test fails
        async def get_one():
            async for msg in manager.listen(agent_name):
                return msg

        received = await asyncio.wait_for(get_one(), timeout=1.0)
    except asyncio.TimeoutError:
        pytest.fail("Listen timed out")

    assert received is not None
    assert received.msg == "hello listener"
    assert received.source == "sender"

    await manager.close()

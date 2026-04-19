import subprocess
from pathlib import Path
from typing import List, Union
import asyncio


def list_files(directory: Union[str, Path]) -> List[str]:
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    files = [str(f) for f in dir_path.iterdir() if f.is_file()]
    return sorted(files)


def read_file(file_path: Union[str, Path]) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path.read_text()


def write_file(file_path: Union[str, Path], content: str) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def run_shell_command(command: str, timeout: int = 20) -> str:
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=timeout
    )
    return result.stdout or result.stderr


async def call_agent(target: str, msg: str) -> str:
    """
    Sends a message to another agent and waits for a response.
    """
    from .messaging import AtlasMessage, RedisManager
    import os
    import uuid

    # Use a unique source ID for the response stream to avoid conflicts
    source = f"call-bridge-{uuid.uuid4().hex[:8]}"
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_manager = RedisManager(redis_url)
    try:
        message = AtlasMessage(
            source=source,
            user="system",
            destination=target,
            msg=msg,
        )
        await redis_manager.send_message(message)

        async def get_response():
            async for response in redis_manager.listen(source):
                return response

        response = await asyncio.wait_for(get_response(), timeout=30.0)
        return response.msg
    except Exception as e:
        return f"Error calling agent '{target}': {str(e)}"
    finally:
        await redis_manager.close()

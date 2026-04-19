import argparse
import asyncio
import os

from dotenv import load_dotenv

from .agent import AtlasAgent
from .messaging import AtlasMessage, RedisManager

load_dotenv()

DEFAULT_MODEL = os.getenv("ATLAS_MODEL", "openai:gpt-5-nano")
DEFAULT_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def run_interactive(model: str):
    agent = AtlasAgent(
        model=model,
        system_prompt="You are Atlas, a helpful AI assistant.",
    )

    print(f"Atlas interactive mode (model: {model})")
    while True:
        try:
            prompt = input("> ")
            if prompt.lower() in ("exit", "quit"):
                break

            response = await agent.run(prompt)
            print(f"\nAtlas: {response}\n")
        except EOFError:
            break
        except Exception as e:
            print(f"\nError: {e}")


async def serve(name: str, model: str, redis_url: str):
    agent = AtlasAgent(
        model=model,
        system_prompt="You are Atlas, a helpful AI assistant.",
        name=name,
    )
    redis_manager = RedisManager(redis_url)

    print(f"Starting agent '{name}' listening on {redis_url}...")
    try:
        async for message in redis_manager.listen(name):
            print(
                f"[{message.timestamp}] Received request from '{message.source}' (user: {message.user}): {message.msg}"
            )

            try:
                # Run the agent
                result = await agent.run(message.msg)

                # Send response back
                response = AtlasMessage(
                    source=name,
                    user=message.user,
                    destination=message.source,
                    msg=str(result),
                )
                await redis_manager.send_message(response)
                print(
                    f"[{response.timestamp}] Sent response to '{response.destination}'"
                )
            except Exception as e:
                print(f"Error processing message: {e}")
                error_response = AtlasMessage(
                    source=name,
                    user=message.user,
                    destination=message.source,
                    msg=f"Error: {str(e)}",
                )
                await redis_manager.send_message(error_response)

    finally:
        await redis_manager.close()


async def send(target: str, msg: str, user: str, source: str, redis_url: str):
    redis_manager = RedisManager(redis_url)
    try:
        message = AtlasMessage(
            source=source,
            user=user,
            destination=target,
            msg=msg,
        )

        print(f"Sending message to '{target}'...")
        await redis_manager.send_message(message)

        print(f"Waiting for response on '{source}' (timeout: 30s)...")
        try:

            async def get_response():
                async for response in redis_manager.listen(source):
                    return response

            response = await asyncio.wait_for(get_response(), timeout=30.0)
            print(f"\nResponse from '{response.source}':\n{response.msg}")
        except asyncio.TimeoutError:
            print(f"\nError: No response received from '{target}' within 30 seconds.")
    finally:
        await redis_manager.close()


def cli():
    parser = argparse.ArgumentParser(description="Atlas CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Interactive mode (default-ish)
    interactive_parser = subparsers.add_parser("chat", help="Start interactive chat")
    interactive_parser.add_argument(
        "--model", default=DEFAULT_MODEL, help="Model to use"
    )

    # Serve mode
    serve_parser = subparsers.add_parser(
        "serve", help="Start agent in Redis listener mode"
    )
    serve_parser.add_argument(
        "--name", required=True, help="Unique name for this agent"
    )
    serve_parser.add_argument("--model", default=DEFAULT_MODEL, help="Model to use")
    serve_parser.add_argument(
        "--redis-url", default=DEFAULT_REDIS_URL, help="Redis URL"
    )

    # Send mode
    send_parser = subparsers.add_parser(
        "send", help="Send a message to an agent via Redis"
    )
    send_parser.add_argument("--to", required=True, help="Target agent name")
    send_parser.add_argument("--msg", required=True, help="Message to send")
    send_parser.add_argument("--user", default="default-user", help="User ID")
    send_parser.add_argument(
        "--source", default="cli-client", help="Source agent/client name"
    )
    send_parser.add_argument("--redis-url", default=DEFAULT_REDIS_URL, help="Redis URL")

    args = parser.parse_args()

    if args.command == "chat" or args.command is None:
        asyncio.run(run_interactive(args.model if args.command else DEFAULT_MODEL))
    elif args.command == "serve":
        asyncio.run(serve(args.name, args.model, args.redis_url))
    elif args.command == "send":
        asyncio.run(send(args.to, args.msg, args.user, args.source, args.redis_url))
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()

import asyncio
from dotenv import load_dotenv

from .agent import AtlasAgent

load_dotenv()


async def run():
    agent = AtlasAgent(
        model="openai:gpt-5-nano",
        system_prompt="You are Atlas, a helpful AI assistant.",
    )

    prompt = input(">")
    print(f"\nUser: {prompt}")

    try:
        response = await agent.run(prompt)
        print(f"\nAtlas: {response}")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTip: Make sure your OPENAI_API_KEY is set in your environment.")


def cli():
    asyncio.run(run())


if __name__ == "__main__":
    cli()

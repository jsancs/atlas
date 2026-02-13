from typing import Optional, Any, Union
from pydantic_ai import Agent
from .tools import list_files, read_file, write_file, run_shell_command


class AtlasAgent:
    """
    A wrapper class for Pydantic AI Agent.
    Designed to simplify agent initialization and interaction.
    """

    def __init__(
        self,
        model: str,
        system_prompt: str,
        name: Optional[str] = None,
    ):
        self.name = name or "AtlasAgent"
        self.agent = Agent[None, str](
            model=model,
            system_prompt=system_prompt,
            tools=[
                list_files,
                read_file,
                write_file,
                run_shell_command,
            ],
        )

    async def run(self, user_prompt: str, **kwargs: Any) -> Any:
        """
        Runs the agent with the given user prompt.
        """
        result = await self.agent.run(user_prompt, **kwargs)
        return result.output

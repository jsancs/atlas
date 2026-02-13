import pytest
from unittest.mock import MagicMock, AsyncMock
from atlas.agent import AtlasAgent


def test_init(mock_pydantic_ai):
    """Test AtlasAgent initialization."""
    mock_agent_class, mock_agent_instance = mock_pydantic_ai

    agent = AtlasAgent(
        model="test-model",
        system_prompt="You are a helpful assistant.",
        name="CustomAgent",
    )

    assert agent.name == "CustomAgent"
    assert mock_agent_class.__getitem__.called


@pytest.mark.asyncio
async def test_run(mock_pydantic_ai):
    """Test AtlasAgent.run() method."""
    mock_agent_class, mock_agent_instance = mock_pydantic_ai

    agent = AtlasAgent(model="test-model", system_prompt="You are a helpful assistant.")

    result = MagicMock()
    result.output = "test response"
    mock_agent_instance.run = AsyncMock(return_value=result)

    response = await agent.run("test prompt")

    assert response == "test response"
    mock_agent_instance.run.assert_called_once_with("test prompt")

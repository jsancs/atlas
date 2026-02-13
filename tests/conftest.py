import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture(autouse=True)
def mock_pydantic_ai():
    """Mock the pydantic_ai Agent for all tests."""
    with patch("atlas.agent.Agent") as mock_agent_class:
        mock_agent_instance = MagicMock()

        result = MagicMock()
        result.output = "test response"
        mock_agent_instance.run = AsyncMock(return_value=result)

        agent_callable = MagicMock(return_value=mock_agent_instance)
        mock_agent_class.__getitem__ = MagicMock(return_value=agent_callable)

        yield mock_agent_class, mock_agent_instance

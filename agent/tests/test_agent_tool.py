import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import pytest
import pytest_asyncio
from agent.agent_backend.tools.agent_tool import AgentTool


def test_agent_tool_stores_name():
    tool = AgentTool("my_tool", lambda: None, {"type": "function"})
    assert tool.name == "my_tool"


def test_agent_tool_stores_description():
    desc = {"type": "function", "function": {"name": "my_tool"}}
    tool = AgentTool("my_tool", lambda: None, desc)
    assert tool.openai_description == desc


@pytest.mark.asyncio
async def test_agent_tool_calls_async_function():
    async def my_func(x: int):
        return x * 2

    tool = AgentTool("double", my_func, {})
    result = await tool.tool(x=5)
    assert result == 10


@pytest.mark.asyncio
async def test_agent_tool_passes_kwargs():
    async def greet(name: str, greeting: str = "Привет"):
        return f"{greeting}, {name}!"

    tool = AgentTool("greet", greet, {})
    result = await tool.tool(name="Кирилл", greeting="Здравствуй")
    assert result == "Здравствуй, Кирилл!"

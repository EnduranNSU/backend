import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import json
import pytest
from unittest.mock import MagicMock, patch

from agent.agent_backend.agent import Agent, GraphState
from agent.agent_backend.tools.agent_tool import AgentTool


def _tool_call_mock(name: str, args: dict, call_id: str = "call_1"):
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = name
    tc.function.arguments = json.dumps(args)
    return tc


def _llm_with_one_tool_call(tool_name: str, args: dict, final_content: str = "done"):
    """Returns a mock that on first call emits a tool call, on second call returns plain text."""
    first = MagicMock()
    first.choices[0].message.content = ""
    first.choices[0].message.tool_calls = [_tool_call_mock(tool_name, args)]

    second = MagicMock()
    second.choices[0].message.content = final_content
    second.choices[0].message.tool_calls = None

    return iter([first, second])


@pytest.mark.asyncio
async def test_tool_result_string_added_to_messages():
    async def str_tool():
        return "hello from tool"

    tool = AgentTool("str_tool", str_tool, {})
    agent = Agent({"str_tool": tool})
    responses = _llm_with_one_tool_call("str_tool", {})

    with patch.object(agent.model.chat.completions, "create", side_effect=lambda **_: next(responses)):
        result = await agent.graph.ainvoke(
            GraphState(messages=[], tool_call=[], user="c", user_id=1, user_token="t"),
            config={"configurable": {"thread_id": "t1"}},
        )

    msgs = GraphState.model_validate(result).messages
    tool_msgs = [m for m in msgs if m.get("role") == "tool"]
    assert len(tool_msgs) == 1
    assert tool_msgs[0]["content"] == "hello from tool"


@pytest.mark.asyncio
async def test_tool_dict_result_json_serialized():
    async def dict_tool():
        return {"key": "value", "num": 42}

    tool = AgentTool("dict_tool", dict_tool, {})
    agent = Agent({"dict_tool": tool})
    responses = _llm_with_one_tool_call("dict_tool", {})

    with patch.object(agent.model.chat.completions, "create", side_effect=lambda **_: next(responses)):
        result = await agent.graph.ainvoke(
            GraphState(messages=[], tool_call=[], user="c", user_id=1, user_token="t"),
            config={"configurable": {"thread_id": "t2"}},
        )

    msgs = GraphState.model_validate(result).messages
    tool_msgs = [m for m in msgs if m.get("role") == "tool"]
    parsed = json.loads(tool_msgs[0]["content"])
    assert parsed["key"] == "value"
    assert parsed["num"] == 42


@pytest.mark.asyncio
async def test_unknown_tool_adds_error_to_messages():
    agent = Agent({})
    responses = _llm_with_one_tool_call("nonexistent_tool", {}, final_content="Инструмент не найден")

    with patch.object(agent.model.chat.completions, "create", side_effect=lambda **_: next(responses)):
        result = await agent.graph.ainvoke(
            GraphState(messages=[], tool_call=[], user="c", user_id=1, user_token="t"),
            config={"configurable": {"thread_id": "t3"}},
        )

    msgs = GraphState.model_validate(result).messages
    tool_msgs = [m for m in msgs if m.get("role") == "tool"]
    assert any("not registered" in m["content"] for m in tool_msgs)


@pytest.mark.asyncio
async def test_tool_exception_captured():
    async def failing_tool():
        raise ValueError("boom")

    tool = AgentTool("bad_tool", failing_tool, {})
    agent = Agent({"bad_tool": tool})
    responses = _llm_with_one_tool_call("bad_tool", {})

    with patch.object(agent.model.chat.completions, "create", side_effect=lambda **_: next(responses)):
        result = await agent.graph.ainvoke(
            GraphState(messages=[], tool_call=[], user="c", user_id=1, user_token="t"),
            config={"configurable": {"thread_id": "t4"}},
        )

    msgs = GraphState.model_validate(result).messages
    tool_msgs = [m for m in msgs if m.get("role") == "tool"]
    assert any("raised" in m["content"] for m in tool_msgs)


@pytest.mark.asyncio
async def test_user_id_injected_into_tool():
    received = {}

    async def needs_user_id(user_id: int):
        received["user_id"] = user_id
        return "ok"

    tool = AgentTool("needs_user_id", needs_user_id, {})
    agent = Agent({"needs_user_id": tool})
    responses = _llm_with_one_tool_call("needs_user_id", {})

    with patch.object(agent.model.chat.completions, "create", side_effect=lambda **_: next(responses)):
        await agent.graph.ainvoke(
            GraphState(messages=[], tool_call=[], user="c", user_id=77, user_token="t"),
            config={"configurable": {"thread_id": "t5"}},
        )

    assert received["user_id"] == 77


@pytest.mark.asyncio
async def test_user_token_injected_into_tool():
    received = {}

    async def needs_token(user_token: str):
        received["token"] = user_token
        return "ok"

    tool = AgentTool("needs_token", needs_token, {})
    agent = Agent({"needs_token": tool})
    responses = _llm_with_one_tool_call("needs_token", {})

    with patch.object(agent.model.chat.completions, "create", side_effect=lambda **_: next(responses)):
        await agent.graph.ainvoke(
            GraphState(messages=[], tool_call=[], user="c", user_id=1, user_token="my_token"),
            config={"configurable": {"thread_id": "t6"}},
        )

    assert received["token"] == "my_token"


@pytest.mark.asyncio
async def test_none_tool_result_becomes_empty_string():
    async def none_tool():
        return None

    tool = AgentTool("none_tool", none_tool, {})
    agent = Agent({"none_tool": tool})
    responses = _llm_with_one_tool_call("none_tool", {})

    with patch.object(agent.model.chat.completions, "create", side_effect=lambda **_: next(responses)):
        result = await agent.graph.ainvoke(
            GraphState(messages=[], tool_call=[], user="c", user_id=1, user_token="t"),
            config={"configurable": {"thread_id": "t7"}},
        )

    msgs = GraphState.model_validate(result).messages
    tool_msgs = [m for m in msgs if m.get("role") == "tool"]
    assert tool_msgs[0]["content"] == ""

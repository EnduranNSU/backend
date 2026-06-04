"""End-to-end-ish test that the agent really wires user_id into user RAG calls.

We mock the LLM to emit a tool call for user_rag_upload, mock the upstream
retriever HTTP, and check the tool got user_id from state.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from agent.agent_backend.agent import Agent, GraphState
from agent.agent_backend.tools.users_rag_upload_tool import user_rag_upload_tool
from agent.agent_backend.tools.users_rag_download_tool import user_rag_download_tool


def _tool_call_mock(name: str, args: dict, call_id: str = "call_1"):
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = name
    tc.function.arguments = json.dumps(args, ensure_ascii=False)
    return tc


def _llm_emits_tool_then_answer(tool_name: str, args: dict, final_text: str):
    first = MagicMock()
    first.choices[0].message.content = ""
    first.choices[0].message.tool_calls = [_tool_call_mock(tool_name, args)]

    second = MagicMock()
    second.choices[0].message.content = final_text
    second.choices[0].message.tool_calls = None
    return iter([first, second])


@pytest.mark.asyncio
async def test_upload_tool_receives_user_id_from_state():
    """When LLM emits user_rag_upload(info=…), the executor must inject user_id."""
    captured = {}

    async def fake_upload(info: str, user_id: int):
        captured["info"] = info
        captured["user_id"] = user_id
        return "ok"

    tool = user_rag_upload_tool
    tool.tool = fake_upload

    agent = Agent({"user_rag_upload": tool})
    responses = _llm_emits_tool_then_answer(
        "user_rag_upload",
        {"info": "У пользователя проблемы со спиной"},
        final_text="Запомнил, что у тебя проблемы со спиной.",
    )

    with patch.object(agent.model.chat.completions, "create",
                      side_effect=lambda **_: next(responses)):
        result = await agent.graph.ainvoke(
            GraphState(messages=[], tool_call=[], user="chat-1", user_id=42, user_token="t"),
            config={"configurable": {"thread_id": "mem-test-1"}},
        )

    assert captured["user_id"] == 42
    assert "спин" in captured["info"].lower()


@pytest.mark.asyncio
async def test_download_tool_receives_user_id_from_state():
    captured = {}

    async def fake_download(query: str, user_id: int):
        captured["query"] = query
        captured["user_id"] = user_id
        return "found: ничего"

    tool = user_rag_download_tool
    tool.tool = fake_download

    agent = Agent({"user_rag_download": tool})
    responses = _llm_emits_tool_then_answer(
        "user_rag_download",
        {"query": "ограничения и травмы"},
        final_text="Ничего пока не помню о тебе.",
    )

    with patch.object(agent.model.chat.completions, "create",
                      side_effect=lambda **_: next(responses)):
        await agent.graph.ainvoke(
            GraphState(messages=[], tool_call=[], user="c", user_id=7, user_token="t"),
            config={"configurable": {"thread_id": "mem-test-2"}},
        )

    assert captured["user_id"] == 7
    assert captured["query"] == "ограничения и травмы"


@pytest.mark.asyncio
async def test_memory_round_trip_save_then_recall():
    """Simulate two-turn scenario: save fact, then recall it later."""
    store: dict[int, list[str]] = {}

    async def fake_upload(info: str, user_id: int):
        store.setdefault(user_id, []).append(info)
        return "saved"

    async def fake_download(query: str, user_id: int):
        return "\n".join(store.get(user_id, [])) or "no memory"

    up = user_rag_upload_tool
    up.tool = fake_upload
    dn = user_rag_download_tool
    dn.tool = fake_download

    agent = Agent({"user_rag_upload": up, "user_rag_download": dn})

    # Turn 1: user says "проблемы со спиной" → LLM emits upload then plain reply
    turn1 = _llm_emits_tool_then_answer(
        "user_rag_upload",
        {"info": "Проблемы со спиной"},
        final_text="Запомнил.",
    )
    with patch.object(agent.model.chat.completions, "create",
                      side_effect=lambda **_: next(turn1)):
        await agent.graph.ainvoke(
            GraphState(
                messages=[{"role": "user", "content": "у меня проблемы со спиной"}],
                tool_call=[], user="c", user_id=99, user_token="t",
            ),
            config={"configurable": {"thread_id": "round-trip"}},
        )

    assert "Проблемы со спиной" in store[99]

    # Turn 2: user asks for exercises → LLM downloads, then answers using memory
    turn2 = _llm_emits_tool_then_answer(
        "user_rag_download",
        {"query": "ограничения"},
        final_text="Помню, у тебя проблемы со спиной — приседы не подойдут.",
    )
    with patch.object(agent.model.chat.completions, "create",
                      side_effect=lambda **_: next(turn2)):
        result = await agent.graph.ainvoke(
            GraphState(
                messages=[{"role": "user", "content": "посоветуй упражнения на ноги"}],
                tool_call=[], user="c", user_id=99, user_token="t",
            ),
            config={"configurable": {"thread_id": "round-trip-2"}},
        )

    msgs = GraphState.model_validate(result).messages
    tool_msgs = [m for m in msgs if m.get("role") == "tool"]
    assert any("Проблемы со спиной" in m["content"] for m in tool_msgs), \
        "memory should have surfaced through user_rag_download"
    final = msgs[-1]["content"]
    assert "спин" in final.lower()

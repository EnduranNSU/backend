import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import pytest
from unittest.mock import MagicMock, patch

# Patch the model import so we don't need real API keys
with patch.dict("sys.modules", {
    "agent.agent_backend.model": MagicMock(client=MagicMock(), CHAT_MODEL="test-model"),
    "langgraph.graph": MagicMock(),
    "langgraph.checkpoint.memory": MagicMock(),
}):
    from agent.agent_backend.agent import _normalize_tool_call


def test_normalize_dict_tool_call():
    tc = {
        "id": "call_123",
        "type": "function",
        "function": {"name": "my_tool", "arguments": '{"key": "val"}'},
    }
    result = _normalize_tool_call(tc)
    assert result["id"] == "call_123"
    assert result["function"]["name"] == "my_tool"
    assert result["function"]["arguments"] == '{"key": "val"}'


def test_normalize_dict_defaults_type():
    tc = {"id": "x", "function": {"name": "tool", "arguments": "{}"}}
    result = _normalize_tool_call(tc)
    assert result["type"] == "function"


def test_normalize_dict_missing_arguments_defaults_to_empty():
    tc = {"id": "x", "function": {"name": "tool"}}
    result = _normalize_tool_call(tc)
    assert result["function"]["arguments"] == "{}"


def test_normalize_sdk_object():
    tc = MagicMock()
    tc.id = "sdk_id"
    tc.function.name = "sdk_tool"
    tc.function.arguments = '{"a": 1}'
    # SDK object is not a dict
    del tc.__class__.__contains__  # ensure isinstance(tc, dict) is False

    result = _normalize_tool_call(tc)
    assert result["id"] == "sdk_id"
    assert result["function"]["name"] == "sdk_tool"
    assert result["function"]["arguments"] == '{"a": 1}'
    assert result["type"] == "function"

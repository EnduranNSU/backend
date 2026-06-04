"""Regression tests for the RAG-tool wiring bugs we just fixed:

  • exercise_rag tool had typo `exrcise_rag_get` in its OpenAI name → the LLM
    would call it and the executor wouldn't find a matching key in `tools`.
  • user_rag_download / user_rag_upload had `required` outside `parameters` —
    technically off-spec, some upstream models reject it.
  • utils/rag.py returned httpx.Response objects, which became
    "<Response [200 OK]>" in the tool message. Now they parse JSON.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import inspect
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from agent.agent_backend.tools import tools
from agent.agent_backend.tools.exercise_rag import exercise_rag_get_tool
from agent.agent_backend.tools.users_rag_download_tool import user_rag_download_tool
from agent.agent_backend.tools.users_rag_upload_tool import user_rag_upload_tool


# ─── Name-vs-registration consistency ────────────────────────────────────────

@pytest.mark.parametrize("tool_obj", [
    exercise_rag_get_tool,
    user_rag_download_tool,
    user_rag_upload_tool,
])
def test_openai_name_matches_registration(tool_obj):
    """The function name surfaced to the LLM must match the dict key in tools."""
    openai_name = tool_obj.openai_description["function"]["name"]
    assert openai_name == tool_obj.name, (
        f"OpenAI exposes '{openai_name}' but AgentTool is registered as '{tool_obj.name}' — "
        f"LLM calls will never resolve to this tool"
    )


def test_every_registered_tool_is_resolvable_by_its_openai_name():
    """Walk the full registry and confirm every advertised name is in the dict."""
    for tool_obj in tools.values():
        advertised = tool_obj.openai_description["function"]["name"]
        assert advertised in tools, (
            f"Tool '{tool_obj.name}' advertises itself as '{advertised}' but that key "
            f"is missing from the tools dict — executor will return 'not registered'"
        )


# ─── OpenAI schema compliance: `required` must be inside `parameters` ───────

@pytest.mark.parametrize("tool_obj", list(tools.values()))
def test_required_lives_inside_parameters(tool_obj):
    """OpenAI spec puts `required` as a property of `parameters`, not `function`."""
    fn = tool_obj.openai_description["function"]
    assert "required" not in fn or fn.get("required") is None, (
        f"{tool_obj.name}: `required` is on the function object — should be inside parameters"
    )
    if "parameters" in fn and "properties" in fn["parameters"]:
        # If there are required fields, they must list valid properties.
        req = fn["parameters"].get("required", [])
        props = set(fn["parameters"]["properties"].keys())
        for r in req:
            assert r in props, f"{tool_obj.name}: required field '{r}' not in properties"


# ─── Tool callables accept the params they advertise ────────────────────────

@pytest.mark.parametrize("tool_obj", list(tools.values()))
def test_advertised_params_are_real_callable_args(tool_obj):
    """Every parameter the LLM may send must be a real keyword on the callable.

    user_id / user_token are injected from agent state, so they are allowed
    to exist on the callable without being in the schema.
    """
    advertised = set(tool_obj.openai_description["function"]
                     .get("parameters", {}).get("properties", {}).keys())
    sig = inspect.signature(tool_obj.tool)
    real_params = set(sig.parameters.keys()) - {"user_id", "user_token"}
    missing = advertised - set(sig.parameters.keys())
    assert not missing, (
        f"{tool_obj.name}: schema advertises {missing} but callable doesn't accept them"
    )


# ─── utils/rag.py must return dicts, not httpx.Response ─────────────────────

@pytest.mark.asyncio
async def test_exercise_rag_returns_parsed_json():
    from agent.utils import rag as rag_module

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"results": [{"id": "1", "score": 0.9}]}
    mock_resp.raise_for_status = MagicMock()

    async def fake_post(*a, **kw):
        return mock_resp

    with patch.object(rag_module.httpx, "AsyncClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=mock_resp)
        result = await rag_module.exercise_rag("technique", ["Приседания", "technique"])

    assert isinstance(result, dict)
    assert "results" in result
    assert result["results"][0]["id"] == "1"


@pytest.mark.asyncio
async def test_user_get_returns_parsed_json():
    from agent.utils import rag as rag_module

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"results": ["проблемы со спиной"]}
    mock_resp.raise_for_status = MagicMock()

    with patch.object(rag_module.httpx, "AsyncClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=mock_resp)
        result = await rag_module.user_get("ограничения", user_id=42)

    assert isinstance(result, dict)
    assert result["results"] == ["проблемы со спиной"]


@pytest.mark.asyncio
async def test_user_save_returns_parsed_json():
    from agent.utils import rag as rag_module

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "ok"}
    mock_resp.raise_for_status = MagicMock()

    with patch.object(rag_module.httpx, "AsyncClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=mock_resp)
        result = await rag_module.user_save("Проблемы со спиной", user_id=7)

    assert isinstance(result, dict)
    assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_rag_network_failure_returns_structured_error():
    """When retriever is unreachable, the tool must return a dict the LLM can read,
    not crash and not return a bare exception string."""
    from agent.utils import rag as rag_module
    import httpx as _httpx

    with patch.object(rag_module.httpx, "AsyncClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.post = AsyncMock(side_effect=_httpx.ConnectError("nope"))
        result = await rag_module.user_get("test", user_id=1)

    assert isinstance(result, dict)
    assert "error" in result
    assert "results" in result
    assert result["results"] == []

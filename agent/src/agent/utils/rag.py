"""HTTP wrappers around the retriever service.

These return PARSED JSON (dict/list), not httpx.Response objects.
The agent's executor serializes whatever tools return into the tool message
content; if we returned a Response, the LLM would just see "<Response [200 OK]>"
and conclude that the tool is broken.
"""
from __future__ import annotations

import httpx

from agent.config import get_config


config = get_config()
_RAG_BASE = f"http://{config.rag.host}:{config.rag.port}"
_TIMEOUT = httpx.Timeout(30.0, connect=5.0)


async def _post(path: str, payload: dict) -> dict:
    """POST + parse JSON. On failure return a dict so the LLM gets structured feedback."""
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(f"{_RAG_BASE}{path}", json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        return {
            "error": f"retriever returned {exc.response.status_code}",
            "detail": exc.response.text[:500],
            "results": [],
        }
    except httpx.RequestError as exc:
        return {
            "error": f"retriever unreachable: {exc.__class__.__name__}: {exc}",
            "results": [],
        }


async def exercise_rag(query: str, tags: list[str]) -> dict:
    return await _post(
        "/exercise/",
        {
            "rag_name": "ex_cool",
            "query": query,
            "limit": 10,
            "tags": tags,
        },
    )


async def user_get(query: str, user_id: int) -> dict:
    return await _post(
        "/user/",
        {
            "rag_name": "tag_only",
            "query": query,
            "limit": 10,
            "tags": [str(user_id)],
        },
    )


async def user_save(info: str, user_id: int) -> dict:
    return await _post(
        "/user/save",
        {"info": info, "user": str(user_id)},
    )

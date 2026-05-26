"""OpenAI-compatible facade. Forwards to the configured upstream provider."""
from __future__ import annotations

import json

import httpx
from fastapi import APIRouter, HTTPException, Request, Response

from .providers import load_config


config = load_config()
_client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))


router = APIRouter(prefix="/v1", tags=["llm"])


def _override_model(body: bytes) -> bytes:
    """If the client sent model='default' (or omitted it), substitute provider default."""
    if not body:
        return body
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return body
    model = payload.get("model", "default")
    if model in (None, "", "default") and config.chat_model:
        payload["model"] = config.chat_model
        return json.dumps(payload).encode()
    return body


@router.post("/chat/completions")
async def chat_completions(request: Request) -> Response:
    if not config.api_key:
        raise HTTPException(
            status_code=503,
            detail="LLM proxy has no api key configured (set YANDEX_API_KEY / OPENAI_API_KEY)",
        )

    body = _override_model(await request.body())
    upstream_url = config.base_url.rstrip("/") + "/chat/completions"

    headers = {
        "Authorization": f"{config.auth_scheme} {config.api_key}",
        "Content-Type": request.headers.get("content-type", "application/json"),
    }

    try:
        upstream = await _client.post(upstream_url, headers=headers, content=body)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream LLM error: {exc}") from exc

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type", "application/json"),
    )


@router.get("/models")
async def models():
    return {
        "object": "list",
        "data": [{"id": config.chat_model or "default", "object": "model"}],
    }

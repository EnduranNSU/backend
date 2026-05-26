"""Tiny HTTP reverse-proxy: by path prefix, forwards request to the right service."""
from __future__ import annotations

import os
from typing import Iterable

import httpx
from fastapi import APIRouter, Request, Response, HTTPException


# (prefix on gateway, upstream base URL, strip-prefix?)
# Order matters: longer prefixes first.
ROUTES: list[tuple[str, str, bool]] = [
    # CV service
    ("/cv",            os.environ.get("CV_URL",       "http://cv_service:9090"), False),
    # Retriever (RAG) — mounted under /search to avoid colliding with backend's /exercise.
    ("/search",        os.environ.get("RAG_URL",      "http://retriever:8888"),  True),
    # LLM agent
    ("/agent",         os.environ.get("AGENT_URL",    "http://agent:8080"),      False),
    # LLM proxy (OpenAI-compatible) — exposed via gateway under /llm
    ("/llm",           os.environ.get("LLM_URL",      "http://llm:9000"),        True),
    # Backend (auth, users, exercises, trainings, measurements)
    ("/token",         os.environ.get("BACKEND_URL",  "http://backend:8000"),    False),
    ("/signup",        os.environ.get("BACKEND_URL",  "http://backend:8000"),    False),
    ("/user",          os.environ.get("BACKEND_URL",  "http://backend:8000"),    False),
    ("/exercise",      os.environ.get("BACKEND_URL",  "http://backend:8000"),    False),
    ("/training",      os.environ.get("BACKEND_URL",  "http://backend:8000"),    False),
    ("/measurements",  os.environ.get("BACKEND_URL",  "http://backend:8000"),    False),
]

# Hop-by-hop headers — never forward.
_HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "host", "content-length",
}


def _filter_headers(headers: Iterable[tuple[str, str]]) -> dict[str, str]:
    return {k: v for k, v in headers if k.lower() not in _HOP_BY_HOP}


def _resolve(path: str) -> tuple[str, str] | None:
    for prefix, base, strip in ROUTES:
        if path == prefix or path.startswith(prefix + "/"):
            tail = path[len(prefix):] if strip else path
            if not tail:
                tail = "/"
            return base, tail
    return None


router = APIRouter()

# Long timeout: video upload to /cv/analyze can take a while.
_client = httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0))


@router.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
)
async def proxy(full_path: str, request: Request) -> Response:
    path = "/" + full_path
    target = _resolve(path)
    if target is None:
        raise HTTPException(status_code=404, detail=f"No upstream for {path}")

    base, tail = target
    upstream_url = base.rstrip("/") + tail

    body = await request.body()
    try:
        upstream = await _client.request(
            request.method,
            upstream_url,
            params=request.query_params,
            headers=_filter_headers(request.headers.items()),
            content=body,
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}") from exc

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=_filter_headers(upstream.headers.items()),
        media_type=upstream.headers.get("content-type"),
    )

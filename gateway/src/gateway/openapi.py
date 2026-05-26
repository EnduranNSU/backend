"""Build a single OpenAPI schema from all upstreams.

Each upstream FastAPI service exposes its own /openapi.json. We fetch them,
rewrite paths so they sit under the gateway prefixes, merge components,
and return one schema so /docs shows every real endpoint with full
request/response info.

Result is cached after first successful aggregation. Set _cache = None
to force a refresh (we do this lazily if any upstream was unreachable).
"""
from __future__ import annotations

from typing import Any

import httpx

from .proxy import ROUTES


_INFRA_PATHS = {"/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"}
_cache: dict | None = None


def _fetch_schemas(timeout: float = 5.0) -> dict[str, dict]:
    """Pull /openapi.json from every unique upstream URL."""
    urls = sorted({base for _, base, _ in ROUTES})
    out: dict[str, dict] = {}
    with httpx.Client(timeout=timeout) as client:
        for url in urls:
            try:
                resp = client.get(f"{url.rstrip('/')}/openapi.json")
                resp.raise_for_status()
                out[url] = resp.json()
            except Exception:
                # missing upstream means its routes simply won't show up; the
                # proxy will still 502 cleanly if someone calls them.
                pass
    return out


def _apply_tag(methods: dict[str, Any], tag: str) -> None:
    for op in methods.values():
        if not isinstance(op, dict):
            continue
        tags = op.get("tags", [])
        if tag not in tags:
            op["tags"] = [tag, *tags]


def _rewrite_for_route(
    schema: dict, gateway_prefix: str, strip: bool
) -> dict[str, dict]:
    """Project this upstream's paths into the gateway's namespace."""
    out: dict[str, dict] = {}
    tag = gateway_prefix.strip("/") or "default"

    for path, methods in schema.get("paths", {}).items():
        if path in _INFRA_PATHS:
            continue

        if strip:
            # Upstream "/v1/x" → gateway "/llm/v1/x"
            new_path = gateway_prefix + path
        else:
            # Upstream "/user/" already sits at the gateway path.
            # Only include if it actually starts with this gateway prefix.
            if not (path == gateway_prefix or path.startswith(gateway_prefix + "/")):
                continue
            new_path = path

        _apply_tag(methods, tag)
        out[new_path] = methods

    return out


def build() -> dict:
    """Merge all upstream schemas into one. Uses a process-local cache."""
    global _cache
    if _cache is not None:
        return _cache

    merged: dict = {
        "openapi": "3.1.0",
        "info": {
            "title": "Gateway",
            "version": "1.0.0",
            "description": "Единая точка входа: backend / cv / retriever / agent / llm",
        },
        "paths": {},
        "components": {"schemas": {}},
    }

    url_schemas = _fetch_schemas()
    any_upstream_seen = False

    for prefix, base_url, strip in ROUTES:
        schema = url_schemas.get(base_url)
        if not schema:
            continue
        any_upstream_seen = True

        merged["paths"].update(_rewrite_for_route(schema, prefix, strip))

        for name, body in schema.get("components", {}).get("schemas", {}).items():
            merged["components"]["schemas"].setdefault(name, body)

        for name, body in (schema.get("components", {}).get("securitySchemes") or {}).items():
            merged["components"].setdefault("securitySchemes", {}).setdefault(name, body)

    # Only cache if at least one upstream was reachable — otherwise next call retries.
    if any_upstream_seen:
        _cache = merged
    return merged


def invalidate() -> None:
    global _cache
    _cache = None

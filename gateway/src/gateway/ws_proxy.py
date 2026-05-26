"""WebSocket reverse proxy.

For each gateway prefix listed in `ROUTES` we mount one WS handler that
pipes bytes/text in both directions between client and upstream.
"""
from __future__ import annotations

import asyncio
from urllib.parse import urlparse

import websockets
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .proxy import ROUTES


router = APIRouter()


def _ws_url(base_url: str, tail: str) -> str:
    parsed = urlparse(base_url)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    return f"{scheme}://{parsed.netloc}{tail}"


async def _pump_client_to_upstream(ws: WebSocket, upstream) -> None:
    try:
        while True:
            msg = await ws.receive()
            if msg.get("type") == "websocket.disconnect":
                break
            if msg.get("bytes") is not None:
                await upstream.send(msg["bytes"])
            elif msg.get("text") is not None:
                await upstream.send(msg["text"])
    except WebSocketDisconnect:
        pass
    finally:
        await upstream.close()


async def _pump_upstream_to_client(ws: WebSocket, upstream) -> None:
    try:
        async for msg in upstream:
            if isinstance(msg, (bytes, bytearray)):
                await ws.send_bytes(msg)
            else:
                await ws.send_text(msg)
    except websockets.ConnectionClosed:
        pass


def _register_ws_proxy(prefix: str, base_url: str, strip: bool) -> None:
    path = f"{prefix}/{{tail:path}}"

    async def handler(websocket: WebSocket, tail: str = ""):
        await websocket.accept()
        upstream_tail = ("/" + tail) if not strip else ("/" + tail)
        if not strip:
            upstream_tail = f"{prefix}/{tail}" if tail else prefix
        upstream_url = _ws_url(base_url, upstream_tail)

        try:
            async with websockets.connect(
                upstream_url, max_size=None, close_timeout=1
            ) as upstream:
                await asyncio.gather(
                    _pump_client_to_upstream(websocket, upstream),
                    _pump_upstream_to_client(websocket, upstream),
                )
        except (OSError, websockets.InvalidURI, websockets.InvalidHandshake) as exc:
            try:
                await websocket.send_json({"error": f"upstream ws failed: {exc}"})
            except Exception:
                pass
            await websocket.close(code=1011)

    router.add_api_websocket_route(path, handler)


for _prefix, _base, _strip in ROUTES:
    _register_ws_proxy(_prefix, _base, _strip)

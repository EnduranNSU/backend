"""WebSocket: live squat coaching.

Protocol:
  client → server: binary JPEG frames (one per ws.send_bytes)
  server → client: JSON per frame:
    {
      "frame": int, "detected": bool,
      "knee_angle": float, "knee_collapse": float,
      "state": "up" | "down",
      "label": "OK" | "BAD" | "IDLE",
      "hint": str,
      "reps_total": int,
      "last_rep_ok": bool | null
    }

  client may send a JSON text message {"cmd": "reset"} to start a new set.
"""
from __future__ import annotations

import json
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from cv_service.exercises import EXERCISE_MAP
from cv_service.live import LiveAnalyzer


router = APIRouter(prefix="/cv", tags=["cv"])

MODEL_PATH = os.environ.get(
    "POSE_MODEL_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                 "pose_landmarker_full.task"),
)


_SUPPORTED_EXERCISES = set(EXERCISE_MAP.keys())


@router.websocket("/ws/{exercise}")
async def ws_live(websocket: WebSocket, exercise: str):
    await websocket.accept()
    if exercise not in _SUPPORTED_EXERCISES:
        await websocket.send_json({
            "error": f"unsupported exercise: {exercise}",
            "supported": sorted(_SUPPORTED_EXERCISES),
        })
        await websocket.close()
        return

    if not os.path.exists(MODEL_PATH):
        await websocket.send_json({"error": f"model not found: {MODEL_PATH}"})
        await websocket.close()
        return

    analyzer = LiveAnalyzer(MODEL_PATH, exercise=exercise)
    try:
        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.disconnect":
                break

            # Text frame → control command
            if "text" in msg and msg["text"] is not None:
                try:
                    cmd = json.loads(msg["text"]).get("cmd")
                except json.JSONDecodeError:
                    cmd = None
                if cmd == "reset":
                    analyzer.close()
                    analyzer = LiveAnalyzer(MODEL_PATH, exercise=exercise)
                    await websocket.send_json({"status": "reset"})
                continue

            # Binary frame → JPEG image
            data = msg.get("bytes")
            if not data:
                continue

            result = analyzer.process(data)
            await websocket.send_json(result)

    except WebSocketDisconnect:
        pass
    finally:
        analyzer.close()

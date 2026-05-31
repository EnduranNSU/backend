"""Stateful per-frame exercise analyzer for WebSocket streaming.

Client sends JPEG bytes; we decode, run MediaPipe, return a small JSON with
key angles, the rep counter, and an OK/BAD label so the UI can paint feedback
in real time.
"""
from __future__ import annotations

import time

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision

from .exercises import EXERCISE_MAP


class LiveAnalyzer:
    """One instance per WebSocket connection."""

    def __init__(self, model_path: str, exercise: str = "squat"):
        self._opts = vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
        )
        self._landmarker = vision.PoseLandmarker.create_from_options(self._opts)
        self._t0 = time.monotonic()
        self._frame_idx = 0
        analyzer_cls = EXERCISE_MAP.get(exercise, EXERCISE_MAP["squat"])
        self._ex = analyzer_cls()

    def close(self) -> None:
        try:
            self._landmarker.close()
        except Exception:
            pass

    def process(self, jpeg_bytes: bytes) -> dict:
        idx = self._frame_idx
        self._frame_idx += 1
        ts_ms = int((time.monotonic() - self._t0) * 1000)

        frame = cv2.imdecode(np.frombuffer(jpeg_bytes, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return {"frame": idx, "detected": False, "error": "decode_failed"}

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
        )
        try:
            result = self._landmarker.detect_for_video(mp_image, ts_ms)
        except Exception as exc:
            return {"frame": idx, "detected": False, "error": str(exc)}

        if not result.pose_landmarks:
            return {
                "frame": idx,
                "detected": False,
                "reps_total": self._ex._r.completed,
                "state": self._ex._r.state,
            }

        lm = result.pose_landmarks[0]
        try:
            payload = self._ex.process(lm, idx)
        except (IndexError, AttributeError) as exc:
            return {"frame": idx, "detected": False, "error": f"landmark_error: {exc}"}

        payload["frame"] = idx
        return payload

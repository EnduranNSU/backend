"""Stateful per-frame squat analyzer for WebSocket streaming.

Client sends JPEG bytes; we decode, run MediaPipe, return a small JSON with
the angle, the rep counter, and an OK/BAD label so the UI can paint feedback
in real time.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision

from .analyzer import (
    LEFT_HIP, LEFT_KNEE, LEFT_ANKLE,
    RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE,
    DEPTH_ANGLE_OK, REP_DOWN_ANGLE, REP_UP_ANGLE,
    KNEE_COLLAPSE_THRESHOLD, MIN_REP_FRAMES,
    _angle, _knee_collapse,
)


@dataclass
class _RepState:
    state: str = "up"
    rep_start_frame: int | None = None
    rep_min_angle: float = 180.0
    rep_max_collapse: float = 0.0
    completed: int = 0
    last_completed_ok: bool | None = None


class LiveAnalyzer:
    """One instance per WebSocket connection."""

    def __init__(self, model_path: str):
        self._opts = vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
        )
        self._landmarker = vision.PoseLandmarker.create_from_options(self._opts)
        self._t0 = time.monotonic()
        self._frame_idx = 0
        self._rep = _RepState()

    def close(self) -> None:
        try:
            self._landmarker.close()
        except Exception:
            pass

    # ------------------------------------------------------------------

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
                "reps_total": self._rep.completed,
                "state": self._rep.state,
            }

        lm = result.pose_landmarks[0]
        try:
            left_vis = lm[LEFT_HIP].visibility + lm[LEFT_KNEE].visibility + lm[LEFT_ANKLE].visibility
            right_vis = lm[RIGHT_HIP].visibility + lm[RIGHT_KNEE].visibility + lm[RIGHT_ANKLE].visibility
            if right_vis > left_vis:
                h_i, k_i, a_i = RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE
            else:
                h_i, k_i, a_i = LEFT_HIP, LEFT_KNEE, LEFT_ANKLE
            hip = (lm[h_i].x, lm[h_i].y)
            knee = (lm[k_i].x, lm[k_i].y)
            ankle = (lm[a_i].x, lm[a_i].y)
        except (IndexError, AttributeError):
            return {"frame": idx, "detected": False, "error": "landmark_missing"}

        knee_ang = _angle(hip, knee, ankle)
        collapse = _knee_collapse(hip, knee, ankle)

        # rep state machine
        r = self._rep
        if r.state == "up":
            if knee_ang <= REP_DOWN_ANGLE:
                r.state = "down"
                r.rep_start_frame = idx
                r.rep_min_angle = knee_ang
                r.rep_max_collapse = collapse
        else:  # down
            r.rep_min_angle = min(r.rep_min_angle, knee_ang)
            r.rep_max_collapse = max(r.rep_max_collapse, collapse)
            if knee_ang >= REP_UP_ANGLE:
                if r.rep_start_frame is not None and idx - r.rep_start_frame >= MIN_REP_FRAMES:
                    deep = r.rep_min_angle <= DEPTH_ANGLE_OK
                    collapsed = r.rep_max_collapse >= KNEE_COLLAPSE_THRESHOLD
                    r.completed += 1
                    r.last_completed_ok = deep and not collapsed
                r.state = "up"
                r.rep_start_frame = None
                r.rep_min_angle = 180.0
                r.rep_max_collapse = 0.0

        # per-frame verdict
        if r.state == "down":
            if collapse >= KNEE_COLLAPSE_THRESHOLD:
                label, color = "BAD", "колени заваливаются внутрь"
            elif knee_ang <= DEPTH_ANGLE_OK:
                label, color = "OK", "глубина норм"
            else:
                label, color = "OK", "опускаемся"
        else:
            label, color = "IDLE", "встал"

        return {
            "frame": idx,
            "detected": True,
            "knee_angle": round(knee_ang, 1),
            "knee_collapse": round(collapse, 4),
            "state": r.state,
            "label": label,
            "hint": color,
            "reps_total": r.completed,
            "last_rep_ok": r.last_completed_ok,
        }

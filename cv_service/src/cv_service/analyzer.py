"""Exercise quality analysis from a video file.

Pipeline:
  1. read frames via OpenCV
  2. run MediaPipe PoseLandmarker per frame
  3. for each frame compute exercise-specific metrics
  4. detect reps as descent/ascent cycles
  5. aggregate into a verdict
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from typing import Iterable

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision


# MediaPipe pose landmark indices
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_HIP = 23
LEFT_KNEE = 25
LEFT_ANKLE = 27
RIGHT_HIP = 24
RIGHT_KNEE = 26
RIGHT_ANKLE = 28

# Empirical thresholds for squats
DEPTH_ANGLE_OK = 100.0
REP_DOWN_ANGLE = 110.0
REP_UP_ANGLE = 160.0
KNEE_COLLAPSE_THRESHOLD = 0.04
MIN_REP_FRAMES = 5


def _angle(a, b, c) -> float:
    """Angle ABC in degrees, given 2D points."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return float(np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0))))


def _knee_collapse(hip, knee, ankle) -> float:
    midline_x = (hip[0] + ankle[0]) / 2.0
    return float(abs(knee[0] - midline_x))


@dataclass
class FrameMetrics:
    frame_idx: int
    timestamp_ms: int
    detected: bool
    knee_angle: float | None = None
    hip_angle: float | None = None
    knee_collapse: float | None = None


@dataclass
class RepMetrics:
    start_frame: int
    end_frame: int
    min_knee_angle: float
    max_knee_collapse: float
    deep_enough: bool
    knee_collapsed: bool


@dataclass
class AnalysisReport:
    frames_total: int
    frames_with_pose: int
    exercise: str = "squat"
    reps: list[RepMetrics] = field(default_factory=list)
    avg_min_knee_angle: float | None = None
    avg_knee_collapse: float | None = None
    knee_collapse_ratio: float = 0.0
    depth_ratio: float = 0.0
    verdict: str = ""
    extra_metrics: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def _iter_frames(video_path: str) -> Iterable[tuple[int, int, np.ndarray]]:
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            ts_ms = int((idx / fps) * 1000)
            yield idx, ts_ms, frame
            idx += 1
    finally:
        cap.release()


def _detect_reps(per_frame: list[FrameMetrics]) -> list[RepMetrics]:
    """Detect squat reps via a tiny state machine on knee angle."""
    reps: list[RepMetrics] = []
    state = "up"
    rep_min_angle = 180.0
    rep_max_collapse = 0.0
    rep_first_idx: int | None = None

    for fm in per_frame:
        if fm.knee_angle is None:
            continue
        if state == "up":
            if fm.knee_angle <= REP_DOWN_ANGLE:
                state = "down"
                rep_first_idx = fm.frame_idx
                rep_min_angle = fm.knee_angle
                rep_max_collapse = fm.knee_collapse or 0.0
        else:
            rep_min_angle = min(rep_min_angle, fm.knee_angle)
            if fm.knee_collapse is not None:
                rep_max_collapse = max(rep_max_collapse, fm.knee_collapse)
            if fm.knee_angle >= REP_UP_ANGLE:
                if rep_first_idx is not None and fm.frame_idx - rep_first_idx >= MIN_REP_FRAMES:
                    reps.append(RepMetrics(
                        start_frame=rep_first_idx,
                        end_frame=fm.frame_idx,
                        min_knee_angle=round(rep_min_angle, 1),
                        max_knee_collapse=round(rep_max_collapse, 4),
                        deep_enough=rep_min_angle <= DEPTH_ANGLE_OK,
                        knee_collapsed=rep_max_collapse >= KNEE_COLLAPSE_THRESHOLD,
                    ))
                state = "up"
                rep_first_idx = None
                rep_min_angle = 180.0
                rep_max_collapse = 0.0
    return reps


def _analyze_generic_video(video_path: str, model_path: str, exercise: str) -> AnalysisReport:
    """Video analysis for non-squat exercises using the exercise-specific live analyzer."""
    from .exercises import EXERCISE_MAP

    options = vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
        running_mode=vision.RunningMode.VIDEO,
    )

    analyzer_cls = EXERCISE_MAP.get(exercise, EXERCISE_MAP["squat"])
    analyzer = analyzer_cls()

    frames_total = 0
    frames_with_pose = 0
    frame_payloads: list[dict] = []

    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        for idx, ts_ms, frame in _iter_frames(video_path):
            frames_total += 1
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
            )
            try:
                result = landmarker.detect_for_video(mp_image, ts_ms)
            except Exception:
                continue

            if not result.pose_landmarks:
                continue

            lm = result.pose_landmarks[0]
            try:
                payload = analyzer.process(lm, idx)
            except (IndexError, AttributeError):
                continue

            frames_with_pose += 1
            frame_payloads.append(payload)

    reps_total: int = analyzer._r.completed  # type: ignore[attr-defined]

    # Aggregate primary angle and fault values from per-frame payloads
    primary_angles: list[float] = []
    fault_values: list[float] = []
    bad_frames = 0
    for p in frame_payloads:
        for key in ("knee_angle", "elbow_angle", "hip_angle"):
            if key in p:
                primary_angles.append(p[key])
                break
        for key in ("knee_collapse", "body_sag", "overtoe", "forward_lean"):
            if key in p:
                fault_values.append(p[key])
                break
        if p.get("label") == "BAD":
            bad_frames += 1

    avg_primary = round(float(np.mean(primary_angles)), 1) if primary_angles else None
    avg_fault = round(float(np.mean(fault_values)), 4) if fault_values else None
    bad_ratio = bad_frames / frames_with_pose if frames_with_pose > 0 else 0.0

    from .exercises import EXERCISE_VERDICTS
    ex_gen, fault_tip, ok_tip = EXERCISE_VERDICTS.get(exercise, ("повторений", "", ""))

    if reps_total == 0:
        verdict = f"Не удалось распознать ни одного {ex_gen}. Сними видео сбоку так, чтобы было хорошо видно движение."
    else:
        parts = [f"Засчитано {ex_gen}: {reps_total}."]
        if bad_ratio >= 0.3 and fault_tip:
            parts.append(fault_tip + ".")
        elif ok_tip:
            parts.append(ok_tip.capitalize() + ".")
        verdict = " ".join(parts)

    return AnalysisReport(
        frames_total=frames_total,
        frames_with_pose=frames_with_pose,
        exercise=exercise,
        verdict=verdict,
        extra_metrics={
            "reps_total": reps_total,
            "avg_primary_angle": avg_primary,
            "avg_fault_value": avg_fault,
            "bad_frame_ratio": round(bad_ratio, 2),
        },
    )


def analyze_video(video_path: str, model_path: str, exercise: str = "squat") -> AnalysisReport:
    """Run the full pipeline on a saved video file."""
    if exercise != "squat":
        return _analyze_generic_video(video_path, model_path, exercise)

    # ── squat-specific path ──────────────────────────────────────────────────
    options = vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
        running_mode=vision.RunningMode.VIDEO,
    )

    per_frame: list[FrameMetrics] = []

    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        for idx, ts_ms, frame in _iter_frames(video_path):
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
            )
            try:
                result = landmarker.detect_for_video(mp_image, ts_ms)
            except Exception:
                per_frame.append(FrameMetrics(idx, ts_ms, detected=False))
                continue

            if not result.pose_landmarks:
                per_frame.append(FrameMetrics(idx, ts_ms, detected=False))
                continue

            lm = result.pose_landmarks[0]
            try:
                left_vis = (lm[LEFT_HIP].visibility + lm[LEFT_KNEE].visibility + lm[LEFT_ANKLE].visibility)
                right_vis = (lm[RIGHT_HIP].visibility + lm[RIGHT_KNEE].visibility + lm[RIGHT_ANKLE].visibility)
                if right_vis > left_vis:
                    h_i, k_i, a_i = RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE
                else:
                    h_i, k_i, a_i = LEFT_HIP, LEFT_KNEE, LEFT_ANKLE
                hip = (lm[h_i].x, lm[h_i].y)
                knee = (lm[k_i].x, lm[k_i].y)
                ankle = (lm[a_i].x, lm[a_i].y)
                shoulder = (lm[LEFT_SHOULDER].x, lm[LEFT_SHOULDER].y)
            except (IndexError, AttributeError):
                per_frame.append(FrameMetrics(idx, ts_ms, detected=False))
                continue

            knee_ang = _angle(hip, knee, ankle)
            hip_ang = _angle(shoulder, hip, knee)
            collapse = _knee_collapse(hip, knee, ankle)

            per_frame.append(FrameMetrics(
                frame_idx=idx,
                timestamp_ms=ts_ms,
                detected=True,
                knee_angle=round(knee_ang, 1),
                hip_angle=round(hip_ang, 1),
                knee_collapse=round(collapse, 4),
            ))

    reps = _detect_reps(per_frame)
    detected = [f for f in per_frame if f.detected]

    avg_min_knee = (
        round(float(np.mean([r.min_knee_angle for r in reps])), 1) if reps else None
    )
    avg_collapse = (
        round(float(np.mean([f.knee_collapse for f in detected if f.knee_collapse is not None])), 4)
        if detected else None
    )
    collapse_ratio = (
        sum(1 for r in reps if r.knee_collapsed) / len(reps) if reps else 0.0
    )
    depth_ratio = (
        sum(1 for r in reps if r.deep_enough) / len(reps) if reps else 0.0
    )

    if not reps:
        verdict = "Не удалось распознать ни одного полного приседа. Сними видео сбоку, чтобы было видно колени и таз."
    else:
        parts = [f"Засчитано приседов: {len(reps)}."]
        if depth_ratio < 0.5:
            parts.append("Глубина недостаточная — старайся опускаться так, чтобы бёдра уходили ниже параллели.")
        else:
            parts.append("Глубина в норме.")
        if collapse_ratio >= 0.3:
            parts.append("Колени заваливаются внутрь — толкай их в стороны на всём движении.")
        else:
            parts.append("Колени держишь стабильно.")
        verdict = " ".join(parts)

    return AnalysisReport(
        frames_total=len(per_frame),
        frames_with_pose=len(detected),
        exercise="squat",
        reps=reps,
        avg_min_knee_angle=avg_min_knee,
        avg_knee_collapse=avg_collapse,
        knee_collapse_ratio=round(collapse_ratio, 2),
        depth_ratio=round(depth_ratio, 2),
        verdict=verdict,
    )

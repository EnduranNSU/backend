"""Exercise-specific live analyzers for WebSocket coaching."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .analyzer import (
    _angle,
    LEFT_SHOULDER, RIGHT_SHOULDER,
    LEFT_HIP, RIGHT_HIP,
    LEFT_KNEE, RIGHT_KNEE,
    LEFT_ANKLE, RIGHT_ANKLE,
)

LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_WRIST = 15
RIGHT_WRIST = 16


def _xy(lm, idx):
    return (lm[idx].x, lm[idx].y)


def _vis(lm, *indices):
    return sum(lm[i].visibility for i in indices)


@dataclass
class _RepState:
    state: str = "up"
    start_frame: int | None = None
    min_angle: float = 180.0
    max_fault: float = 0.0
    completed: int = 0
    last_ok: bool | None = None

    def reset(self):
        self.state = "up"
        self.start_frame = None
        self.min_angle = 180.0
        self.max_fault = 0.0
        self.completed = 0
        self.last_ok = None


# ── Squat ─────────────────────────────────────────────────────────────────────

class SquatAnalyzer:
    DOWN_ANGLE = 110.0
    UP_ANGLE = 160.0
    DEPTH_OK = 100.0
    COLLAPSE_THRESHOLD = 0.04
    MIN_REP_FRAMES = 5

    def __init__(self):
        self._r = _RepState()

    def reset(self):
        self._r = _RepState()

    def process(self, lm, frame_idx: int) -> dict:
        left_vis = _vis(lm, LEFT_HIP, LEFT_KNEE, LEFT_ANKLE)
        right_vis = _vis(lm, RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE)
        h_i, k_i, a_i = (RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE) if right_vis > left_vis else (LEFT_HIP, LEFT_KNEE, LEFT_ANKLE)

        hip = _xy(lm, h_i)
        knee = _xy(lm, k_i)
        ankle = _xy(lm, a_i)
        knee_ang = _angle(hip, knee, ankle)
        collapse = float(abs(knee[0] - (hip[0] + ankle[0]) / 2.0))

        r = self._r
        if r.state == "up":
            if knee_ang <= self.DOWN_ANGLE:
                r.state, r.start_frame, r.min_angle, r.max_fault = "down", frame_idx, knee_ang, collapse
        else:
            r.min_angle = min(r.min_angle, knee_ang)
            r.max_fault = max(r.max_fault, collapse)
            if knee_ang >= self.UP_ANGLE:
                if r.start_frame is not None and frame_idx - r.start_frame >= self.MIN_REP_FRAMES:
                    r.completed += 1
                    r.last_ok = r.min_angle <= self.DEPTH_OK and r.max_fault < self.COLLAPSE_THRESHOLD
                r.state, r.start_frame, r.min_angle, r.max_fault = "up", None, 180.0, 0.0

        if r.state == "down":
            if collapse >= self.COLLAPSE_THRESHOLD:
                label, hint = "BAD", "колени заваливаются внутрь"
            elif knee_ang <= self.DEPTH_OK:
                label, hint = "OK", "глубина норм"
            else:
                label, hint = "OK", "опускаемся"
        else:
            label, hint = "IDLE", "встал"

        return {"detected": True, "knee_angle": round(knee_ang, 1), "knee_collapse": round(collapse, 4),
                "state": r.state, "label": label, "hint": hint,
                "reps_total": r.completed, "last_rep_ok": r.last_ok}


# ── Lunge ─────────────────────────────────────────────────────────────────────

class LungeAnalyzer:
    DOWN_ANGLE = 100.0
    UP_ANGLE = 160.0
    OVERTOE_THRESHOLD = 0.05
    MIN_REP_FRAMES = 4

    def __init__(self):
        self._r = _RepState()

    def reset(self):
        self._r = _RepState()

    def process(self, lm, frame_idx: int) -> dict:
        left_ang = _angle(_xy(lm, LEFT_HIP), _xy(lm, LEFT_KNEE), _xy(lm, LEFT_ANKLE))
        right_ang = _angle(_xy(lm, RIGHT_HIP), _xy(lm, RIGHT_KNEE), _xy(lm, RIGHT_ANKLE))
        if left_ang < right_ang:
            h_i, k_i, a_i = LEFT_HIP, LEFT_KNEE, LEFT_ANKLE
            knee_ang = left_ang
        else:
            h_i, k_i, a_i = RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE
            knee_ang = right_ang

        knee = _xy(lm, k_i)
        ankle = _xy(lm, a_i)
        overtoe = float(abs(knee[0] - ankle[0]))

        r = self._r
        if r.state == "up":
            if knee_ang <= self.DOWN_ANGLE:
                r.state, r.start_frame, r.min_angle, r.max_fault = "down", frame_idx, knee_ang, overtoe
        else:
            r.min_angle = min(r.min_angle, knee_ang)
            r.max_fault = max(r.max_fault, overtoe)
            if knee_ang >= self.UP_ANGLE:
                if r.start_frame is not None and frame_idx - r.start_frame >= self.MIN_REP_FRAMES:
                    r.completed += 1
                    r.last_ok = r.min_angle <= self.DOWN_ANGLE and r.max_fault < self.OVERTOE_THRESHOLD
                r.state, r.start_frame, r.min_angle, r.max_fault = "up", None, 180.0, 0.0

        if r.state == "down":
            if overtoe >= self.OVERTOE_THRESHOLD:
                label, hint = "BAD", "колено уходит за носок"
            elif knee_ang <= self.DOWN_ANGLE:
                label, hint = "OK", "хорошая глубина"
            else:
                label, hint = "OK", "опускаемся"
        else:
            label, hint = "IDLE", "встал"

        return {"detected": True, "knee_angle": round(knee_ang, 1), "overtoe": round(overtoe, 4),
                "state": r.state, "label": label, "hint": hint,
                "reps_total": r.completed, "last_rep_ok": r.last_ok}


# ── Deadlift / hip-hinge ──────────────────────────────────────────────────────

class DeadliftAnalyzer:
    HINGE_ANGLE = 120.0
    LOCKOUT_ANGLE = 165.0
    ROUND_THRESHOLD = 0.55
    MIN_REP_FRAMES = 5

    def __init__(self):
        self._r = _RepState()

    def reset(self):
        self._r = _RepState()

    def process(self, lm, frame_idx: int) -> dict:
        left_vis = _vis(lm, LEFT_SHOULDER, LEFT_HIP, LEFT_KNEE)
        right_vis = _vis(lm, RIGHT_SHOULDER, RIGHT_HIP, RIGHT_KNEE)
        if right_vis > left_vis:
            s_i, h_i, k_i = RIGHT_SHOULDER, RIGHT_HIP, RIGHT_KNEE
        else:
            s_i, h_i, k_i = LEFT_SHOULDER, LEFT_HIP, LEFT_KNEE

        shoulder = _xy(lm, s_i)
        hip = _xy(lm, h_i)
        knee = _xy(lm, k_i)
        hip_ang = _angle(shoulder, hip, knee)

        torso_len = float(np.linalg.norm(np.array(shoulder) - np.array(hip))) + 1e-6
        forward_lean = float(abs(shoulder[0] - hip[0])) / torso_len

        r = self._r
        if r.state == "up":
            if hip_ang <= self.HINGE_ANGLE:
                r.state, r.start_frame, r.min_angle, r.max_fault = "down", frame_idx, hip_ang, forward_lean
        else:
            r.min_angle = min(r.min_angle, hip_ang)
            r.max_fault = max(r.max_fault, forward_lean)
            if hip_ang >= self.LOCKOUT_ANGLE:
                if r.start_frame is not None and frame_idx - r.start_frame >= self.MIN_REP_FRAMES:
                    r.completed += 1
                    r.last_ok = r.max_fault < self.ROUND_THRESHOLD
                r.state, r.start_frame, r.min_angle, r.max_fault = "up", None, 180.0, 0.0

        if r.state == "down":
            if forward_lean >= self.ROUND_THRESHOLD:
                label, hint = "BAD", "спина округляется — тяни грудью"
            else:
                label, hint = "OK", "тянем вверх"
        else:
            label, hint = "IDLE", "фиксация"

        return {"detected": True, "hip_angle": round(hip_ang, 1), "forward_lean": round(forward_lean, 4),
                "state": r.state, "label": label, "hint": hint,
                "reps_total": r.completed, "last_rep_ok": r.last_ok}


# ── Pushup / elbow-extension ──────────────────────────────────────────────────

class PushupAnalyzer:
    DOWN_ANGLE = 90.0
    UP_ANGLE = 150.0
    SAG_THRESHOLD = 0.06
    MIN_REP_FRAMES = 4

    def __init__(self):
        self._r = _RepState()

    def reset(self):
        self._r = _RepState()

    def process(self, lm, frame_idx: int) -> dict:
        left_vis = _vis(lm, LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST)
        right_vis = _vis(lm, RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST)
        if right_vis > left_vis:
            s_i, e_i, w_i, h_i, a_i = RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST, RIGHT_HIP, RIGHT_ANKLE
        else:
            s_i, e_i, w_i, h_i, a_i = LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST, LEFT_HIP, LEFT_ANKLE

        shoulder = _xy(lm, s_i)
        elbow = _xy(lm, e_i)
        wrist = _xy(lm, w_i)
        hip = _xy(lm, h_i)
        ankle = _xy(lm, a_i)
        elbow_ang = _angle(shoulder, elbow, wrist)

        t = (hip[0] - shoulder[0]) / (ankle[0] - shoulder[0] + 1e-6)
        expected_hip_y = shoulder[1] + t * (ankle[1] - shoulder[1])
        sag = float(hip[1] - expected_hip_y)

        r = self._r
        if r.state == "up":
            if elbow_ang <= self.DOWN_ANGLE:
                r.state, r.start_frame, r.min_angle, r.max_fault = "down", frame_idx, elbow_ang, sag
        else:
            r.min_angle = min(r.min_angle, elbow_ang)
            r.max_fault = max(r.max_fault, sag)
            if elbow_ang >= self.UP_ANGLE:
                if r.start_frame is not None and frame_idx - r.start_frame >= self.MIN_REP_FRAMES:
                    r.completed += 1
                    r.last_ok = r.min_angle <= self.DOWN_ANGLE and r.max_fault < self.SAG_THRESHOLD
                r.state, r.start_frame, r.min_angle, r.max_fault = "up", None, 180.0, 0.0

        if r.state == "down":
            if sag >= self.SAG_THRESHOLD:
                label, hint = "BAD", "таз провисает — держи тело прямым"
            elif elbow_ang <= self.DOWN_ANGLE:
                label, hint = "OK", "достаточная глубина"
            else:
                label, hint = "OK", "опускаемся"
        else:
            label, hint = "IDLE", "вверху"

        return {"detected": True, "elbow_angle": round(elbow_ang, 1), "body_sag": round(sag, 4),
                "state": r.state, "label": label, "hint": hint,
                "reps_total": r.completed, "last_rep_ok": r.last_ok}


# ── Curl / elbow-flexion (bicep curl, pull-up, row) ───────────────────────────

class CurlAnalyzer:
    """Tracks elbow flexion for curls, pull-ups, and rows."""
    CURL_ANGLE = 80.0    # sufficiently curled
    EXTEND_ANGLE = 150.0  # arm extended
    MIN_REP_FRAMES = 4

    def __init__(self):
        self._r = _RepState()

    def reset(self):
        self._r = _RepState()

    def process(self, lm, frame_idx: int) -> dict:
        left_vis = _vis(lm, LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST)
        right_vis = _vis(lm, RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST)
        if right_vis > left_vis:
            s_i, e_i, w_i = RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST
        else:
            s_i, e_i, w_i = LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST

        elbow_ang = _angle(_xy(lm, s_i), _xy(lm, e_i), _xy(lm, w_i))

        r = self._r
        # "up" = extended (start), "down" = curled (contracted)
        if r.state == "up":
            if elbow_ang <= self.CURL_ANGLE:
                r.state, r.start_frame, r.min_angle = "down", frame_idx, elbow_ang
        else:
            r.min_angle = min(r.min_angle, elbow_ang)
            if elbow_ang >= self.EXTEND_ANGLE:
                if r.start_frame is not None and frame_idx - r.start_frame >= self.MIN_REP_FRAMES:
                    r.completed += 1
                    r.last_ok = r.min_angle <= self.CURL_ANGLE
                r.state, r.start_frame, r.min_angle = "up", None, 180.0

        if r.state == "down":
            label = "OK" if elbow_ang <= self.CURL_ANGLE else "OK"
            hint = "сожми!" if elbow_ang <= self.CURL_ANGLE else "тянем"
        else:
            label, hint = "IDLE", "опускаем"

        return {"detected": True, "elbow_angle": round(elbow_ang, 1),
                "state": r.state, "label": label, "hint": hint,
                "reps_total": r.completed, "last_rep_ok": r.last_ok}


# ── Registry ──────────────────────────────────────────────────────────────────

EXERCISE_MAP: dict[str, type] = {
    # Squats
    "squat":          SquatAnalyzer,
    "barbell_squat":  SquatAnalyzer,
    "sumo_squat":     SquatAnalyzer,
    "leg_press":      SquatAnalyzer,
    # Lunges
    "lunge":          LungeAnalyzer,
    "lunge_back":     LungeAnalyzer,
    "bulgarian_squat": LungeAnalyzer,
    # Hip-hinge / deadlift
    "deadlift":           DeadliftAnalyzer,
    "romanian_deadlift":  DeadliftAnalyzer,
    "barbell_row":        DeadliftAnalyzer,
    "glute_bridge":       DeadliftAnalyzer,
    "hyperextension":     DeadliftAnalyzer,
    # Push / elbow extension
    "pushup":           PushupAnalyzer,
    "bench_press":      PushupAnalyzer,
    "dumbbell_press":   PushupAnalyzer,
    "incline_press":    PushupAnalyzer,
    "shoulder_press":   PushupAnalyzer,
    "dips":             PushupAnalyzer,
    "tricep_extension": PushupAnalyzer,
    # Curl / pull / elbow flexion
    "pullup":       CurlAnalyzer,
    "lat_pulldown": CurlAnalyzer,
    "cable_row":    CurlAnalyzer,
    "dumbbell_row": CurlAnalyzer,
    "bicep_curl":   CurlAnalyzer,
    "hammer_curl":  CurlAnalyzer,
    "upright_row":  CurlAnalyzer,
}

EXERCISE_LABELS: dict[str, str] = {
    "squat":             "Приседания",
    "barbell_squat":     "Приседания со штангой",
    "sumo_squat":        "Сумо-присед",
    "leg_press":         "Жим ногами",
    "lunge":             "Выпады",
    "lunge_back":        "Обратные выпады",
    "bulgarian_squat":   "Болгарский присед",
    "deadlift":          "Становая тяга",
    "romanian_deadlift": "Румынская тяга",
    "barbell_row":       "Тяга штанги в наклоне",
    "glute_bridge":      "Ягодичный мост",
    "hyperextension":    "Гиперэкстензия",
    "pushup":            "Отжимания",
    "bench_press":       "Жим лёжа",
    "dumbbell_press":    "Жим гантелей лёжа",
    "incline_press":     "Жим на наклонной скамье",
    "shoulder_press":    "Жим над головой",
    "dips":              "Отжимания на брусьях",
    "tricep_extension":  "Разгибание трицепса",
    "pullup":            "Подтягивания",
    "lat_pulldown":      "Тяга верхнего блока",
    "cable_row":         "Горизонтальная тяга в блоке",
    "dumbbell_row":      "Тяга гантели",
    "bicep_curl":        "Подъём штанги на бицепс",
    "hammer_curl":       "Молотковые сгибания",
    "upright_row":       "Тяга штанги к подбородку",
}

# Verdict texts: (genitive_plural, fault_tip, ok_tip)
EXERCISE_VERDICTS: dict[str, tuple[str, str, str]] = {
    "squat":             ("приседаний",          "глубина недостаточная — опускайся ниже",         "глубина в норме"),
    "barbell_squat":     ("приседаний",          "глубина недостаточная — опускайся ниже",         "глубина в норме"),
    "sumo_squat":        ("сумо-приседов",       "глубина недостаточная",                          "глубина в норме"),
    "leg_press":         ("жимов ногами",        "недостаточная амплитуда",                        "амплитуда в норме"),
    "lunge":             ("выпадов",             "колено уходит за носок — укороти шаг",           "техника выпадов ок"),
    "lunge_back":        ("обратных выпадов",    "колено уходит за носок",                         "техника ок"),
    "bulgarian_squat":   ("болгарских приседов", "колено уходит за носок",                         "техника ок"),
    "deadlift":          ("становых тяг",        "спина округляется — акцентируй на нейтральной спине", "спина держится хорошо"),
    "romanian_deadlift": ("румынских тяг",       "спина округляется",                              "спина держится хорошо"),
    "barbell_row":       ("тяг в наклоне",       "спина округляется — держи корпус стабильно",     "корпус стабилен"),
    "glute_bridge":      ("ягодичных мостов",    "неполная амплитуда",                             "амплитуда в норме"),
    "hyperextension":    ("гиперэкстензий",      "спина округляется",                              "спина держится хорошо"),
    "pushup":            ("отжиманий",           "таз провисает — держи тело прямым",              "таз стабилен"),
    "bench_press":       ("жимов лёжа",          "недостаточная амплитуда",                        "амплитуда в норме"),
    "dumbbell_press":    ("жимов гантелей",      "недостаточная амплитуда",                        "амплитуда в норме"),
    "incline_press":     ("жимов на наклонной",  "недостаточная амплитуда",                        "амплитуда в норме"),
    "shoulder_press":    ("жимов над головой",   "неполная амплитуда",                             "амплитуда в норме"),
    "dips":              ("отжиманий на брусьях","недостаточная глубина",                          "глубина в норме"),
    "tricep_extension":  ("разгибаний трицепса", "неполная амплитуда",                             "амплитуда в норме"),
    "pullup":            ("подтягиваний",        "неполная амплитуда — тяни до подбородка над перекладиной", "амплитуда в норме"),
    "lat_pulldown":      ("тяг верхнего блока",  "неполная амплитуда",                             "амплитуда в норме"),
    "cable_row":         ("горизонтальных тяг",  "неполная амплитуда",                             "амплитуда в норме"),
    "dumbbell_row":      ("тяг гантели",         "неполная амплитуда",                             "амплитуда в норме"),
    "bicep_curl":        ("подъёмов на бицепс",  "неполная амплитуда — полностью разгибай руку",   "амплитуда в норме"),
    "hammer_curl":       ("молотковых сгибаний", "неполная амплитуда",                             "амплитуда в норме"),
    "upright_row":       ("тяг к подбородку",    "неполная амплитуда",                             "амплитуда в норме"),
}

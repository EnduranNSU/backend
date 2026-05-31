import os
import tempfile

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from cv_service.analyzer import analyze_video
from cv_service.exercises import EXERCISE_MAP


router = APIRouter(prefix="/cv", tags=["cv"])

MODEL_PATH = os.environ.get(
    "POSE_MODEL_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                 "pose_landmarker_full.task"),
)

_ALLOWED_SUFFIXES = {".mp4", ".mov", ".webm", ".avi", ".mkv", ".gif"}
_SUPPORTED_EXERCISES = set(EXERCISE_MAP.keys())


@router.post("/analyze")
async def analyze(
    video: UploadFile = File(...),
    exercise: str = Query(default="squat", description="Exercise type: squat, pushup, lunge, deadlift"),
):
    if exercise not in _SUPPORTED_EXERCISES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported exercise: {exercise}. Supported: {sorted(_SUPPORTED_EXERCISES)}",
        )

    suffix = os.path.splitext(video.filename or "")[1].lower() or ".mp4"
    if suffix not in _ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported video format: {suffix}",
        )

    if not os.path.exists(MODEL_PATH):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pose model not found at {MODEL_PATH}",
        )

    data = await video.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty upload")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        report = analyze_video(tmp_path, MODEL_PATH, exercise=exercise)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    return report.to_dict()


@router.get("/exercises")
async def list_exercises():
    from cv_service.exercises import EXERCISE_LABELS
    return sorted(
        [{"slug": slug, "label": label} for slug, label in EXERCISE_LABELS.items()],
        key=lambda x: x["label"],
    )


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "model_present": os.path.exists(MODEL_PATH),
        "supported_exercises": sorted(_SUPPORTED_EXERCISES),
    }

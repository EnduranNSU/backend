import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from cv_service.analyzer import analyze_video


router = APIRouter(prefix="/cv", tags=["cv"])

MODEL_PATH = os.environ.get(
    "POSE_MODEL_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                 "pose_landmarker_full.task"),
)

_ALLOWED_SUFFIXES = {".mp4", ".mov", ".webm", ".avi", ".mkv", ".gif"}


@router.post("/analyze")
async def analyze(video: UploadFile = File(...)):
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
        report = analyze_video(tmp_path, MODEL_PATH)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    return report.to_dict()


@router.get("/health")
async def health():
    return {"status": "ok", "model_present": os.path.exists(MODEL_PATH)}

import json
from pydantic import BaseModel

class Exercise(BaseModel):
    id: int
    title: str
    description: str
    video_href: str
    tags: list[str]


exercises = []

from pathlib import Path
here = Path(__file__).resolve().parent
path = here / "exercises.json"
        

with open(path, "r", encoding="utf-8") as f:
    exercises = [Exercise.model_validate_json(ex) for ex in json.load(f)]


def get_exercises() -> list[Exercise]:
    return exercises

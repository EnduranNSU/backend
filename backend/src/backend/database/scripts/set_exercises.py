import json
from pydantic import BaseModel

from backend.database.sqlalchemy.session import create_session
from backend.database.sqlalchemy.crud.exercise import create_exercise
from backend.models.exercise import ExerciseCreate

from backend.minio.S3Client import S3Client
from backend.config import get_config

config = get_config()
endpoint = "{}:{}".format(config.s3.host, config.s3.port)
S3Client(endpoint, config.s3.user, config.s3.password)  

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



async def main():
    session = await create_session()
    for exercise in exercises:
        exercise_create = ExerciseCreate(
            title=exercise.title,
            description=exercise.description,
            hrefs=[exercise.video_href],
            tags=exercise.tags,
        )

        await create_exercise(session, exercise_create)
    await session.close()

import asyncio
import selectors


if __name__ == "__main__":
    loop = asyncio.SelectorEventLoop(selector=selectors.SelectSelector())
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


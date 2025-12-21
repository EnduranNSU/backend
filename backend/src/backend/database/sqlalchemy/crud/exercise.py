from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.minio.S3Client import S3Client
from backend.models.exercise import ExerciseCreate, ExerciseRead, ExerciseReadVerbose
from backend.database.sqlalchemy.orm_models import Exercise

password_hash = PasswordHash.recommended()

async def create_exercise(session: AsyncSession, exercise_in: ExerciseCreate) -> ExerciseRead | None:
    s3_client = S3Client.get_instance()
    exercise = Exercise(title=exercise_in.title, hrefs=exercise_in.hrefs, tags=exercise_in.tags)
    session.add(exercise)
    await session.commit()
    await session.refresh(exercise)


    stmt = select(Exercise).where(Exercise.title == exercise_in.title)
    result = await session.execute(stmt)
    exercise = result.scalar_one_or_none()

    if exercise is None:
        return None

    s3_client.upload_exercise_description(exercise.id, exercise_in.description)
    
    exercise_read = ExerciseRead(id=exercise.id, title=exercise.title, hrefs=exercise.hrefs, tags=exercise.tags)

    return exercise_read

async def get_exercises(session:AsyncSession) -> list[ExerciseRead]:
    stmt = select(Exercise)
    result = await session.execute(stmt)
    exercises = result.scalars().all()

    result = []
    for exercise in exercises:
        exercise_read = ExerciseRead(id=exercise.id, title=exercise.title, hrefs=exercise.hrefs, tags=exercise.tags)
        result.append(exercise_read)

    return result

async def get_exercise_by_id(session: AsyncSession, exercise_id: int) -> ExerciseReadVerbose | None:
    exercise = await session.get(Exercise, exercise_id)

    if exercise is None:
        return None

    s3_client = S3Client.get_instance()
    description = s3_client.download_exercise_description(exercise_id)

    exercise_read = ExerciseReadVerbose(
        id=exercise.id, 
        description=description, 
        title=exercise.title, 
        hrefs=exercise.hrefs, 
        tags=exercise.tags)

    return exercise_read

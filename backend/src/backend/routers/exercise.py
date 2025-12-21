from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.exercise import ExerciseRead, ExerciseReadVerbose
from backend.database.sqlalchemy.crud.exercise import get_exercises, get_exercise_by_id
from backend.database.sqlalchemy.session import get_session

router = APIRouter(prefix="/exercise", tags=["exercise"])

@router.get("/")
async def get_exercises_route(session: AsyncSession = Depends(get_session)) -> list[ExerciseRead]:
    return await get_exercises(session)

@router.get("/{id}")
async def get_exercise_route(id: int, session: AsyncSession = Depends(get_session)) -> ExerciseReadVerbose:
    res = await get_exercise_by_id(session, id)

    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    
    return res

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.training import (
    PlannedTrainingRead, PlannedTrainingCreateUser, PlannedTrainningCreate,
    UserPerformedTrainingRead, UserPerformedTrainingCreateUser, UserPerformedTrainingCreate
)
from backend.database.sqlalchemy.crud.training import (
    get_planned_trainings, get_planned_training, create_planned_training, delete_planned_training, update_planned_training,
    get_user_performed_trainings, get_user_performed_training, create_user_performed_training, 
    delete_user_performed_training, update_user_performed_training,
)
from backend.database.sqlalchemy.session import get_session


from .access import get_current_user

from backend.models.user import UserRead

router = APIRouter(prefix="/training", tags=["training"])

@router.get("/planned")
async def get_planned_trainings_route(
                    user: UserRead = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)) -> list[PlannedTrainingRead]:
    trainings = await get_planned_trainings(session, user.id)

    return trainings

@router.get("/planned/{id}")
async def get_planned_training_route(id: int, 
                                     user: UserRead = Depends(get_current_user), 
                                     session: AsyncSession = Depends(get_session)) -> PlannedTrainingRead:
    res = await get_planned_training(session, id)

    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planned training not found")

    return res

@router.post("/planned/create")
async def create_planned_training_route(
                    training_in: PlannedTrainningCreate,
                    user: UserRead = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)) -> PlannedTrainingRead:
    
    training_user = PlannedTrainingCreateUser(user_id=user.id, **training_in.model_dump())

    res = await create_planned_training(session, training_user)

    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="It should not happen. Ask developer what is going on")

    return res

@router.post("/planned/delete/{id}")
async def delete_planned_training_route(id: int, 
                                        user: UserRead = Depends(get_current_user), 
                                        session: AsyncSession = Depends(get_session)) -> None:
    await delete_planned_training(session, id)

@router.post("/planned/update/{id}")
async def update_planned_training_route(id: int, 
                                        training_in: PlannedTrainningCreate,
                                        user: UserRead = Depends(get_current_user), 
                                        session: AsyncSession = Depends(get_session)) -> PlannedTrainingRead:
    training_user = PlannedTrainingCreateUser(user_id=user.id, **training_in.model_dump())

    res = await update_planned_training(session, id, training_user)

    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="It should not happen. Ask developer what is going on")

    return res




@router.get("/user_performed")
async def get_user_performed_route(
                    user: UserRead = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)) -> list[UserPerformedTrainingRead]:
    trainings = await get_user_performed_trainings(session, user.id)

    return trainings

@router.get("/user_performed/{id}")
async def get_user_performed_training_route(id: int, 
                                     user: UserRead = Depends(get_current_user), 
                                     session: AsyncSession = Depends(get_session)) -> UserPerformedTrainingRead:
    res = await get_user_performed_training(session, id)

    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planned training not found")

    return res

@router.post("/user_performed/create")
async def create_user_performed_training_route(
                    training_in: PlannedTrainningCreate,
                    user: UserRead = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)) -> UserPerformedTrainingRead:
    
    training_user = UserPerformedTrainingCreateUser(user_id=user.id, **training_in.model_dump())

    res = await create_user_performed_training(session, training_user)

    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="It should not happen. Ask developer what is going on")

    return res

@router.post("/user_performed/delete/{id}")
async def delete_user_performed_training_route(id: int, 
                                        user: UserRead = Depends(get_current_user), 
                                        session: AsyncSession = Depends(get_session)) -> None:
    await delete_user_performed_training(session, id)

@router.post("/user_performed/update/{id}")
async def update_user_performed_training_route(id: int, 
                                        training_in: UserPerformedTrainingCreate,
                                        user: UserRead = Depends(get_current_user), 
                                        session: AsyncSession = Depends(get_session)) -> UserPerformedTrainingRead:
    training_user = UserPerformedTrainingCreateUser(user_id=user.id, **training_in.model_dump())

    res = await update_user_performed_training(session, id, training_user)

    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="It should not happen. Ask developer what is going on")

    return res

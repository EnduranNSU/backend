from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload


from backend.models.training import (
    PlannedTrainingCreateUser, PlannedTrainingRead,
    UserPerformedTrainingRead, UserPerformedTrainingCreateUser
)
from backend.database.sqlalchemy.orm_models import (Set, 
                                                    PerfomableExercise,
                                                    Training,
                                                    UserPerformedTraining, 
                                                    PlannedTrainnings)

password_hash = PasswordHash.recommended()

async def get_planned_trainings(
    session: AsyncSession,
    user_id: int
) -> list[PlannedTrainingRead]:

    stmt = (
        select(PlannedTrainnings)
        .where(PlannedTrainnings.user_id == user_id)
        .options(
            selectinload(PlannedTrainnings.training)
            .selectinload(Training.perfomable_exercises)
            .selectinload(PerfomableExercise.sets),

            selectinload(PlannedTrainnings.training)
            .selectinload(Training.perfomable_exercises)
            .selectinload(PerfomableExercise.exercise),
        )
    )

    result = await session.execute(stmt)
    planned_trainings = result.scalars().all()

    return [
        PlannedTrainingRead.model_validate(pt, from_attributes=True)
        for pt in planned_trainings
    ]

async def get_planned_training(
    session: AsyncSession,
    training_id: int
) -> PlannedTrainingRead | None:

    stmt = (
        select(PlannedTrainnings)
        .where(PlannedTrainnings.id == training_id)
        .options(
            selectinload(PlannedTrainnings.training)
            .selectinload(Training.perfomable_exercises)
            .selectinload(PerfomableExercise.sets),

            selectinload(PlannedTrainnings.training)
            .selectinload(Training.perfomable_exercises)
            .selectinload(PerfomableExercise.exercise),
        )
    )

    result = await session.execute(stmt)
    pt = result.scalar_one_or_none()

    if pt is None:
        return None

    return PlannedTrainingRead.model_validate(pt, from_attributes=True)



async def create_planned_training(
    session: AsyncSession,
    data: PlannedTrainingCreateUser
) -> PlannedTrainingRead | None:

    training = Training(title=data.training.title)

    for pe in data.training.perfomable_exercises:
        perf = PerfomableExercise(
            exercise_id=pe.exercise_id
        )

        for s in pe.sets:
            perf.sets.append(
                Set(
                    weight=s.weight,
                    repetitions=s.repetitions,
                    rest_duration=s.rest_duration,
                ))
        training.perfomable_exercises.append(perf)

    session.add(training)
    await session.flush()  

    planned_training = PlannedTrainnings(
        user_id=data.user_id,
        training_id=training.id,
        weekdays=data.weekdays,
    )

    session.add(planned_training)
    await session.commit()
    await session.refresh(planned_training)

    return await get_planned_training(session, planned_training.id)


async def delete_planned_training(session: AsyncSession, training_id: int) -> None:
    stmt = delete(PlannedTrainnings).where(PlannedTrainnings.id == training_id)
    await session.execute(stmt)
    await session.commit()

async def update_planned_training(session: AsyncSession, training_id: int, data: PlannedTrainingCreateUser) -> PlannedTrainingRead | None:
    stmt = delete(PlannedTrainnings).where(PlannedTrainnings.id == training_id)
    await session.execute(stmt)

    return await create_planned_training(session, data)









async def get_user_performed_trainings(
    session: AsyncSession,
    user_id: int
) -> list[UserPerformedTrainingRead]:

    stmt = (
        select(UserPerformedTraining)
        .where(UserPerformedTraining.user_id == user_id)
        .options(
            selectinload(UserPerformedTraining.training)
            .selectinload(Training.perfomable_exercises)
            .selectinload(PerfomableExercise.sets),

            selectinload(PlannedTrainnings.training)
            .selectinload(Training.perfomable_exercises)
            .selectinload(PerfomableExercise.exercise),
        )
    )

    result = await session.execute(stmt)
    planned_trainings = result.scalars().all()

    return [
        UserPerformedTrainingRead.model_validate(pt, from_attributes=True)
        for pt in planned_trainings
    ]

async def get_user_performed_training(
    session: AsyncSession,
    training_id: int
) -> UserPerformedTrainingRead | None:

    stmt = (
        select(UserPerformedTraining)
        .where(UserPerformedTraining.id == training_id)
        .options(
            selectinload(UserPerformedTraining.training)
            .selectinload(Training.perfomable_exercises)
            .selectinload(PerfomableExercise.sets),

            selectinload(UserPerformedTraining.training)
            .selectinload(Training.perfomable_exercises)
            .selectinload(PerfomableExercise.exercise),
        )
    )

    result = await session.execute(stmt)
    pt = result.scalar_one_or_none()

    if pt is None:
        return None

    return UserPerformedTrainingRead.model_validate(pt, from_attributes=True)



async def create_user_performed_training(
    session: AsyncSession,
    data: UserPerformedTrainingCreateUser
) -> UserPerformedTrainingRead | None:

    training = Training(title=data.training.title)

    for pe in data.training.perfomable_exercises:
        perf = PerfomableExercise(
            exercise_id=pe.exercise_id
        )

        for s in pe.sets:
            perf.sets.append(
                Set(
                    weight=s.weight,
                    repetitions=s.repetitions,
                    rest_duration=s.rest_duration,
                ))
        training.perfomable_exercises.append(perf)

    session.add(training)
    await session.flush()  

    planned_training = UserPerformedTraining(
        user_id=data.user_id,
        training_id=training.id,
        date=data.date
    )

    session.add(planned_training)
    await session.commit()
    await session.refresh(planned_training)

    return await get_user_performed_training(session, planned_training.id)


async def delete_user_performed_training(session: AsyncSession, training_id: int) -> None:
    stmt = delete(UserPerformedTraining).where(UserPerformedTraining.id == training_id)
    await session.execute(stmt)

async def update_user_performed_training(session: AsyncSession, training_id: int, data: UserPerformedTrainingCreateUser) -> UserPerformedTrainingRead | None:
    stmt = delete(UserPerformedTraining).where(UserPerformedTraining.id == training_id)
    await session.execute(stmt)

    return await create_user_performed_training(session, data)

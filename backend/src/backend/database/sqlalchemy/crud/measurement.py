from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.models.measurement import MeasurementCreate, MeasurementRead
from backend.database.sqlalchemy.orm_models import Measurement

password_hash = PasswordHash.recommended()

async def create_measurement(session: AsyncSession, measurement_in: MeasurementCreate) -> MeasurementRead | None:
    measurement = Measurement(user_id=measurement_in.user_id, 
                           type=measurement_in.type, 
                           value=measurement_in.value, 
                           date=measurement_in.date)
    session.add(measurement)
    await session.commit()
    await session.refresh(measurement)


    stmt = select(Measurement).where(Measurement.type == measurement_in.type)
    result = await session.execute(stmt)
    measurement = result.scalar_one_or_none()

    if measurement is None:
        return None
    
    exercise_read = MeasurementRead(id=measurement.id, 
                                    type=measurement.type, 
                                    value=measurement.value, 
                                    date=measurement.date)

    return exercise_read

async def get_measurements(session:AsyncSession, user_id: int) -> list[MeasurementRead]:
    stmt = select(Measurement).where(Measurement.user_id == user_id)
    result = await session.execute(stmt)
    exercises = result.scalars().all()

    result = []
    for exercise in exercises:
        exercise_read = MeasurementRead(id=exercise.id, 
                                        type=exercise.type, 
                                        value=exercise.value, 
                                        date=exercise.date)
        result.append(exercise_read)

    return result

async def update_measurements(session: AsyncSession, user_id: int, measurements_in: list[MeasurementCreate]) -> list[MeasurementRead] | None:    
    stmt = delete(Measurement).where(Measurement.user_id == user_id)
    result = await session.execute(stmt)
    
    for measurement_in in measurements_in:
        await create_measurement(session, measurement_in)

    return await get_measurements(session, user_id)

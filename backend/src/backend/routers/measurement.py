from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.measurement import MeasurementRead, MeasurementCreate, MeasurementBase
from backend.database.sqlalchemy.crud.measurement import get_measurements, create_measurement, update_measurements
from backend.database.sqlalchemy.session import get_session


from .access import get_current_user

from backend.models.user import UserRead

router = APIRouter(prefix="/measurements", tags=["measurements"])

@router.get("/")
async def get_measurements_route(
                    user: UserRead = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)) -> list[MeasurementRead]:
    measurements = await get_measurements(session, user.id)

    return measurements

@router.post("/create")
async def create_measurement_route(
                    measurement_in: MeasurementBase,
                    user: UserRead = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)) -> MeasurementRead:
    
    res = await create_measurement(session, 
                                   MeasurementCreate(user_id=user.id, 
                                                        type=measurement_in.type, 
                                                        value=measurement_in.value, 
                                                        date=measurement_in.date))

    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="It should not happen. Ask developer what is going on")

    return res


@router.post("/update")
async def update_measurements_route(
                    measurements_in: list[MeasurementBase],
                    user: UserRead = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)) -> list[MeasurementRead]:
    
    measurements_create_in = [MeasurementCreate(user_id=user.id, 
                                         type=measurement_in.type, 
                                         value=measurement_in.value, 
                                         date=measurement_in.date) for measurement_in in measurements_in]

    res = await update_measurements(session, user.id, measurements_create_in)

    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="It should not happen. Ask developer what is going on")

    return res



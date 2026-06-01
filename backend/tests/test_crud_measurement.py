import pytest
from backend.database.sqlalchemy.crud.measurement import (
    create_measurement, get_measurements, update_measurements
)
from backend.models.measurement import MeasurementCreate

pytestmark = pytest.mark.asyncio


async def test_create_measurement(db_session):
    m = await create_measurement(db_session, MeasurementCreate(
        user_id=1, type="weight", value=75, date="2026-01-01"
    ))
    assert m is not None
    assert m.type == "weight"
    assert m.value == 75
    assert m.date == "2026-01-01"
    assert m.id is not None


async def test_get_measurements_empty(db_session):
    result = await get_measurements(db_session, user_id=999)
    assert result == []


async def test_get_measurements_returns_user_data(db_session):
    await create_measurement(db_session, MeasurementCreate(user_id=2, type="weight", value=80, date="2026-01-01"))
    await create_measurement(db_session, MeasurementCreate(user_id=2, type="height", value=180, date="2026-01-01"))
    await create_measurement(db_session, MeasurementCreate(user_id=3, type="weight", value=60, date="2026-01-01"))

    result = await get_measurements(db_session, user_id=2)
    assert len(result) == 2
    types = {m.type for m in result}
    assert types == {"weight", "height"}


async def test_update_measurements_replaces_old(db_session):
    await create_measurement(db_session, MeasurementCreate(user_id=4, type="weight", value=70, date="2026-01-01"))

    new_data = [
        MeasurementCreate(user_id=4, type="weight", value=72, date="2026-02-01"),
        MeasurementCreate(user_id=4, type="body_fat", value=18, date="2026-02-01"),
    ]
    result = await update_measurements(db_session, user_id=4, measurements_in=new_data)
    assert len(result) == 2
    values = {m.value for m in result}
    assert 72 in values
    assert 70 not in values


async def test_create_measurement_id_increments(db_session):
    m1 = await create_measurement(db_session, MeasurementCreate(user_id=5, type="weight", value=65, date="2026-01-01"))
    m2 = await create_measurement(db_session, MeasurementCreate(user_id=5, type="weight", value=66, date="2026-01-02"))
    assert m1.id != m2.id

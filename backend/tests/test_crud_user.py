import pytest
import pytest_asyncio
from backend.database.sqlalchemy.crud.user import (
    create_user, get_user, get_user_auth, get_user_by_id
)
from backend.models.user import UserCreate

pytestmark = pytest.mark.asyncio


async def test_create_user_returns_user_read(db_session):
    user = await create_user(db_session, UserCreate(name="Кирилл", email="k@test.com", password="pass"))
    assert user is not None
    assert user.email == "k@test.com"
    assert user.name == "Кирилл"
    assert user.id is not None


async def test_create_user_hashes_password(db_session):
    await create_user(db_session, UserCreate(name="A", email="a@test.com", password="plain"))
    auth = await get_user_auth(db_session, email="a@test.com")
    assert auth is not None
    assert auth.hashed_password != "plain"
    assert len(auth.hashed_password) > 20


async def test_get_user_returns_existing(db_session):
    await create_user(db_session, UserCreate(name="Bob", email="bob@test.com", password="x"))
    user = await get_user(db_session, email="bob@test.com")
    assert user is not None
    assert user.email == "bob@test.com"


async def test_get_user_returns_none_for_missing(db_session):
    result = await get_user(db_session, email="nobody@test.com")
    assert result is None


async def test_get_user_auth_returns_hashed_password(db_session):
    await create_user(db_session, UserCreate(name="C", email="c@test.com", password="secret"))
    auth = await get_user_auth(db_session, email="c@test.com")
    assert auth is not None
    assert hasattr(auth, "hashed_password")


async def test_get_user_auth_missing_returns_none(db_session):
    result = await get_user_auth(db_session, email="missing@test.com")
    assert result is None


async def test_get_user_by_id(db_session):
    created = await create_user(db_session, UserCreate(name="D", email="d@test.com", password="p"))
    found = await get_user_by_id(db_session, created.id)
    assert found is not None
    assert found.id == created.id


async def test_get_user_by_id_missing_returns_none(db_session):
    result = await get_user_by_id(db_session, 99999)
    assert result is None

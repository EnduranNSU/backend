import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.routers.access.auth import authenticate_user
from backend.models.user import UserAuth

pytestmark = pytest.mark.asyncio


async def test_authenticate_user_success():
    from backend.routers.access.password import get_password_hash
    hashed = get_password_hash("correct_password")
    fake_user = UserAuth(id=1, email="user@test.com", name="User", hashed_password=hashed)

    mock_session = AsyncMock()
    with patch("backend.routers.access.auth.get_user_auth", return_value=fake_user):
        result = await authenticate_user(mock_session, "user@test.com", "correct_password")
    assert result is not None
    assert result.email == "user@test.com"


async def test_authenticate_user_wrong_password():
    from backend.routers.access.password import get_password_hash
    hashed = get_password_hash("correct_password")
    fake_user = UserAuth(id=1, email="user@test.com", name="User", hashed_password=hashed)

    mock_session = AsyncMock()
    with patch("backend.routers.access.auth.get_user_auth", return_value=fake_user):
        result = await authenticate_user(mock_session, "user@test.com", "wrong_password")
    assert result is None


async def test_authenticate_user_not_found():
    mock_session = AsyncMock()
    with patch("backend.routers.access.auth.get_user_auth", return_value=None):
        result = await authenticate_user(mock_session, "ghost@test.com", "any")
    assert result is None

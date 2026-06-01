import pytest
from datetime import timedelta, timezone, datetime
import jwt as pyjwt

from unittest.mock import patch, MagicMock

SECRET = "test-secret-key"
ALGORITHM = "HS256"

mock_cfg = MagicMock()
mock_cfg.authentication.secret_key = SECRET
mock_cfg.authentication.algorithm = ALGORITHM


@patch("backend.routers.access.token.config", mock_cfg)
def test_token_contains_subject():
    from backend.routers.access.token import create_access_token
    token = create_access_token({"sub": "user@test.com"})
    payload = pyjwt.decode(token, SECRET, algorithms=[ALGORITHM])
    assert payload["sub"] == "user@test.com"


@patch("backend.routers.access.token.config", mock_cfg)
def test_token_has_expiry():
    from backend.routers.access.token import create_access_token
    token = create_access_token({"sub": "u@x.com"}, expires_delta=timedelta(minutes=30))
    payload = pyjwt.decode(token, SECRET, algorithms=[ALGORITHM])
    assert "exp" in payload


@patch("backend.routers.access.token.config", mock_cfg)
def test_token_expires_in_future():
    from backend.routers.access.token import create_access_token
    token = create_access_token({"sub": "u@x.com"}, expires_delta=timedelta(minutes=5))
    payload = pyjwt.decode(token, SECRET, algorithms=[ALGORITHM])
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc)


@patch("backend.routers.access.token.config", mock_cfg)
def test_token_default_expiry_is_15min():
    from backend.routers.access.token import create_access_token
    before = datetime.now(timezone.utc)
    token = create_access_token({"sub": "u@x.com"})
    payload = pyjwt.decode(token, SECRET, algorithms=[ALGORITHM])
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    delta = exp - before
    assert timedelta(minutes=14) < delta < timedelta(minutes=16)


@patch("backend.routers.access.token.config", mock_cfg)
def test_expired_token_raises():
    from backend.routers.access.token import create_access_token
    token = create_access_token({"sub": "u@x.com"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(pyjwt.ExpiredSignatureError):
        pyjwt.decode(token, SECRET, algorithms=[ALGORITHM])


@patch("backend.routers.access.token.config", mock_cfg)
def test_wrong_secret_raises():
    from backend.routers.access.token import create_access_token
    token = create_access_token({"sub": "u@x.com"})
    with pytest.raises(pyjwt.InvalidSignatureError):
        pyjwt.decode(token, "wrong-secret", algorithms=[ALGORITHM])

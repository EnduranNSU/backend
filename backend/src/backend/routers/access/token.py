from datetime import datetime, timedelta, timezone
import jwt

from backend.config import get_config

config = get_config()
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.authentication.secret_key,
                            algorithm=config.authentication.algorithm)
    return encoded_jwt

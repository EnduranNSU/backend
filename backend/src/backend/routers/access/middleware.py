from typing import Annotated

from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.sqlalchemy.crud.user import get_user
from backend.database.sqlalchemy.session import get_session
from backend.models.user import UserRead
from backend.models.token import TokenData
from backend.config import get_config


config = get_config()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(get_session)
    ) -> UserRead:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.authentication.secret_key, algorithms=[config.authentication.algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    if token_data.username is None:
        raise credentials_exception

    user = await get_user(session, email=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

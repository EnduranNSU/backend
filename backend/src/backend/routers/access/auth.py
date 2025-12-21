from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .password import verify_password
from .token import create_access_token
from backend.database.sqlalchemy.crud.user import get_user_auth
from backend.database.sqlalchemy.session import get_session
from backend.models.token import Token
from backend.models.user import UserAuth
from backend.config import get_config

config = get_config()
router = APIRouter()


async def authenticate_user(session: AsyncSession, email: str, password: str) -> UserAuth | None:
    user = await get_user_auth(session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session)
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.authentication.access_token_expiration_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

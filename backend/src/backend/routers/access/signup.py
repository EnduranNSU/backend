
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.sqlalchemy.crud.user import  create_user
from backend.database.sqlalchemy.session import get_session
from backend.models.user import UserRead, UserCreate

router = APIRouter()

@router.post("/")
async def sigup(user_in: UserCreate, session: AsyncSession = Depends(get_session)) -> UserRead:
    user_create = UserCreate(name=user_in.name, email=user_in.email, password=user_in.password)
    user = await create_user(session, user_create)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    return user

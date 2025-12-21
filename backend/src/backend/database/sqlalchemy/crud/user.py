from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from backend.models.user import UserCreate, UserRead, UserAuth, UserBase
from backend.database.sqlalchemy.orm_models import User

password_hash = PasswordHash.recommended()

async def create_user(session: AsyncSession, user_in: UserCreate) -> UserRead | None:
    hashed_password = password_hash.hash(user_in.password)
    user = User(name=user_in.name, email=user_in.email, hashed_password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)


    stmt = select(User).where(User.email == user_in.email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return None
    
    user_read = UserRead(id=user.id, email=user.email, name=user.name)

    return user_read

async def get_user_auth(session: AsyncSession, email: str) -> UserAuth | None:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return None

    return UserAuth(id=user.id, email=user.email, name=user.name, hashed_password=user.hashed_password)

async def get_user(session: AsyncSession, email: str) -> UserRead | None:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return None

    return UserRead(id=user.id, email=user.email, name=user.name)


async def get_user_by_id(session: AsyncSession, user_id: int) -> UserBase | None:
    user = await session.get(User, user_id)

    if user is None:
        return None

    return UserRead(id=user.id, email=user.email, name=user.name)



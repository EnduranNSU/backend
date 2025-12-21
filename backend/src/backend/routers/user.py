from fastapi import APIRouter, Depends

from .access import get_current_user

from backend.models.user import UserRead

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/")
async def get_user(user: UserRead = Depends(get_current_user)):
    return user

from fastapi import APIRouter
from .auth import router as auth_router
from .signup import router as signin_router

router = APIRouter()

router.include_router(auth_router, prefix="", tags=["signin"])
router.include_router(signin_router, prefix="/signup", tags=["signup"])

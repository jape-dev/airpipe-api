from fastapi import APIRouter

from api.user import auth, user

router = APIRouter(prefix="/user")

router.include_router(auth.router)
router.include_router(user.router)

"""API routes for connector endpoints"""

from fastapi import APIRouter

from api.admin import user

router = APIRouter(prefix="/admin")

router.include_router(user.router)

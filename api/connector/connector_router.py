"""API routes for connector endpoints"""

from fastapi import APIRouter

from api.connector import google, facebook

router = APIRouter(prefix="/connector")

router.include_router(google.router)
router.include_router(facebook.router)

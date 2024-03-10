"""API routes for connector endpoints"""

from fastapi import APIRouter

from api.connector import google, facebook, google_analytics, looker, sheets, youtube, instagram, airbyte

router = APIRouter(prefix="/connector")

router.include_router(google.router)
router.include_router(facebook.router)
router.include_router(google_analytics.router)
router.include_router(looker.router)
router.include_router(sheets.router)
router.include_router(youtube.router)
router.include_router(instagram.router)
router.include_router(airbyte.router)

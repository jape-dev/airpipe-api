"""API routes for connector endpoints"""

from fastapi import APIRouter

from api.query import codex, data, conversation

router = APIRouter(prefix="/query")

router.include_router(data.router)
router.include_router(codex.router)
router.include_router(conversation.router)

# app/api/__init__.py
from fastapi import APIRouter

from .meetings import router as meetings_router

api_router = APIRouter()
api_router.include_router(meetings_router)

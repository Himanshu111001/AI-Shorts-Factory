from fastapi import APIRouter
from backend.api import health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])

from fastapi import APIRouter
from backend.api import health, channels, videos, jobs

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(channels.router, prefix="/channels", tags=["channels"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])


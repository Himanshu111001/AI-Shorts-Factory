from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from backend.models.enums.video_status import VideoStatus

class VideoBase(BaseModel):
    """Base schema for Video with shared attributes."""
    channel_id: UUID
    topic: str

class VideoCreate(VideoBase):
    """Schema for creating a new Video."""
    pass

class VideoUpdate(BaseModel):
    """Schema for updating an existing Video."""
    title: Optional[str] = None
    description: Optional[str] = None
    script: Optional[str] = None
    hashtags: Optional[List[str]] = None
    status: Optional[VideoStatus] = None

class VideoResponse(VideoBase):
    """Schema for returning a Video from the API."""
    id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    script: Optional[str] = None
    hashtags: Optional[List[str]] = None
    status: VideoStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

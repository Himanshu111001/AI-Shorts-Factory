from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class ChannelBase(BaseModel):
    """Base schema for Channel with shared attributes."""
    name: str
    niche: str
    youtube_account: str
    is_active: bool = True

class ChannelCreate(ChannelBase):
    """Schema for creating a new Channel."""
    pass

class ChannelUpdate(BaseModel):
    """Schema for updating an existing Channel. All fields are optional."""
    name: Optional[str] = None
    niche: Optional[str] = None
    youtube_account: Optional[str] = None
    is_active: Optional[bool] = None

class ChannelResponse(ChannelBase):
    """Schema for returning a Channel from the API."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

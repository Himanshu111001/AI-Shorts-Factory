from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from backend.models.enums.job_status import JobStatus

class JobResponse(BaseModel):
    """Schema for returning a Job from the API."""
    id: UUID
    video_id: UUID
    status: JobStatus
    progress: int
    current_step: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

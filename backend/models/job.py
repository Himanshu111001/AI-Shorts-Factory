import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Text, ForeignKey, String, Integer, Enum, DateTime, Uuid, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from backend.models.base import Base
from backend.models.enums.job_status import JobStatus
from backend.utils.datetime import utc_now

class Job(Base):
    """
    Represents a single execution attempt of a background processing pipeline (e.g. video generation).
    
    Attributes:
        id: Unique identifier for the job attempt.
        video_id: The UUID of the video this job is processing.
        status: The execution status of the job attempt.
        progress: An integer representing completion percentage (0-100).
        current_step: A string indicating the current task being executed.
        error: A message storing failure details if the job crashes.
        created_at: Timestamp when the job was queued.
        started_at: Timestamp when the job began processing.
        finished_at: Timestamp when the job completed or failed.
    """
    __tablename__ = "jobs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("videos.id"), nullable=False, index=True
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), default=JobStatus.QUEUED, nullable=False, index=True
    )
    progress: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    current_step: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    __table_args__ = (
        CheckConstraint('progress >= 0 AND progress <= 100', name='check_progress_range'),
    )

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Text, ForeignKey, JSON, Enum, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from backend.models.base import Base
from backend.models.enums.video_status import VideoStatus
from backend.utils.datetime import utc_now

class Video(Base):
    """
    Represents a video generation project in the AI Media Factory.
    
    Attributes:
        id: Unique identifier for the video job.
        channel_id: The UUID of the channel this video belongs to.
        topic: The initial seed topic or idea for the video.
        title: The generated title of the video.
        description: The generated YouTube description.
        script: The generated script/narration for the video.
        hashtags: A JSON list of generated hashtags.
        status: The current lifecycle stage of the video generation.
        created_at: Timestamp when the video project was created.
        updated_at: Timestamp when the video project was last updated.
    """
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("channels.id"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    script: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hashtags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    
    status: Mapped[VideoStatus] = mapped_column(
        Enum(VideoStatus), default=VideoStatus.CREATED, nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

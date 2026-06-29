import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from backend.models.base import Base
from backend.utils.datetime import utc_now

class Channel(Base):
    """
    Represents a YouTube channel managed by the AI Media Factory.
    
    Attributes:
        id: Unique identifier for the channel.
        name: The display name of the channel.
        niche: The content niche or category of the channel.
        youtube_account: The account identifier associated with the channel.
        is_active: Whether the channel is currently active and generating content.
        created_at: Timestamp when the channel record was created.
        updated_at: Timestamp when the channel record was last updated.
    """
    __tablename__ = "channels"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    niche: Mapped[str] = mapped_column(String(255), nullable=False)
    youtube_account: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

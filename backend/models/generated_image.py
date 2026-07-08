import uuid
from datetime import datetime
from sqlalchemy import Text, ForeignKey, Integer, DateTime, Uuid, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from backend.models.base import Base
from backend.utils.datetime import utc_now

class GeneratedImage(Base):
    """
    Represents a generated image artifact associated with a Video.
    """
    __tablename__ = "generated_images"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("videos.id"), nullable=False, index=True
    )
    sequence_index: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("video_id", "sequence_index", name="uq_generated_image_video_sequence"),
        CheckConstraint("sequence_index >= 1", name="chk_generated_image_sequence_index_positive"),
    )

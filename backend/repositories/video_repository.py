import uuid
from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.models.video import Video
from backend.models.enums.video_status import VideoStatus

class VideoRepository:
    """
    Repository for managing Video entities in the database.
    Handles all CRUD operations directly via SQLAlchemy 2.0 conventions.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with an active SQLAlchemy Session.
        """
        self.db = db

    def create(self, video_data: dict) -> Video:
        """
        Create a new video record.
        
        Args:
            video_data: Dictionary containing fields like 'channel_id' and 'topic'.
            
        Returns:
            The created and persisted Video object.
        """
        video = Video(**video_data)
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    def get_by_id(self, video_id: uuid.UUID) -> Optional[Video]:
        """
        Retrieve a video by its UUID.
        
        Args:
            video_id: The UUID of the video to lookup.
            
        Returns:
            The Video object if found, else None.
        """
        stmt = select(Video).where(Video.id == video_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Video]:
        """
        Retrieve a list of videos with optional pagination.
        
        Args:
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.
            
        Returns:
            A sequence of Video objects.
        """
        stmt = select(Video).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def get_by_channel(self, channel_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Video]:
        """
        Retrieve a list of videos for a specific channel.
        
        Args:
            channel_id: The UUID of the channel.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            A sequence of Video objects belonging to the channel.
        """
        stmt = select(Video).where(Video.channel_id == channel_id).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def get_by_status(self, status: VideoStatus, skip: int = 0, limit: int = 100) -> Sequence[Video]:
        """
        Retrieve a list of videos filtered by their current generation status.
        
        Args:
            status: The VideoStatus enum to filter by.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            A sequence of Video objects with the given status.
        """
        stmt = select(Video).where(Video.status == status).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def update_status(self, video_id: uuid.UUID, status: VideoStatus) -> Video:
        """
        Convenience method to quickly update just the status of a video.
        
        Args:
            video_id: The UUID of the video.
            status: The new VideoStatus to apply.
            
        Raises:
            ValueError: If the video is not found.
            
        Returns:
            The updated Video object.
        """
        video = self.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video with id {video_id} not found.")
            
        video.status = status
        self.db.commit()
        self.db.refresh(video)
        return video

    def update(self, video_id: uuid.UUID, update_data: dict) -> Video:
        """
        Update an existing video's generic attributes (e.g. title, description).
        
        Args:
            video_id: The UUID of the video to update.
            update_data: Dictionary of fields to modify.
            
        Raises:
            ValueError: If the video is not found.
            
        Returns:
            The updated Video object.
        """
        video = self.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video with id {video_id} not found.")

        for key, value in update_data.items():
            setattr(video, key, value)
            
        self.db.commit()
        self.db.refresh(video)
        return video

    def delete(self, video_id: uuid.UUID) -> bool:
        """
        Delete a video by its UUID.
        
        Args:
            video_id: The UUID of the video to delete.
            
        Raises:
            ValueError: If the video is not found.
            
        Returns:
            True if deletion was successful.
        """
        video = self.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video with id {video_id} not found.")

        self.db.delete(video)
        self.db.commit()
        return True

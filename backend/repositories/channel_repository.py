import uuid
from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.models.channel import Channel

class ChannelRepository:
    """
    Repository for managing Channel entities in the database.
    Handles all CRUD operations directly via SQLAlchemy 2.0 conventions.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with an active SQLAlchemy Session.
        """
        self.db = db

    def create(self, channel_data: dict) -> Channel:
        """
        Create a new channel record.
        
        Args:
            channel_data: Dictionary containing fields like 'name', 'niche', 'youtube_account'.
            
        Returns:
            The created and persisted Channel object.
        """
        channel = Channel(**channel_data)
        self.db.add(channel)
        self.db.commit()
        self.db.refresh(channel)
        return channel

    def get_by_id(self, channel_id: uuid.UUID) -> Optional[Channel]:
        """
        Retrieve a channel by its UUID.
        
        Args:
            channel_id: The UUID of the channel to lookup.
            
        Returns:
            The Channel object if found, else None.
        """
        stmt = select(Channel).where(Channel.id == channel_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Channel]:
        """
        Retrieve a list of channels with optional pagination.
        
        Args:
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.
            
        Returns:
            A sequence of Channel objects.
        """
        stmt = select(Channel).offset(skip).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def update(self, channel_id: uuid.UUID, update_data: dict) -> Channel:
        """
        Update an existing channel.
        
        Args:
            channel_id: The UUID of the channel to update.
            update_data: Dictionary of fields to modify.
            
        Raises:
            ValueError: If the channel is not found.
            
        Returns:
            The updated Channel object.
        """
        channel = self.get_by_id(channel_id)
        if not channel:
            raise ValueError(f"Channel with id {channel_id} not found.")

        for key, value in update_data.items():
            # Allow SQLAlchemy to map dynamic fields safely onto the object
            setattr(channel, key, value)
            
        self.db.commit()
        self.db.refresh(channel)
        return channel

    def delete(self, channel_id: uuid.UUID) -> bool:
        """
        Delete a channel by its UUID.
        
        Args:
            channel_id: The UUID of the channel to delete.
            
        Raises:
            ValueError: If the channel is not found.
            
        Returns:
            True if deletion was successful.
        """
        channel = self.get_by_id(channel_id)
        if not channel:
            raise ValueError(f"Channel with id {channel_id} not found.")

        self.db.delete(channel)
        self.db.commit()
        return True

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.config.session import get_db
from backend.repositories.channel_repository import ChannelRepository
from backend.schemas.channel import ChannelCreate, ChannelResponse

router = APIRouter()

@router.post("/", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
def create_channel(channel_in: ChannelCreate, db: Session = Depends(get_db)):
    """
    Create a new channel record.
    """
    repo = ChannelRepository(db)
    return repo.create(channel_in.model_dump())

@router.get("/", response_model=List[ChannelResponse])
def get_channels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a paginated list of all channels.
    """
    repo = ChannelRepository(db)
    return repo.get_all(skip=skip, limit=limit)

@router.get("/{channel_id}", response_model=ChannelResponse)
def get_channel(channel_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific channel by its UUID.
    """
    repo = ChannelRepository(db)
    channel = repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return channel

@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_channel(channel_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Delete a specific channel by its UUID.
    """
    repo = ChannelRepository(db)
    try:
        repo.delete(channel_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

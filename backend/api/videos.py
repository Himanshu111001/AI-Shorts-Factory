import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from backend.config.session import get_db
from backend.repositories.video_repository import VideoRepository
from backend.schemas.video import VideoCreate, VideoUpdate, VideoResponse
from backend.models.enums.video_status import VideoStatus
from backend.services.video_service import VideoService

router = APIRouter()

@router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
def create_video(video_in: VideoCreate, db: Session = Depends(get_db)):
    """
    Create a new video project.
    """
    service = VideoService(db)
    try:
        return service.create_video(video_in.model_dump())
    except ValueError as e:
        msg = str(e)
        if "Channel not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.get("/", response_model=List[VideoResponse])
def get_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a paginated list of all videos.
    """
    repo = VideoRepository(db)
    return repo.get_all(skip=skip, limit=limit)

# Note on Route Ordering:
# Specific sub-paths (like /channel/{channel_id}) must be registered before dynamic path parameters 
# (like /{video_id}) so FastAPI doesn't mistakenly parse 'channel' as a video UUID.
@router.get("/channel/{channel_id}", response_model=List[VideoResponse])
def get_videos_by_channel(channel_id: uuid.UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all videos belonging to a specific channel.
    """
    repo = VideoRepository(db)
    return repo.get_by_channel(channel_id=channel_id, skip=skip, limit=limit)

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a specific video by its UUID.
    """
    repo = VideoRepository(db)
    video = repo.get_by_id(video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return video

@router.patch("/{video_id}", response_model=VideoResponse)
def update_video(video_id: uuid.UUID, video_update: VideoUpdate, db: Session = Depends(get_db)):
    """
    Update general attributes of a video (title, description, script, etc.).
    """
    repo = VideoRepository(db)
    update_data = video_update.model_dump(exclude_unset=True)
    
    # If nothing to update, just return the video
    if not update_data:
        video = repo.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        return video

    try:
        return repo.update(video_id, update_data)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

@router.patch("/{video_id}/status", response_model=VideoResponse)
def update_video_status(
    video_id: uuid.UUID, 
    video_status: VideoStatus = Body(..., embed=True, alias="status"), 
    db: Session = Depends(get_db)
):
    """
    Fast-path endpoint to update only the lifecycle status of a video.
    """
    service = VideoService(db)
    try:
        return service.transition_status(video_id, video_status)
    except ValueError as e:
        msg = str(e)
        if "Video not found" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(video_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Delete a specific video by its UUID.
    """
    repo = VideoRepository(db)
    try:
        repo.delete(video_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

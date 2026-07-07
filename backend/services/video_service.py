import uuid
from sqlalchemy.orm import Session
from backend.repositories.video_repository import VideoRepository
from backend.repositories.channel_repository import ChannelRepository
from backend.models.video import Video
from backend.models.enums.video_status import VideoStatus

class VideoService:
    """
    Business logic layer for managing Video entities.
    Orchestrates validation, state transitions, and repository interactions.
    """
    
    # Define valid state transitions based on the business rules
    ALLOWED_TRANSITIONS = {
        VideoStatus.CREATED: {VideoStatus.PROCESSING},
        VideoStatus.PROCESSING: {VideoStatus.REVIEW, VideoStatus.FAILED},
        VideoStatus.REVIEW: {VideoStatus.APPROVED, VideoStatus.REJECTED},
        VideoStatus.REJECTED: {VideoStatus.PROCESSING},
        VideoStatus.APPROVED: {VideoStatus.UPLOADED},
        VideoStatus.FAILED: set(),
        VideoStatus.UPLOADED: set(),
    }

    def __init__(self, db: Session):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.channel_repo = ChannelRepository(db)

    def create_video(self, video_data: dict) -> Video:
        """
        Create a new video with business rules enforcement.
        
        Business Rules:
        - The associated channel must exist.
        - The associated channel must be active.
        - The initial video status is strictly set to CREATED.
        
        Args:
            video_data: Dictionary containing video fields.
            
        Returns:
            The created Video object.
            
        Raises:
            ValueError: If channel doesn't exist or is inactive.
        """
        channel_id_raw = video_data.get("channel_id")
        if not channel_id_raw:
            raise ValueError("Channel ID is required")
            
        try:
            channel_id = uuid.UUID(str(channel_id_raw))
        except ValueError:
            raise ValueError("Invalid Channel ID format")

        channel = self.channel_repo.get_by_id(channel_id)
        if not channel:
            raise ValueError("Channel not found")
            
        if not channel.is_active:
            raise ValueError("Channel is inactive")
            
        # Create a copy to prevent mutating the input dictionary
        creation_data = video_data.copy()
        
        # Force the initial status to prevent rogue inputs
        creation_data["status"] = VideoStatus.CREATED
        
        return self.video_repo.create(creation_data)

    def transition_status(self, video_id: uuid.UUID, new_status: VideoStatus) -> Video:
        """
        Transition a video to a new status while enforcing valid state machine rules.
        
        Args:
            video_id: UUID of the video.
            new_status: The target VideoStatus to transition to.
            
        Returns:
            The updated Video object.
            
        Raises:
            ValueError: If video is not found or the transition is invalid.
        """
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise ValueError("Video not found")
            
        current_status = video.status
        
        # Check against the allowed transitions map
        valid_next_states = self.ALLOWED_TRANSITIONS.get(current_status, set())
        if new_status not in valid_next_states:
            raise ValueError(f"Invalid status transition: {current_status.value} -> {new_status.value}")
            
        return self.video_repo.update_status(video_id, new_status)

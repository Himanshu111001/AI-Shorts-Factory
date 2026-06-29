from enum import Enum

class VideoStatus(str, Enum):
    """
    Represents the various lifecycle stages of a generated video.
    """
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    UPLOADED = "UPLOADED"
    FAILED = "FAILED"

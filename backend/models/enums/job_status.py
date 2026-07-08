from enum import Enum

class JobStatus(str, Enum):
    """
    Represents the execution lifecycle stages of a specific background processing attempt.
    """
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

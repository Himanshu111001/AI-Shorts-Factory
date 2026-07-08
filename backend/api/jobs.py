from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from backend.schemas.job import JobResponse
from backend.services.job_service import JobService
from backend.api.dependencies import get_job_service_dependency
from backend.api.pipeline_dependencies import get_video_worker_dependency
from backend.workers.video_worker import VideoWorker
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Note: GET /video/{video_id} must be registered BEFORE GET /{job_id} 
# to avoid the literal "video" being interpreted as a dynamic job_id.

@router.get("/video/{video_id}", response_model=list[JobResponse])
def get_jobs_for_video(
    video_id: UUID,
    job_service: JobService = Depends(get_job_service_dependency)
):
    try:
        return job_service.get_jobs_for_video(video_id)
    except ValueError as e:
        if str(e) == "Video not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: UUID,
    job_service: JobService = Depends(get_job_service_dependency)
):
    try:
        return job_service.get_job(job_id)
    except ValueError as e:
        if str(e) == "Job not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/video/{video_id}", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    video_id: UUID,
    job_service: JobService = Depends(get_job_service_dependency)
):
    try:
        return job_service.create_job(video_id)
    except ValueError as e:
        if str(e) == "Video not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif str(e) == "Video already has an active job":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{job_id}/execute", response_model=JobResponse)
def execute_job(
    job_id: UUID,
    worker: VideoWorker = Depends(get_video_worker_dependency)
):
    """
    Executes a Job synchronously.
    This is intended as the current execution mechanism before migration to a background task queue.
    """
    try:
        return worker.execute(job_id)
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "Job not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        if "Invalid job status transition" in error_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg)
        if error_msg == "Video not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        if error_msg == "Channel not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        if "Text generation requires PROCESSING status" in error_msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
            
        if "provider" in error_msg.lower() or "configured" in error_msg.lower():
            logger.exception(f"Configuration error: {error_msg}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server configuration error")
            
        logger.exception("Unexpected execution ValueError")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Job execution failed")
    except Exception:
        logger.exception("Unexpected execution failure")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Job execution failed")


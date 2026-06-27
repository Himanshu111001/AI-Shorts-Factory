from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def get_health():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

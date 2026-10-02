from fastapi import APIRouter
from backend.schemas import StandardResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=StandardResponse)
def health_check():
    return StandardResponse(
        success=True,
        data={
            "status": "healthy",
            "service": "ResumeForge AI Backend",
            "version": "1.0.0"
        }
    )

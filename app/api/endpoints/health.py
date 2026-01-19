from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.db.session import get_db
from app.services.storage_service import StorageService
from app.services.gemini_service import GeminiService, get_gemini_service
from app.dependencies import get_storage_service

router = APIRouter()


@router.get("/health")
async def api_health(
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
    gemini: GeminiService = Depends(get_gemini_service)
):
    """
    Detailed API health check endpoint.
    Returns service status and dependency checks.
    """
    # Test database connection
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Test storage
    storage_check = storage.health_check()

    # Test Gemini
    gemini_check = gemini.health_check()

    return {
        "status": "healthy",
        "service": "listing-genie",
        "version": "1.0.0",
        "environment": settings.app_env,
        "dependencies": {
            "database": db_status,
            "storage": storage_check["status"],
            "gemini": gemini_check["status"]
        }
    }

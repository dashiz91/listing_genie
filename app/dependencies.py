"""
Dependency injection for FastAPI.

This module provides dependency functions for services that will be
injected into API endpoints.
"""

from app.config import settings
from app.db.session import get_db  # Re-export for convenience
from app.services.storage_service import StorageService
from app.services.gemini_service import GeminiService, get_gemini_service


# Re-export database dependency
get_db = get_db

# Re-export gemini service
get_gemini_service = get_gemini_service


def get_storage_service() -> StorageService:
    """Dependency injection for storage service"""
    return StorageService(storage_path=settings.storage_path)

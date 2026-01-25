"""
Dependency injection for FastAPI.

This module provides dependency functions for services that will be
injected into API endpoints.
"""
import logging
from functools import lru_cache

from app.config import settings
from app.db.session import get_db  # Re-export for convenience
from app.services.supabase_storage_service import SupabaseStorageService
from app.services.gemini_service import GeminiService, get_gemini_service

logger = logging.getLogger(__name__)

# Re-export database dependency
get_db = get_db

# Re-export gemini service
get_gemini_service = get_gemini_service

# Singleton storage service instance
_storage_service = None


def get_storage_service() -> SupabaseStorageService:
    """Dependency injection for Supabase storage service"""
    global _storage_service
    if _storage_service is None:
        _storage_service = SupabaseStorageService()
        logger.info("Initialized Supabase storage service")
    return _storage_service

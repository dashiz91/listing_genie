"""
Dependency injection for FastAPI.

This module provides dependency functions for services that will be
injected into API endpoints.
"""
import logging
from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db  # Re-export for convenience
from app.services.supabase_storage_service import SupabaseStorageService
from app.services.gemini_service import GeminiService, get_gemini_service
from app.services.credits_service import CreditsService, MODEL_COSTS

logger = logging.getLogger(__name__)

# Re-export database dependency
get_db = get_db

# Re-export gemini service
get_gemini_service = get_gemini_service

# Singleton storage service instance
_storage_service = None


def get_credits_service(db: Session = Depends(get_db)) -> CreditsService:
    """Dependency injection for credits service"""
    return CreditsService(db)


def get_storage_service() -> SupabaseStorageService:
    """Dependency injection for Supabase storage service"""
    global _storage_service
    if _storage_service is None:
        _storage_service = SupabaseStorageService()
        logger.info("Initialized Supabase storage service")
    return _storage_service

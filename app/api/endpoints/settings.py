"""
User Settings API Endpoints

Manage user preferences, brand presets, and usage stats.
"""
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies import get_db, get_storage_service
from app.core.auth import User, get_current_user
from app.models.database import UserSettings, GenerationSession, ImageRecord, GenerationStatusEnum
from app.services.supabase_storage_service import SupabaseStorageService
from app.config import settings as app_settings

logger = logging.getLogger(__name__)


def _get_image_url(relative_path: str) -> str:
    """Convert a relative API path to an absolute URL."""
    if app_settings.backend_url:
        return f"{app_settings.backend_url.rstrip('/')}{relative_path}"
    return relative_path


router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class BrandPresetsUpdate(BaseModel):
    """Update brand presets"""
    default_brand_name: Optional[str] = None
    default_brand_colors: Optional[List[str]] = None
    default_logo_path: Optional[str] = None
    default_style_reference_path: Optional[str] = None


class BrandPresetsResponse(BaseModel):
    """Brand presets with signed URLs"""
    default_brand_name: Optional[str] = None
    default_brand_colors: List[str] = []
    default_logo_path: Optional[str] = None
    default_logo_url: Optional[str] = None
    default_style_reference_path: Optional[str] = None
    default_style_reference_url: Optional[str] = None


class UsageStatsResponse(BaseModel):
    """User usage statistics"""
    images_generated_total: int = 0
    images_generated_this_month: int = 0
    projects_count: int = 0
    last_generation_at: Optional[str] = None
    credits_balance: int = 0
    plan_tier: str = "free"


class FullSettingsResponse(BaseModel):
    """Complete settings response"""
    brand_presets: BrandPresetsResponse
    usage: UsageStatsResponse
    email: str


# ============================================================================
# Helper Functions
# ============================================================================

def get_or_create_settings(db: Session, user_id: str) -> UserSettings:
    """Get user settings or create default if not exists."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def calculate_usage_stats(db: Session, user_id: str) -> dict:
    """Calculate real-time usage stats from database."""
    # Count projects
    projects_count = db.query(GenerationSession).filter(
        GenerationSession.user_id == user_id
    ).count()

    # Count completed images total
    from sqlalchemy import func
    images_total = db.query(func.count(ImageRecord.id)).join(GenerationSession).filter(
        GenerationSession.user_id == user_id,
        ImageRecord.status == GenerationStatusEnum.COMPLETE
    ).scalar() or 0

    # Count images this month
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    images_this_month = db.query(func.count(ImageRecord.id)).join(GenerationSession).filter(
        GenerationSession.user_id == user_id,
        ImageRecord.status == GenerationStatusEnum.COMPLETE,
        ImageRecord.completed_at >= current_month_start
    ).scalar() or 0

    # Last generation date
    last_image = db.query(ImageRecord).join(GenerationSession).filter(
        GenerationSession.user_id == user_id,
        ImageRecord.status == GenerationStatusEnum.COMPLETE
    ).order_by(ImageRecord.completed_at.desc()).first()

    return {
        "projects_count": projects_count,
        "images_generated_total": images_total,
        "images_generated_this_month": images_this_month,
        "last_generation_at": last_image.completed_at.isoformat() if last_image and last_image.completed_at else None,
    }


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/", response_model=FullSettingsResponse)
async def get_settings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    Get all user settings including brand presets and usage stats.
    """
    settings = get_or_create_settings(db, user.id)
    usage_stats = calculate_usage_stats(db, user.id)

    # Build logo URL if exists
    logo_url = None
    if settings.default_logo_path:
        logo_url = _get_image_url(f"/api/images/file?path={settings.default_logo_path}")

    # Build style reference URL if exists
    style_ref_url = None
    if settings.default_style_reference_path:
        style_ref_url = _get_image_url(f"/api/images/file?path={settings.default_style_reference_path}")

    return FullSettingsResponse(
        brand_presets=BrandPresetsResponse(
            default_brand_name=settings.default_brand_name,
            default_brand_colors=settings.default_brand_colors or [],
            default_logo_path=settings.default_logo_path,
            default_logo_url=logo_url,
            default_style_reference_path=settings.default_style_reference_path,
            default_style_reference_url=style_ref_url,
        ),
        usage=UsageStatsResponse(
            images_generated_total=usage_stats["images_generated_total"],
            images_generated_this_month=usage_stats["images_generated_this_month"],
            projects_count=usage_stats["projects_count"],
            last_generation_at=usage_stats["last_generation_at"],
            credits_balance=settings.credits_balance,
            plan_tier=settings.plan_tier,
        ),
        email=user.email or "",
    )


@router.get("/brand-presets", response_model=BrandPresetsResponse)
async def get_brand_presets(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's brand presets for auto-filling new projects.
    """
    settings = get_or_create_settings(db, user.id)

    logo_url = None
    if settings.default_logo_path:
        logo_url = _get_image_url(f"/api/images/file?path={settings.default_logo_path}")

    style_ref_url = None
    if settings.default_style_reference_path:
        style_ref_url = _get_image_url(f"/api/images/file?path={settings.default_style_reference_path}")

    return BrandPresetsResponse(
        default_brand_name=settings.default_brand_name,
        default_brand_colors=settings.default_brand_colors or [],
        default_logo_path=settings.default_logo_path,
        default_logo_url=logo_url,
        default_style_reference_path=settings.default_style_reference_path,
        default_style_reference_url=style_ref_url,
    )


@router.patch("/brand-presets", response_model=BrandPresetsResponse)
async def update_brand_presets(
    updates: BrandPresetsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update user's brand presets.
    Only provided fields will be updated.
    """
    settings = get_or_create_settings(db, user.id)

    # Update only provided fields
    if updates.default_brand_name is not None:
        settings.default_brand_name = updates.default_brand_name or None  # Empty string -> None
    if updates.default_brand_colors is not None:
        settings.default_brand_colors = updates.default_brand_colors
    if updates.default_logo_path is not None:
        settings.default_logo_path = updates.default_logo_path or None
    if updates.default_style_reference_path is not None:
        settings.default_style_reference_path = updates.default_style_reference_path or None

    db.commit()
    db.refresh(settings)

    logger.info(f"Updated brand presets for user {user.id}")

    # Return updated presets with URLs
    logo_url = None
    if settings.default_logo_path:
        logo_url = _get_image_url(f"/api/images/file?path={settings.default_logo_path}")

    style_ref_url = None
    if settings.default_style_reference_path:
        style_ref_url = _get_image_url(f"/api/images/file?path={settings.default_style_reference_path}")

    return BrandPresetsResponse(
        default_brand_name=settings.default_brand_name,
        default_brand_colors=settings.default_brand_colors or [],
        default_logo_path=settings.default_logo_path,
        default_logo_url=logo_url,
        default_style_reference_path=settings.default_style_reference_path,
        default_style_reference_url=style_ref_url,
    )


@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's usage statistics.
    """
    settings = get_or_create_settings(db, user.id)
    stats = calculate_usage_stats(db, user.id)

    return UsageStatsResponse(
        images_generated_total=stats["images_generated_total"],
        images_generated_this_month=stats["images_generated_this_month"],
        projects_count=stats["projects_count"],
        last_generation_at=stats["last_generation_at"],
        credits_balance=settings.credits_balance,
        plan_tier=settings.plan_tier,
    )

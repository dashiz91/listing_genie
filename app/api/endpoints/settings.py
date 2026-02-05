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
from app.services.credits_service import (
    CreditsService, PLANS, MODEL_COSTS, estimate_generation_cost
)
from app.config import settings as app_config
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


# ============================================================================
# Credits Endpoints
# ============================================================================

class CreditsResponse(BaseModel):
    """Current credits info"""
    balance: int
    plan_tier: str
    plan_name: str
    credits_per_period: int
    period: str  # "day" or "month"
    is_admin: bool = False  # Admin users have unlimited credits


class PlanInfo(BaseModel):
    """Plan information"""
    id: str
    name: str
    price: int
    credits_per_period: int
    period: str
    features: List[str]


class PlansResponse(BaseModel):
    """All available plans"""
    plans: List[PlanInfo]
    current_plan: str


class CostEstimateRequest(BaseModel):
    """Request to estimate generation cost"""
    operation: str  # "full_listing", "listing_images", "aplus", "single_image"
    model: str = "gemini-3-pro-image-preview"
    count: int = 1


class CostEstimateResponse(BaseModel):
    """Estimated cost breakdown"""
    total: int
    breakdown: dict
    can_afford: bool
    current_balance: int


@router.get("/credits", response_model=CreditsResponse)
async def get_credits(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current credits balance and plan info.
    """
    credits_service = CreditsService(db)
    # Pass email to store/update it in user settings for admin lookup
    user_settings = credits_service.get_user_settings(user.id, email=user.email)
    plan_info = credits_service.get_plan_info(user_settings.plan_tier)
    is_admin = credits_service.is_admin(user.id, user.email)

    return CreditsResponse(
        balance=user_settings.credits_balance,
        plan_tier=user_settings.plan_tier,
        plan_name=plan_info["name"],
        credits_per_period=plan_info["credits_per_period"],
        period=plan_info["period"],
        is_admin=is_admin,
    )


@router.get("/plans", response_model=PlansResponse)
async def get_plans(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all available plans with features.
    """
    settings = get_or_create_settings(db, user.id)

    plans = [
        PlanInfo(
            id=plan_id,
            name=plan["name"],
            price=plan["price"],
            credits_per_period=plan["credits_per_period"],
            period=plan["period"],
            features=plan["features"],
        )
        for plan_id, plan in PLANS.items()
    ]

    return PlansResponse(
        plans=plans,
        current_plan=settings.plan_tier,
    )


@router.post("/credits/estimate", response_model=CostEstimateResponse)
async def estimate_cost(
    request: CostEstimateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Estimate credit cost for a generation operation.
    """
    credits_service = CreditsService(db)
    settings = credits_service.get_user_settings(user.id)

    if request.operation == "full_listing":
        # Full listing = framework analysis + 4 previews + 6 listing + 6 A+ desktop + 6 A+ mobile
        estimate = estimate_generation_cost(
            num_listing_images=6,
            num_aplus_modules=6,
            include_mobile=True,
            num_previews=4,
            model=request.model,
        )
        total = estimate["total"]
        breakdown = estimate
    elif request.operation == "listing_images":
        # Just the 6 listing images
        cost = credits_service.get_credit_cost("listing_image", request.model, 6)
        total = cost
        breakdown = {"listing_images": cost}
    elif request.operation == "aplus":
        # A+ section (6 desktop + 6 mobile)
        model_cost = MODEL_COSTS.get(request.model, 2)
        desktop = 6 * model_cost
        mobile = 6 * 1  # Mobile transforms are always 1 credit
        total = desktop + mobile
        breakdown = {"aplus_desktop": desktop, "aplus_mobile": mobile}
    elif request.operation == "single_image":
        total = credits_service.get_credit_cost("listing_image", request.model, request.count)
        breakdown = {"images": total}
    elif request.operation == "framework":
        # Framework analysis (1) + 4 previews (4)
        total = 1 + 4
        breakdown = {"analysis": 1, "previews": 4}
    else:
        total = credits_service.get_credit_cost(request.operation, request.model, request.count)
        breakdown = {request.operation: total}

    return CostEstimateResponse(
        total=total,
        breakdown=breakdown,
        can_afford=settings.credits_balance >= total,
        current_balance=settings.credits_balance,
    )


@router.get("/credits/model-costs")
async def get_model_costs(
    user: User = Depends(get_current_user),
):
    """
    Get credit costs for each model and operation.

    Models:
    - Flash (~$0.039/image): 1 credit
    - Pro (~$0.134/image): 3 credits

    Full listing costs:
    - With Pro: ~47 credits
    - With Flash: ~23 credits
    """
    return {
        "models": {
            "gemini-2.5-flash": {
                "name": "Flash (Fast)",
                "cost": 1,
                "description": "Fast generation, great quality (~4¢/image)",
            },
            "gemini-3-pro-image-preview": {
                "name": "Pro (Best)",
                "cost": 3,
                "description": "Highest quality, best for final images (~13¢/image)",
            },
        },
        "operations": {
            "framework_analysis": {"cost": 1, "description": "AI product analysis"},
            "framework_preview": {"cost": 1, "description": "Style preview image"},
            "listing_image_flash": {"cost": 1, "description": "Listing image (Flash)"},
            "listing_image_pro": {"cost": 3, "description": "Listing image (Pro)"},
            "aplus_module_flash": {"cost": 1, "description": "A+ module (Flash)"},
            "aplus_module_pro": {"cost": 3, "description": "A+ module (Pro)"},
            "aplus_mobile": {"cost": 1, "description": "Mobile transform"},
            "edit_image": {"cost": 1, "description": "Edit existing image"},
        },
        "full_listing": {
            "with_pro": {
                "total": 47,
                "breakdown": "1 analysis + 4 previews + 18 listing (6×3) + 18 A+ desktop (6×3) + 6 mobile",
            },
            "with_flash": {
                "total": 23,
                "breakdown": "1 analysis + 4 previews + 6 listing + 6 A+ desktop + 6 mobile",
            },
        },
    }

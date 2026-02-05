"""
Admin API Endpoints

Admin-only endpoints for managing users and credits.
Only users with emails in ADMIN_EMAILS can access these endpoints.
"""
import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.dependencies import get_db
from app.core.auth import User, get_current_user
from app.models.database import UserSettings
from app.services.credits_service import CreditsService

logger = logging.getLogger(__name__)


router = APIRouter()


# ============================================================================
# Auth Helper - Require Admin
# ============================================================================

async def require_admin(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    """
    Dependency that ensures the current user is an admin.
    Raises 403 if not an admin.
    """
    credits_service = CreditsService(db)
    if not credits_service.is_admin(user.id, user.email):
        logger.warning(f"Non-admin user {user.email} attempted to access admin endpoint")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


# ============================================================================
# Pydantic Models
# ============================================================================

class CreditAdjustmentRequest(BaseModel):
    """Request to adjust a user's credits"""
    email: EmailStr
    amount: int  # Positive to add, negative to subtract
    reason: str = ""  # Optional reason for the adjustment


class CreditAdjustmentResponse(BaseModel):
    """Response after adjusting credits"""
    success: bool
    email: str
    previous_balance: int
    new_balance: int
    amount_adjusted: int
    reason: str


class UserSearchResult(BaseModel):
    """User info for admin search"""
    email: str
    user_id: str
    credits_balance: int
    plan_tier: str


class UserSearchResponse(BaseModel):
    """Response for user search"""
    users: List[UserSearchResult]
    total: int


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/credits/adjust", response_model=CreditAdjustmentResponse)
async def adjust_user_credits(
    request: CreditAdjustmentRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Adjust a user's credit balance by email.

    - **email**: Target user's email address
    - **amount**: Credits to add (positive) or subtract (negative)
    - **reason**: Optional reason for the adjustment (for logging)

    Admins only. The target user will have their balance updated.
    If the user doesn't exist in settings yet, creates their settings first.
    """
    target_email = request.email.lower().strip()

    # Find user settings by looking up through all users
    # Note: UserSettings links to user_id, but we need to find by email
    # We'll need to query Supabase or check existing sessions

    # For now, search in UserSettings - but we need the user_id
    # Since we don't have a direct email->user_id mapping in our DB,
    # we'll search through GenerationSessions which have user_id
    from app.models.database import GenerationSession

    # Find a user_id that has sessions or settings
    session_with_email = None

    # First check if we have any user with this email in our session data
    # Since sessions don't store email, we need a different approach

    # For MVP: Allow admin to paste the user_id directly OR
    # create a new approach where we store email in UserSettings

    # Let's update UserSettings to include email
    # For now, we'll search existing settings and try to match

    # Better approach: Store email in UserSettings when we see it
    # Check if target email matches a user we know about

    # Query all user settings to find one that might match
    # This is a temporary solution - in production, we'd have proper email indexing

    # For now, let admin provide user_id OR email
    # We'll add email to UserSettings going forward

    # Check if we have a UserSettings with this email stored
    user_settings = db.query(UserSettings).filter(
        UserSettings.email == target_email
    ).first()

    if not user_settings:
        # No settings found with this email - create a placeholder
        # Note: This won't work unless user has logged in before
        # because we need their Supabase user_id
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{target_email}' not found. They need to log in at least once first."
        )

    # Get current balance
    previous_balance = user_settings.credits_balance

    # Apply the adjustment
    new_balance = previous_balance + request.amount

    # Prevent negative balance
    if new_balance < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot set negative balance. Current: {previous_balance}, Adjustment: {request.amount}"
        )

    # Update balance
    user_settings.credits_balance = new_balance
    db.commit()

    logger.info(
        f"Admin {admin.email} adjusted credits for {target_email}: "
        f"{previous_balance} -> {new_balance} ({request.amount:+d}). "
        f"Reason: {request.reason or 'No reason provided'}"
    )

    return CreditAdjustmentResponse(
        success=True,
        email=target_email,
        previous_balance=previous_balance,
        new_balance=new_balance,
        amount_adjusted=request.amount,
        reason=request.reason,
    )


@router.get("/users/search", response_model=UserSearchResponse)
async def search_users(
    email: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Search for users by email (partial match).

    - **email**: Email to search for (partial match)

    Returns list of matching users with their credit info.
    """
    query = db.query(UserSettings)

    if email:
        # Case-insensitive partial match
        query = query.filter(UserSettings.email.ilike(f"%{email}%"))

    # Limit results
    users = query.limit(20).all()

    results = [
        UserSearchResult(
            email=u.email or f"user_{u.user_id[:8]}",  # Fallback if no email
            user_id=u.user_id,
            credits_balance=u.credits_balance,
            plan_tier=u.plan_tier,
        )
        for u in users
    ]

    return UserSearchResponse(
        users=results,
        total=len(results),
    )


@router.get("/users/{user_id}/credits")
async def get_user_credits(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get a specific user's credit info by user_id.
    """
    user_settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()

    if not user_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "user_id": user_settings.user_id,
        "email": user_settings.email,
        "credits_balance": user_settings.credits_balance,
        "plan_tier": user_settings.plan_tier,
    }

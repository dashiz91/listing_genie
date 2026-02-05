"""
Credits Service

Manages user credits for AI image generation.
Similar to Krea.ai's compute units system.

Credit Costs:
- Flash model (fast): 1 credit per image
- Pro model (quality): 3 credits per image

Plans:
- Free: 50 credits/day (resets daily)
- Starter ($9/mo): 500 credits/month
- Pro ($29/mo): 2000 credits/month
- Business ($79/mo): 10000 credits/month

Admin:
- Admin emails (configured in settings) have unlimited credits
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.database import UserSettings
from app.config import settings as app_settings

logger = logging.getLogger(__name__)


# ============================================================================
# Credit Cost Configuration
# ============================================================================
#
# Pricing based on actual Gemini API costs (Jan 2025):
# - gemini-2.5-flash: $0.039/image (~4¢)
# - gemini-3-pro-image-preview: $0.134/image (~13¢, 3.4x Flash)
#
# 1 credit ≈ $0.04 (roughly Flash cost)
# ============================================================================

# Model credit costs
MODEL_COSTS = {
    # Flash models - fast & cheap (~$0.039/image = 1 credit)
    "gemini-2.0-flash": 1,
    "gemini-2.5-flash": 1,
    "gemini-3-flash-preview": 1,
    # Pro models - best quality (~$0.134/image = 3 credits)
    "gemini-2.0-pro": 3,
    "gemini-3-pro-image-preview": 3,
    # Fallback
    "default": 2,
}

# Operation credit costs (overrides model costs for specific operations)
OPERATION_COSTS = {
    "framework_analysis": 1,      # Vision/text analysis (cheap, no image gen)
    "framework_preview": 1,       # Preview image (always Flash)
    "listing_image": None,        # Uses model cost (1 for Flash, 3 for Pro)
    "aplus_module": None,         # Uses model cost (1 for Flash, 3 for Pro)
    "aplus_mobile": 1,            # Edit API transform (cheap)
    "edit_image": 1,              # Edit API (cheap)
}

# Plan configurations
# Pricing designed for ~25-30% margin when users use mostly Pro model
PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "credits_per_period": 30,
        "period": "day",  # Credits reset daily
        "features": [
            "30 credits per day",
            "~1 full listing with Flash",
            "Access to all models",
            "Great for testing",
        ],
    },
    "starter": {
        "name": "Starter",
        "price": 15,
        "credits_per_period": 300,
        "period": "month",
        "features": [
            "300 credits per month",
            "~6 full Pro listings",
            "Access to all models",
            "Commercial license",
            "Email support",
        ],
    },
    "pro": {
        "name": "Pro",
        "price": 49,
        "credits_per_period": 1000,
        "period": "month",
        "features": [
            "1,000 credits per month",
            "~21 full Pro listings",
            "Access to all models",
            "Commercial license",
            "Priority queue",
            "Priority support",
        ],
    },
    "business": {
        "name": "Business",
        "price": 149,
        "credits_per_period": 3000,
        "period": "month",
        "features": [
            "3,000 credits per month",
            "~64 full Pro listings",
            "Access to all models",
            "Commercial license",
            "Highest priority",
            "Dedicated support",
            "API access (coming soon)",
        ],
    },
}


# ============================================================================
# Credits Service
# ============================================================================

class CreditsService:
    """Service for managing user credits."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def is_admin_email(email: Optional[str]) -> bool:
        """Check if an email is in the admin list (unlimited credits)."""
        if not email:
            return False
        admin_emails_str = app_settings.admin_emails or ""
        if not admin_emails_str:
            return False
        admin_list = [e.strip().lower() for e in admin_emails_str.split(",") if e.strip()]
        return email.lower() in admin_list

    def is_admin(self, user_id: str, email: Optional[str] = None) -> bool:
        """Check if a user has admin privileges (unlimited credits)."""
        return self.is_admin_email(email)

    def get_user_settings(self, user_id: str) -> UserSettings:
        """Get or create user settings."""
        settings = self.db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()

        if not settings:
            settings = UserSettings(
                user_id=user_id,
                credits_balance=PLANS["free"]["credits_per_period"],
                plan_tier="free",
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
            logger.info(f"Created new user settings for {user_id} with {settings.credits_balance} credits")

        return settings

    def get_credit_cost(
        self,
        operation: str,
        model: Optional[str] = None,
        count: int = 1
    ) -> int:
        """
        Calculate credit cost for an operation.

        Args:
            operation: Type of operation (framework_analysis, listing_image, etc.)
            model: AI model being used (optional)
            count: Number of items being generated

        Returns:
            Total credit cost
        """
        # Check if operation has fixed cost
        op_cost = OPERATION_COSTS.get(operation)
        if op_cost is not None:
            return op_cost * count

        # Use model cost
        if model:
            model_cost = MODEL_COSTS.get(model, MODEL_COSTS["default"])
        else:
            model_cost = MODEL_COSTS["default"]

        return model_cost * count

    def check_credits(
        self,
        user_id: str,
        required_credits: int,
        email: Optional[str] = None,
    ) -> Tuple[bool, int, str]:
        """
        Check if user has enough credits.

        Args:
            user_id: The user's ID
            required_credits: Credits needed for the operation
            email: User's email (to check admin status)

        Returns:
            Tuple of (has_enough, current_balance, message)
        """
        # Admins always have enough credits
        if self.is_admin(user_id, email):
            settings = self.get_user_settings(user_id)
            return True, settings.credits_balance, "Admin: unlimited credits"

        settings = self.get_user_settings(user_id)

        # Check for daily reset (free tier)
        if settings.plan_tier == "free":
            self._check_daily_reset(settings)

        has_enough = settings.credits_balance >= required_credits

        if has_enough:
            message = f"Cost: {required_credits} credits"
        else:
            message = f"Insufficient credits. Need {required_credits}, have {settings.credits_balance}."

        return has_enough, settings.credits_balance, message

    def deduct_credits(
        self,
        user_id: str,
        amount: int,
        operation: str,
        description: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[bool, int]:
        """
        Deduct credits from user's balance.

        Args:
            user_id: The user's ID
            amount: Credits to deduct
            operation: Type of operation (for logging)
            description: Optional description
            email: User's email (to check admin status)

        Returns:
            Tuple of (success, new_balance)
        """
        settings = self.get_user_settings(user_id)

        # Admins don't have credits deducted
        if self.is_admin(user_id, email):
            logger.info(
                f"Admin user {user_id} ({email}) - skipping {amount} credit deduction for {operation}"
            )
            return True, settings.credits_balance

        # Check for daily reset (free tier)
        if settings.plan_tier == "free":
            self._check_daily_reset(settings)

        if settings.credits_balance < amount:
            logger.warning(
                f"Insufficient credits for user {user_id}: "
                f"need {amount}, have {settings.credits_balance}"
            )
            return False, settings.credits_balance

        settings.credits_balance -= amount
        self.db.commit()

        logger.info(
            f"Deducted {amount} credits from user {user_id} for {operation}. "
            f"New balance: {settings.credits_balance}"
        )

        return True, settings.credits_balance

    def check_and_deduct(
        self,
        user_id: str,
        operation: str,
        model: Optional[str] = None,
        count: int = 1,
        email: Optional[str] = None,
    ) -> Tuple[bool, int, str]:
        """
        Check if user has enough credits and deduct them in one operation.

        This is the main method to use for generation endpoints.

        Args:
            user_id: The user's ID
            operation: Type of operation (listing_image, aplus_module, etc.)
            model: AI model being used (affects cost)
            count: Number of images being generated
            email: User's email (to check admin status)

        Returns:
            Tuple of (success, new_balance, message)
        """
        # Calculate cost
        cost = self.get_credit_cost(operation, model, count)

        # Check if user has enough
        has_enough, balance, message = self.check_credits(user_id, cost, email)
        if not has_enough:
            return False, balance, message

        # Deduct credits
        success, new_balance = self.deduct_credits(
            user_id, cost, operation, email=email
        )

        if success:
            return True, new_balance, f"Deducted {cost} credits"
        else:
            return False, new_balance, "Failed to deduct credits"

    def add_credits(
        self,
        user_id: str,
        amount: int,
        reason: str
    ) -> int:
        """
        Add credits to user's balance.

        Returns:
            New balance
        """
        settings = self.get_user_settings(user_id)
        settings.credits_balance += amount
        self.db.commit()

        logger.info(
            f"Added {amount} credits to user {user_id} for {reason}. "
            f"New balance: {settings.credits_balance}"
        )

        return settings.credits_balance

    def _check_daily_reset(self, settings: UserSettings) -> None:
        """Reset daily credits for free tier if new day."""
        now = datetime.now(timezone.utc)
        last_reset = settings.updated_at

        if last_reset is None or last_reset.date() < now.date():
            # New day, reset credits
            settings.credits_balance = PLANS["free"]["credits_per_period"]
            settings.updated_at = now
            self.db.commit()
            logger.info(f"Daily credit reset for user {settings.user_id}")

    def get_plan_info(self, plan_tier: str) -> dict:
        """Get plan information."""
        return PLANS.get(plan_tier, PLANS["free"])

    def upgrade_plan(self, user_id: str, new_plan: str) -> bool:
        """
        Upgrade user's plan (called after payment).

        Returns:
            Success status
        """
        if new_plan not in PLANS:
            logger.error(f"Invalid plan: {new_plan}")
            return False

        settings = self.get_user_settings(user_id)
        old_plan = settings.plan_tier

        # Update plan
        settings.plan_tier = new_plan

        # Add new plan's credits
        plan_info = PLANS[new_plan]
        settings.credits_balance += plan_info["credits_per_period"]

        self.db.commit()

        logger.info(
            f"Upgraded user {user_id} from {old_plan} to {new_plan}. "
            f"Added {plan_info['credits_per_period']} credits."
        )

        return True


# ============================================================================
# Helper Functions
# ============================================================================

def get_credits_service(db: Session) -> CreditsService:
    """Factory function for credits service."""
    return CreditsService(db)


def estimate_generation_cost(
    num_listing_images: int = 6,
    num_aplus_modules: int = 6,
    include_mobile: bool = True,
    num_previews: int = 4,
    model: str = "gemini-3-pro-image-preview"
) -> dict:
    """
    Estimate total credit cost for a full generation.

    Full listing with Pro model:
    - Framework analysis: 1 credit
    - 4 previews: 4 credits (Flash)
    - 6 listing images: 18 credits (Pro @ 3 each)
    - 6 A+ desktop: 18 credits (Pro @ 3 each)
    - 6 A+ mobile: 6 credits (edit @ 1 each)
    - TOTAL: 47 credits

    Full listing with Flash model:
    - Framework analysis: 1 credit
    - 4 previews: 4 credits
    - 6 listing images: 6 credits
    - 6 A+ desktop: 6 credits
    - 6 A+ mobile: 6 credits
    - TOTAL: 23 credits

    Returns:
        Dict with breakdown and total
    """
    model_cost = MODEL_COSTS.get(model, MODEL_COSTS["default"])

    # Framework analysis (1 credit, text/vision)
    analysis_cost = OPERATION_COSTS["framework_analysis"]

    # Framework previews (always 1 credit each, uses Flash)
    preview_cost = num_previews * OPERATION_COSTS["framework_preview"]

    # Listing images (model-dependent: 1 for Flash, 3 for Pro)
    listing_cost = num_listing_images * model_cost

    # A+ modules desktop (model-dependent: 1 for Flash, 3 for Pro)
    aplus_cost = num_aplus_modules * model_cost

    # A+ mobile transforms (always 1 credit each, edit API)
    mobile_cost = num_aplus_modules * OPERATION_COSTS["aplus_mobile"] if include_mobile else 0

    total = analysis_cost + preview_cost + listing_cost + aplus_cost + mobile_cost

    return {
        "framework_analysis": analysis_cost,
        "framework_previews": preview_cost,
        "listing_images": listing_cost,
        "aplus_desktop": aplus_cost,
        "aplus_mobile": mobile_cost,
        "total": total,
        "model": model,
        "model_cost_per_image": model_cost,
    }

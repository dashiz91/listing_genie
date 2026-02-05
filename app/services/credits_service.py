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
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.database import UserSettings

logger = logging.getLogger(__name__)


# ============================================================================
# Credit Cost Configuration
# ============================================================================

# Model credit costs
MODEL_COSTS = {
    "gemini-2.0-flash": 1,        # Fast, cheap
    "gemini-3-flash-preview": 1,  # Fast, cheap (current flash)
    "gemini-2.0-pro": 3,          # Quality, expensive
    "gemini-3-pro-image-preview": 3,  # Quality (current pro)
    "default": 2,                 # Fallback
}

# Operation credit costs (overrides model costs for specific operations)
OPERATION_COSTS = {
    "framework_analysis": 2,      # Vision analysis (cheap)
    "framework_preview": 1,       # Single preview image
    "listing_image": None,        # Uses model cost
    "aplus_module": None,         # Uses model cost
    "aplus_mobile": 1,            # Edit operation (cheap)
    "edit_image": 1,              # Edit operation (cheap)
}

# Plan configurations
PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "credits_per_period": 50,
        "period": "day",  # Credits reset daily
        "features": [
            "50 credits per day",
            "Access to Flash model",
            "Basic support",
        ],
    },
    "starter": {
        "name": "Starter",
        "price": 9,
        "credits_per_period": 500,
        "period": "month",
        "features": [
            "500 credits per month",
            "Access to all models",
            "Commercial license",
            "Priority support",
        ],
    },
    "pro": {
        "name": "Pro",
        "price": 29,
        "credits_per_period": 2000,
        "period": "month",
        "features": [
            "2,000 credits per month",
            "Access to all models",
            "Commercial license",
            "Priority queue",
            "Premium support",
        ],
    },
    "business": {
        "name": "Business",
        "price": 79,
        "credits_per_period": 10000,
        "period": "month",
        "features": [
            "10,000 credits per month",
            "Access to all models",
            "Commercial license",
            "Highest priority",
            "Dedicated support",
            "Custom integrations",
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
        required_credits: int
    ) -> Tuple[bool, int, str]:
        """
        Check if user has enough credits.

        Returns:
            Tuple of (has_enough, current_balance, message)
        """
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
        description: Optional[str] = None
    ) -> Tuple[bool, int]:
        """
        Deduct credits from user's balance.

        Returns:
            Tuple of (success, new_balance)
        """
        settings = self.get_user_settings(user_id)

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
    num_aplus_modules: int = 5,
    include_mobile: bool = True,
    model: str = "gemini-3-pro-image-preview"
) -> dict:
    """
    Estimate total credit cost for a full generation.

    Returns:
        Dict with breakdown and total
    """
    model_cost = MODEL_COSTS.get(model, MODEL_COSTS["default"])

    # Framework analysis + 4 previews
    framework_cost = OPERATION_COSTS["framework_analysis"] + (4 * OPERATION_COSTS["framework_preview"])

    # Listing images
    listing_cost = num_listing_images * model_cost

    # A+ modules (desktop)
    aplus_cost = num_aplus_modules * model_cost

    # A+ mobile transforms
    mobile_cost = num_aplus_modules * OPERATION_COSTS["aplus_mobile"] if include_mobile else 0

    total = framework_cost + listing_cost + aplus_cost + mobile_cost

    return {
        "framework_analysis": framework_cost,
        "listing_images": listing_cost,
        "aplus_desktop": aplus_cost,
        "aplus_mobile": mobile_cost,
        "total": total,
        "model": model,
        "model_cost_per_image": model_cost,
    }

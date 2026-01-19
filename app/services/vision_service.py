"""
Unified Vision Service - Principal Designer AI

Automatically selects the best vision provider based on configuration.
Supports both Gemini (recommended - 10x cheaper) and OpenAI (fallback).

COST COMPARISON (December 2025):
┌─────────────────┬────────────┬─────────────┬───────────────┐
│ Provider        │ Input/1M   │ Output/1M   │ vs GPT-4o     │
├─────────────────┼────────────┼─────────────┼───────────────┤
│ GPT-4o          │ $5.00      │ $15.00      │ baseline      │
│ Gemini 3 Flash  │ $0.50      │ $3.00       │ 10x/5x cheaper│
│ Gemini 2.0 Flash│ $0.10      │ $0.40       │ 50x/37x cheaper│
└─────────────────┴────────────┴─────────────┴───────────────┘

Set VISION_PROVIDER=gemini in .env to use Gemini (default)
Set VISION_PROVIDER=openai to use OpenAI
"""

import logging
from typing import Optional, List, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)


class VisionService:
    """
    Unified Vision Service that delegates to Gemini or OpenAI.

    This is the recommended way to use the Principal Designer AI.
    It automatically selects the best provider based on configuration.
    """

    def __init__(self):
        """Initialize the appropriate vision provider"""
        self.provider = settings.vision_provider.lower()

        if self.provider == "gemini":
            from app.services.gemini_vision_service import GeminiVisionService
            self._service = GeminiVisionService()
            logger.info("Vision Service initialized with Gemini (10x cost savings)")
        elif self.provider == "openai":
            from app.services.openai_vision_service import OpenAIVisionService
            self._service = OpenAIVisionService()
            logger.info("Vision Service initialized with OpenAI")
        else:
            # Default to Gemini for cost savings
            from app.services.gemini_vision_service import GeminiVisionService
            self._service = GeminiVisionService()
            logger.warning(f"Unknown provider '{self.provider}', defaulting to Gemini")
            self.provider = "gemini"

    async def generate_frameworks(
        self,
        product_image_path: str,
        product_name: str,
        brand_name: Optional[str] = None,
        features: Optional[List[str]] = None,
        target_audience: Optional[str] = None,
        primary_color: Optional[str] = None,
        additional_image_paths: Optional[List[str]] = None,
        color_mode: Optional[str] = None,
        locked_colors: Optional[List[str]] = None,
        style_reference_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate 4 unique design frameworks by ANALYZING the product image(s).

        Delegates to the configured provider (Gemini or OpenAI).
        Now supports multiple images so AI Designer can see the product from all angles.

        Color Mode Options:
        - ai_decides: AI picks all colors based on product (default)
        - suggest_primary: User suggests primary, AI builds rest of palette
        - locked_palette: User locks exact colors, AI must use them in ALL 4 frameworks

        Style Reference:
        - If provided, AI sees the style image and extracts colors/style from it
        """
        image_count = 1 + (len(additional_image_paths) if additional_image_paths else 0)
        style_info = f", style_ref=YES" if style_reference_path else ""
        logger.info(f"[{self.provider.upper()}] Generating frameworks for: {product_name} ({image_count} images, color_mode={color_mode or 'ai_decides'}{style_info})")

        result = await self._service.generate_frameworks(
            product_image_path=product_image_path,
            product_name=product_name,
            brand_name=brand_name,
            features=features,
            target_audience=target_audience,
            primary_color=primary_color,
            additional_image_paths=additional_image_paths,
            color_mode=color_mode,
            locked_colors=locked_colors,
            style_reference_path=style_reference_path,
        )

        # Add provider info to result
        result['_vision_provider'] = self.provider

        return result

    async def generate_image_prompts(
        self,
        framework: Dict[str, Any],
        product_name: str,
        product_description: str = "",
        features: Optional[List[str]] = None,
        target_audience: Optional[str] = None,
        global_note: Optional[str] = None,
        has_style_reference: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        STEP 2: Generate 5 detailed image prompts for the SELECTED framework.

        Delegates to the configured provider (Gemini or OpenAI).

        Args:
            global_note: User's global instructions - AI Designer interprets
                         these differently for each of the 5 image types.
            has_style_reference: Whether user provided a style reference image.
        """
        logger.info(f"[{self.provider.upper()}] Generating image prompts for: {framework.get('framework_name')}")
        if global_note:
            logger.info(f"[{self.provider.upper()}] Including global note for AI interpretation")
        if has_style_reference:
            logger.info(f"[{self.provider.upper()}] User provided style reference - prompts will include style match instructions")

        return await self._service.generate_image_prompts(
            framework=framework,
            product_name=product_name,
            product_description=product_description,
            features=features,
            target_audience=target_audience,
            global_note=global_note,
            has_style_reference=has_style_reference,
        )

    def framework_to_prompt(self, framework: Dict[str, Any], image_type: str) -> str:
        """
        Convert a design framework to a complete prompt for image generation.

        This method is model-agnostic - it just builds the prompt string.
        Uses the OpenAI service's implementation since it's shared logic.
        """
        # Import the method from OpenAI service (it's model-agnostic)
        from app.services.openai_vision_service import OpenAIVisionService
        temp_service = OpenAIVisionService.__new__(OpenAIVisionService)
        return temp_service.framework_to_prompt(framework, image_type)

    def health_check(self) -> dict:
        """Check health of the vision service"""
        base_health = self._service.health_check()
        base_health['active_provider'] = self.provider
        return base_health


def get_vision_service() -> VisionService:
    """Dependency injection helper - returns unified vision service"""
    return VisionService()

"""
Unified Vision Service - Principal Designer AI.

Runtime default and recommendation: Gemini.
OpenAI vision remains in codebase only as a deprecated emergency path and is
ignored unless explicitly enabled with ALLOW_OPENAI_VISION=true.
"""

import logging
from typing import Optional, List, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)


class VisionService:
    """
    Unified Vision Service with Gemini-first provider selection.

    OpenAI vision is deprecated and opt-in only.
    """

    def __init__(self):
        """Initialize vision provider (Gemini by default)."""
        requested_provider = (settings.vision_provider or "gemini").strip().lower()
        self.requested_provider = requested_provider
        self.provider = "gemini"

        from app.services.gemini_vision_service import GeminiVisionService
        self._service = GeminiVisionService()

        if requested_provider == "openai":
            if settings.allow_openai_vision:
                from app.services.openai_vision_service import OpenAIVisionService
                self._service = OpenAIVisionService()
                self.provider = "openai"
                logger.warning(
                    "VISION_PROVIDER=openai is deprecated and enabled only for emergency use."
                )
            else:
                logger.warning(
                    "VISION_PROVIDER=openai requested but OpenAI vision is disabled. "
                    "Using Gemini. Set ALLOW_OPENAI_VISION=true only for emergency opt-in."
                )
        elif requested_provider != "gemini":
            logger.warning(
                f"Unknown VISION_PROVIDER '{requested_provider}'. Using Gemini."
            )
        else:
            logger.info("Vision Service initialized with Gemini")

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
        Generate frameworks by analyzing product image(s).

        Delegates to the active provider (Gemini by default).
        """
        image_count = 1 + (len(additional_image_paths) if additional_image_paths else 0)
        style_info = ", style_ref=YES" if style_reference_path else ""
        logger.info(
            f"[{self.provider.upper()}] Generating frameworks for: {product_name} "
            f"({image_count} images, color_mode={color_mode or 'ai_decides'}{style_info})"
        )

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

        result["_vision_provider"] = self.provider
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
        brand_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate detailed image prompts for a selected framework.

        Delegates to the active provider (Gemini by default).
        """
        logger.info(
            f"[{self.provider.upper()}] Generating image prompts for: {framework.get('framework_name')}"
        )
        if global_note:
            logger.info(f"[{self.provider.upper()}] Including global note for AI interpretation")
        if has_style_reference:
            logger.info(
                f"[{self.provider.upper()}] User provided style reference - prompts include style-match instructions"
            )

        return await self._service.generate_image_prompts(
            framework=framework,
            product_name=product_name,
            product_description=product_description,
            features=features,
            target_audience=target_audience,
            global_note=global_note,
            has_style_reference=has_style_reference,
            brand_name=brand_name,
        )

    async def enhance_prompt_with_feedback(
        self,
        original_prompt: str,
        user_feedback: str,
        image_type: str,
        framework: Optional[Dict[str, Any]] = None,
        product_analysis: Optional[str] = None,
        structural_context: str = "",
    ) -> Dict[str, Any]:
        """
        Rewrite a prompt based on user feedback while preserving context.

        Delegates to the active provider (Gemini by default).
        """
        logger.info(
            f"[{self.provider.upper()}] Enhancing prompt for {image_type} based on user feedback"
        )
        return await self._service.enhance_prompt_with_feedback(
            original_prompt=original_prompt,
            user_feedback=user_feedback,
            image_type=image_type,
            framework=framework,
            product_analysis=product_analysis,
            structural_context=structural_context,
        )

    async def plan_edit_instructions(
        self,
        source_image_path: str,
        user_feedback: str,
        image_type: str,
        original_prompt: Optional[str] = None,
        framework: Optional[Dict[str, Any]] = None,
        product_analysis: Optional[str] = None,
        reference_image_paths: Optional[List[str]] = None,
        structural_context: str = "",
    ) -> Dict[str, Any]:
        """
        Generate concise edit instructions for image-edit API calls.

        Delegates to the active provider (Gemini by default).
        """
        logger.info(
            f"[{self.provider.upper()}] Planning edit instructions for {image_type}"
        )
        return await self._service.plan_edit_instructions(
            source_image_path=source_image_path,
            user_feedback=user_feedback,
            image_type=image_type,
            original_prompt=original_prompt,
            framework=framework,
            product_analysis=product_analysis,
            reference_image_paths=reference_image_paths,
            structural_context=structural_context,
        )

    def framework_to_prompt(self, framework: Dict[str, Any], image_type: str) -> str:
        """
        Convert a design framework to a complete prompt for image generation.

        This method is model-agnostic - it just builds the prompt string.
        """
        return self._service.framework_to_prompt(framework, image_type)

    def health_check(self) -> dict:
        """Check health of the vision service."""
        base_health = self._service.health_check()
        base_health["active_provider"] = self.provider
        base_health["requested_provider"] = self.requested_provider
        base_health["openai_vision_allowed"] = settings.allow_openai_vision
        return base_health


def get_vision_service() -> VisionService:
    """Dependency injection helper - returns unified vision service."""
    return VisionService()

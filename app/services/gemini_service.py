"""
Gemini API Service for Image Generation
Based on: gemini_mcp/src/tools/image_generator.py
"""
from google import genai
from google.genai import types
from PIL import Image as PILImage
from pathlib import Path
from typing import Optional, List, Tuple, TYPE_CHECKING
from io import BytesIO
import asyncio
import logging
from app.config import settings

if TYPE_CHECKING:
    from app.services.supabase_storage_service import SupabaseStorageService

logger = logging.getLogger(__name__)

# Storage service singleton for loading images
_storage_service: Optional["SupabaseStorageService"] = None


def _get_storage_service() -> "SupabaseStorageService":
    """Get or create the storage service singleton"""
    global _storage_service
    if _storage_service is None:
        from app.services.supabase_storage_service import SupabaseStorageService
        _storage_service = SupabaseStorageService()
    return _storage_service


def _load_image_from_path(path: str) -> PILImage.Image:
    """
    Load an image from a path (either local or Supabase).

    Args:
        path: File path - either local or supabase:// URL

    Returns:
        PIL Image object
    """
    if path.startswith("supabase://"):
        storage = _get_storage_service()
        return storage.load_image(path)
    else:
        # Local file path (for backwards compatibility during transition)
        return PILImage.open(path)


class GeminiService:
    """Wrapper for Gemini API image generation with reference image support"""

    def __init__(self, api_key: str = None):
        """
        Initialize Gemini client

        Args:
            api_key: Optional API key override. Defaults to settings.
        """
        self.api_key = api_key or settings.gemini_api_key
        self.model = settings.gemini_model  # gemini-3-pro-image-preview

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set - Gemini features will be unavailable")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    async def generate_image(
        self,
        prompt: str,
        reference_image_path: Optional[str] = None,
        reference_image_paths: Optional[List[str]] = None,
        named_images: Optional[List[Tuple[str, str]]] = None,
        aspect_ratio: str = "1:1",
        image_size: str = "1K",
        max_retries: int = 3
    ) -> Optional[PILImage.Image]:
        """
        Generate an image using Gemini with optional reference product image(s).

        Args:
            prompt: The generation prompt including style and context
            reference_image_path: Single reference image path (backwards compat)
            reference_image_paths: List of reference image paths (unnamed)
            named_images: List of (label, path) tuples — images are interleaved with
                          text labels so the model can reference them by name.
                          When provided, reference_image_path(s) are ignored.
            aspect_ratio: Output aspect ratio. Supported: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
            image_size: Output resolution. "1K" ($0.134), "2K" ($0.134), "4K" ($0.24). Default 1K for cost savings.
            max_retries: Number of retry attempts on failure

        Returns:
            PIL Image object or None if generation failed
        """
        if not self.client:
            raise ValueError("Gemini client not initialized - check GEMINI_API_KEY")

        contents = []

        if named_images:
            # New path: interleave text labels with images, then prompt last
            for label, path in named_images:
                try:
                    img = _load_image_from_path(path)
                    contents.append(f"{label}:")
                    contents.append(img)
                except Exception as e:
                    logger.error(f"Error loading named image '{label}' from '{path}': {e}")
                    raise ValueError(f"Failed to load named image '{label}': {path}")
            contents.append(prompt)
        else:
            # Legacy path: prompt first, then unnamed images
            contents = [prompt]

            # Handle single path (backwards compat)
            if reference_image_path and not reference_image_paths:
                reference_image_paths = [reference_image_path]

            # Add reference images if provided
            if reference_image_paths:
                for ref_path in reference_image_paths:
                    try:
                        reference_image = _load_image_from_path(ref_path)
                        contents.append(reference_image)
                    except Exception as e:
                        logger.error(f"Error loading reference image '{ref_path}': {e}")
                        raise ValueError(f"Failed to load reference image: {ref_path}")

        # === COMPREHENSIVE GEMINI API LOGGING ===
        logger.info("=" * 80)
        logger.info("[GEMINI IMAGE GEN] === FULL REQUEST DETAILS ===")
        logger.info(f"[GEMINI IMAGE GEN] Model: {self.model}")
        logger.info(f"[GEMINI IMAGE GEN] Aspect Ratio: {aspect_ratio}")
        logger.info(f"[GEMINI IMAGE GEN] Image Size: {image_size}")
        logger.info(f"[GEMINI IMAGE GEN] Max Retries: {max_retries}")
        logger.info(f"[GEMINI IMAGE GEN] Response Modalities: ['Image']")
        logger.info(f"[GEMINI IMAGE GEN] Named Images: {bool(named_images)}")
        logger.info("-" * 40)
        logger.info("[GEMINI IMAGE GEN] PROMPT TEXT:")
        logger.info("-" * 40)
        prompt_lines = prompt.split('\n')
        for i, line in enumerate(prompt_lines):
            logger.info(f"[PROMPT L{i+1:03d}] {line}")
        logger.info("-" * 40)
        if named_images:
            logger.info(f"[GEMINI IMAGE GEN] NAMED IMAGES ({len(named_images)} total):")
            for label, path in named_images:
                logger.info(f"[GEMINI IMAGE GEN]   {label}: {path}")
        else:
            logger.info(f"[GEMINI IMAGE GEN] REFERENCE IMAGES ({len(reference_image_paths) if reference_image_paths else 0} total):")
            if reference_image_paths:
                for i, ref_path in enumerate(reference_image_paths):
                    logger.info(f"[GEMINI IMAGE GEN]   Image {i+1}: {ref_path}")
            else:
                logger.info("[GEMINI IMAGE GEN]   (No reference images)")
        logger.info("=" * 80)

        for attempt in range(max_retries):
            try:
                logger.info(f"[GEMINI IMAGE GEN] Generating image (attempt {attempt + 1}/{max_retries})")

                # Use ASYNC API for parallel generation (aio = async io)
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['Image'],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                            image_size=image_size
                        )
                    )
                )

                # Extract generated image from response
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        image = PILImage.open(BytesIO(part.inline_data.data))
                        logger.info(f"Image generated successfully: {image.size}")
                        return image

                logger.warning("No image in response")
                return None

            except Exception as e:
                logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

        return None

    async def generate_image_from_pil(
        self,
        prompt: str,
        reference_image: PILImage.Image,
        aspect_ratio: str = "1:1",
        image_size: str = "1K",
        max_retries: int = 3
    ) -> Optional[PILImage.Image]:
        """
        Generate an image using Gemini with a PIL Image reference.

        Args:
            prompt: The generation prompt
            reference_image: PIL Image object as reference
            aspect_ratio: Output aspect ratio
            image_size: Output resolution ("1K", "2K", "4K"). Default 1K for cost savings.
            max_retries: Number of retry attempts

        Returns:
            PIL Image object or None if generation failed
        """
        if not self.client:
            raise ValueError("Gemini client not initialized - check GEMINI_API_KEY")

        # Prepare contents
        contents = [prompt, reference_image]

        for attempt in range(max_retries):
            try:
                logger.info(f"Generating image from PIL (attempt {attempt + 1}/{max_retries})")

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['Image'],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                            image_size=image_size
                        )
                    )
                )

                # Extract generated image
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        image = PILImage.open(BytesIO(part.inline_data.data))
                        logger.info(f"Image generated successfully: {image.size}")
                        return image

                return None

            except Exception as e:
                logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)

        return None

    async def edit_image(
        self,
        source_image_path: str,
        edit_instructions: str,
        aspect_ratio: str = "1:1",
        image_size: str = "1K",
        max_retries: int = 3
    ) -> Optional[PILImage.Image]:
        """
        Edit an existing image using Gemini's image editing capability.

        Unlike generate_image (which uses product photos as reference to create new images),
        this takes an EXISTING generated image and modifies it based on instructions.

        Args:
            source_image_path: Path to the image to edit
            edit_instructions: What to change (e.g., "Change the headline to 'New Text'")
            aspect_ratio: Output aspect ratio (should match source)
            image_size: Output resolution ("1K", "2K", "4K"). Default 1K for cost savings.
            max_retries: Number of retry attempts

        Returns:
            PIL Image object with edits applied, or None if failed
        """
        if not self.client:
            raise ValueError("Gemini client not initialized - check GEMINI_API_KEY")

        # Build edit-focused prompt
        prompt = f"""Edit this image. {edit_instructions}

IMPORTANT: Keep all other elements exactly the same.
Only modify what was specifically requested.
Maintain the same style, colors, layout, composition, and any text/graphics not mentioned."""

        # Load the source image as the ONLY reference
        try:
            source_image = _load_image_from_path(source_image_path)
            logger.info(f"Loaded source image for editing: {source_image.size}")
        except Exception as e:
            logger.error(f"Error loading source image '{source_image_path}': {e}")
            raise ValueError(f"Failed to load source image: {source_image_path}")

        contents = [prompt, source_image]

        # === COMPREHENSIVE GEMINI EDIT API LOGGING ===
        logger.info("=" * 80)
        logger.info("[GEMINI EDIT] === FULL EDIT REQUEST DETAILS ===")
        logger.info(f"[GEMINI EDIT] Model: {self.model}")
        logger.info(f"[GEMINI EDIT] Aspect Ratio: {aspect_ratio}")
        logger.info(f"[GEMINI EDIT] Image Size: {image_size}")
        logger.info(f"[GEMINI EDIT] Source Image: {source_image_path}")
        logger.info(f"[GEMINI EDIT] Source Image Size: {source_image.size}")
        logger.info("-" * 40)
        logger.info("[GEMINI EDIT] EDIT INSTRUCTIONS:")
        logger.info(f"[GEMINI EDIT] {edit_instructions}")
        logger.info("-" * 40)
        logger.info("[GEMINI EDIT] FULL PROMPT (with wrapper):")
        for i, line in enumerate(prompt.split('\n')):
            logger.info(f"[EDIT PROMPT L{i+1:03d}] {line}")
        logger.info("=" * 80)

        for attempt in range(max_retries):
            try:
                logger.info(f"[GEMINI EDIT] Editing image (attempt {attempt + 1}/{max_retries})")

                # Use ASYNC API for editing
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['Image'],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                            image_size=image_size
                        )
                    )
                )

                # Extract edited image from response
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        image = PILImage.open(BytesIO(part.inline_data.data))
                        logger.info(f"Image edited successfully: {image.size}")
                        return image

                logger.warning("No image in edit response")
                return None

            except Exception as e:
                logger.error(f"Edit attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

        return None

    async def generate_text_with_images(
        self,
        prompt: str,
        image_paths: List[str],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> str:
        """
        Generate text using Gemini with image context (for Art Director).

        Loads images from paths and includes them alongside the text prompt,
        allowing the AI to SEE the product while planning.

        Args:
            prompt: The generation prompt
            image_paths: List of image paths (local or supabase://)
            max_tokens: Maximum output tokens
            temperature: Creativity level (0-1)
            max_retries: Number of retry attempts

        Returns:
            Generated text string
        """
        if not self.client:
            raise ValueError("Gemini client not initialized - check GEMINI_API_KEY")

        text_model = "gemini-2.0-flash"

        # Build contents: prompt + images
        contents: list = [prompt]
        for img_path in image_paths:
            try:
                img = _load_image_from_path(img_path)
                contents.append(img)
            except Exception as e:
                logger.warning(f"Failed to load image for text generation: {img_path}: {e}")

        for attempt in range(max_retries):
            try:
                logger.info(f"Generating text with {len(image_paths)} images (attempt {attempt + 1}/{max_retries})")

                response = await self.client.aio.models.generate_content(
                    model=text_model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    )
                )

                if response.candidates and response.candidates[0].content.parts:
                    text = response.candidates[0].content.parts[0].text
                    logger.info(f"Text with images generated successfully: {len(text)} chars")
                    return text

                logger.warning("No text in response")
                return ""

            except Exception as e:
                logger.error(f"Text+image generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)

        return ""

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> str:
        """
        Generate text using Gemini (for Principal Designer AI).

        Args:
            prompt: The generation prompt
            max_tokens: Maximum output tokens
            temperature: Creativity level (0-1)
            max_retries: Number of retry attempts

        Returns:
            Generated text string
        """
        if not self.client:
            raise ValueError("Gemini client not initialized - check GEMINI_API_KEY")

        # Use a text-focused model for design framework generation
        text_model = "gemini-2.0-flash"  # Fast and good for structured output

        for attempt in range(max_retries):
            try:
                logger.info(f"Generating text (attempt {attempt + 1}/{max_retries})")

                response = self.client.models.generate_content(
                    model=text_model,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    )
                )

                # Extract text from response
                if response.candidates and response.candidates[0].content.parts:
                    text = response.candidates[0].content.parts[0].text
                    logger.info(f"Text generated successfully: {len(text)} chars")
                    return text

                logger.warning("No text in response")
                return ""

            except Exception as e:
                logger.error(f"Text generation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)

        return ""

    def health_check(self) -> dict:
        """
        Verify API connection is working

        Returns:
            Dict with status and details
        """
        if not self.api_key:
            return {
                "status": "not_configured",
                "message": "GEMINI_API_KEY not set"
            }

        if not self.client:
            return {
                "status": "error",
                "message": "Client not initialized"
            }

        return {
            "status": "configured",
            "model": self.model
        }


def get_gemini_service() -> GeminiService:
    """Dependency injection helper"""
    return GeminiService()

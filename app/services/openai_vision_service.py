"""
OpenAI Vision Service - Principal Designer AI

Uses GPT-4o Vision to ANALYZE the actual product image and generate
intelligent, tailored design frameworks.

This is the BRAIN that SEES the product before designing for it.
"""

import base64
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from openai import AsyncOpenAI

from app.config import settings
from app.prompts.ai_designer import (
    PRINCIPAL_DESIGNER_VISION_PROMPT,
    GENERATE_IMAGE_PROMPTS_PROMPT,
    ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT,
    GLOBAL_NOTE_INSTRUCTIONS,
    STYLE_REFERENCE_INSTRUCTIONS,
)

if TYPE_CHECKING:
    from app.services.supabase_storage_service import SupabaseStorageService

logger = logging.getLogger(__name__)

# Storage service singleton for loading images from Supabase
_storage_service: Optional["SupabaseStorageService"] = None


def _get_storage_service() -> "SupabaseStorageService":
    """Get or create the storage service singleton"""
    global _storage_service
    if _storage_service is None:
        from app.services.supabase_storage_service import SupabaseStorageService
        _storage_service = SupabaseStorageService()
    return _storage_service


def _image_path_exists(path: str) -> bool:
    """
    Check if an image path exists (handles both local paths and Supabase URLs).

    For Supabase URLs (supabase://...), we trust they exist since they come from
    our upload endpoint. For local paths, we check if the file exists.
    """
    if path.startswith("supabase://"):
        # Trust Supabase URLs - they came from our upload endpoint
        return True
    else:
        # Local file path - check if it exists
        return Path(path).exists()


def _load_image_bytes(image_path: str) -> bytes:
    """Load image file as bytes (from local path or Supabase)"""
    if image_path.startswith("supabase://"):
        storage = _get_storage_service()
        return storage.get_file_bytes(image_path)
    else:
        # Local file path (for backwards compatibility)
        with open(image_path, "rb") as f:
            return f.read()

# NOTE: All AI Designer prompts live in app/prompts/ai_designer.py
# Dead copies that used to live here have been removed (they shadowed imports).



class OpenAIVisionService:
    """
    Principal Designer AI using OpenAI GPT-4o Vision.

    SEES the actual product image and generates intelligent,
    tailored design frameworks based on visual analysis.
    """

    def __init__(self, api_key: str = None):
        """Initialize OpenAI client"""
        self.api_key = api_key or settings.openai_api_key
        self.model = settings.openai_vision_model

        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set - Vision features unavailable")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API (handles both local paths and Supabase URLs)"""
        image_bytes = _load_image_bytes(image_path)
        return base64.b64encode(image_bytes).decode("utf-8")

    def _get_image_media_type(self, image_path: str) -> str:
        """Get media type from file extension"""
        ext = Path(image_path).suffix.lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return media_types.get(ext, "image/jpeg")

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

        Args:
            product_image_path: Path to the primary product image
            product_name: The product title
            brand_name: Optional brand name
            features: List of key features
            target_audience: Target audience description
            primary_color: Optional preferred primary color (hex)
            additional_image_paths: Optional list of additional product images
            color_mode: How to handle colors (ai_decides, suggest_primary, locked_palette)
            locked_colors: List of hex colors to use when color_mode is locked_palette
            style_reference_path: Optional style reference image - AI extracts colors/style from this

        Returns:
            Dict with 'product_analysis', 'frameworks' list and metadata
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized - check OPENAI_API_KEY")

        # Validate primary image exists (handles both local paths and Supabase URLs)
        if not _image_path_exists(product_image_path):
            raise ValueError(f"Product image not found: {product_image_path}")

        # Build list of all images to send
        all_image_paths = [product_image_path]
        style_ref_index = None

        if additional_image_paths:
            for path in additional_image_paths:
                if _image_path_exists(path):
                    all_image_paths.append(path)
                else:
                    logger.warning(f"Additional image not found, skipping: {path}")

        # Add style reference if provided
        if style_reference_path and _image_path_exists(style_reference_path):
            all_image_paths.append(style_reference_path)
            style_ref_index = len(all_image_paths)
            logger.info(f"[OpenAI] Including style reference as Image #{style_ref_index}")
        elif style_reference_path:
            logger.warning(f"Style reference not found, skipping: {style_reference_path}")

        # Encode all images
        encoded_images = []
        for i, img_path in enumerate(all_image_paths):
            base64_image = self._encode_image(img_path)
            media_type = self._get_image_media_type(img_path)
            # Determine label based on image type
            if i == 0:
                label = "PRIMARY product image"
            elif style_ref_index and i + 1 == style_ref_index:
                label = "STYLE REFERENCE - Extract colors and visual style from this!"
            else:
                label = f"Additional product image {i}"
            encoded_images.append({
                "base64": base64_image,
                "media_type": media_type,
                "label": label,
            })

        logger.info(f"Analyzing {len(encoded_images)} product image(s) for framework generation")

        # Build the prompt
        prompt = PRINCIPAL_DESIGNER_VISION_PROMPT.format(
            product_name=product_name,
            brand_name=brand_name or "Not specified",
            features=", ".join(features) if features else "Not specified",
            target_audience=target_audience or "General consumers",
            primary_color=primary_color or "AI to determine based on product image",
        )

        # Handle color mode - add instructions based on mode
        color_mode_text = ""
        effective_color_mode = color_mode or "ai_decides"

        # === DETAILED COLOR MODE LOGGING ===
        logger.info("=" * 60)
        logger.info("[COLOR MODE DEBUG] Starting color mode processing")
        logger.info(f"[COLOR MODE DEBUG] Received color_mode parameter: {color_mode}")
        logger.info(f"[COLOR MODE DEBUG] Effective color_mode: {effective_color_mode}")
        logger.info(f"[COLOR MODE DEBUG] Received locked_colors: {locked_colors}")
        logger.info(f"[COLOR MODE DEBUG] Received primary_color: {primary_color}")
        logger.info("=" * 60)

        if effective_color_mode == "locked_palette" and locked_colors:
            # LOCKED MODE: AI MUST use exactly these colors in ALL 4 frameworks
            color_list = ", ".join(locked_colors)
            num_locked = len(locked_colors)
            logger.info(f"[COLOR MODE DEBUG] LOCKED PALETTE MODE ACTIVATED!")
            logger.info(f"[COLOR MODE DEBUG] Colors to lock: {color_list}")
            logger.info(f"[COLOR MODE DEBUG] Number of locked colors: {num_locked}")

            # Build color assignment rules based on how many colors are locked
            color_mode_text = f"""

=== MANDATORY COLOR PALETTE (LOCKED) ===
CRITICAL: The user has LOCKED exactly {num_locked} color(s). You MUST use ONLY these colors.
Do NOT add additional colors. Do NOT suggest alternatives. Do NOT be creative with colors.

LOCKED COLORS: {color_list}

COLOR ASSIGNMENT (STRICT):
"""
            if num_locked >= 1:
                color_mode_text += f"- PRIMARY color: {locked_colors[0]} (MANDATORY - use this exact hex)\n"
            if num_locked >= 2:
                color_mode_text += f"- SECONDARY color: {locked_colors[1]} (MANDATORY - use this exact hex)\n"
            if num_locked >= 3:
                color_mode_text += f"- ACCENT color: {locked_colors[2]} (MANDATORY - use this exact hex)\n"

            # Smart accent derivation based on number of locked colors
            if num_locked == 1:
                color_mode_text += """
USER PROVIDED ONLY 1 COLOR:
- Use it as PRIMARY
- For SECONDARY: Derive using color theory (complementary, analogous, or a shade)
- For ACCENT: Look at the product image - if there's a prominent color on the product
  (like on the label, cap, or packaging), use that. Otherwise derive from primary.
"""
            elif num_locked == 2:
                color_mode_text += """
USER PROVIDED ONLY 2 COLORS:
- Use them as PRIMARY and SECONDARY (exactly as provided)
- For ACCENT: You have two options (pick the best one):

  OPTION A - PRODUCT-INSPIRED: Look at the actual product image. If there's a third
  prominent color ON the product itself (label accent, cap color, design element),
  use that as the accent. This creates cohesion between the listing and product.

  OPTION B - COLOR THEORY DERIVED: If the product doesn't have an obvious third color,
  derive the accent using color theory from the two locked colors:
  - A lighter or darker shade of the primary
  - A tint between the two colors
  - A warm/cool complement that harmonizes

  DO NOT randomly pick an unrelated color. The accent must feel intentional and cohesive.
"""

            color_mode_text += f"""
ADDITIONAL RULES:
- text_dark and text_light: You may generate these for readability
- ALL 4 frameworks MUST have IDENTICAL color hex codes for primary/secondary/accent
- The frameworks should differ in typography, layout, voice - NOT in colors

OUTPUT VERIFICATION:
- colors[0].hex MUST be: {locked_colors[0]}
"""
            if num_locked >= 2:
                color_mode_text += f"- colors[1].hex MUST be: {locked_colors[1]}\n"
            if num_locked >= 3:
                color_mode_text += f"- colors[2].hex MUST be: {locked_colors[2]}\n"

            color_mode_text += "\nThis is NOT a suggestion. These colors are MANDATORY. DO NOT DEVIATE.\n"

            logger.info(f"[COLOR MODE DEBUG] Color mode text added to prompt (length: {len(color_mode_text)} chars)")
        elif effective_color_mode == "suggest_primary" and primary_color:
            # SUGGEST MODE: Use primary as base, AI builds the rest
            logger.info(f"[COLOR MODE DEBUG] SUGGEST PRIMARY MODE - using {primary_color}")
            color_mode_text = f"""

=== COLOR GUIDANCE (SUGGESTED PRIMARY) ===
The user has suggested {primary_color} as their preferred primary color.
Use this as the foundation for each framework's palette.
You may vary the secondary and accent colors across frameworks, but the primary
should be {primary_color} or very close to it in all 4 frameworks.
"""
        else:
            # AI_DECIDES MODE: Full creative freedom
            logger.info("[COLOR MODE DEBUG] AI DECIDES MODE - full creative freedom")
            color_mode_text = """

=== COLOR GUIDANCE (AI DECIDES) ===
You have full creative freedom to choose colors based on what you see in the product.
Make each framework's palette distinct but appropriate for the product.
"""

        prompt += color_mode_text
        logger.info(f"[COLOR MODE DEBUG] Final prompt length: {len(prompt)} characters")
        logger.info(f"Analyzing {len(encoded_images)} product image(s) and generating frameworks for: {product_name} (color_mode={effective_color_mode})")

        try:
            # Build content array with text prompt and all images
            content_array = [
                {
                    "type": "text",
                    "text": prompt,
                },
            ]

            # Add image inventory note if multiple images
            if len(encoded_images) > 1:
                inventory_text = f"\n\n=== IMAGE INVENTORY ===\nYou are being shown {len(encoded_images)} images:\n"
                for i, img in enumerate(encoded_images):
                    inventory_text += f"- Image {i+1}: {img['label']}\n"
                inventory_text += "\nAnalyze ALL images to understand the product from multiple angles.\n"
                content_array[0]["text"] += inventory_text

            # Add all images to the content
            for img in encoded_images:
                content_array.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{img['media_type']};base64,{img['base64']}",
                        "detail": "high",  # High detail for product analysis
                    },
                })

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": content_array,
                    }
                ],
                max_tokens=8000,  # Sufficient for 4 style frameworks (no detailed prompts yet)
                temperature=0.8,
            )

            # Extract the response content
            content = response.choices[0].message.content

            # Parse JSON from response
            frameworks_data = self._parse_response(content)

            # === LOG WHAT COLORS THE AI RETURNED ===
            logger.info("=" * 60)
            logger.info("[COLOR MODE DEBUG] AI RESPONSE - CHECKING COLORS RETURNED")
            frameworks = frameworks_data.get('frameworks', [])
            for i, fw in enumerate(frameworks):
                fw_name = fw.get('framework_name', f'Framework {i+1}')
                colors = fw.get('colors', [])
                logger.info(f"[COLOR MODE DEBUG] Framework {i+1} ({fw_name}):")
                for j, color in enumerate(colors):
                    color_hex = color.get('hex', 'N/A')
                    color_role = color.get('role', 'N/A')
                    logger.info(f"[COLOR MODE DEBUG]   Color {j+1}: {color_hex} ({color_role})")
            logger.info("=" * 60)

            logger.info(f"Generated {len(frameworks_data.get('frameworks', []))} frameworks")

            return frameworks_data

        except Exception as e:
            logger.error(f"Failed to generate frameworks: {e}")
            raise

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response into structured data"""
        try:
            # Find JSON in the response (might have markdown code blocks)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            # Validate structure
            if 'frameworks' not in data:
                raise ValueError("Response missing 'frameworks' key")

            if len(data['frameworks']) < 4:
                logger.warning(f"Only got {len(data['frameworks'])} frameworks, expected 4")

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Raw response: {response[:1000]}...")
            raise ValueError(f"Invalid JSON in AI response: {e}")

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
        STEP 2: Generate 5 detailed image prompts for the SELECTED framework.

        Called AFTER user selects a framework from the 4 options.
        This generates the actual detailed prompts that will be sent to Gemini.

        Args:
            framework: The selected design framework dict
            product_name: The product title
            product_description: Optional product description
            features: List of key features
            target_audience: Target audience description
            global_note: User's global instructions - interpreted differently per image
            has_style_reference: Whether user provided a style reference image
            brand_name: The brand name for the product

        Returns:
            List of 5 ImageGenerationPrompt dicts
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized - check OPENAI_API_KEY")

        # Build color palette string and extract specific hex values
        colors = framework.get('colors', [])
        color_palette = ""
        primary_hex = "#000000"
        accent_hex = "#000000"
        text_dark_hex = "#2D2D2D"
        text_light_hex = "#FFFFFF"

        for color in colors:
            role = color.get('role', 'color').lower()
            hex_val = color.get('hex', '#000000')
            color_palette += f"- {role.upper()}: {hex_val} ({color.get('name', 'Color')}) - {color.get('usage', '')}\n"

            # Extract specific colors by role
            if role == 'primary':
                primary_hex = hex_val
            elif role == 'accent':
                accent_hex = hex_val
            elif role == 'text_dark':
                text_dark_hex = hex_val
            elif role == 'text_light':
                text_light_hex = hex_val
            elif role == 'secondary' and accent_hex == "#000000":
                # Use secondary as accent if no accent specified
                accent_hex = hex_val

        # Build image copy JSON
        image_copy = framework.get('image_copy', [])
        image_copy_json = json.dumps(image_copy, indent=2) if image_copy else "[]"

        # Get typography
        typo = framework.get('typography', {})

        # Get visual treatment
        visual = framework.get('visual_treatment', {})

        # Get story arc
        story = framework.get('story_arc', {})

        # Build the prompt
        prompt = GENERATE_IMAGE_PROMPTS_PROMPT.format(
            product_name=product_name,
            product_description=product_description or product_name,
            features=", ".join(features) if features else "Not specified",
            target_audience=target_audience or "General consumers",
            brand_name=brand_name or "Not specified",
            framework_name=framework.get('framework_name', 'Design Framework'),
            design_philosophy=framework.get('design_philosophy', ''),
            brand_voice=framework.get('brand_voice', 'Professional'),
            color_palette=color_palette,
            primary_hex=primary_hex,
            accent_hex=accent_hex,
            text_dark_hex=text_dark_hex,
            text_light_hex=text_light_hex,
            headline_font=typo.get('headline_font', 'Montserrat'),
            headline_weight=typo.get('headline_weight', 'Bold'),
            body_font=typo.get('body_font', 'Inter'),
            lighting_style=visual.get('lighting_style', 'Soft studio lighting'),
            background_treatment=visual.get('background_treatment', 'Clean and appropriate'),
            mood_keywords=", ".join(visual.get('mood_keywords', ['professional'])),
            story_theme=story.get('theme', ''),
            story_hook=story.get('hook', ''),
            story_reveal=story.get('reveal', ''),
            story_proof=story.get('proof', ''),
            story_dream=story.get('dream', ''),
            story_close=story.get('close', ''),
            image_copy_json=image_copy_json,
            global_note_section="",  # Appended separately below
            style_reference_section="",  # Appended separately below
        )

        # Add global note instructions if provided - AI Designer interprets for each image
        if global_note:
            prompt += GLOBAL_NOTE_INSTRUCTIONS.format(global_note=global_note)
            logger.info(f"[OpenAI Vision] Including global note in prompt generation")

        # Add style reference instructions if user provided a style image
        if has_style_reference:
            prompt += STYLE_REFERENCE_INSTRUCTIONS.format(style_image_index="N")
            logger.info(f"[OpenAI Vision] Including style reference instructions in prompt generation")

        logger.info(f"Generating 5 detailed image prompts for framework: {framework.get('framework_name')}")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=8000,  # 5 prompts of 300-600 words each
                temperature=0.7,
            )

            # Extract and parse response
            content = response.choices[0].message.content
            data = self._parse_prompts_response(content)

            logger.info(f"Generated {len(data)} image prompts")
            return data

        except Exception as e:
            logger.error(f"Failed to generate image prompts: {e}")
            raise

    def _parse_prompts_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the image prompts response"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            if 'generation_prompts' not in data:
                raise ValueError("Response missing 'generation_prompts' key")

            return data['generation_prompts']

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse prompts JSON: {e}")
            raise ValueError(f"Invalid JSON in prompts response: {e}")

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
        Enhance/rewrite a prompt based on user feedback.

        Works for both listing images and A+ modules. The structural_context
        param tells the AI Designer what elements to preserve verbatim
        (e.g. canvas inpainting instructions, named image labels, format constraints).

        Args:
            original_prompt: The prompt that was used for the original image
            user_feedback: What the user wants changed
            image_type: Which image type (main, infographic_1, aplus_0, aplus_hero, etc.)
            framework: Optional - the design framework for context
            product_analysis: Optional - the AI's notes from initial analysis
            structural_context: Preservation rules for this image type

        Returns:
            Dict with 'interpretation', 'changes_made', and 'enhanced_prompt'
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized - check OPENAI_API_KEY")

        # Map image type to number
        # Build image type context line for the prompt
        _listing_number = {
            'main': 1, 'infographic_1': 2, 'infographic_2': 3,
            'lifestyle': 4, 'comparison': 5,
        }
        if image_type in _listing_number:
            image_type_context = f"Listing image {_listing_number[image_type]} of 5"
        elif image_type == "aplus_hero":
            image_type_context = "A+ Content hero pair (tall image split into modules 0+1)"
        elif image_type.startswith("aplus_"):
            image_type_context = f"A+ Content module banner (1464x600, wide format)"
        else:
            image_type_context = ""

        # Extract framework info if provided
        framework_name = "Design Framework"
        design_philosophy = "Professional Amazon listing design"
        color_palette = "Not specified"
        typography = "Not specified"
        brand_voice = "Professional and compelling"

        if framework:
            framework_name = framework.get('framework_name', framework_name)
            design_philosophy = framework.get('design_philosophy', design_philosophy)
            brand_voice = framework.get('brand_voice', brand_voice)

            # Format color palette from framework
            colors = framework.get('colors', [])
            if colors:
                color_lines = []
                for c in colors:
                    color_lines.append(f"- {c.get('role', 'color')}: {c.get('hex', 'N/A')} ({c.get('name', '')})")
                color_palette = "\n".join(color_lines)

            # Format typography from framework
            typo = framework.get('typography', {})
            if typo:
                typography = f"Headline: {typo.get('headline_font', 'N/A')} {typo.get('headline_weight', '')} | Body: {typo.get('body_font', 'N/A')}"

        # Use product analysis or provide a default
        analysis_text = product_analysis or "No product analysis available - use the original prompt as your guide."

        # Build the prompt with full context
        prompt = ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT.format(
            product_analysis=analysis_text,
            image_type=image_type,
            image_type_context=image_type_context,
            framework_name=framework_name,
            design_philosophy=design_philosophy,
            color_palette=color_palette,
            typography=typography,
            brand_voice=brand_voice,
            original_prompt=original_prompt,
            user_feedback=user_feedback,
            structural_context=structural_context or "No special structural rules.",
        )

        logger.info(f"[REGENERATION] Enhancing prompt for {image_type}")
        logger.info(f"[REGENERATION] Has product_analysis: {bool(product_analysis)}")
        logger.info(f"[REGENERATION] Has framework: {bool(framework)}")
        logger.info(f"[REGENERATION] User feedback: {user_feedback[:100]}...")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=3000,
                temperature=0.7,
            )

            # Extract and parse response
            content = response.choices[0].message.content
            result = self._parse_enhancement_response(content)

            logger.info(f"Successfully enhanced prompt. Changes: {result.get('changes_made', [])}")
            return result

        except Exception as e:
            logger.error(f"Failed to enhance prompt: {e}")
            # Fallback: just append the feedback
            return {
                "interpretation": f"Direct append (AI enhancement failed: {e})",
                "changes_made": ["Appended user feedback to original prompt"],
                "enhanced_prompt": f"{original_prompt}\n\n[USER FEEDBACK]: {user_feedback}",
            }

    def _parse_enhancement_response(self, response: str) -> Dict[str, Any]:
        """Parse the enhancement response"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            # Validate required fields
            if 'enhanced_prompt' not in data:
                raise ValueError("Response missing 'enhanced_prompt' key")

            return {
                "interpretation": data.get("interpretation", "Feedback processed"),
                "changes_made": data.get("changes_made", []),
                "enhanced_prompt": data["enhanced_prompt"],
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse enhancement JSON: {e}")
            raise ValueError(f"Invalid JSON in enhancement response: {e}")

    def framework_to_prompt(self, framework: Dict[str, Any], image_type: str) -> str:
        """
        Convert a design framework to a complete prompt for image generation.

        Args:
            framework: The design framework dict
            image_type: Which image to generate (main, infographic_1, etc.)

        Returns:
            Complete prompt string for Gemini image generation
        """
        # Find the copy for this image
        image_copy = None
        image_number = {
            'main': 1,
            'infographic_1': 2,
            'infographic_2': 3,
            'lifestyle': 4,
            'comparison': 5,
        }.get(image_type, 1)

        for copy in framework.get('image_copy', []):
            if copy.get('image_number') == image_number:
                image_copy = copy
                break

        # Build color section
        colors = framework.get('colors', [])
        color_section = "[COLOR PALETTE - EXACT VALUES]\n"
        for color in colors:
            color_section += f"- {color['role'].upper()}: {color['hex']} ({color['name']}) - {color['usage']}\n"

        # Build typography section
        typo = framework.get('typography', {})
        typo_section = f"""[TYPOGRAPHY - EXACT SPECIFICATIONS]
Headlines: {typo.get('headline_font', 'Montserrat')} {typo.get('headline_weight', 'Bold')}, {typo.get('headline_size', '48px')}
Subheads: {typo.get('subhead_font', 'Montserrat')} {typo.get('subhead_weight', 'Regular')}, {typo.get('subhead_size', '24px')}
Body: {typo.get('body_font', 'Inter')} {typo.get('body_weight', 'Regular')}, {typo.get('body_size', '16px')}
Letter Spacing: {typo.get('letter_spacing', '0px')}
"""

        # Build story arc section
        story = framework.get('story_arc', {})
        chapter_keys = ['hook', 'reveal', 'proof', 'dream', 'close']
        current_chapter = chapter_keys[image_number - 1] if image_number <= 5 else 'hook'
        story_section = f"""[STORY ARC - THIS IS IMAGE {image_number} OF 5]
Overall Theme: {story.get('theme', '')}
This Image's Chapter: {current_chapter.upper()}
This Image's Role: {story.get(current_chapter, '')}
"""

        # Build copy section
        copy_section = "[COPY FOR THIS IMAGE]\n"
        if image_copy:
            if image_copy.get('headline'):
                copy_section += f'HEADLINE: "{image_copy["headline"]}"\n'
            if image_copy.get('subhead'):
                copy_section += f'SUBHEAD: "{image_copy["subhead"]}"\n'
            if image_copy.get('feature_callouts'):
                copy_section += "FEATURE CALLOUTS:\n"
                for i, callout in enumerate(image_copy['feature_callouts'], 1):
                    copy_section += f"  {i}. {callout}\n"
            if image_copy.get('cta'):
                copy_section += f'CTA: "{image_copy["cta"]}"\n'
        else:
            if image_type == 'main':
                copy_section += "No text - pure product hero shot on white background\n"

        # Build layout section
        layout = framework.get('layout', {})
        layout_section = f"""[LAYOUT SPECIFICATIONS]
Composition: {layout.get('composition_style', 'centered')}
Whitespace: {layout.get('whitespace_philosophy', 'balanced')}
Product Prominence: {layout.get('product_prominence', 'hero focus')}
Text Placement: {layout.get('text_placement', 'as appropriate')}
Visual Flow: {layout.get('visual_flow', 'natural reading order')}
"""

        # Build visual treatment section
        visual = framework.get('visual_treatment', {})
        visual_section = f"""[VISUAL TREATMENT]
Lighting: {visual.get('lighting_style', 'soft studio lighting')}
Shadows: {visual.get('shadow_spec', 'subtle drop shadows')}
Background: {visual.get('background_treatment', 'clean and appropriate')}
Texture: {visual.get('texture', 'clean')}
Mood: {', '.join(visual.get('mood_keywords', ['professional', 'appealing']))}
"""

        # Build the complete prompt
        prompt = f"""[CREATIVE BRIEF: {framework.get('framework_name', 'Design Framework')}]
{framework.get('design_philosophy', '')}

Brand Voice: {framework.get('brand_voice', 'Professional and appealing')}

{color_section}

{typo_section}

{story_section}

{copy_section}

{layout_section}

{visual_section}

[AMAZON REQUIREMENTS]
- Image {image_number} of 5 in listing set
- {'Pure white background (#FFFFFF) required by Amazon' if image_type == 'main' else 'Background per design brief above'}
- 1500x1500px minimum, 1:1 aspect ratio
- Must be cohesive with other images in set
- Thumbnail must be clear at 100px
- Mobile-optimized (70% of shoppers are on mobile)

[COHESION REQUIREMENT - CRITICAL]
All 5 images in this set MUST share:
- The exact color palette specified above
- The typography specifications above
- The visual treatment above
- The brand voice above
The customer should INSTANTLY recognize these images belong together.

[REFERENCE IMAGE]
Use the provided product photo as the source of truth.
Enhance and stage the product, do not alter the product itself.
"""

        return prompt

    def health_check(self) -> dict:
        """Verify API connection"""
        if not self.api_key:
            return {"status": "not_configured", "message": "OPENAI_API_KEY not set"}
        if not self.client:
            return {"status": "error", "message": "Client not initialized"}
        return {"status": "configured", "model": self.model}


def get_openai_vision_service() -> OpenAIVisionService:
    """Dependency injection helper"""
    return OpenAIVisionService()

"""
Gemini Vision Service - Principal Designer AI (Cost-Effective Alternative)

Uses Gemini 3 Flash Vision to ANALYZE the actual product image and generate
intelligent, tailored design frameworks.

COST COMPARISON (December 2025):
- GPT-4o: $5.00/1M input, $15.00/1M output
- Gemini 3 Flash: $0.50/1M input, $3.00/1M output (10x/5x cheaper!)
- Gemini 2.0 Flash: $0.10/1M input, $0.40/1M output (50x/37x cheaper!)

This service provides the same functionality as OpenAIVisionService but at
a fraction of the cost. Gemini 3 Flash actually outperforms GPT-4o on many
vision benchmarks (MMMU-Pro: 81.2% vs competitors).
"""

import base64
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from google import genai
from google.genai import types

from app.config import settings

if TYPE_CHECKING:
    from app.services.supabase_storage_service import SupabaseStorageService

# Storage service singleton for loading images
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

# Import the prompts from standalone prompts module (they're model-agnostic)
from app.prompts.ai_designer import (
    PRINCIPAL_DESIGNER_VISION_PROMPT,
    STYLE_REFERENCE_FRAMEWORK_PROMPT,
    GENERATE_IMAGE_PROMPTS_PROMPT,
    ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT,
    PLAN_EDIT_INSTRUCTIONS_PROMPT,
    GLOBAL_NOTE_INSTRUCTIONS,
    STYLE_REFERENCE_INSTRUCTIONS,
)

logger = logging.getLogger(__name__)

_DISALLOWED_FEEDBACK_MARKERS = (
    "CLIENT DIRECTION:",
    "CLIENT NOTE:",
    "[USER FEEDBACK]:",
    "=== REGENERATION INSTRUCTIONS ===",
)


def _find_disallowed_feedback_marker(text: str) -> Optional[str]:
    """Return disallowed raw-feedback marker if present in rewritten prompt."""
    lowered = text.lower()
    for marker in _DISALLOWED_FEEDBACK_MARKERS:
        if marker.lower() in lowered:
            return marker
    return None


class GeminiVisionService:
    """
    Principal Designer AI using Google Gemini Vision.

    SEES the actual product image and generates intelligent,
    tailored design frameworks based on visual analysis.

    10x cheaper than GPT-4o with comparable or better quality!
    """

    def __init__(self, api_key: str = None):
        """Initialize Gemini client"""
        self.api_key = api_key or settings.gemini_api_key
        self.model = settings.gemini_vision_model  # gemini-3-flash-preview

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set - Vision features unavailable")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    def _load_image_bytes(self, image_path: str) -> bytes:
        """Load image file as bytes (from local path or Supabase)"""
        if image_path.startswith("supabase://"):
            storage = _get_storage_service()
            return storage.get_file_bytes(image_path)
        else:
            # Local file path (for backwards compatibility)
            with open(image_path, "rb") as f:
                return f.read()

    def _get_image_mime_type(self, image_path: str) -> str:
        """Get MIME type from file extension"""
        ext = Path(image_path).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return mime_types.get(ext, "image/jpeg")

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
            raise ValueError("Gemini client not initialized - check GEMINI_API_KEY")

        # Validate primary image exists (handles both local paths and Supabase URLs)
        if not _image_path_exists(product_image_path):
            raise ValueError(f"Product image not found: {product_image_path}")

        # Build list of all images to send
        all_image_paths = [product_image_path]
        style_ref_index = None  # Track which image is the style reference

        if additional_image_paths:
            for path in additional_image_paths:
                if _image_path_exists(path):
                    all_image_paths.append(path)
                else:
                    logger.warning(f"Additional image not found, skipping: {path}")

        # Add style reference image (if provided)
        has_style_reference = False
        if style_reference_path and _image_path_exists(style_reference_path):
            all_image_paths.append(style_reference_path)
            style_ref_index = len(all_image_paths)  # 1-indexed
            has_style_reference = True
            logger.info(f"[GEMINI] Including style reference as Image #{style_ref_index}")
            logger.info(f"[GEMINI] SINGLE FRAMEWORK MODE - Style reference provided")
        elif style_reference_path:
            logger.warning(f"Style reference not found, skipping: {style_reference_path}")

        # Determine which prompt to use based on whether style reference is provided
        if has_style_reference:
            # SINGLE FRAMEWORK MODE: Style reference provided
            # Build color mode instructions for the single-framework prompt
            effective_color_mode = color_mode or "ai_decides"
            if effective_color_mode == "locked_palette" and locked_colors:
                color_mode_instructions = f"""
LOCKED PALETTE MODE: The user has LOCKED these specific colors: {', '.join(locked_colors)}
- Use EXACTLY these colors as PRIMARY, SECONDARY, ACCENT (in order provided)
- Do NOT extract different colors from the style reference
- Extract lighting, mood, typography, and composition from the style reference
- But use the LOCKED colors, not colors from the style reference
"""
            else:
                color_mode_instructions = """
EXTRACT COLORS (2 by default): Study the style reference image and extract:
- The dominant color → PRIMARY (60%)
- The supporting color → SECONDARY (40%)
Only add a 3rd ACCENT color if the style reference clearly uses one.

Premium brands use FEWER colors. Default to 2. Text colors derive from the palette.
Use the ACTUAL colors you see in the style reference. Do NOT invent colors.
"""

            # Build image inventory for style reference mode
            # This tells the AI exactly what each image is
            image_inventory = f"=== IMAGE INVENTORY ===\nI'm showing you {len(all_image_paths)} image(s):\n"
            for i, img_path in enumerate(all_image_paths):
                img_num = i + 1
                if i == 0:
                    label = "PRIMARY PRODUCT IMAGE - the product you're creating listing images for"
                elif img_num == style_ref_index:
                    label = "STYLE REFERENCE IMAGE - the EXACT visual style the user wants to follow"
                else:
                    label = f"ADDITIONAL PRODUCT IMAGE - another angle/view of the product"
                image_inventory += f"- Image {img_num}: {label}\n"

            image_inventory += f"\nIMPORTANT: Image {style_ref_index} is the STYLE REFERENCE. Extract colors, mood, lighting, and typography feel from it."
            image_inventory += "\nAnalyze ALL product images to understand the product from multiple angles."

            logger.info(f"[GEMINI] Image inventory for style ref mode:\n{image_inventory}")

            # Use the single-framework prompt
            prompt = STYLE_REFERENCE_FRAMEWORK_PROMPT.format(
                product_name=product_name,
                brand_name=brand_name or "Not specified",
                features=", ".join(features) if features else "Not specified",
                target_audience=target_audience or "General consumers",
                primary_color=primary_color or "Extract from style reference",
                color_mode_instructions=color_mode_instructions,
                image_inventory=image_inventory,
            )

            logger.info(f"[GEMINI] Using STYLE_REFERENCE_FRAMEWORK_PROMPT (1 framework)")
        else:
            # STANDARD MODE: No style reference - generate 4 frameworks
            prompt = PRINCIPAL_DESIGNER_VISION_PROMPT.format(
                product_name=product_name,
                brand_name=brand_name or "Not specified",
                features=", ".join(features) if features else "Not specified",
                target_audience=target_audience or "General consumers",
                primary_color=primary_color or "AI to determine based on product image",
            )

            logger.info(f"[GEMINI] Using PRINCIPAL_DESIGNER_VISION_PROMPT (4 frameworks)")

            # Add image inventory note if multiple images (only for standard mode)
            if len(all_image_paths) > 1:
                inventory_text = f"\n\n=== IMAGE INVENTORY ===\nYou are being shown {len(all_image_paths)} images:\n"
                for i, path in enumerate(all_image_paths):
                    if i == 0:
                        label = "PRIMARY product image"
                    else:
                        label = f"Additional product image {i}"
                    inventory_text += f"- Image {i+1}: {label}\n"
                inventory_text += "\nAnalyze ALL images to understand the product from multiple angles.\n"
                prompt += inventory_text

        # Handle color mode - add instructions based on mode
        # NOTE: Only add these for STANDARD mode (4 frameworks)
        # Style reference mode already has color handling built into STYLE_REFERENCE_FRAMEWORK_PROMPT
        effective_color_mode = color_mode or "ai_decides"

        # === DETAILED COLOR MODE LOGGING ===
        logger.info("=" * 60)
        logger.info("[GEMINI COLOR MODE DEBUG] Starting color mode processing")
        logger.info(f"[GEMINI COLOR MODE DEBUG] Has style reference: {has_style_reference}")
        logger.info(f"[GEMINI COLOR MODE DEBUG] Received color_mode parameter: {color_mode}")
        logger.info(f"[GEMINI COLOR MODE DEBUG] Effective color_mode: {effective_color_mode}")
        logger.info(f"[GEMINI COLOR MODE DEBUG] Received locked_colors: {locked_colors}")
        logger.info(f"[GEMINI COLOR MODE DEBUG] Received primary_color: {primary_color}")
        logger.info("=" * 60)

        # Only add color mode instructions for STANDARD mode (not style reference mode)
        if not has_style_reference:
            if effective_color_mode == "locked_palette" and locked_colors:
                # LOCKED MODE: AI MUST use exactly these colors in ALL 4 frameworks
                color_list = ", ".join(locked_colors)
                num_locked = len(locked_colors)
                logger.info(f"[GEMINI COLOR MODE DEBUG] LOCKED PALETTE MODE ACTIVATED!")
                logger.info(f"[GEMINI COLOR MODE DEBUG] Colors to lock: {color_list}")
                logger.info(f"[GEMINI COLOR MODE DEBUG] Number of locked colors: {num_locked}")

                # Build color assignment rules based on how many colors are locked
                color_rules = f"""
=== MANDATORY COLOR PALETTE (LOCKED) ===
CRITICAL: The user has LOCKED exactly {num_locked} color(s). You MUST use ONLY these colors.
Do NOT add additional colors. Do NOT suggest alternatives. Do NOT be creative with colors.

LOCKED COLORS: {color_list}

COLOR ASSIGNMENT (STRICT):
"""
                if num_locked >= 1:
                    color_rules += f"- PRIMARY color: {locked_colors[0]} (MANDATORY - use this exact hex)\n"
                if num_locked >= 2:
                    color_rules += f"- SECONDARY color: {locked_colors[1]} (MANDATORY - use this exact hex)\n"
                if num_locked >= 3:
                    color_rules += f"- ACCENT color: {locked_colors[2]} (MANDATORY - use this exact hex)\n"

                # Smart accent derivation based on number of locked colors
                if num_locked == 1:
                    color_rules += """
USER PROVIDED ONLY 1 COLOR:
- Use it as PRIMARY
- For SECONDARY: Derive using color theory (complementary, analogous, or a shade)
- For ACCENT: Look at the product image - if there's a prominent color on the product
  (like on the label, cap, or packaging), use that. Otherwise derive from primary.
"""
                elif num_locked == 2:
                    color_rules += """
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

                color_rules += f"""
ADDITIONAL RULES:
- ONLY 3 colors per framework (primary, secondary, accent). No text_dark or text_light.
- ALL 4 frameworks MUST have IDENTICAL color hex codes for primary/secondary/accent
- The frameworks should differ in typography, layout, voice - NOT in colors

OUTPUT VERIFICATION:
- colors[0].hex MUST be: {locked_colors[0]}
"""
                if num_locked >= 2:
                    color_rules += f"- colors[1].hex MUST be: {locked_colors[1]}\n"
                if num_locked >= 3:
                    color_rules += f"- colors[2].hex MUST be: {locked_colors[2]}\n"

                color_rules += "\nThis is NOT a suggestion. These colors are MANDATORY. DO NOT DEVIATE.\n"

                prompt += color_rules
                logger.info(f"[GEMINI COLOR MODE DEBUG] Color mode text added to prompt")
            elif effective_color_mode == "suggest_primary":
                # SUGGEST MODE: AI extracts colors from product/style reference
                if primary_color:
                    logger.info(f"[GEMINI COLOR MODE DEBUG] SUGGEST PRIMARY MODE - using {primary_color}")
                    prompt += f"""

=== COLOR GUIDANCE (SUGGESTED PRIMARY) ===
The user has suggested {primary_color} as their preferred primary color.
Use this as the foundation for each framework's palette.
You may vary the secondary and accent colors across frameworks, but the primary
should be {primary_color} or very close to it in all 4 frameworks.
"""
                else:
                    # Style reference provided but no specific colors - extract from what you see
                    logger.info("[GEMINI COLOR MODE DEBUG] SUGGEST PRIMARY MODE - extracting from product/style")
                    prompt += """

=== COLOR GUIDANCE (EXTRACT FROM IMAGES) ===
The user has provided a style reference image. Study it carefully and:
1. Extract the dominant colors from the style reference
2. Use those colors as inspiration for ALL 4 frameworks
3. All frameworks should feel cohesive with the style reference's color palette
4. Do NOT invent random colors - base them on what you SEE in the images

The color palette should feel like it belongs with the style reference image.
"""
            else:
                # AI_DECIDES MODE: Full creative freedom
                logger.info("[GEMINI COLOR MODE DEBUG] AI DECIDES MODE - full creative freedom")
                prompt += """

=== COLOR GUIDANCE (AI DECIDES) ===
You have full creative freedom to choose colors based on what you see in the product.
Make each framework's palette distinct but appropriate for the product.
"""
        else:
            logger.info("[GEMINI COLOR MODE DEBUG] STYLE REFERENCE MODE - color handling already in prompt")

        logger.info(f"[GEMINI COLOR MODE DEBUG] Final prompt length: {len(prompt)} characters")
        logger.info(f"[Gemini Vision] Analyzing {len(all_image_paths)} product image(s) for: {product_name} (color_mode={effective_color_mode})")
        logger.info(f"[Gemini Vision] Using model: {self.model}")

        # === COMPREHENSIVE GEMINI VISION API LOGGING (Framework Generation) ===
        framework_mode = "SINGLE (Style Reference)" if has_style_reference else "STANDARD (4 options)"
        logger.info("=" * 80)
        logger.info("[GEMINI VISION FRAMEWORK] === FULL REQUEST DETAILS ===")
        logger.info(f"[GEMINI VISION FRAMEWORK] Mode: {framework_mode}")
        logger.info(f"[GEMINI VISION FRAMEWORK] Model: {self.model}")
        logger.info(f"[GEMINI VISION FRAMEWORK] Temperature: 0.8")
        logger.info(f"[GEMINI VISION FRAMEWORK] Max Output Tokens: 8000")
        logger.info(f"[GEMINI VISION FRAMEWORK] Product: {product_name}")
        logger.info(f"[GEMINI VISION FRAMEWORK] Brand: {brand_name or 'Not specified'}")
        logger.info(f"[GEMINI VISION FRAMEWORK] Color Mode: {effective_color_mode}")
        logger.info(f"[GEMINI VISION FRAMEWORK] Locked Colors: {locked_colors}")
        logger.info(f"[GEMINI VISION FRAMEWORK] Primary Color: {primary_color}")
        logger.info(f"[GEMINI VISION FRAMEWORK] Style Ref Index: {style_ref_index}")
        logger.info(f"[GEMINI VISION FRAMEWORK] Has Style Reference: {has_style_reference}")
        logger.info("-" * 40)
        logger.info(f"[GEMINI VISION FRAMEWORK] IMAGES ({len(all_image_paths)} total):")
        for i, img_path in enumerate(all_image_paths):
            label = "PRIMARY" if i == 0 else ("STYLE REF" if style_ref_index and i + 1 == style_ref_index else f"ADDITIONAL {i}")
            logger.info(f"[GEMINI VISION FRAMEWORK]   [{label}] {img_path}")
        logger.info("-" * 40)
        logger.info("[GEMINI VISION FRAMEWORK] FULL PROMPT:")
        logger.info("-" * 40)
        for i, line in enumerate(prompt.split('\n')):
            logger.info(f"[FW PROMPT L{i+1:03d}] {line}")
        logger.info("=" * 80)

        try:
            # Create parts array starting with the prompt
            parts = [types.Part.from_text(text=prompt)]

            # Add all images as parts
            for img_path in all_image_paths:
                image_bytes = self._load_image_bytes(img_path)
                mime_type = self._get_image_mime_type(img_path)
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                )
                parts.append(image_part)

            # Generate content with vision
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        role="user",
                        parts=parts,
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=8000,
                ),
            )

            # Extract the response content
            content = response.text

            # Parse JSON from response
            frameworks_data = self._parse_response(content)

            # === LOG WHAT COLORS THE AI RETURNED ===
            logger.info("=" * 60)
            logger.info("[GEMINI COLOR MODE DEBUG] AI RESPONSE - CHECKING COLORS RETURNED")
            frameworks = frameworks_data.get('frameworks', [])
            for i, fw in enumerate(frameworks):
                fw_name = fw.get('framework_name', f'Framework {i+1}')
                colors = fw.get('colors', [])
                logger.info(f"[GEMINI COLOR MODE DEBUG] Framework {i+1} ({fw_name}):")
                for j, color in enumerate(colors):
                    # Handle both dict format and string format for colors
                    if isinstance(color, dict):
                        color_hex = color.get('hex', 'N/A')
                        color_role = color.get('role', 'N/A')
                    else:
                        color_hex = str(color) if color else 'N/A'
                        color_role = 'unknown'
                    logger.info(f"[GEMINI COLOR MODE DEBUG]   Color {j+1}: {color_hex} ({color_role})")
            logger.info("=" * 60)

            logger.info(f"[Gemini Vision] Generated {len(frameworks_data.get('frameworks', []))} frameworks")

            # Enforce 3-color maximum per framework
            for fw in frameworks_data.get('frameworks', []):
                if 'colors' in fw and len(fw['colors']) > 3:
                    logger.info(f"Truncating framework colors from {len(fw['colors'])} to 3")
                    fw['colors'] = fw['colors'][:3]

            return frameworks_data

        except Exception as e:
            logger.error(f"[Gemini Vision] Failed to generate frameworks: {e}")
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

            # Note: 1 framework is valid for style reference mode, 4 for standard mode
            num_frameworks = len(data['frameworks'])
            if num_frameworks == 0:
                raise ValueError("Response contains no frameworks")
            logger.info(f"[GEMINI] Parsed {num_frameworks} framework(s) from response")

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
            has_style_reference: Whether user provided a style reference image
            features: List of key features
            target_audience: Target audience description

        Returns:
            List of 5 ImageGenerationPrompt dicts
        """
        if not self.client:
            raise ValueError("Gemini client not initialized - check GEMINI_API_KEY")

        # Build color palette string and extract specific hex values
        colors = framework.get('colors', [])
        if not isinstance(colors, list):
            colors = []
        colors = colors[:3]  # Enforce 3-color maximum
        color_palette = ""
        primary_hex = "#000000"
        accent_hex = "#000000"
        text_dark_hex = "#2D2D2D"
        text_light_hex = "#FFFFFF"

        for color in colors:
            # Handle both dict format and string format for colors
            if isinstance(color, dict):
                role = color.get('role', 'color').lower()
                hex_val = color.get('hex', '#000000')
                color_name = color.get('name', 'Color')
                color_usage = color.get('usage', '')
            else:
                # Color is a string (just hex value)
                role = 'color'
                hex_val = str(color) if color else '#000000'
                color_name = 'Color'
                color_usage = ''
            color_palette += f"- {role.upper()}: {hex_val} ({color_name}) - {color_usage}\n"

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
                accent_hex = hex_val

        # Build image copy JSON
        image_copy = framework.get('image_copy', [])
        image_copy_json = json.dumps(image_copy, indent=2) if image_copy else "[]"

        # Get typography (handle string case)
        typo = framework.get('typography', {})
        if not isinstance(typo, dict):
            typo = {}

        # Get visual treatment (handle string case)
        visual = framework.get('visual_treatment', {})
        if not isinstance(visual, dict):
            visual = {}

        # Get story arc (handle string case)
        story = framework.get('story_arc', {})
        if not isinstance(story, dict):
            story = {}

        # Get conversion insights from product_analysis (if available)
        product_analysis = framework.get('product_analysis', {})
        conversion_insights = product_analysis.get('conversion_insights', {})

        # Format conversion insights for prompt
        objections = conversion_insights.get('top_objections', [])
        objections_json = json.dumps(objections, indent=2) if objections else "No objections identified - infer from product category"

        social_proof = conversion_insights.get('social_proof_angles', [])
        social_proof_json = json.dumps(social_proof, indent=2) if social_proof else '["Customer testimonial opportunity", "Rating/review highlight"]'

        trust_signals = conversion_insights.get('trust_signals', [])
        trust_signals_json = json.dumps(trust_signals, indent=2) if trust_signals else '["Quality materials visible", "Craftsmanship details"]'

        key_differentiator = conversion_insights.get('key_differentiator', 'Unique design and quality that sets it apart')

        mobile_priorities = conversion_insights.get('mobile_priorities', ['Product clearly visible', 'Text readable at small size'])
        mobile_priorities_json = json.dumps(mobile_priorities, indent=2)

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
            story_transform=story.get('transform', ''),
            story_close=story.get('close', ''),
            image_copy_json=image_copy_json,
            # Conversion insights
            objections_json=objections_json,
            social_proof_json=social_proof_json,
            trust_signals_json=trust_signals_json,
            key_differentiator=key_differentiator,
            mobile_priorities_json=mobile_priorities_json,
            global_note_section="",  # Appended separately below
            style_reference_section="",  # Appended separately below
        )

        # Add global note instructions if provided - AI Designer interprets for each image
        if global_note:
            prompt += GLOBAL_NOTE_INSTRUCTIONS.format(global_note=global_note)
            logger.info(f"[Gemini Vision] Including global note in prompt generation")

        # Add style reference instructions if user provided a style image
        # Note: The actual image index will be handled at generation time by STYLE_REFERENCE_PROMPT_PREFIX
        # Here we just tell the AI Designer to use generic "style reference" language (no image numbers)
        if has_style_reference:
            prompt += STYLE_REFERENCE_INSTRUCTIONS
            logger.info(f"[Gemini Vision] Including style reference instructions in prompt generation")

        logger.info(f"[Gemini Vision] Generating 5 image prompts for: {framework.get('framework_name')}")

        # === COMPREHENSIVE GEMINI VISION API LOGGING (Prompt Generation) ===
        logger.info("=" * 80)
        logger.info("[GEMINI VISION PROMPTS] === FULL REQUEST DETAILS ===")
        logger.info(f"[GEMINI VISION PROMPTS] Model: {self.model}")
        logger.info(f"[GEMINI VISION PROMPTS] Temperature: 0.7")
        logger.info(f"[GEMINI VISION PROMPTS] Max Output Tokens: 8000")
        logger.info(f"[GEMINI VISION PROMPTS] Product: {product_name}")
        logger.info(f"[GEMINI VISION PROMPTS] Framework: {framework.get('framework_name')}")
        logger.info(f"[GEMINI VISION PROMPTS] Features: {features}")
        logger.info(f"[GEMINI VISION PROMPTS] Target Audience: {target_audience}")
        logger.info(f"[GEMINI VISION PROMPTS] Global Note: {global_note[:100] if global_note else 'None'}...")
        logger.info(f"[GEMINI VISION PROMPTS] Has Style Reference: {has_style_reference}")
        logger.info("-" * 40)
        logger.info("[GEMINI VISION PROMPTS] FRAMEWORK COLORS:")
        for color in colors:
            if isinstance(color, dict):
                logger.info(f"[GEMINI VISION PROMPTS]   {color.get('role', '?')}: {color.get('hex', '?')} ({color.get('name', '?')})")
            else:
                logger.info(f"[GEMINI VISION PROMPTS]   color: {color}")
        logger.info("-" * 40)
        logger.info("[GEMINI VISION PROMPTS] FULL PROMPT:")
        logger.info("-" * 40)
        for i, line in enumerate(prompt.split('\n')):
            logger.info(f"[IMG PROMPT L{i+1:03d}] {line}")
        logger.info("=" * 80)

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=8000,
                ),
            )

            # Extract and parse response
            content = response.text
            data = self._parse_prompts_response(content)

            logger.info(f"[Gemini Vision] Generated {len(data)} image prompts")
            return data

        except Exception as e:
            logger.error(f"[Gemini Vision] Failed to generate image prompts: {e}")
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
        parameter tells the AI Designer which structural elements must remain
        unchanged.
        """
        if not self.client:
            raise ValueError("Gemini client not initialized - check GEMINI_API_KEY")

        listing_number = {
            "main": 1,
            "infographic_1": 2,
            "infographic_2": 3,
            "lifestyle": 4,
            "comparison": 5,
        }
        if image_type in listing_number:
            image_type_context = f"Listing image {listing_number[image_type]} of 5"
        elif image_type == "aplus_hero":
            image_type_context = "A+ Content hero pair (tall image split into modules 0+1)"
        elif image_type.startswith("aplus_"):
            image_type_context = "A+ Content module banner (1464x600, wide format)"
        else:
            image_type_context = ""

        framework_name = "Design Framework"
        design_philosophy = "Professional Amazon listing design"
        color_palette = "Not specified"
        typography = "Not specified"
        brand_voice = "Professional and compelling"

        if framework:
            framework_name = framework.get("framework_name", framework_name)
            design_philosophy = framework.get("design_philosophy", design_philosophy)
            brand_voice = framework.get("brand_voice", brand_voice)

            colors = framework.get("colors", [])
            if colors:
                color_lines = []
                for color in colors:
                    color_lines.append(
                        f"- {color.get('role', 'color')}: {color.get('hex', 'N/A')} ({color.get('name', '')})"
                    )
                color_palette = "\n".join(color_lines)

            typo = framework.get("typography", {})
            if typo:
                typography = (
                    f"Headline: {typo.get('headline_font', 'N/A')} {typo.get('headline_weight', '')} | "
                    f"Body: {typo.get('body_font', 'N/A')}"
                )

        analysis_text = (
            product_analysis
            or "No product analysis available - use the original prompt as your guide."
        )

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

        logger.info(f"[REGENERATION][GEMINI] Enhancing prompt for {image_type}")
        logger.info(f"[REGENERATION][GEMINI] Has product_analysis: {bool(product_analysis)}")
        logger.info(f"[REGENERATION][GEMINI] Has framework: {bool(framework)}")
        logger.info(f"[REGENERATION][GEMINI] User feedback: {user_feedback[:100]}...")

        attempts = [
            (prompt, 0.7, "primary"),
            (
                prompt
                + "\n\nRETRY MODE: Return ONLY valid JSON with keys "
                + "\"interpretation\", \"changes_made\", and \"enhanced_prompt\". "
                + "Do not include markdown, code fences, or any extra text.",
                0.2,
                "json_retry",
            ),
        ]
        last_error: Optional[Exception] = None

        for idx, (attempt_prompt, temperature, label) in enumerate(attempts, start=1):
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=attempt_prompt)],
                        )
                    ],
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=3000,
                    ),
                )

                content = response.text or ""
                result = self._parse_enhancement_response(content)

                enhanced_prompt = (result.get("enhanced_prompt") or "").strip()
                if not enhanced_prompt:
                    raise ValueError("enhanced_prompt is empty")

                disallowed_marker = _find_disallowed_feedback_marker(enhanced_prompt)
                if disallowed_marker:
                    raise ValueError(
                        f"enhanced_prompt contains disallowed marker: {disallowed_marker}"
                    )

                result["enhanced_prompt"] = enhanced_prompt
                logger.info(
                    f"[REGENERATION][GEMINI] Successfully enhanced prompt on attempt {idx} ({label}). "
                    f"Changes: {result.get('changes_made', [])}"
                )
                return result
            except Exception as e:
                last_error = e
                logger.warning(
                    f"[REGENERATION][GEMINI] Prompt enhancement attempt {idx} ({label}) failed: {e}"
                )

        raise RuntimeError(
            "AI Designer could not rewrite feedback into a clean generation prompt."
        ) from last_error

    def _parse_enhancement_response(self, response: str) -> Dict[str, Any]:
        """Parse prompt-enhancement response JSON."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            if "enhanced_prompt" not in data:
                raise ValueError("Response missing 'enhanced_prompt' key")

            return {
                "interpretation": data.get("interpretation", "Feedback processed"),
                "changes_made": data.get("changes_made", []),
                "enhanced_prompt": data["enhanced_prompt"],
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse enhancement JSON: {e}")
            raise ValueError(f"Invalid JSON in enhancement response: {e}")

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
        Generate concise edit instructions from feedback for image editing API calls.

        Unlike regeneration prompt rewriting, this returns DELTA edit instructions
        to apply on the existing source image.
        """
        if not self.client:
            raise ValueError("Gemini client not initialized - check GEMINI_API_KEY")

        if not _image_path_exists(source_image_path):
            raise ValueError(f"Source image not found for edit planning: {source_image_path}")

        listing_number = {
            "main": 1,
            "infographic_1": 2,
            "infographic_2": 3,
            "lifestyle": 4,
            "comparison": 5,
        }
        if image_type in listing_number:
            image_type_context = f"Listing image {listing_number[image_type]} of 5"
        elif image_type == "aplus_hero":
            image_type_context = "A+ Content hero pair (tall image split into modules 0+1)"
        elif image_type.startswith("aplus_"):
            image_type_context = "A+ Content module banner (1464x600, wide format)"
        else:
            image_type_context = ""

        framework_name = "Design Framework"
        design_philosophy = "Professional Amazon listing design"
        color_palette = "Not specified"
        typography = "Not specified"
        brand_voice = "Professional and compelling"

        if framework:
            framework_name = framework.get("framework_name", framework_name)
            design_philosophy = framework.get("design_philosophy", design_philosophy)
            brand_voice = framework.get("brand_voice", brand_voice)

            colors = framework.get("colors", [])
            if colors:
                color_lines = []
                for color in colors:
                    color_lines.append(
                        f"- {color.get('role', 'color')}: {color.get('hex', 'N/A')} ({color.get('name', '')})"
                    )
                color_palette = "\n".join(color_lines)

            typo = framework.get("typography", {})
            if typo:
                typography = (
                    f"Headline: {typo.get('headline_font', 'N/A')} {typo.get('headline_weight', '')} | "
                    f"Body: {typo.get('body_font', 'N/A')}"
                )

        analysis_text = (
            product_analysis
            or "No product analysis available - use the current image and feedback as primary context."
        )

        prompt = PLAN_EDIT_INSTRUCTIONS_PROMPT.format(
            product_analysis=analysis_text,
            image_type=image_type,
            image_type_context=image_type_context,
            framework_name=framework_name,
            design_philosophy=design_philosophy,
            color_palette=color_palette,
            typography=typography,
            brand_voice=brand_voice,
            original_prompt=original_prompt or "No prior prompt context available.",
            user_feedback=user_feedback,
            structural_context=structural_context or "No special structural rules.",
        )

        source_image_bytes = self._load_image_bytes(source_image_path)
        source_image_mime = self._get_image_mime_type(source_image_path)

        loaded_refs: List[tuple[str, bytes, str]] = []
        for idx, ref_path in enumerate(reference_image_paths or []):
            if not _image_path_exists(ref_path):
                logger.warning(f"[EDIT][GEMINI] Reference image not found, skipping: {ref_path}")
                continue
            try:
                loaded_refs.append(
                    (
                        f"REFERENCE_IMAGE_{idx + 1}",
                        self._load_image_bytes(ref_path),
                        self._get_image_mime_type(ref_path),
                    )
                )
            except Exception as e:
                logger.warning(f"[EDIT][GEMINI] Failed loading reference image {ref_path}: {e}")

        def _build_parts(prompt_text: str) -> List[types.Part]:
            parts: List[types.Part] = [
                types.Part.from_text(text=prompt_text),
                types.Part.from_text(text="CURRENT_IMAGE_TO_EDIT:"),
                types.Part.from_bytes(data=source_image_bytes, mime_type=source_image_mime),
            ]
            for label, ref_bytes, ref_mime in loaded_refs:
                parts.append(types.Part.from_text(text=f"{label}:"))
                parts.append(types.Part.from_bytes(data=ref_bytes, mime_type=ref_mime))
            return parts

        logger.info(f"[EDIT][GEMINI] Planning edit instructions for {image_type}")
        logger.info(f"[EDIT][GEMINI] Source image: {source_image_path}")
        logger.info(f"[EDIT][GEMINI] Reference images: {len(loaded_refs)}")
        logger.info(f"[EDIT][GEMINI] User feedback: {user_feedback[:120]}...")

        attempts = [
            (prompt, 0.5, "primary"),
            (
                prompt
                + "\n\nRETRY MODE: Return ONLY valid JSON with keys "
                + "\"interpretation\", \"changes_made\", and \"edit_instructions\". "
                + "Do not include markdown, code fences, or extra text.",
                0.2,
                "json_retry",
            ),
        ]
        last_error: Optional[Exception] = None

        for idx, (attempt_prompt, temperature, label) in enumerate(attempts, start=1):
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Content(
                            role="user",
                            parts=_build_parts(attempt_prompt),
                        )
                    ],
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=1200,
                    ),
                )

                content = response.text or ""
                result = self._parse_edit_plan_response(content)

                edit_instructions = (result.get("edit_instructions") or "").strip()
                if not edit_instructions:
                    raise ValueError("edit_instructions is empty")

                disallowed_marker = _find_disallowed_feedback_marker(edit_instructions)
                if disallowed_marker:
                    raise ValueError(
                        f"edit_instructions contains disallowed marker: {disallowed_marker}"
                    )

                result["edit_instructions"] = edit_instructions
                logger.info(
                    f"[EDIT][GEMINI] Planned edit instructions on attempt {idx} ({label}). "
                    f"Changes: {result.get('changes_made', [])}"
                )
                return result
            except Exception as e:
                last_error = e
                logger.warning(
                    f"[EDIT][GEMINI] Edit planning attempt {idx} ({label}) failed: {e}"
                )

        raise RuntimeError(
            "AI Designer could not plan clean edit instructions."
        ) from last_error

    def _parse_edit_plan_response(self, response: str) -> Dict[str, Any]:
        """Parse edit-instructions planning response JSON."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            if "edit_instructions" not in data:
                raise ValueError("Response missing 'edit_instructions' key")

            return {
                "interpretation": data.get("interpretation", "Feedback processed"),
                "changes_made": data.get("changes_made", []),
                "edit_instructions": data["edit_instructions"],
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse edit planning JSON: {e}")
            raise ValueError(f"Invalid JSON in edit planning response: {e}")

    def framework_to_prompt(self, framework: Dict[str, Any], image_type: str) -> str:
        """
        Convert a design framework to a complete prompt for image generation.

        This is model-agnostic and does not call any external API.
        """
        image_copy = None
        image_number = {
            "main": 1,
            "infographic_1": 2,
            "infographic_2": 3,
            "lifestyle": 4,
            "comparison": 5,
        }.get(image_type, 1)

        for copy in framework.get("image_copy", []):
            if copy.get("image_number") == image_number:
                image_copy = copy
                break

        colors = framework.get("colors", [])
        color_section = "[COLOR PALETTE - EXACT VALUES]\n"
        for color in colors:
            color_section += (
                f"- {color['role'].upper()}: {color['hex']} ({color['name']}) - "
                f"{color['usage']}\n"
            )

        typo = framework.get("typography", {})
        typo_section = f"""[TYPOGRAPHY - EXACT SPECIFICATIONS]
Headlines: {typo.get('headline_font', 'Montserrat')} {typo.get('headline_weight', 'Bold')}, {typo.get('headline_size', '48px')}
Subheads: {typo.get('subhead_font', 'Montserrat')} {typo.get('subhead_weight', 'Regular')}, {typo.get('subhead_size', '24px')}
Body: {typo.get('body_font', 'Inter')} {typo.get('body_weight', 'Regular')}, {typo.get('body_size', '16px')}
Letter Spacing: {typo.get('letter_spacing', '0px')}
"""

        story = framework.get("story_arc", {})
        chapter_keys = ["hook", "reveal", "proof", "dream", "close"]
        current_chapter = chapter_keys[image_number - 1] if image_number <= 5 else "hook"
        story_section = f"""[STORY ARC - THIS IS IMAGE {image_number} OF 5]
Overall Theme: {story.get('theme', '')}
This Image's Chapter: {current_chapter.upper()}
This Image's Role: {story.get(current_chapter, '')}
"""

        copy_section = "[COPY FOR THIS IMAGE]\n"
        if image_copy:
            if image_copy.get("headline"):
                copy_section += f'HEADLINE: "{image_copy["headline"]}"\n'
            if image_copy.get("subhead"):
                copy_section += f'SUBHEAD: "{image_copy["subhead"]}"\n'
            if image_copy.get("feature_callouts"):
                copy_section += "FEATURE CALLOUTS:\n"
                for i, callout in enumerate(image_copy["feature_callouts"], 1):
                    copy_section += f"  {i}. {callout}\n"
            if image_copy.get("cta"):
                copy_section += f'CTA: "{image_copy["cta"]}"\n'
        elif image_type == "main":
            copy_section += "No text - pure product hero shot on white background\n"

        layout = framework.get("layout", {})
        layout_section = f"""[LAYOUT SPECIFICATIONS]
Composition: {layout.get('composition_style', 'centered')}
Whitespace: {layout.get('whitespace_philosophy', 'balanced')}
Product Prominence: {layout.get('product_prominence', 'hero focus')}
Text Placement: {layout.get('text_placement', 'as appropriate')}
Visual Flow: {layout.get('visual_flow', 'natural reading order')}
"""

        visual = framework.get("visual_treatment", {})
        visual_section = f"""[VISUAL TREATMENT]
Lighting: {visual.get('lighting_style', 'soft studio lighting')}
Shadows: {visual.get('shadow_spec', 'subtle drop shadows')}
Background: {visual.get('background_treatment', 'clean and appropriate')}
Texture: {visual.get('texture', 'clean')}
Mood: {', '.join(visual.get('mood_keywords', ['professional', 'appealing']))}
"""

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

    async def generate_alt_text(
        self,
        image_path: str,
        product_name: str,
        image_type: str,
        features: Optional[List[str]] = None,
    ) -> str:
        """
        Generate SEO-friendly alt text for a listing image.

        Args:
            image_path: Path to the generated listing image
            product_name: The product name
            image_type: Type of image (main, infographic_1, lifestyle, etc.)
            features: Optional product features for context

        Returns:
            SEO-optimized alt text string (max 125 characters)
        """
        if not self.client:
            raise ValueError("Gemini client not initialized - check GEMINI_API_KEY")

        # Load image
        image_bytes = self._load_image_bytes(image_path)
        mime_type = self._get_image_mime_type(image_path)

        # Build prompt for alt text generation
        features_text = ", ".join(features[:3]) if features else ""
        prompt = f"""Generate SEO-optimized alt text for this Amazon listing image.

Product: {product_name}
Image Type: {image_type.replace("_", " ").title()}
{f"Key Features: {features_text}" if features_text else ""}

REQUIREMENTS:
1. Maximum 125 characters (crucial for accessibility)
2. Include the product name naturally
3. Describe what's visually shown in the image
4. Include 1-2 relevant keywords for SEO
5. No phrases like "image of" or "picture of"
6. Be specific and descriptive

Return ONLY the alt text, nothing else."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt
                ]
            )

            alt_text = response.text.strip()

            # Ensure it's not too long
            if len(alt_text) > 125:
                # Truncate at last word boundary before 125 chars
                alt_text = alt_text[:122].rsplit(' ', 1)[0] + '...'

            logger.info(f"Generated alt text for {image_type}: {alt_text}")
            return alt_text

        except Exception as e:
            logger.error(f"Alt text generation failed: {e}")
            # Fallback to generic alt text
            return f"{product_name} - {image_type.replace('_', ' ').title()} Image"

    def health_check(self) -> dict:
        """Verify API connection"""
        if not self.api_key:
            return {"status": "not_configured", "message": "GEMINI_API_KEY not set"}
        if not self.client:
            return {"status": "error", "message": "Client not initialized"}
        return {
            "status": "configured",
            "model": self.model,
            "provider": "gemini",
            "cost_savings": "10x cheaper than GPT-4o"
        }


def get_gemini_vision_service() -> GeminiVisionService:
    """Dependency injection helper"""
    return GeminiVisionService()

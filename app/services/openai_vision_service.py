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

# NOTE: AI Designer prompts are now in app/prompts/ai_designer.py
# Imported at top: PRINCIPAL_DESIGNER_VISION_PROMPT, GENERATE_IMAGE_PROMPTS_PROMPT,
#                  ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT, GLOBAL_NOTE_INSTRUCTIONS


_OLD_PROMPTS_START = '''You are a Principal Designer with 20+ years experience at top agencies (Apple, Nike, Pentagram).
You're known for creating cohesive, compelling Amazon listing image sets that convert browsers into buyers.

I'm showing you a PRODUCT IMAGE. Analyze it carefully.

PRODUCT CONTEXT:
Product Name: {product_name}
Brand Name: {brand_name}
Key Features: {features}
Target Audience: {target_audience}
Primary Color Preference: {primary_color}

FIRST, ANALYZE THE PRODUCT IMAGE:
- What is the product? Describe what you see.
- What are its visual characteristics (shape, color, texture, size)?
- What category does it belong to?
- What mood/feeling does the product itself convey?
- What type of customer would buy this?

THEN, GENERATE 4 COMPLETELY UNIQUE DESIGN FRAMEWORKS for this product's Amazon listing.
Each framework must be distinctly different in personality, color palette, and approach.
Think like you're presenting 4 options to a Fortune 500 client.

FRAMEWORK REQUIREMENTS:

1. COLOR PALETTE (5 colors with EXACT hex codes):
   IMPORTANT: Base the colors on what you SEE in the product image!
   - Primary (60%): Should complement or enhance the product's natural colors
   - Secondary (30%): Supporting color that creates harmony
   - Accent (10%): Pop of contrast for calls-to-action
   - Text Dark: For dark text on light backgrounds
   - Text Light: For light text on dark backgrounds

2. TYPOGRAPHY (SPECIFIC font names):
   Choose fonts that match the product's personality.
   Good options: Montserrat, Playfair Display, Inter, Poppins, Oswald, Quicksand,
   Source Sans Pro, Roboto, Open Sans, Lato, Raleway, Nunito, DM Sans, Space Grotesk

3. STORY ARC (tailored to THIS specific product):
   - Theme: The narrative thread that connects all 5 images
   - Hook, Reveal, Proof, Dream, Close - BE SPECIFIC to this product

4. COPY FOR EACH IMAGE (tailored headlines for THIS product)

5. VISUAL TREATMENT (lighting, shadows, backgrounds, mood)

FRAMEWORK DIVERSITY:
- Framework 1: "Safe Excellence" - Most likely to convert, professional and polished
- Framework 2: "Bold Creative" - Unexpected but compelling, takes a design risk
- Framework 3: "Emotional Story" - Focuses on feelings and lifestyle aspirations
- Framework 4: "Premium Elevation" - Makes the product feel more luxurious/premium

OUTPUT FORMAT:
Return a valid JSON object with this exact structure:
{{
  "product_analysis": {{
    "what_i_see": "Detailed description of the product from the image",
    "visual_characteristics": "Shape, colors, textures, materials observed",
    "product_category": "Category this product belongs to",
    "natural_mood": "The mood/feeling the product itself conveys",
    "ideal_customer": "Who would buy this product",
    "market_positioning": "Where this product sits in the market"
  }},
  "frameworks": [
    {{
      "framework_id": "framework_1",
      "framework_name": "Creative name for this approach",
      "framework_type": "safe_excellence",
      "design_philosophy": "2-3 sentence design vision tailored to this product",
      "colors": [
        {{"hex": "#XXXXXX", "name": "Color Name", "role": "primary", "usage": "60% - usage description"}},
        {{"hex": "#XXXXXX", "name": "Color Name", "role": "secondary", "usage": "30% - usage description"}},
        {{"hex": "#XXXXXX", "name": "Color Name", "role": "accent", "usage": "10% - usage description"}},
        {{"hex": "#XXXXXX", "name": "Color Name", "role": "text_dark", "usage": "Dark text on light backgrounds"}},
        {{"hex": "#XXXXXX", "name": "Color Name", "role": "text_light", "usage": "Light text on dark backgrounds"}}
      ],
      "typography": {{
        "headline_font": "Font Name",
        "headline_weight": "Bold",
        "headline_size": "48px",
        "subhead_font": "Font Name",
        "subhead_weight": "Regular",
        "subhead_size": "24px",
        "body_font": "Font Name",
        "body_weight": "Regular",
        "body_size": "16px",
        "letter_spacing": "0.5px"
      }},
      "story_arc": {{
        "theme": "The narrative thread for THIS product",
        "hook": "Image 1 strategy specific to this product",
        "reveal": "Image 2 story for this product",
        "proof": "Image 3 demonstration for this product",
        "dream": "Image 4 aspiration with this product",
        "close": "Image 5 conviction for this product"
      }},
      "image_copy": [
        {{"image_number": 1, "image_type": "main", "headline": "", "subhead": null, "feature_callouts": [], "cta": null}},
        {{"image_number": 2, "image_type": "infographic_1", "headline": "Product-specific headline", "subhead": "Optional subhead", "feature_callouts": [], "cta": null}},
        {{"image_number": 3, "image_type": "infographic_2", "headline": "Features headline", "subhead": null, "feature_callouts": ["Feature 1 for THIS product", "Feature 2 for THIS product", "Feature 3 for THIS product"], "cta": null}},
        {{"image_number": 4, "image_type": "lifestyle", "headline": "Aspirational headline for this product", "subhead": null, "feature_callouts": [], "cta": null}},
        {{"image_number": 5, "image_type": "comparison", "headline": "Trust headline for this product", "subhead": null, "feature_callouts": [], "cta": "Call to action"}}
      ],
      "brand_voice": "Description of the copy tone and personality",
      "layout": {{
        "composition_style": "e.g., centered symmetric",
        "whitespace_philosophy": "e.g., generous breathing room",
        "product_prominence": "e.g., hero focus at 60% frame",
        "text_placement": "e.g., left-aligned blocks",
        "visual_flow": "e.g., Z-pattern reading flow"
      }},
      "visual_treatment": {{
        "lighting_style": "e.g., soft diffused from top-left",
        "shadow_spec": "e.g., 0px 8px 24px rgba(0,0,0,0.12)",
        "background_treatment": "e.g., gradient from #BDAEC9 to white, top to bottom",
        "texture": "e.g., subtle grain overlay",
        "mood_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
      }},
      "rationale": "Why this framework works for THIS specific product",
      "target_appeal": "Who this most appeals to"
    }}
  ],
  "generation_notes": "Any notes about your creative decisions based on what you saw in the image"
}}

Generate 4 frameworks following this exact structure.
CRITICAL: Base your designs on what you ACTUALLY SEE in the product image.
Every hex code must be valid. Every font must be real. Every headline must be compelling and SPECIFIC to this product.
'''


# ============================================================================
# STEP 2 PROMPT - GENERATE 5 DETAILED IMAGE PROMPTS FOR SELECTED FRAMEWORK
# ============================================================================
# This prompt has been engineered based on analysis of what makes AI-generated
# images look professional. Each prompt MUST contain the 7 Essential Building Blocks.

GENERATE_IMAGE_PROMPTS_PROMPT = '''You are a world-class Principal Designer creating Amazon listing images.
You have 20+ years experience at Apple, Nike, and Pentagram. Your images CONVERT.

The user has selected a design framework. Now generate 5 DETAILED IMAGE GENERATION PROMPTS
that will be sent DIRECTLY to an AI image generator (Gemini).

=====================================================================
                    THE 7 ESSENTIAL BUILDING BLOCKS
              (Each of your 5 prompts MUST contain ALL 7)
=====================================================================

1. SCENE TYPE DECLARATION (First sentence - sets the foundation)
   - State exactly what KIND of image: "Professional e-commerce product photography",
     "Technical product infographic", "Editorial lifestyle photograph", etc.
   - This tells the AI what visual language to use BEFORE anything else.

2. PHYSICAL INTERACTION & ACTION (What's happening)
   - Static = stock photo feel. Action = editorial quality.
   - Use specific verbs: placing, adjusting, reaching, organizing, demonstrating
   - For lifestyle: "hands gently placing", "person actively using"

3. ENVIRONMENT SPECIFICITY (The context - be VERY detailed)
   - Room type: living room, modern kitchen, minimalist office, bright bathroom
   - Furniture: specific pieces (wooden side table, white floating shelf, marble counter)
   - Lighting: time of day, natural vs artificial, color temperature (e.g., "~5200K daylight")
   - Décor style: minimalist, bohemian, scandinavian, modern farmhouse

4. COLOR SYSTEM (Brand DNA - for UI ONLY, NEVER on product)
   - Primary {primary_hex}, Accent {accent_hex} - for backgrounds, icons, text, UI
   - ★ CRITICAL: Product must appear in its NATURAL colors, not tinted by brand colors
   - Describe WHERE colors appear: "subtle corner gradient", "text in charcoal", "icon accents"
   - NEVER say "product in [brand color]" - the product has its own real colors

5. TYPOGRAPHY SPECIFICATION (The voice - exact details)
   - Font name: "{headline_font}" not just "sans-serif"
   - Weight: "Bold" or "SemiBold" or "Regular"
   - Exact text content in quotes: 'See It in Action' not "a headline"
   - Position: "top center", "bottom left corner", "above the product"

6. COMPOSITION RULES (The structure)
   - Focal point: "product and hands are focal point", "product center, benefits radiating"
   - Safe zones: "leave center clear for Amazon overlay", "text in top third"
   - Hierarchy: what draws the eye first, second, third

7. PHOTOGRAPHY STYLE ANCHOR (The quality standard - last sentence)
   - Reference real-world standards: "Apple product photography quality",
     "editorial lifestyle photography", "professional Amazon listing quality"
   - This sets the QUALITY BAR for the entire image.

=====================================================================
                         PRODUCT INFORMATION
=====================================================================
Product Name: {product_name}
Product Description: {product_description}
Key Features: {features}
Target Audience: {target_audience}

=====================================================================
                      SELECTED DESIGN FRAMEWORK
=====================================================================
Framework Name: {framework_name}
Design Philosophy: {design_philosophy}
Brand Voice: {brand_voice}

COLOR PALETTE (Use these EXACT hex codes in every prompt):
{color_palette}

TYPOGRAPHY SYSTEM (Use these EXACT fonts in every prompt):
- Headlines: {headline_font} {headline_weight}
- Body/Labels: {body_font}

VISUAL TREATMENT:
- Lighting: {lighting_style}
- Background: {background_treatment}
- Mood Keywords: {mood_keywords}

STORY ARC:
- Theme: {story_theme}
- Hook: {story_hook}
- Reveal: {story_reveal}
- Proof: {story_proof}
- Dream: {story_dream}
- Close: {story_close}

IMAGE COPY (Headlines/text for each image):
{image_copy_json}

=====================================================================
              TECHNICAL REQUIREMENTS FOR EACH IMAGE TYPE
           (These are NON-NEGOTIABLE professional standards)
=====================================================================

█████ IMAGE 1: MAIN HERO █████
PURPOSE: Win the click in Amazon search results. Amazon compliance.

AMAZON REQUIREMENTS (NON-NEGOTIABLE):
• Pure white background (#FFFFFF) - MANDATORY
• NO text, NO graphics, NO watermarks, NO logos - NOTHING but product
• Product fills 85%+ of frame
• No props, no lifestyle elements, no hands
• Professional studio lighting (soft, diffused, even)

PHOTOGRAPHY STYLE:
• High-key product photography
• Soft, diffused lighting from multiple angles
• Subtle shadow beneath product for grounding (not floating)
• Hero angle: 3/4 view showing depth and dimension
• Think: Apple product photography, catalog quality

PROMPT STRUCTURE:
"Professional e-commerce product photography of [EXACT PRODUCT] on pure white
background (#FFFFFF). Studio lighting setup with soft diffused key light,
subtle fill, and [specific shadow description]. Product shown at [angle]
filling 85% of frame. [Product details from what you know]. No text,
no graphics, no props. High-resolution catalog photography, Apple product
photography quality."

█████ IMAGE 2: TECHNICAL INFOGRAPHIC █████
PURPOSE: Educate on features, specifications, dimensions.

VISUAL LANGUAGE (What makes it a REAL infographic):
• CALLOUT LINES with pointer arrows connecting to product parts
• FEATURE LABELS: short text (2-4 words) at end of each callout line
• DIMENSION INDICATORS: arrows showing size with measurements
• Multiple product angles if helpful (exploded view, side view)
• Clean GRID or RADIAL layout
• NOT: Splashes, abstract shapes, "creative" decorations

BACKGROUND:
• Light solid color (white, light gray, or brand's lightest color)
• Subtle gradient acceptable (top to bottom or radial)
• NO busy patterns, NO lifestyle elements

TYPOGRAPHY:
• Feature labels: {headline_font} {headline_weight} in small size
• Headline at top: {headline_font} {headline_weight}
• Color: Dark text ({text_dark_hex}) on light background

PROMPT STRUCTURE:
"Technical product infographic for [PRODUCT]. Clean [background color] background
with subtle gradient. Product shown at center with [N] callout lines extending
to feature labels: [Feature 1], [Feature 2], [Feature 3]. Thin lines in
[accent color] with arrow endpoints. Dimension arrows showing [size].
Headline '[HEADLINE TEXT]' at top in {headline_font} Bold. Professional
technical illustration style, Amazon listing infographic quality."

█████ IMAGE 3: BENEFITS SHOWCASE █████
PURPOSE: Communicate WHY to buy. Emotional benefits, not just features.

VISUAL LANGUAGE:
• ICON + TEXT pairings (grid layout: 2x3 or 3x2)
• Benefits as OUTCOMES: "Brighten Any Room" not "Made of Ceramic"
• Simple, recognizable icons (not complex illustrations)
• Product shown at medium size (30-40% of frame)
• Clear visual hierarchy: headline > product > benefits grid

LAYOUT OPTIONS:
• Product center or left, benefits radiating/listed on right
• 2x3 grid of benefit icons with short labels
• Clean sections with breathing room between elements

BACKGROUND:
• Brand color (light/subtle version): {primary_hex} at 15-20% opacity
• Or complementary soft color
• Can include subtle geometric pattern

PROMPT STRUCTURE:
"Benefits-focused infographic for [PRODUCT]. [Layout description] with product
positioned [where]. Background: subtle [color] gradient. Show [N] benefit
icons in [icon style] style with labels: '[Benefit 1]', '[Benefit 2]',
'[Benefit 3]'. Icons in [accent color]. Headline '[HEADLINE]' at top in
{headline_font} Bold [color]. Brand logo '[BRAND]' in top-right corner,
small. Clean, modern Amazon listing design quality."

█████ IMAGE 4: LIFESTYLE PHOTOGRAPHY █████
PURPOSE: Help buyer visualize owning and using the product.

CRITICAL REQUIREMENTS (What makes it REAL lifestyle):
• REAL HUMAN BEING: At minimum hands, ideally arms or more
• REAL ENVIRONMENT: Actual room/space, not studio, not abstract
• ACTIVE INTERACTION: Person USING/TOUCHING the product, not posed statue
• NATURAL LIGHTING: Daylight feeling, not harsh studio lights
• CONTEXTUAL PROPS: Furniture and décor matching target audience

WHAT LIFESTYLE IS NOT:
✗ Product on colored background with "creative" splashes
✗ Product floating in abstract space
✗ Product with illustrated elements around it
✗ Stock photo feeling (stiff poses, fake smiles)

ENVIRONMENT SPECIFICITY (Be EXTREMELY detailed):
• Room: "bright modern living room", "cozy bedroom with soft linens"
• Furniture: "small wooden side table", "white marble kitchen counter"
• Lighting: "natural daylight streaming through window, ~5200K"
• Style: "scandinavian minimalist", "warm bohemian", "clean modern"
• Props: Other items that would naturally be nearby

PERSON DESCRIPTION:
• Demographics matching target audience
• What they're wearing (casual, professional, etc.)
• What they're doing with the product (specific action verb)
• Their positioning relative to product

TEXT (Minimal or none):
• Lifestyle images speak for themselves
• If text: small emotional headline in corner, not blocking action
• Brand logo small in corner (optional)

★★★ EXAMPLE OF EXCELLENT LIFESTYLE PROMPT ★★★
(Use this structure as your template for Image 4)

"Editorial lifestyle photograph showing real human hands (feminine, well-manicured)
gently placing or adjusting a small succulent plant inside [THE PRODUCT].

Scene Setup:
- Real person's hands actively interacting with the product - placing it on a
  small table or adjusting the plant inside
- Setting: Bright, modern interior room with white or soft pastel walls
- Surface: Small wooden side table next to a window
- Natural daylight streaming in, crisp and bright (approximately 5200K)

Color Palette & Accents:
- Primary accent color: [brand primary color]
- Subtle [primary color] corner accents or soft fade in upper corners
- Clean, minimal aesthetic

Typography (if any text):
- Top of image: '[HEADLINE]' in {headline_font} Bold, dark gray text
- Positioned near top to keep center clear

Branding:
- '[BRAND NAME]' logo text in top-right corner, modest size

Composition:
- Leave center of image clear (no text blocking the action)
- Product and hands are the focal point
- Casual, inviting at-home atmosphere
- Lifestyle demonstration feel - capturing a moment of real use

Style: Professional Amazon listing quality, editorial lifestyle photography,
bright and inviting, NOT stock photo feel."

█████ IMAGE 5: COMPARISON / PACKAGE / MULTI-USE █████
PURPOSE: Overcome final objections. Close the sale.

OPTIONS (Choose the most appropriate for this product):

OPTION A - SIZE COMPARISON:
• Product next to common objects (hand, coin, phone, ruler, coffee cup)
• Clear dimension callouts
• Helps customer understand actual size
• Layout: product + comparison object side by side

OPTION B - PACKAGE CONTENTS:
• Flat lay of EVERYTHING included in the purchase
• "What's in the box" layout
• Each item labeled
• Shows value (customer sees all they get)
• Clean white or brand-color background

OPTION C - MULTIPLE USE CASES:
• 2x2 or 3x1 grid showing product in different situations
• "Perfect for..." scenarios
• Different rooms, occasions, or ways to use
• Expands perceived versatility

OPTION D - BEFORE/AFTER or VS COMPARISON:
• If applicable to product category
• Clear visual difference
• Trust-building comparison

BACKGROUND:
• Clean, neutral (white or very light brand color)
• Consistent with other images in set

TEXT:
• Labels for each element/use case
• Small headline describing what's shown
• Trust badges if applicable (ratings, certifications)

PROMPT STRUCTURE:
"[Type: Package contents/Size comparison/Use cases] image for [PRODUCT].
[Specific layout: flat lay on white, 2x2 grid, side-by-side]. Show
[specific elements to include]. Each [item/scene] labeled with
{headline_font} Regular text in [color]. Headline '[TEXT]' at top.
Background: [clean white/light brand color]. Professional Amazon
listing quality, clear and informative."

=====================================================================
                      BRAND COHESION REQUIREMENTS
               (What makes all 5 images look like a SET)
=====================================================================

All 5 images MUST share these elements for cohesion:

1. COLOR CONSISTENCY (CRITICAL - FOR UI ELEMENTS ONLY):
   ★★★ NEVER APPLY BRAND COLORS TO THE PRODUCT ITSELF ★★★
   The product must ALWAYS appear in its NATURAL, REAL-WORLD colors.
   Brand colors are ONLY for:
   - Background gradients, color washes, corner accents
   - Text and headlines
   - Icons and callout elements
   - Decorative UI elements (bars, dividers, badges)

   WHERE TO USE PRIMARY COLOR {primary_hex}:
   - Subtle background gradient or accent
   - Icon fills
   - Headline color (if appropriate)
   - Decorative elements

   WHERE NEVER TO USE BRAND COLORS:
   - The product itself (keep product natural)
   - Hands/skin of people in lifestyle shots
   - Natural elements (plants, wood, etc.)

   Text colors: {text_dark_hex} or {text_light_hex}

2. TYPOGRAPHY CONSISTENCY:
   - Same font family ({headline_font}) for all headlines
   - Same font ({body_font}) for all body/labels
   - Consistent sizing hierarchy

3. LIGHTING CONSISTENCY:
   - Same color temperature feel (~5200K bright, or whatever the framework specifies)
   - Same mood (bright/airy vs warm/cozy) across all images
   - Product MUST retain its natural color - lighting should enhance, not tint

4. QUALITY CONSISTENCY:
   - All images at same professional level
   - No mixing of styles (e.g., one photorealistic, one illustrated)

5. BRAND ELEMENTS:
   - Logo in same position (top-right corner) on images 2-5
   - Logo at same relative size
   - (Image 1 has NO logo - Amazon requirement)

=====================================================================
                         OUTPUT FORMAT
=====================================================================
Return a valid JSON object with this exact structure:

★★★ CRITICAL PROMPT REQUIREMENTS ★★★
Each prompt in "prompt" field MUST be:
- MINIMUM 300 words, ideally 400-500 words
- Contain ALL 7 building blocks mentioned above
- Be SPECIFIC and DETAILED, not vague
- NEVER truncate or cut short
- Include EXACT text for any headlines/labels
- Specify EXACT colors (hex codes) for UI elements
- Describe the product in its NATURAL colors (not brand colors)

If a prompt is under 250 words, it is TOO SHORT and will produce poor results.
Take your time. Be meticulous. These prompts go directly to the AI image generator.

{{
  "generation_prompts": [
    {{
      "image_number": 1,
      "image_type": "main",
      "composition_notes": "Pure product hero on white, 85% fill, studio lighting",
      "key_elements": ["white background", "product only", "no text", "studio lighting"],
      "prompt": "[Your detailed 400-500 word prompt - must include all 7 building blocks]"
    }},
    {{
      "image_number": 2,
      "image_type": "infographic_1",
      "composition_notes": "Technical breakdown with callout lines and feature labels",
      "key_elements": ["callout lines", "arrows", "feature labels", "dimensions"],
      "prompt": "[Your detailed 400-500 word prompt - include specific callout text, line descriptions]"
    }},
    {{
      "image_number": 3,
      "image_type": "infographic_2",
      "composition_notes": "Benefits grid with icons and emotional outcomes",
      "key_elements": ["benefit icons", "grid layout", "emotional headlines", "brand colors"],
      "prompt": "[Your detailed 400-500 word prompt - include specific benefit labels, icon descriptions]"
    }},
    {{
      "image_number": 4,
      "image_type": "lifestyle",
      "composition_notes": "Real person using product in natural environment",
      "key_elements": ["real hands/person", "natural environment", "action/interaction", "editorial quality"],
      "prompt": "[Your detailed 400-500 word prompt - be VERY specific about person, environment, action]"
    }},
    {{
      "image_number": 5,
      "image_type": "comparison",
      "composition_notes": "[Size comparison / Package contents / Multiple uses] layout",
      "key_elements": ["[relevant elements for chosen type]"],
      "prompt": "[Your detailed 300-500 word prompt following the appropriate COMPARISON template above]"
    }}
  ]
}}

=====================================================================
                           CRITICAL REMINDERS
=====================================================================

1. Each prompt MUST be 300-500 words - EXTREMELY DETAILED
2. Each prompt MUST be RADICALLY DIFFERENT (5 different image TYPES!)
3. Each prompt MUST include ALL 7 building blocks
4. Each prompt MUST use the EXACT hex codes from the framework
5. Each prompt MUST use the EXACT font names from the framework
6. Image 1 MUST have pure white background and NO text whatsoever
7. Image 4 MUST feature a real human being (hands minimum) in a real environment
8. The lifestyle image (4) should follow the example template structure closely
9. All prompts should end with a quality anchor statement
'''


# ============================================================================
# STEP 3 PROMPT - ENHANCE PROMPT WITH USER FEEDBACK (REGENERATION)
# ============================================================================
# This prompt enables the AI Designer to intelligently interpret user feedback
# and rewrite prompts rather than just appending notes.
#
# IMPORTANT: This uses the AI's OWN NOTES from the initial analysis, not the
# actual images. This is intentional - the AI already "saw" the product and
# wrote down what it observed. Re-sending images would be wasteful.

ENHANCE_PROMPT_WITH_FEEDBACK_PROMPT = '''You are the Principal Designer who created the original image prompt.
The user has seen the generated image and provided feedback for regeneration.

Your job is to INTERPRET their feedback and REWRITE the prompt to achieve what they want.
Do NOT just append their note. UNDERSTAND what they're asking for and modify the prompt accordingly.

=====================================================================
                    YOUR NOTES ABOUT THE PRODUCT
=====================================================================
When you first analyzed this product, you wrote these observations:

{product_analysis}

=====================================================================
                    THE DESIGN FRAMEWORK YOU CREATED
=====================================================================
Framework: {framework_name}
Philosophy: {design_philosophy}

Color Palette:
{color_palette}

Typography: {typography}

Brand Voice: {brand_voice}

=====================================================================
                    CURRENT IMAGE CONTEXT
=====================================================================
Image Type: {image_type} (Image {image_number} of 5)

ORIGINAL PROMPT YOU WROTE:
{original_prompt}

=====================================================================
                         USER FEEDBACK
=====================================================================
{user_feedback}

=====================================================================
                         YOUR TASK
=====================================================================

1. INTERPRET the feedback:
   - What is the user actually asking for?
   - Is it about colors? Lighting? Composition? Text? Background? Product placement?
   - Are they asking for more/less of something?
   - Are they pointing out something that went wrong?
   - Reference YOUR NOTES about the product if needed (you already analyzed it)

2. REWRITE the prompt:
   - Keep everything that was working
   - Modify the specific parts that address the feedback
   - Be EXPLICIT about the changes (AI image generators need clear instruction)
   - If they want "more glow", say exactly HOW (e.g., "add soft ethereal glow effect around product edges, with subtle light bloom")
   - If they want a "white table", specify it clearly in the scene description
   - Use YOUR NOTES to inform decisions (e.g., if they say "match the product color", refer to your analysis)

3. MAINTAIN COHESION:
   - Use the EXACT color palette from the framework (hex codes listed above)
   - Keep the same typography specifications
   - Keep the brand voice consistent
   - The image should still feel like part of the set

=====================================================================
                         OUTPUT FORMAT
=====================================================================
Return a JSON object with this structure:
{{
  "interpretation": "What I understand the user wants changed",
  "changes_made": ["Change 1", "Change 2", "Change 3"],
  "enhanced_prompt": "The complete rewritten prompt (300-500 words, ready to send to image generator)"
}}

CRITICAL: The enhanced_prompt must be a COMPLETE prompt, not just the changes.
It should be ready to send directly to the image generator.
'''
# END OF OLD PROMPTS - These are now imported from app/prompts/ai_designer.py
# The variable assignments above are kept for backwards compatibility but NOT USED
# All actual prompts come from the import at the top of this file


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
    ) -> Dict[str, Any]:
        """
        STEP 3: Enhance/rewrite a prompt based on user feedback.

        Called when user requests regeneration with a note. Instead of just
        appending the note, the AI Designer interprets the feedback and
        rewrites the prompt intelligently.

        IMPORTANT: This uses the AI's OWN NOTES (product_analysis) from the
        initial framework generation, not the actual images. The AI already
        "saw" the product and wrote down observations - no need to re-send images.

        Args:
            original_prompt: The prompt that was used for the original image
            user_feedback: What the user wants changed
            image_type: Which image type (main, infographic_1, etc.)
            framework: Optional - the design framework for context
            product_analysis: Optional - the AI's notes from initial analysis

        Returns:
            Dict with 'interpretation', 'changes_made', and 'enhanced_prompt'
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized - check OPENAI_API_KEY")

        # Map image type to number
        image_number = {
            'main': 1,
            'infographic_1': 2,
            'infographic_2': 3,
            'lifestyle': 4,
            'comparison': 5,
        }.get(image_type, 1)

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
            image_number=image_number,
            framework_name=framework_name,
            design_philosophy=design_philosophy,
            color_palette=color_palette,
            typography=typography,
            brand_voice=brand_voice,
            original_prompt=original_prompt,
            user_feedback=user_feedback,
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

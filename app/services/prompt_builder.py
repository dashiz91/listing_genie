"""
Listing image prompt builder.

Consolidates the 5 per-image-type prompt template methods that were
duplicated in GenerationService into a single module with shared setup.
"""
import logging
from typing import List, Optional

from app.models.database import GenerationSession, ImageTypeEnum
from app.schemas.generation import DesignFramework

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared setup helpers
# ---------------------------------------------------------------------------

def _extract_features(session: GenerationSession) -> List[str]:
    return [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]


def _extract_colors(fw: DesignFramework):
    """Return (primary, secondary, accent) hex strings."""
    primary = fw.colors[0].hex if fw.colors else '#1a1a1a'
    secondary = fw.colors[1].hex if len(fw.colors) > 1 else '#4a90d9'
    accent = fw.colors[2].hex if len(fw.colors) > 2 else '#27ae60'
    return primary, secondary, accent


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_framework_prompt(
    session: GenerationSession,
    image_type: ImageTypeEnum,
    framework: DesignFramework,
) -> str:
    """
    Build a prompt for the given image type using the design framework.

    Priority:
    1. If framework has GPT-4o generated prompts for this image number, use directly.
    2. Otherwise fall back to our template-based prompts.
    """
    image_type_map = {
        ImageTypeEnum.MAIN: 1,
        ImageTypeEnum.INFOGRAPHIC_1: 2,
        ImageTypeEnum.INFOGRAPHIC_2: 3,
        ImageTypeEnum.LIFESTYLE: 4,
        ImageTypeEnum.COMPARISON: 5,
    }
    image_num = image_type_map.get(image_type, 1)

    # Priority 1: GPT-4o generated prompts
    if framework.generation_prompts:
        for gen_prompt in framework.generation_prompts:
            if gen_prompt.image_number == image_num:
                logger.info(f"Using GPT-4o generated prompt for {image_type.value} (image {image_num})")
                return gen_prompt.prompt

    # Priority 2: Template-based prompts
    logger.info(f"No GPT-4o prompt found, using template for {image_type.value}")

    # Get the specific copy for this image type
    image_copy = None
    for copy in framework.image_copy:
        if copy.image_number == image_num:
            image_copy = copy
            break
    if not image_copy and framework.image_copy:
        image_copy = framework.image_copy[0]

    builder = _TEMPLATE_BUILDERS.get(image_type, _build_main_image_prompt)
    if image_type == ImageTypeEnum.MAIN:
        return builder(session, framework)
    return builder(session, framework, image_copy)


# ---------------------------------------------------------------------------
# Template builders (one per image type)
# ---------------------------------------------------------------------------

def _build_main_image_prompt(
    session: GenerationSession,
    fw: DesignFramework,
    _image_copy=None,
) -> str:
    features = _extract_features(session)
    features_str = ', '.join(features) if features else 'premium quality product'

    return f"""=== AMAZON MAIN LISTING IMAGE - HERO SHOT ===

PRODUCT: {session.product_title}
KEY FEATURES: {features_str}

=== CRITICAL AMAZON REQUIREMENTS (MANDATORY) ===
This is Image 1 of 5 - The MAIN HERO image that appears in search results.
Amazon has STRICT requirements that MUST be followed:

1. PURE WHITE BACKGROUND (#FFFFFF)
   - The background MUST be completely white, no gradients, no off-white
   - No shadows on the background (product shadow on white is OK if subtle)
   - White must extend to all edges of the image

2. PRODUCT ONLY - ABSOLUTELY NO TEXT
   - NO headlines, NO captions, NO watermarks, NO logos
   - NO call-to-action text, NO feature callouts
   - NO brand names written in the image
   - The ONLY element in the image is the product itself

3. NO ADDITIONAL GRAPHICS
   - NO icons, NO badges, NO stickers
   - NO "Best Seller" labels or similar
   - NO decorative elements whatsoever
   - NO lifestyle props or accessories (unless part of the actual product)

4. PRODUCT FILLS 85% OF FRAME
   - The product should dominate the image
   - Some white space around edges (but product is prominent)
   - Product should be shown at its most flattering angle

=== PHOTOGRAPHY STYLE ===
Think: Apple product photography, high-end catalog, premium e-commerce

LIGHTING:
- Soft, diffused studio lighting from multiple angles
- No harsh shadows - use fill lights to soften
- Subtle product shadows allowed (grounds the product, adds dimension)
- Even illumination across the entire product
- Highlight the product's best features through strategic lighting

ANGLE & COMPOSITION:
- 3/4 view angle is often most flattering (shows depth)
- Or straight-on hero shot if product is flat/simple
- Center the product in the frame
- Slight elevation can add gravitas
- Show the full product - no cropping of important features

PRODUCT PRESENTATION:
- Product should look pristine, perfect condition
- Show the product in its "hero state" - how it looks when brand new
- If the product has multiple parts, show them arranged attractively
- Any packaging should be removed unless packaging IS the product

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format (Amazon standard)
- High resolution, sharp focus on product
- No motion blur, no depth of field effects that obscure product
- True-to-life colors (accurate product representation)
- Professional e-commerce product photography quality

=== DESIGN CONTEXT (FOR CONSISTENCY) ===
Framework: {fw.framework_name}
Visual Mood: {', '.join(fw.visual_treatment.mood_keywords)}

The product photography style should subtly reflect the premium, professional nature
of the {fw.framework_name} design system while strictly adhering to Amazon requirements.

=== FINAL OUTPUT ===
Generate a PURE PRODUCT PHOTOGRAPHY image:
- Pristine white background
- Product as the sole hero
- Zero text, zero graphics
- Professional studio lighting
- 85% frame fill
- Ready for Amazon search results

This image must STOP THE SCROLL when shoppers browse Amazon search results.
It should communicate quality, professionalism, and trustworthiness through
the product presentation alone - no text needed.
"""


def _build_infographic_1_prompt(
    session: GenerationSession,
    fw: DesignFramework,
    image_copy=None,
) -> str:
    features = _extract_features(session)
    primary_color, accent_color, _ = _extract_colors(fw)
    # Use secondary as accent for infographic 1
    accent_color = fw.colors[1].hex if len(fw.colors) > 1 else '#4a90d9'

    callouts = []
    if image_copy and image_copy.feature_callouts:
        callouts = image_copy.feature_callouts
    elif features:
        callouts = features[:4]
    callouts_str = '\n'.join([f"   - {c}" for c in callouts]) if callouts else "   - Premium Materials\n   - Quality Construction"

    return f"""=== AMAZON INFOGRAPHIC IMAGE 1 - TECHNICAL BREAKDOWN ===

PRODUCT: {session.product_title}

=== IMAGE PURPOSE ===
This is Image 2 of 5 - The TECHNICAL INFOGRAPHIC.
Purpose: Show customers the TECHNICAL DETAILS, MATERIALS, and SPECIFICATIONS.
Think: Product engineering diagram meets clean marketing infographic.

=== VISUAL COMPOSITION TYPE ===
This is NOT a simple product photo with text overlay.
This is a TECHNICAL BREAKDOWN with the following elements:

1. CENTRAL PRODUCT IMAGE
   - Product shown from an angle that reveals multiple components
   - Could be: 3/4 view, exploded view, or cross-section view
   - Product is still the hero but not filling entire frame
   - Leave space around product for callouts

2. CALLOUT LINES & ARROWS (MANDATORY)
   - Clean, thin lines (2-3px) extending from product to text
   - Lines should be straight with 90-degree bends (not curved)
   - Arrow tips pointing TO specific product features
   - Color: {accent_color} or white with subtle shadow
   - Professional engineering drawing style

3. FEATURE CALLOUT BOXES
   - Small, clean text boxes at the end of each callout line
   - Semi-transparent or solid background for readability
   - Each box highlights ONE specific feature

   CALLOUTS TO INCLUDE:
{callouts_str}

4. DIMENSION ANNOTATIONS (if applicable)
   - Include measurement lines showing product size
   - Use standard dimension notation: arrows on both ends
   - Display key measurements (height, width, depth)
   - Professional technical drawing style

=== DESIGN SPECIFICATIONS ===
COLOR PALETTE:
- Primary text/elements: {primary_color}
- Accent color (arrows, highlights): {accent_color}
- Background: Clean gradient or subtle pattern (NOT pure white - distinguish from main image)
- Recommended: Light gray to white gradient, or subtle brand color tint

TYPOGRAPHY:
- Font: {fw.typography.headline_font} or clean sans-serif
- Callout text: Bold, legible at thumbnail size (14-18pt equivalent)
- Use ALL CAPS for feature names, sentence case for descriptions
- High contrast for readability

LAYOUT:
- Product centered or slightly left/right to balance callouts
- Callouts distributed evenly around product
- Visual flow guides eye from product to features
- Whitespace between elements for clarity

=== INFOGRAPHIC ELEMENTS STYLE ===
DO include:
- Technical callout lines with arrows
- Small icons next to features (optional)
- Dimension lines with measurements
- Clean boxes/badges for feature text
- Subtle background pattern or gradient

DO NOT include:
- Lifestyle elements or people
- Busy or cluttered backgrounds
- Decorative swirls or flourishes
- Too many competing focal points
- Text that overlaps the product

=== VISUAL MOOD ===
Framework: {fw.framework_name}
Mood: {', '.join(fw.visual_treatment.mood_keywords)}

This should feel: Technical, Informative, Premium, Professional, Trustworthy
Think: High-end product specification sheet as a beautiful infographic

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format
- All text must be legible at 100x100px thumbnail
- High contrast between text and background
- Professional, clean, engineering-meets-marketing aesthetic

=== FINAL OUTPUT ===
Generate an INFOGRAPHIC-STYLE technical breakdown showing:
- Product with space for callouts
- 3-5 callout lines with arrows pointing to specific features
- Feature text in clean boxes
- Dimension annotations (if applicable)
- Professional, technical, yet beautiful presentation

This image should EDUCATE the customer about product specifications
while maintaining visual appeal and brand consistency.
"""


def _build_infographic_2_prompt(
    session: GenerationSession,
    fw: DesignFramework,
    image_copy=None,
) -> str:
    features = _extract_features(session)
    primary_color, secondary_color, accent_color = _extract_colors(fw)

    headline = image_copy.headline if image_copy else "Why Choose Our Product?"

    benefits = []
    if image_copy and image_copy.feature_callouts:
        benefits = image_copy.feature_callouts
    elif features:
        benefits = features
    benefits_str = '\n'.join([f"   {i+1}. {b}" for i, b in enumerate(benefits)]) if benefits else "   1. Premium Quality\n   2. Durable Design\n   3. Easy to Use"

    return f"""=== AMAZON INFOGRAPHIC IMAGE 2 - BENEFITS & FEATURES ===

PRODUCT: {session.product_title}

=== IMAGE PURPOSE ===
This is Image 3 of 5 - The BENEFITS INFOGRAPHIC.
Purpose: Show customers the KEY BENEFITS in an organized, scannable format.
Think: Marketing flyer meets modern icon-driven design.

=== VISUAL COMPOSITION TYPE ===
This is a BENEFITS-FOCUSED INFOGRAPHIC with organized layout:

1. HEADLINE (Top section)
   - Bold, attention-grabbing headline
   - Text: "{headline}"
   - Font: {fw.typography.headline_font}, {fw.typography.headline_weight}
   - Color: {primary_color}

2. PRODUCT IMAGE (Center or Side)
   - Product shown at medium size (not dominating like main image)
   - Position: Center with benefits around it, OR left side with benefits on right
   - Product should be clearly visible but not competing with benefit icons

3. BENEFIT ICONS + TEXT (THE MAIN FEATURE)
   - 3-5 benefit points with ICONS and short text

   BENEFITS TO DISPLAY:
{benefits_str}

   ICON STYLE:
   - Simple, flat icons (not 3D or overly detailed)
   - Consistent style across all icons (all outline OR all filled)
   - Size: Medium (visible at thumbnail)
   - Color: {secondary_color} or {accent_color}

   TEXT STYLE:
   - Bold benefit name/headline
   - Optional: 1-line description below
   - High contrast for readability

4. ORGANIZED LAYOUT
   Options (choose most appropriate):
   - GRID: 2x2 or 3x2 grid of icon+text blocks
   - VERTICAL LIST: Icons stacked with text to the right
   - CIRCULAR: Benefits arranged around central product
   - BANNER: Horizontal rows of benefits

=== DESIGN SPECIFICATIONS ===
COLOR PALETTE:
- Headlines: {primary_color}
- Icons: {secondary_color} or {accent_color}
- Background: Subtle gradient or clean solid (brand-aligned)
- Text backgrounds: Optional subtle boxes for contrast

TYPOGRAPHY:
- Headline: {fw.typography.headline_font}, {fw.typography.headline_weight}
- Benefit titles: Bold, {fw.typography.subhead_font}
- Descriptions: Regular weight, good contrast

LAYOUT PRINCIPLES:
- Clear visual hierarchy: Headline > Product > Benefits
- Even spacing between benefit blocks
- Aligned icons and text (professional grid)
- Breathing room (not cluttered)

=== VISUAL STYLE ===
Framework: {fw.framework_name}
Brand Voice: {fw.brand_voice}
Mood: {', '.join(fw.visual_treatment.mood_keywords)}

STYLE GUIDE:
- Modern, clean, organized
- Scannable at a glance
- Professional marketing quality
- Consistent icon style throughout
- Clear visual hierarchy

DO include:
- Simple, recognizable icons
- Bold benefit headlines
- Subtle supporting text
- Professional layout grid
- Product image (but not dominating)

DO NOT include:
- Photo collages
- Busy backgrounds
- Too many font styles
- Cluttered layouts
- Illegible small text

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format
- All text must be legible at 100x100px thumbnail
- Icons should be recognizable at small sizes
- High contrast for accessibility

=== FINAL OUTPUT ===
Generate a BENEFIT-FOCUSED infographic with:
- Clear headline at top
- Product image (center or side)
- 3-5 benefit icons with short text
- Organized grid or list layout
- Professional, modern, marketing aesthetic

This image should CONVINCE customers of the product's value
through clear, scannable benefit communication.
"""


def _build_lifestyle_prompt(
    session: GenerationSession,
    fw: DesignFramework,
    image_copy=None,
) -> str:
    audience = session.target_audience or "everyday consumers"
    mood = ', '.join(fw.visual_treatment.mood_keywords) if fw.visual_treatment.mood_keywords else 'natural, authentic, relatable'
    headline = image_copy.headline if image_copy else None

    return f"""=== AMAZON LIFESTYLE IMAGE - REAL PERSON IN REAL ENVIRONMENT ===

PRODUCT: {session.product_title}
TARGET AUDIENCE: {audience}

=== IMAGE PURPOSE ===
This is Image 4 of 5 - The LIFESTYLE IMAGE.
Purpose: Show a REAL PERSON using the product in a REAL ENVIRONMENT.
This creates EMOTIONAL CONNECTION and helps customers visualize ownership.
Think: Magazine editorial, authentic photography, aspirational yet relatable.

=== CRITICAL REQUIREMENTS ===
This image MUST feature:

1. A REAL HUMAN BEING (MANDATORY)
   - NOT just the product alone
   - NOT just hands holding the product
   - A FULL or PARTIAL person visible in the image
   - Person should be using/enjoying the product naturally

2. AUTHENTIC ENVIRONMENT (MANDATORY)
   - Real-world setting (home, office, outdoors, etc.)
   - NOT a studio white background
   - NOT an abstract or artificial setting
   - Environment should match product use case

3. NATURAL INTERACTION (MANDATORY)
   - Person actively using or demonstrating the product
   - Natural, candid pose (not stiff or posed)
   - Shows the EXPERIENCE of using the product
   - Product is clearly visible but person is primary subject

=== PERSON SPECIFICATIONS ===
Based on target audience ({audience}):

DEMOGRAPHICS:
- Select a person that represents or appeals to the target audience
- Age, style, and appearance should resonate with likely buyers
- Authentic, relatable, aspirational but not unrealistic

EXPRESSION & POSE:
- Natural, genuine expression (not forced smile)
- Active engagement with product (using, examining, enjoying)
- Body language suggests satisfaction/enjoyment
- Candid feel, not overly posed

CLOTHING & STYLING:
- Appropriate to the environment and activity
- Clean, tasteful, not distracting from product
- Aligns with brand mood: {mood}

=== ENVIRONMENT SPECIFICATIONS ===
SETTING:
- Choose a setting where this product would naturally be used
- Examples based on product type:
  * Kitchen product → Modern home kitchen
  * Fitness product → Gym or outdoor exercise space
  * Office product → Clean, well-lit workspace
  * Beauty product → Bathroom or vanity area
  * Outdoor product → Nature, park, backyard
  * Tech product → Modern living room or office

LIGHTING:
- Natural lighting preferred (window light, golden hour, etc.)
- Soft, flattering lighting on both person and product
- {fw.visual_treatment.lighting_style}
- Warm, inviting atmosphere

BACKGROUND:
- Real environment, slightly blurred (depth of field)
- Not distracting but adds context
- Complementary to brand colors when possible
- Clean but lived-in feel

=== PRODUCT VISIBILITY ===
The product should be:
- Clearly visible in the shot
- Being actively used or held
- NOT the primary focus (person is primary)
- Naturally integrated into the scene
- Visible enough to recognize what it is

Product prominence: 30-40% of viewer attention
Person prominence: 60-70% of viewer attention

=== TEXT OVERLAY (OPTIONAL) ===
{"Include this headline if it enhances the image: " + chr(34) + headline + chr(34) if headline else "Text overlay is OPTIONAL for lifestyle images. The image should tell the story visually."}

If including text:
- Keep it minimal (headline only, if anything)
- Position where it doesn't obscure person or product
- Use brand typography: {fw.typography.headline_font}

=== PHOTOGRAPHY STYLE ===
OVERALL AESTHETIC:
- Editorial/magazine quality photography
- Natural, candid feel (not stock photo fake)
- Warm, inviting atmosphere
- Professional but relatable
- Aspirational without being unattainable

TECHNICAL:
- Shallow depth of field (subject in focus, background slightly soft)
- Natural color grading (not over-processed)
- Good composition following rule of thirds
- Person positioned at 1/3 line, product visible

MOOD:
- {mood}
- {fw.design_philosophy}

=== VISUAL MOOD ===
Framework: {fw.framework_name}
Brand Voice: {fw.brand_voice}

The image should feel:
- Authentic and natural
- Warm and inviting
- Aspirational but achievable
- Connected to real life

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format
- High resolution, professional photography quality
- Natural color grading
- Sharp focus on subject (person with product)

=== FINAL OUTPUT ===
Generate a LIFESTYLE PHOTOGRAPH featuring:
- A real person actively using the product
- Authentic, real-world environment
- Natural lighting and candid feel
- Editorial/magazine photography quality
- Emotional connection that helps customers visualize ownership

This image should make customers FEEL what it's like to own and use this product.
It sells the EXPERIENCE, not just the item.
"""


def _build_comparison_prompt(
    session: GenerationSession,
    fw: DesignFramework,
    image_copy=None,
) -> str:
    primary_color, secondary_color, accent_color = _extract_colors(fw)

    cta = image_copy.cta if image_copy and image_copy.cta else "Order Now"
    headline = image_copy.headline if image_copy else "Everything You Need"

    return f"""=== AMAZON FINAL IMAGE - COMPARISON/CLOSING IMAGE ===

PRODUCT: {session.product_title}

=== IMAGE PURPOSE ===
This is Image 5 of 5 - The CLOSING IMAGE.
Purpose: CLOSE THE SALE. This image should eliminate remaining objections
and give the customer confidence to purchase.
Think: The final push that converts browsers to buyers.

=== COMPOSITION OPTIONS ===
Choose ONE of these approaches based on what would best close the sale:

OPTION A: MULTIPLE USE CASES
- Show 2-4 scenarios where the product excels
- Grid layout showing versatility
- "Use it for X, Y, and Z" visual story
- Demonstrates value through variety

OPTION B: PACKAGE CONTENTS / WHAT'S INCLUDED
- Show all items that come with purchase
- Organized flatlay or arranged display
- Clearly shows everything customer receives
- "You get all of this" presentation

OPTION C: TRUST & CREDIBILITY
- Include trust badges, certifications, awards
- Satisfaction guarantee badges
- Star ratings or review snippets
- "100% Satisfaction Guaranteed" messaging

OPTION D: STYLED BEAUTY SHOT
- Premium styled product photography
- Complementary props that elevate perception
- Aspirational setting (marble surface, greenery, etc.)
- Editorial magazine quality presentation

For this generation, create OPTION A or B (most common for Amazon).

=== VISUAL COMPOSITION ===

IF MULTIPLE USE CASES (Option A):
- 2x2 grid or triptych layout
- Each section shows a different use case
- Consistent styling across all sections
- Labels for each use case (optional)
- Product visible in each scenario

IF PACKAGE CONTENTS (Option B):
- Clean flatlay arrangement
- All items organized aesthetically
- Main product as hero, accessories around it
- Clear labeling of each item (optional)
- Premium presentation of what's included

=== DESIGN SPECIFICATIONS ===
COLOR PALETTE:
- Primary: {primary_color}
- Secondary: {secondary_color}
- Accent: {accent_color}
- Background: Clean, premium (subtle gradient or solid)

HEADLINE:
- Text: "{headline}"
- Position: Top or bottom of image
- Font: {fw.typography.headline_font}, bold
- Color: High contrast for readability

OPTIONAL CTA:
- Text: "{cta}"
- Position: Bottom of image
- Style: Button or badge format
- Color: {accent_color} or contrasting

LAYOUT:
- Clear visual hierarchy
- Organized, professional grid (if applicable)
- Product(s) prominently featured
- Text enhances but doesn't overwhelm

=== VISUAL ELEMENTS ===
DO include:
- Product shown in multiple scenarios OR complete package
- Clear, organized layout
- Optional headline and CTA
- Trust elements (if applicable)
- Premium, professional styling

OPTIONAL additions:
- Satisfaction guarantee badge
- "What's Included" label
- Use case labels
- Subtle icons representing benefits

DO NOT include:
- Cluttered or messy layouts
- Low-quality graphics
- Overwhelming amount of text
- Disconnected visual elements

=== BRAND ALIGNMENT ===
Framework: {fw.framework_name}
Brand Voice: {fw.brand_voice}
Mood: {', '.join(fw.visual_treatment.mood_keywords)}

Visual Treatment:
- Lighting: {fw.visual_treatment.lighting_style}
- Background: {fw.visual_treatment.background_treatment}
- Overall feel: Premium, trustworthy, compelling

=== CLOSING PSYCHOLOGY ===
This image should address:
1. "Is this product versatile enough?" → Show multiple uses
2. "What exactly do I get?" → Show package contents
3. "Can I trust this brand?" → Include trust elements
4. "Is this really premium?" → Styled beauty presentation

The image should make the customer think:
"Yes, I need this. I'm confident in this purchase."

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format
- All text legible at 100x100px thumbnail
- High contrast, clear visual hierarchy
- Professional, e-commerce ready quality

=== FINAL OUTPUT ===
Generate a CLOSING/COMPARISON image that:
- Shows multiple use cases OR package contents
- Includes compelling headline
- Features trust elements or premium styling
- Maintains professional, organized layout
- Creates confidence and urgency to purchase

This image is the FINAL impression before the customer decides to buy.
Make it count.
"""


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_TEMPLATE_BUILDERS = {
    ImageTypeEnum.MAIN: _build_main_image_prompt,
    ImageTypeEnum.INFOGRAPHIC_1: _build_infographic_1_prompt,
    ImageTypeEnum.INFOGRAPHIC_2: _build_infographic_2_prompt,
    ImageTypeEnum.LIFESTYLE: _build_lifestyle_prompt,
    ImageTypeEnum.COMPARISON: _build_comparison_prompt,
}


# ---------------------------------------------------------------------------
# Structural context for AI enhancement (per image type)
# ---------------------------------------------------------------------------

def get_structural_context(image_type: str, *, has_canvas: bool = False) -> str:
    """
    Return preservation rules for AI-enhanced prompt rewriting.

    These rules tell the AI Designer what structural elements must be preserved
    verbatim when rewriting a prompt based on user feedback. Different image types
    have different sacred elements (canvas inpainting, named image labels, format
    constraints, etc.).
    """
    if has_canvas:
        return (
            "PRESERVE VERBATIM: All canvas inpainting instructions, "
            "the 'completing a partially filled canvas' block, CANVAS_TO_COMPLETE reference, "
            "split/crop directives, and named image labels (PRODUCT_PHOTO, STYLE_REFERENCE, PREVIOUS_MODULE). "
            "Only modify creative/visual scene description."
        )
    if image_type == "aplus_hero":
        return (
            "PRESERVE VERBATIM: The tall 4:3 format, the split-into-two-halves instruction, "
            "and named image references (PRODUCT_PHOTO, STYLE_REFERENCE). "
            "Only modify creative/visual direction."
        )
    if image_type.startswith("aplus_"):
        return (
            "PRESERVE VERBATIM: Named image labels (PRODUCT_PHOTO, STYLE_REFERENCE, PREVIOUS_MODULE), "
            "1464x600 A+ banner format constraints, and module position/continuity instructions. "
            "Only modify creative/visual scene description."
        )
    # Listing types
    if image_type == "main":
        return "PRESERVE: White/clean background requirement. Product must remain centered and prominent."
    return "PRESERVE: Product reference instructions and typography specifications."

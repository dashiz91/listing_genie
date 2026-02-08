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
        ImageTypeEnum.TRANSFORMATION: 5,
        ImageTypeEnum.COMPARISON: 6,
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


def _build_transformation_prompt(
    session: GenerationSession,
    fw: DesignFramework,
    image_copy=None,
) -> str:
    """
    Build the TRANSFORMATION image prompt (Image 5 of 6).

    Based on StoryBrand + JTBD: The customer is the HERO on a journey.
    This image shows their transformation - the before/after of their LIFE STATE.
    Not a product comparison, but a LIFE comparison.
    """
    primary_color, secondary_color, accent_color = _extract_colors(fw)

    headline = image_copy.headline if image_copy else "Your Life, Upgraded"

    return f"""=== AMAZON TRANSFORMATION IMAGE - THE HERO'S JOURNEY ===

PRODUCT: {session.product_title}

=== THE FRAMEWORK ===
This image is built on three principles from the world's greatest business thinkers:

1. JOBS TO BE DONE (Clayton Christensen):
   The customer isn't buying a product. They're "hiring" it to do a JOB.
   What job is {session.product_title} hired to do? Show the JOB GETTING DONE.

2. STORYBRAND (Donald Miller):
   The customer is the HERO, not your product. Your product is the GUIDE.
   Show the hero's transformation — who they BECOME with this product.

3. SYSTEM 1 THINKING (Daniel Kahneman):
   Decisions are emotional first, rational second.
   Trigger FEELING before thinking. Show, don't tell.

=== IMAGE PURPOSE ===
This is Image 5 of 6 - The TRANSFORMATION IMAGE.
Purpose: Show the HERO'S JOURNEY. The customer's life BEFORE vs AFTER.
Not a product comparison — a LIFE STATE comparison.

The viewer should see themselves transforming from:
→ Struggling/Incomplete/Frustrated (subtle, not dramatic)
TO:
→ Successful/Complete/Satisfied (aspirational, achievable)

=== COMPOSITION OPTIONS ===
Choose ONE approach that best shows the transformation:

OPTION A: SPLIT LIFE COMPARISON
- Left side: Life WITHOUT (muted, incomplete, subtle frustration)
- Right side: Life WITH (vibrant, complete, satisfaction)
- Same person/setting, different states
- Product visible on the "after" side
- The contrast should be FELT, not analyzed

OPTION B: THE MOMENT OF TRANSFORMATION
- Single scene showing the pivotal moment
- The instant where the job gets DONE
- Customer experiencing the solution
- Before state implied, after state shown
- Emotional peak of the journey

OPTION C: THE HERO VICTORIOUS
- Customer in their "success state"
- Having completed the job they hired the product for
- Confidence, satisfaction, completion visible
- Product present but customer is the hero
- Aspirational but attainable

OPTION D: THE JOURNEY MAP
- Visual narrative showing progression
- Multiple moments: struggle → discovery → success
- Product as the turning point
- Story arc visible in composition
- Before/during/after flow

For this generation, create OPTION A or B (strongest transformation impact).

=== THE JOB TO BE DONE ===
Think: What frustrating situation made them search for this product?
What does their life look like when that frustration is SOLVED?

NOT: "This vase holds flowers"
BUT: "Their living room finally feels put-together when guests arrive"

NOT: "This pan heats evenly"
BUT: "They're confident cooking for people they want to impress"

NOT: "This organizer has 12 compartments"
BUT: "They start each day feeling in control, not frantic"

Show the JOB getting done, not the product features.

=== VISUAL COMPOSITION ===

IF SPLIT COMPARISON (Option A):
- 50/50 or 60/40 split (favor the "after")
- "Before" side: Desaturated, cooler tones, subtle tension
- "After" side: Warm, vibrant, resolution
- Same environment, transformed mood
- Product bridges the gap visually
- NO text labels like "Before/After" — let the image speak

IF MOMENT OF TRANSFORMATION (Option B):
- Single powerful scene
- The exact moment the job gets done
- Customer's expression shows relief/satisfaction
- Product in use, solving the problem
- Golden hour or warm lighting
- Editorial magazine quality

=== DESIGN SPECIFICATIONS ===
COLOR PALETTE:
- "Before" elements: Cooler, muted, less saturated
- "After" elements: {primary_color}, {secondary_color} warmth
- Accent: {accent_color} on transformation moment
- Overall: Warm, hopeful, resolved

HEADLINE (Optional):
- Text: "{headline}"
- Position: Supporting the transformation narrative
- Font: {fw.typography.headline_font}, bold
- Only include if it enhances, not explains

EMOTIONAL TEMPERATURE:
- Before: Slight tension, incompleteness (subtle, not dramatic)
- After: Warmth, satisfaction, completion
- Transition: Hope, possibility, relief

=== THE CUSTOMER AS HERO ===
This image answers: "Who do I BECOME when I own this?"

The customer should see themselves in the "after" state and think:
"That's who I want to be. That's the life I want."

The product is Yoda, not Luke. The mentor, not the hero.
The customer is the hero who transforms.

=== VISUAL ELEMENTS ===
DO include:
- Real person experiencing the transformation
- Authentic emotion (not stock photo smiles)
- The job being DONE, not the product being used
- Life context that grounds the transformation
- Aspirational but achievable outcome

DO NOT include:
- Fake before/after text labels
- Dramatic over-the-top transformation
- Product as the hero/centerpiece
- Feature callouts or specifications
- Anything that feels like an ad vs a story

=== BRAND ALIGNMENT ===
Framework: {fw.framework_name}
Brand Voice: {fw.brand_voice}
Mood: {', '.join(fw.visual_treatment.mood_keywords)}

Visual Treatment:
- Lighting: {fw.visual_treatment.lighting_style}
- Background: {fw.visual_treatment.background_treatment}
- Overall feel: Transformative, hopeful, achieved

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format
- High emotional impact
- Professional photography quality
- Warm color temperature overall
- Clear visual narrative

=== FINAL OUTPUT ===
Generate a TRANSFORMATION image that:
- Shows the customer's life state before vs after (not product comparison)
- Makes the customer the HERO of the story
- Demonstrates the JOB getting done
- Triggers emotional response (System 1) before rational thought
- Creates desire to experience that transformation

The viewer should think:
"I want to go from THERE to HERE. This product is how I get there."

This image sells the TRANSFORMATION, not the transaction.
"""


def _build_comparison_prompt(
    session: GenerationSession,
    fw: DesignFramework,
    image_copy=None,
) -> str:
    primary_color, secondary_color, accent_color = _extract_colors(fw)

    cta = image_copy.cta if image_copy and image_copy.cta else "Upgrade Your Life"
    headline = image_copy.headline if image_copy else "Experience the Difference"

    return f"""=== AMAZON FINAL IMAGE - FOMO/CLOSING IMAGE ===

PRODUCT: {session.product_title}

=== IMAGE PURPOSE ===
This is Image 6 of 6 - The FOMO CLOSING IMAGE.
Purpose: Create EMOTIONAL URGENCY. Make them feel what they're missing.
This isn't about logic — it's about the gap between their current life
and the upgraded life that's one click away.
Think: "Others are already enjoying this. Why aren't you?"

=== COMPOSITION OPTIONS ===
Choose ONE approach that creates the strongest FOMO for THIS product:

OPTION A: TRANSFORMATION / BEFORE-AFTER FEELING
- Split or comparison showing the UPGRADE in life quality
- Left: The "without" state (subtle, muted, incomplete)
- Right: The "with" state (vibrant, complete, elevated)
- NOT a product comparison — a LIFE comparison
- The viewer should FEEL the gap

OPTION B: SOCIAL PROOF / "EVERYONE HAS THIS"
- Show the product in an aspirational lifestyle context
- Multiple instances suggesting widespread adoption
- "Join thousands who've upgraded" visual story
- Create the feeling of being left behind without it
- Premium, curated, enviable presentation

OPTION C: THE MOMENT THEY'RE MISSING
- Capture a specific, desirable moment the product enables
- Golden hour lighting, perfect composition
- The exact moment they've been dreaming about
- Make them viscerally WANT to be in that scene
- "This could be your life" energy

OPTION D: CURATED LIFESTYLE FLATLAY
- Product as centerpiece of an aspirational life
- Surrounding items suggest taste, success, intentionality
- "People who own this also have refined taste"
- Premium surface (marble, wood, linen)
- Editorial, magazine-quality presentation

For this generation, create OPTION A, B, or C (strongest FOMO drivers).

=== VISUAL COMPOSITION ===

IF TRANSFORMATION (Option A):
- Split composition or subtle before/after
- "Without" side: desaturated, incomplete, ordinary
- "With" side: vibrant, complete, elevated
- Product bridges the transformation
- Emotional contrast is key

IF SOCIAL PROOF (Option B):
- Lifestyle setting showing widespread use
- Multiple people or contexts enjoying the product
- Premium, aspirational environment
- "You're missing out" energy
- Subtle urgency without pressure

IF THE MOMENT (Option C):
- Single powerful lifestyle shot
- Perfect lighting (golden hour, soft natural)
- Human interaction or implied human presence
- The exact moment they fantasize about
- Kinfolk/Cereal magazine aesthetic

=== DESIGN SPECIFICATIONS ===
COLOR PALETTE:
- Primary: {primary_color}
- Secondary: {secondary_color}
- Accent: {accent_color}
- Background: Premium, aspirational (warm tones for desire)

HEADLINE:
- Text: "{headline}"
- Position: Creates maximum emotional impact
- Font: {fw.typography.headline_font}, bold
- Tone: Speaks to desire, not features

CTA (Amazon-Compliant):
- Text: "{cta}"
- Position: Bottom of image
- Style: Inviting, not pushy
- NO fake urgency, NO "limited time", NO scarcity claims

LAYOUT:
- Emotional impact over information density
- Product is the hero of a desirable scene
- Text enhances the feeling, doesn't explain it
- White space creates aspiration

=== VISUAL ELEMENTS ===
DO include:
- Product in an aspirational, desirable context
- Warm, inviting lighting
- Human elements (hands, lifestyle, implied presence)
- Premium styling and surfaces
- Emotional resonance over information

FOMO TRIGGERS (subtle, not aggressive):
- The life they could be living
- The moment they're not experiencing yet
- The upgrade others are enjoying
- The gap between "now" and "with this product"

DO NOT include:
- Fake urgency ("Limited time!", "Almost gone!")
- Misleading scarcity claims
- Aggressive countdown timers
- Price comparisons or discounts
- Anything that violates Amazon ToS

=== BRAND ALIGNMENT ===
Framework: {fw.framework_name}
Brand Voice: {fw.brand_voice}
Mood: {', '.join(fw.visual_treatment.mood_keywords)}

Visual Treatment:
- Lighting: {fw.visual_treatment.lighting_style} — warm, inviting
- Background: {fw.visual_treatment.background_treatment}
- Overall feel: Aspirational, desirable, attainable

=== FOMO PSYCHOLOGY ===
This image should trigger:
1. "Others are enjoying this right now" → Social proof
2. "My life could look like this" → Aspiration gap
3. "I don't want to miss this feeling" → Emotional urgency
4. "This is the upgrade I've been waiting for" → Permission to desire

The viewer should think:
"I can see myself in this picture. I WANT to be in this picture.
Others are already there. Why am I still hesitating?"

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format
- All text legible at 100x100px thumbnail
- Warm color temperature for desire
- Professional, editorial quality

=== FINAL OUTPUT ===
Generate a FOMO-driven closing image that:
- Creates emotional urgency through aspiration, not pressure
- Shows the life/moment the product enables
- Makes the viewer FEEL what they're missing
- Uses social proof or transformation visuals
- Stays 100% Amazon ToS compliant (no fake urgency)

This is the image that converts "maybe later" into "add to cart."
Make them FEEL the gap. Make them want to close it.
"""


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_TEMPLATE_BUILDERS = {
    ImageTypeEnum.MAIN: _build_main_image_prompt,
    ImageTypeEnum.INFOGRAPHIC_1: _build_infographic_1_prompt,
    ImageTypeEnum.INFOGRAPHIC_2: _build_infographic_2_prompt,
    ImageTypeEnum.LIFESTYLE: _build_lifestyle_prompt,
    ImageTypeEnum.TRANSFORMATION: _build_transformation_prompt,
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
            "PRESERVE VERBATIM: The leading '=== REFERENCE IMAGES ===' header block, "
            "the tall 4:3 format, the split-into-two-halves instruction, "
            "and named image references (PRODUCT_PHOTO, STYLE_REFERENCE). "
            "Only modify creative/visual direction."
        )
    if image_type.startswith("aplus_"):
        return (
            "PRESERVE VERBATIM: The leading '=== REFERENCE IMAGES ===' header block, "
            "named image labels (PRODUCT_PHOTO, STYLE_REFERENCE, PREVIOUS_MODULE), "
            "1464x600 A+ banner format constraints, and module position/continuity instructions. "
            "Only modify creative/visual scene description."
        )
    # Listing types
    if image_type == "main":
        return "PRESERVE: White/clean background requirement. Product must remain centered and prominent."
    return "PRESERVE: Product reference instructions and typography specifications."

"""
A+ Content Module Prompt Templates - Emotional Storytelling

These templates power the Art Director visual script system for generating
Premium A+ Content images. Uses the same emotional storytelling approach
as listing images — making viewers FEEL, not just understand.

Philosophy: Great A+ content is a visual journey that deepens the emotional
connection established by the listing images. Each banner pulls the customer
deeper into desire until buying feels inevitable.
"""
import json
from typing import Optional

from ..vocabulary import get_aplus_quality_standard, get_storytelling_standard, EMOTIONAL_ARC
from ..product_protection import PRODUCT_PROTECTION_DIRECTIVE


# ============================================================================
# LEGACY PROMPTS (fallback when no visual script exists)
# ============================================================================

APLUS_FULL_IMAGE_BASE = """Sotheby's catalog. Campaign imagery. Cinematic.

You're creating a premium A+ Content banner for {product_title}.
Brand "{brand_name}" needs a wide frame that makes them FEEL something.

The audience — {target_audience} — should feel drawn in instantly.
This isn't a product photo. This is a moment they want to live in.

Don't show features. Show the FEELING of owning this:
{features}

CREATIVE DIRECTION ({framework_name}):
{framework_style}
Hero color: {primary_color} — anchor the composition, don't flood it.
Palette: {color_palette}
Mood: {framework_mood}

THE PRODUCT IS SACRED:
Use the product reference photos to capture the REAL product — its materials,
proportions, colors, and character. Never invent a different product.
Brand colors live in atmosphere — lighting, surfaces, gradients.
Never flat graphic overlays. Never touching the product itself.

CREATE FEELING, NOT INFORMATION:
- Don't describe what the product IS
- Show what life FEELS LIKE with it
- Create a scene they want to step into
- Make them imagine reaching for it

FORMAT:
Wide cinematic banner (2.4:1). Editorial, not catalog.
Breathing room at edges — the design extends beyond the frame.

ABSOLUTE RULES:
- NEVER include website UI, Amazon navigation, browser chrome
- Render SHORT bold text baked into the image (headlines 2-5 words max)
- Render brand name / product name prominently
- If BRAND_LOGO reference image is provided, reproduce the logo
- Use EXACT framework font names and hex colors for all text
- HIGH CONTRAST text — light on dark, dark on light. Readable at 50% zoom.
"""

APLUS_CONTINUITY_ADDITION = """
CONTINUITY:
This banner sits directly below another. Make the seam disappear.
Match gradient direction, color temperature, lighting angle, shadow behavior.
Both banners are one continuous canvas split in two.
"""

APLUS_FULL_IMAGE_FIRST = APLUS_FULL_IMAGE_BASE + """
OPENING MOVE — AWE:
First thing they see in your A+ section. Create immediate impact.
The viewer should think: "Wow, this is beautiful."
Design with downward momentum — draw them deeper into the story.
"""

APLUS_FULL_IMAGE_CHAINED = APLUS_FULL_IMAGE_BASE + APLUS_CONTINUITY_ADDITION

APLUS_FULL_IMAGE_LAST = APLUS_FULL_IMAGE_BASE + APLUS_CONTINUITY_ADDITION + """
CLOSING FRAME — CERTAINTY:
Final banner. The emotional journey resolves.
Customer feels: "I've seen enough. I want this. I'm ready."
No more questions. Just quiet confidence in their choice.
"""


def get_aplus_prompt(
    module_type: str,
    position: str,  # "first", "middle", "last", or "only"
    product_title: str,
    brand_name: str,
    features: list[str],
    target_audience: str,
    framework_name: str,
    framework_style: str,
    primary_color: str,
    color_palette: list[str],
    framework_mood: str,
    custom_instructions: str = ""
) -> str:
    """
    Generate the appropriate A+ module prompt based on position in chain.
    Used as fallback when no Art Director visual script exists.
    """
    if module_type == "full_image":
        if position == "first":
            template = APLUS_FULL_IMAGE_FIRST
        elif position in ("middle", "last"):
            template = APLUS_FULL_IMAGE_CHAINED if position == "middle" else APLUS_FULL_IMAGE_LAST
        else:
            template = APLUS_FULL_IMAGE_BASE
    else:
        template = APLUS_FULL_IMAGE_BASE

    prompt = template.format(
        product_title=product_title,
        brand_name=brand_name or "Premium Brand",
        features=", ".join(features) if features else "Quality craftsmanship",
        target_audience=target_audience or "Discerning customers",
        framework_name=framework_name,
        framework_style=framework_style,
        primary_color=primary_color,
        color_palette=", ".join(color_palette) if color_palette else primary_color,
        framework_mood=framework_mood,
    )

    if custom_instructions:
        prompt += f"\n\nCLIENT NOTE:\n{custom_instructions}"

    return prompt


# ============================================================================
# ART DIRECTOR VISUAL SCRIPT SYSTEM
# ============================================================================

VISUAL_SCRIPT_PROMPT = """You are an Art Director creating COHESIVE A+ Content that extends the listing's brand story.

═══════════════════════════════════════════════════════════════════════════════
                     THE FUNDAMENTAL TRUTH ABOUT A+ CONTENT
═══════════════════════════════════════════════════════════════════════════════

The listing images created a brand impression. If your A+ modules use DIFFERENT
fonts, colors, or visual language, you DESTROY that trust instantly.

The shopper thinks: "Wait, this looks different... is this even the same product?"

**A+ Content must be VISUALLY CONTINUOUS with the listing images.**

Same fonts. Same colors. Same visual language. ONE cohesive brand story.

═══════════════════════════════════════════════════════════════════════════════

Today: Amazon Premium A+ Content — {module_count} full-width banners (1464×600).
These stack below the listing images as ONE emotional journey.

THE PRODUCT:
- {product_title}
- Brand: {brand_name}
- What makes it special: {features}
- Who it's for: {target_audience}

═══════════════════════════════════════════════════════════════════════════════
        ⚠️  THE DESIGN SYSTEM - MUST MATCH LISTING IMAGES EXACTLY  ⚠️
═══════════════════════════════════════════════════════════════════════════════

Framework: {framework_name}
Philosophy: {design_philosophy}

**COLOR PALETTE** (Use ONLY these colors — same as listing images):
{color_palette}

**TYPOGRAPHY** (Use ONLY these fonts — same as listing images):
{typography}

⚠️  CRITICAL RULES:
1. Every text element uses the framework fonts — NO OTHER FONTS
2. Every background/accent color comes from the palette — NO INVENTED COLORS
3. When writing prompts, specify EXACT font names and hex codes
4. This consistency is what makes 6 listings + 6 A+ modules feel like ONE brand

Story arc: {story_arc}
Visual treatment: {visual_treatment}

Study the attached product photos. Notice materials, finish, scale, color.
Your script must reflect the REAL product, not an imagined one.

═══════════════════════════════════════════════════════════════════════════════
                    🎯 A+ IS THE CLOSE, NOT ANOTHER HOOK
═══════════════════════════════════════════════════════════════════════════════

CRITICAL: Listings and A+ have DIFFERENT JOBS in the conversion funnel.

**LISTINGS (Images 1-6) = THE HOOK**
Job: Get them interested enough to KEEP SCROLLING
- Already showed: Product beauty, features, lifestyle, transformation, social proof
- Already answered: "What is it?", "Is it quality?", "What do I get?", "Will it fit my life?"

**A+ CONTENT (Modules 0-5) = THE CLOSE**
Job: Remove final objections and get them to BUY NOW
- Must NOT repeat listing content (they already saw it!)
- Must go DEEPER: details they couldn't see, objections they still have, more contexts

⚠️  REPETITION = WASTED REAL ESTATE
If listings showed a before/after transformation, A+ should NOT show another before/after.
If listings showed lifestyle context, A+ should show DIFFERENT lifestyle contexts.

WHAT A+ SHOULD DO DIFFERENTLY:
- Extreme close-ups (craftsmanship details not visible in listings)
- Address the #1 remaining objection explicitly
- Show MORE lifestyle contexts (different rooms, different uses)
- Final certainty push (the "why not?" becomes "why wait?")

═══════════════════════════════════════════════════════════════════════════════
                    THE EMOTIONAL JOURNEY — DEEPEN INTO DESIRE
═══════════════════════════════════════════════════════════════════════════════

By the time they reach A+ Content, they've seen the listing images.
They're already INTERESTED. Now deepen that into IRRESISTIBLE DESIRE.

Each module should make them FEEL something NEW:
- Not "4,900 mAh battery" → "A full day without worrying about power"
- Not "Premium ceramic" → "The kind of object you reach for every morning"
- Not "Modern design" → "Understated confidence on your shelf"

THE A+ EMOTIONAL ARC (builds on listings, doesn't repeat):
- Modules 0+1 (Hero): AWE — "Wow, this is even more beautiful up close"
- Module 2: DEPTH — "There's more here than I realized" (details not in listings)
- Module 3: REASSURANCE — "My concern is addressed" (objection handling)
- Module 4: IMAGINATION — "I can see this in multiple parts of my life"
- Module 5: CERTAINTY — "I have no more questions. I'm ready."

═══════════════════════════════════════════════════════════════════════════════
                         THE EDITORIAL DESIGN SYSTEM
═══════════════════════════════════════════════════════════════════════════════

STRUCTURE — THE {module_count}-MODULE ARC:

Modules 0+1 = HERO PAIR. ONE continuous image split in half.
Product DRAMATICALLY LARGE, filling full height of both modules combined.
Module 0: Top portion (50-60% of product visible, cropped at bottom).
Module 1: Reveals the rest + brand name + product name as bold text.
Together: "wow" moment — brand statement + visual impact.

Modules 2-5 = INDEPENDENT editorial compositions. Each one MUST use a
DIFFERENT archetype (see below). Variety is what makes premium A+ stand out.

═══════════════════════════════════════════════════════════════════════════════
                    MODULE DESIGN ARCHETYPES
═══════════════════════════════════════════════════════════════════════════════

Assign ONE archetype per module — EVERY module MUST use a DIFFERENT archetype.
This creates the visual variety seen in Apple, Sony, Bose, GoPro, Anker A+ pages.

"hero_brand": Large product + bold brand name + product name + tagline
  → Text: Product name LARGE, brand name, short tagline (2-4 words)
  → Always modules 0+1 (hero pair)
  → Think: Bose burgundy monochrome, Sony Bravia hero

"exploded_detail": Product broken into components, extreme close-ups of internals
  → Text: Component labels (1-2 words each: "ND Filter", "Macro Lens", "USB-C Port")
  → Think: GoPro lens exploded view, Dyson cutaway, Anker charger internals

"in_the_box": All included items laid out cleanly on solid background with labels
  → Text: "WHAT'S INCLUDED" header + item name labels
  → Think: Nintendo Switch unboxing layout, Apple AirPods box contents

"lifestyle_action": Product in dramatic real-world use with a person
  → Text: One aspirational headline (2-4 words) OR no text
  → Think: Stanley pickleball action, New Balance running, GoPro surfing

"trust_authority": Social proof, awards, stats — the credibility module
  → Text: 2-3 stat badges ("#1 Brand", "6.5M+ Users", "35 Patents", "Award Winner")
  → Think: Levoit "#1 HUMIDIFIER BRAND", Anker "#1 Mobile Charging Brand"

"product_in_context": Product shown in natural environment (room, desk, kitchen, shelf)
  → Text: One evocative headline (2-4 words) OR no text
  → Think: Sony TV on wall, Bose headphones on nightstand, YETI cooler at campsite

"dramatic_mono": Single product on bold solid color, dramatic studio lighting, minimal
  → Text: Brand name only, or NO text — let the product speak
  → Think: Bose burgundy/ice blue monochrome shots, Apple product-on-white

DIVERSITY RULE: Each module MUST use a DIFFERENT archetype. If 6 modules,
use 6 different archetypes. NEVER repeat the same archetype twice.

BACKGROUND RHYTHM — Alternate using ONLY framework palette colors:
- Modules 0+1 (hero): Framework primary color
- Module 2: Lightest palette color
- Module 3: Darkest palette color (drama beat)
- Module 4: Light again
- Module 5: Return to primary/secondary (bookend)

Every background MUST be from the framework palette or a tint/shade of one.

MODULE EMOTIONAL ROLES (pair with archetype):
- "hero_reveal": Pure visual impact — "Wow" (always modules 0+1, archetype: hero_brand)
- "intrigue": Draw them deeper — "Tell me more"
- "trust": Prove quality through craft — "This is well-made"
- "belonging": Show their life with it — "This fits me"
- "desire": Create longing — "I want this feeling"
- "certainty": Remove doubt — "I'm ready to buy"

═══════════════════════════════════════════════════════════════════════════════
                         TYPOGRAPHY — WORDS THAT FEEL
═══════════════════════════════════════════════════════════════════════════════

TEXT IN IMAGE — PREMIUM BRAND STANDARD:
Premium Amazon A+ always renders text BAKED INTO the image. This is non-negotiable.

HERO PAIR (modules 0+1):
- Module 0: Product dominates. Brand name can appear small at top.
- Module 1: Brand name + Product name (large, bold). Short tagline optional.

FEATURE MODULES (2-5) — text depends on archetype:
- hero_brand: Brand name LARGE, product name, tagline
- exploded_detail: Component labels (1-2 words each), arranged near parts
- in_the_box: "WHAT'S INCLUDED" header + item labels
- lifestyle_action: One aspirational headline (2-4 words) OR no text
- trust_authority: 2-3 stat badges rendered as bold text/graphics
- product_in_context: One evocative headline (2-4 words) OR no text
- dramatic_mono: Brand name only OR no text

TEXT RENDERING RULES:
- ALL text SHORT — 2-5 words max per headline. Fewer words = cleaner.
- Use EXACT framework font names and EXACT hex colors for text
- HIGH CONTRAST: light text on dark, dark text on light. Always readable.
- Text must be LARGE enough to read at 50% zoom
- Keep text to ONE SIDE — never scatter across image
- NO paragraphs, NO long sentences, NO fine print
- Stat badges: bold number + short label ("6.5M+ Users", "#1 Brand")

COPYWRITING RULES:
- Headlines create FEELING, not describe features
- WRONG: "Water-Tight Interior" → RIGHT: "Every Morning, Fresh"
- WRONG: "Premium Ceramic Material" → RIGHT: "Made to Last"
- Body copy paints a moment, not lists specs

⚠️  FONT/COLOR CONSISTENCY (NON-NEGOTIABLE):
- Use the EXACT font names from the typography section — not "elegant serif"
- Use the EXACT hex codes from the palette — not "soft blue" or "warm tone"
- This ensures A+ modules match the listing images perfectly

CRITICAL: Describe fonts and colors SEPARATELY from text strings.
  BAD:  "BRAND NAME" in Quicksand Bold #544381
  GOOD: The text "BRAND NAME" appears large and bold, colored #544381.

═══════════════════════════════════════════════════════════════════════════════
                         CONTINUITY SYSTEM
═══════════════════════════════════════════════════════════════════════════════

Modules 0+1 = HERO PAIR technique: ONE tall 4:3 image split at midpoint.
Both halves from same pixel output — guaranteed perfect alignment.

Write a single `hero_pair_prompt` (200-350 words) at top level of JSON.
Do NOT write `generation_prompt` for modules 0 or 1.

hero_pair_prompt must include:
1. Format: "Single tall 4:3 image (~1464×1098). Split at midpoint."
2. Product: ONE product crossing midline — large, dynamic angle
3. Background: exact hex from palette, continuous top to bottom
4. Typography: bottom half only — brand name + product name
5. Top half: NO text, pure product photography
6. Reference images: "Use PRODUCT_PHOTO. Match STYLE_REFERENCE mood."
7. Rules: no website UI, no Amazon navigation, no product packaging

═══════════════════════════════════════════════════════════════════════════════
                         REFERENCE IMAGES
═══════════════════════════════════════════════════════════════════════════════

Each banner receives:
- `PRODUCT_PHOTO` — the actual product (always)
- `STYLE_REFERENCE` — visual style direction (if available)
- `BRAND_LOGO` — the brand's logo image (if available)
- `PREVIOUS_MODULE` — banner above (modules 1+ only)

Your prompts MUST reference PRODUCT_PHOTO, STYLE_REFERENCE, and BRAND_LOGO by name.
If BRAND_LOGO is provided, hero pair and trust/brand modules should reproduce it.

═══════════════════════════════════════════════════════════════════════════════
                         OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

Respond with ONLY valid JSON:
{{
  "narrative_theme": "Single sentence capturing the EMOTIONAL journey",
  "color_flow": "How palette evolves — which module gets which color",
  "background_strategy": "Rhythm pattern",
  "hero_pair_prompt": "COMPLETE 200-350 word prompt for tall 4:3 hero image — MUST include brand name + product name as bold text in bottom half. Reference PRODUCT_PHOTO, STYLE_REFERENCE, and BRAND_LOGO by name.",
  "modules": [
    {{
      "index": 0,
      "archetype": "hero_brand",
      "role": "hero_reveal",
      "emotional_beat": "awe",
      "viewer_thought": "Wow, this is beautiful",
      "headline": "NO TEXT",
      "mood": "Feeling this evokes",
      "scene_description": "50-100 words: top half — describe the FEELING, not just visuals",
      "render_text": null
    }},
    {{
      "index": 1,
      "archetype": "hero_brand",
      "role": "hero_reveal",
      "emotional_beat": "awe",
      "viewer_thought": "I want to know more",
      "headline": "Brand + Product Name",
      "mood": "Feeling",
      "scene_description": "50-100 words: bottom half — brand name + product name as text",
      "render_text": {{"headline": "Product Name", "brand_name": "BRAND", "tagline": "Short tagline 2-4 words", "text_position": "center"}}
    }},
    {{
      "index": 2,
      "archetype": "exploded_detail | in_the_box | lifestyle_action | trust_authority | product_in_context | dramatic_mono",
      "role": "intrigue | trust | belonging | desire | certainty",
      "emotional_beat": "intrigue",
      "viewer_thought": "What the viewer unconsciously thinks",
      "mood": "...",
      "scene_description": "OPTIONAL — only for continuity",
      "render_text": {{
        "headline": "2-5 evocative words OR null",
        "brand_name": "BRAND or null",
        "stat_badges": ["#1 Brand", "6.5M+ Users"],
        "component_labels": ["Part Name", "Feature Name"],
        "text_position": "left | right | center | scattered"
      }},
      "generation_prompt": "COMPLETE 200-350 word prompt — FEELING first, then visuals. MUST specify what text to render in the image and where."
    }}
  ]
}}

IMPORTANT: Each module index 2-5 MUST have a DIFFERENT archetype value.
The render_text fields depend on archetype:
- hero_brand: headline, brand_name, tagline
- exploded_detail: component_labels, headline optional
- in_the_box: headline ("WHAT'S INCLUDED"), component_labels for items
- lifestyle_action: headline only (or null for no text)
- trust_authority: stat_badges (2-3 bold stats), brand_name
- product_in_context: headline only (or null for no text)
- dramatic_mono: brand_name only (or null for no text)

Generate exactly {module_count} modules. Each creates FEELING — no filler, no feature lists.
"""


APLUS_MODULE_WITH_SCRIPT = """Sotheby's catalog. Campaign imagery. Cinematic.

You're executing a premium A+ banner for {product_title}.
The Art Director scripted the entire section as one EMOTIONAL JOURNEY.
Bring THIS frame to life — faithful to the feeling, with craft and instinct.

PRODUCT:
- Brand: {brand_name}
- What creates desire: {features}
- Who dreams of this: {target_audience}

VISUAL IDENTITY ({framework_name}):
{design_philosophy}
Anchor color: {primary_color} | Palette: {color_palette}
Mood: {framework_mood}

THE ART DIRECTOR'S EMOTIONAL VISION:
"{narrative_theme}"
Color journey: {color_flow}
Background world: {background_strategy}
Seam technique: {edge_connection_strategy}

YOUR FRAME — Module {module_index} of {module_count} ({module_role}):
DESIGN ARCHETYPE: {module_archetype}
Headline: "{module_headline}"
Product treatment: {module_product_angle}
Background: {module_background}
Visual elements: {module_elements}
THE FEELING: {module_mood}
What the viewer thinks: {module_content_focus}

{render_text_instruction}

EDGE CONTRACTS:
- Top edge resolves to: {top_edge}
- Bottom edge sets up: {bottom_edge}

POSITION: {module_position}
{position_instruction}

FEELING FIRST:
- Don't just show the product — create a moment they want to live in
- Every element should deepen desire, not deliver information
- The viewer should FEEL something, not just understand something
- Wide format (2.4:1) — cinematic, not catalog

CRAFT NOTES:
- Use PRODUCT_PHOTO for REAL product. Honor materials and proportions.
- Use STYLE_REFERENCE for visual direction. Match mood, lighting, sophistication.
- If BRAND_LOGO is provided, reproduce it faithfully in the image where appropriate.
- Brand colors in scene naturally — lighting, surfaces, atmosphere
- Frame from a premium brand film, not a template
- NEVER include website UI, Amazon navigation, browser chrome
- Render text SHORT and BOLD — baked into the image like premium brand A+
- Text must be LARGE enough to read at 50% zoom, HIGH CONTRAST

{continuity_instruction}"""


# ============================================================================
# IMAGE LABEL CONSTANTS
# ============================================================================

IMAGE_LABEL_PRODUCT = "PRODUCT_PHOTO"
IMAGE_LABEL_STYLE = "STYLE_REFERENCE"
IMAGE_LABEL_PREVIOUS = "PREVIOUS_MODULE"


CANVAS_INPAINTING_PROMPT = """CANVAS_TO_COMPLETE is split in two:
- TOP HALF: Finished photograph showing {previous_scene_description}
- BOTTOM HALF: Solid bright green (#00FF00) — placeholder to replace

YOUR TASK: Replace bottom green half with new content. ONE seamless photograph.
Bottom half should show: {current_scene_description}

EMOTIONAL CONTINUITY:
The previous module created a feeling. Continue that feeling while deepening it.
The viewer shouldn't notice a transition — just a continuous journey of desire.

RULES:
- Keep top half intact — do NOT change it
- Replace ONLY the bottom green half
- Transition must be seamless — ONE continuous image, no visible seam
- Same lighting direction, perspective, surfaces continuing
- Same EMOTIONAL temperature — don't jar them out of the feeling
- Use PRODUCT_PHOTO for real product reference
- Use STYLE_REFERENCE for visual style and mood
"""


HERO_PAIR_PROMPT = """Generate ONE single tall portrait photograph — NOT two separate panels.
This image will later be cropped into two halves. Must look like one seamless photo top to bottom.

THE GOAL: Create immediate AWE. The viewer's first thought should be "Wow."
Not "What is this?" or "What are the features?" Just: "Wow, this is beautiful."

CRITICAL: Do NOT compose as "top section" and "bottom section."
Think: ONE tall editorial magazine photograph that happens to be cropped later.
The viewer should NOT be able to tell where the crop line is.

REFERENCE IMAGES:
- PRODUCT_PHOTO: The actual product — honor materials, proportions, character
- STYLE_REFERENCE: Match this visual style, mood, and color treatment
- BRAND_LOGO: If provided, reproduce this logo in the bottom half near brand name

═══ ART DIRECTOR'S CREATIVE BRIEF ═══

{hero_pair_brief}

═══ EMOTIONAL IMPACT (NON-NEGOTIABLE) ═══
- This is the FIRST thing they see in A+ content
- After listing images, they're interested — now make them DESIRE
- Pure visual impact. No information needed.
- Create the "wow" moment that pulls them deeper into the story

═══ COMPOSITION RULES (NON-NEGOTIABLE) ═══
- ONE continuous photograph, NOT two stacked panels
- Product naturally spans vertical center of image
- Background: one continuous color/gradient top to bottom — no dividing lines
- Bottom half: brand name + product name as BOLD text, integrated naturally
- If BRAND_LOGO provided, place logo in bottom half near brand name
- Top half: pure product photography, minimal or no text
- NEVER include website UI, Amazon navigation, browser chrome
- Do NOT duplicate the product — show it ONCE, large, crossing center

{custom_instructions_block}"""


def build_hero_pair_prompt(
    visual_script: dict,
    product_title: str,
    brand_name: str,
    custom_instructions: str = "",
) -> str:
    """Build unified prompt for hero pair (modules 0+1)."""
    hero_brief = visual_script.get("hero_pair_prompt")

    # Fallback for old visual scripts
    if not hero_brief:
        modules = visual_script.get("modules", [])
        parts = []
        if len(modules) > 0 and modules[0].get("generation_prompt"):
            parts.append(f"TOP HALF:\n{modules[0]['generation_prompt']}")
        if len(modules) > 1 and modules[1].get("generation_prompt"):
            parts.append(f"BOTTOM HALF:\n{modules[1]['generation_prompt']}")
        hero_brief = "\n\n".join(parts) if parts else (
            f"Dramatic product hero for {product_title} by {brand_name}. "
            f"Single tall 4:3 image (~1464×1098). Product crosses midline, dramatically large. "
            f"Typography in bottom half only — brand name smaller, product name large and bold. "
            f"Top half is pure product photography, no text."
        )

    custom_block = f"\nCLIENT NOTE:\n{custom_instructions}" if custom_instructions else ""

    return HERO_PAIR_PROMPT.format(
        hero_pair_brief=hero_brief,
        custom_instructions_block=custom_block,
    )


def build_canvas_inpainting_prompt(
    previous_scene_description: str,
    current_scene_description: str,
) -> str:
    """Build the inpainting prompt for canvas extension."""
    return CANVAS_INPAINTING_PROMPT.format(
        previous_scene_description=previous_scene_description,
        current_scene_description=current_scene_description,
    )


def get_aplus_module_prompt(visual_script: dict, module_index: int, custom_instructions: str = "") -> Optional[str]:
    """
    Look up pre-written generation prompt for a module from visual script.
    Returns None if not found (caller should fall back to legacy).
    """
    modules = visual_script.get("modules", [])
    if module_index >= len(modules):
        return None
    module = modules[module_index]
    prompt = module.get("generation_prompt")
    if not prompt:
        return None
    if custom_instructions:
        prompt += f"\n\nCLIENT NOTE:\n{custom_instructions}"
    return prompt


def get_visual_script_prompt(
    product_title: str,
    brand_name: str,
    features: list[str],
    target_audience: str,
    framework: dict,
    module_count: int = 5,
    listing_prompts: Optional[list] = None,
) -> str:
    """Build the Art Director visual script prompt with listing context."""

    # Build listing context summary so A+ knows what NOT to repeat
    listing_context = ""
    if listing_prompts:
        listing_summary = []
        for p in listing_prompts:
            img_type = p.get("image_type", "unknown")
            job = p.get("job", p.get("emotional_beat", ""))
            listing_summary.append(f"- Image {p.get('image_number', '?')} ({img_type}): {job}")

        listing_context = f"""
═══════════════════════════════════════════════════════════════════════════════
                    📋 WHAT LISTINGS ALREADY COVERED (DO NOT REPEAT)
═══════════════════════════════════════════════════════════════════════════════

The listing images already showed:
{chr(10).join(listing_summary)}

⚠️  A+ Content must NOT duplicate these concepts. Go DEEPER, not WIDER.
- If listings showed transformation → A+ shows DIFFERENT transformation or skips it
- If listings showed lifestyle → A+ shows DIFFERENT lifestyle contexts
- If listings showed features → A+ shows DETAILS (close-ups, craftsmanship)

"""

    prompt = VISUAL_SCRIPT_PROMPT.format(
        module_count=module_count,
        product_title=product_title,
        brand_name=brand_name or "Premium Brand",
        features=", ".join(features) if features else "Quality craftsmanship",
        target_audience=target_audience or "Discerning customers",
        framework_name=framework.get("framework_name", "Professional"),
        design_philosophy=framework.get("design_philosophy", "Clean and modern"),
        color_palette=", ".join(
            c.get("hex", "") for c in framework.get("colors", [])
        ) or "#C85A35",
        typography=json.dumps(framework.get("typography", {})),
        story_arc=json.dumps(framework.get("story_arc", {})),
        visual_treatment=json.dumps(framework.get("visual_treatment", {})),
    )

    # Insert listing context after the design system section
    if listing_context:
        # Find a good insertion point
        insertion_marker = "Study the attached product photos."
        if insertion_marker in prompt:
            prompt = prompt.replace(insertion_marker, listing_context + insertion_marker)

    return prompt


def build_aplus_module_prompt(
    product_title: str,
    brand_name: str,
    features: list[str],
    target_audience: str,
    framework: dict,
    visual_script: dict,
    module_index: int,
    module_count: int = 5,
    custom_instructions: str = "",
    is_chained: bool = False,
) -> str:
    """Build rich per-module prompt using Art Director's visual script."""
    modules = visual_script.get("modules", [])
    if module_index >= len(modules):
        position = "first" if module_index == 0 else "middle"
        colors = framework.get("colors", [])
        return get_aplus_prompt(
            module_type="full_image",
            position=position,
            product_title=product_title,
            brand_name=brand_name,
            features=features,
            target_audience=target_audience,
            framework_name=framework.get("framework_name", "Professional"),
            framework_style=framework.get("design_philosophy", "Clean and modern"),
            primary_color=colors[0].get("hex", "#C85A35") if colors else "#C85A35",
            color_palette=[c.get("hex", "") for c in colors],
            framework_mood=framework.get("brand_voice", "Professional"),
            custom_instructions=custom_instructions,
        )

    mod = modules[module_index]

    # Extract archetype and render_text from visual script
    module_archetype = mod.get("archetype", "product_in_context")
    render_text = mod.get("render_text") or {}

    # Build render_text instruction based on archetype
    render_text_parts = []
    if render_text:
        headline = render_text.get("headline")
        brand_name = render_text.get("brand_name")
        tagline = render_text.get("tagline")
        stat_badges = render_text.get("stat_badges", [])
        component_labels = render_text.get("component_labels", [])
        text_position = render_text.get("text_position", "left")

        render_text_parts.append(f"TEXT RENDERING (bake into image, {text_position} side):")
        if brand_name:
            render_text_parts.append(f"- Brand name: \"{brand_name}\" — render prominently")
        if headline:
            render_text_parts.append(f"- Headline: \"{headline}\" — bold, large, readable at 50% zoom")
        if tagline:
            render_text_parts.append(f"- Tagline: \"{tagline}\" — smaller, below headline")
        if stat_badges:
            badges_str = ", ".join(f'"{b}"' for b in stat_badges)
            render_text_parts.append(f"- Stat badges: {badges_str} — bold numbers, short labels")
        if component_labels:
            labels_str = ", ".join(f'"{l}"' for l in component_labels)
            render_text_parts.append(f"- Component labels: {labels_str} — near their respective parts")
        render_text_parts.append("- Use EXACT framework font names and hex colors for all text")
        render_text_parts.append("- HIGH CONTRAST: light text on dark bg, dark text on light bg")
    render_text_instruction = "\n".join(render_text_parts) if render_text_parts else "TEXT: Follow archetype guidelines for text rendering."

    # Position instructions with emotional context
    if module_index == 0:
        position_instruction = (
            "Opening frame — AWE. Create immediate visual impact. "
            "The viewer should think: 'Wow, this is beautiful.' "
            "Plant the emotional seed that grows through all modules."
        )
        module_position = "FIRST (the opening)"
    elif module_index == module_count - 1:
        position_instruction = (
            "Closing frame — CERTAINTY. The emotional journey resolves. "
            "Customer feels confident and ready to buy. No more questions. "
            "Just quiet certainty: 'I want this. I'm ready.'"
        )
        module_position = "LAST (the close)"
    else:
        position_instruction = (
            "Middle frame. Deepen the desire they already feel. "
            "Don't inform — intensify. Each module should make them want it MORE."
        )
        module_position = f"{module_index + 1} of {module_count} (middle)"

    # Continuity instruction with emotional context
    if is_chained and module_index > 0:
        continuity_instruction = (
            "CONTINUITY NON-NEGOTIABLE:\n"
            "Reference image = banner above. Look at its BOTTOM EDGE — exact colors, gradient, lighting. "
            "Your TOP EDGE starts with those same colors, then transitions into your background. "
            "Top 20% of your image = natural extension of previous banner.\n\n"
            "EMOTIONAL CONTINUITY: The previous module created a feeling. "
            "Continue that feeling while deepening it. Don't jar them out of the desire."
        )
    else:
        continuity_instruction = ""

    colors = framework.get("colors", [])
    primary_color = next(
        (c.get("hex") for c in colors if c.get("role") == "primary"),
        colors[0].get("hex", "#C85A35") if colors else "#C85A35",
    )

    prompt = APLUS_MODULE_WITH_SCRIPT.format(
        product_title=product_title,
        brand_name=brand_name or "Premium Brand",
        features=", ".join(features) if features else "Quality craftsmanship",
        target_audience=target_audience or "Discerning customers",
        framework_name=framework.get("framework_name", "Professional"),
        design_philosophy=framework.get("design_philosophy", "Clean and modern"),
        primary_color=primary_color,
        color_palette=", ".join(c.get("hex", "") for c in colors) or primary_color,
        framework_mood=framework.get("brand_voice", "Professional"),
        narrative_theme=visual_script.get("narrative_theme", ""),
        color_flow=visual_script.get("color_flow", ""),
        background_strategy=visual_script.get("background_strategy", ""),
        edge_connection_strategy=visual_script.get("edge_connection_strategy", ""),
        module_index=module_index,
        module_count=module_count,
        module_role=mod.get("role", f"Module {module_index + 1}"),
        module_archetype=module_archetype,
        module_headline=mod.get("headline", ""),
        module_product_angle=mod.get("product_angle", ""),
        module_background=mod.get("background_description", ""),
        module_elements=", ".join(mod.get("key_elements", [])),
        module_mood=mod.get("mood", ""),
        module_content_focus=mod.get("content_focus", ""),
        render_text_instruction=render_text_instruction,
        top_edge=mod.get("top_edge", "Clean start"),
        bottom_edge=mod.get("bottom_edge", "Flows downward"),
        module_position=module_position,
        position_instruction=position_instruction,
        continuity_instruction=continuity_instruction,
    )

    if custom_instructions:
        prompt += f"\n\nCLIENT NOTE:\n{custom_instructions}"

    return prompt

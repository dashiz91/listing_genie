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
- Do NOT render text, headlines, logos in the image
- Pure photographic/visual composition only
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

VISUAL_SCRIPT_PROMPT = """You are an Art Director at a top-tier agency. Samsung, Dyson, Apple, Glossier, Aesop.
Today: Amazon Premium A+ Content — {module_count} full-width banners (1464×600) stacking into one emotional journey.

Campaign imagery standards. But more importantly: FEELING first.

THE PRODUCT:
- {product_title}
- Brand: {brand_name}
- What makes it special: {features}
- Who it's for: {target_audience}

THE DESIGN LANGUAGE:
- Identity: {framework_name}
- Philosophy: {design_philosophy}
- Palette: {color_palette}
- Typography: {typography}
- Story arc: {story_arc}
- Visual treatment: {visual_treatment}

Study the attached product photos. Notice materials, finish, scale, color.
Your script must reflect the REAL product, not an imagined one.

═══════════════════════════════════════════════════════════════════════════════
                    THE EMOTIONAL JOURNEY — NOT INFORMATION
═══════════════════════════════════════════════════════════════════════════════

By the time they reach A+ Content, they've seen the listing images.
They're already INTERESTED. Now deepen that into DESIRE.

Each module should make them FEEL something:
- Not "4,900 mAh battery" → "A full day without worrying about power"
- Not "Premium ceramic" → "The kind of object you reach for every morning"
- Not "Modern design" → "Understated confidence on your shelf"

THE EMOTIONAL ARC FOR A+:
- Modules 0+1 (Hero): AWE — "Wow, this is beautiful"
- Module 2: INTRIGUE — "Tell me more about this"
- Module 3: TRUST — "I can see the quality"
- Module 4: BELONGING — "This fits my life"
- Module 5: CERTAINTY — "I'm ready to buy"

═══════════════════════════════════════════════════════════════════════════════
                         THE EDITORIAL DESIGN SYSTEM
═══════════════════════════════════════════════════════════════════════════════

STRUCTURE — THE {module_count}-MODULE ARC:

Modules 0+1 = HERO PAIR. ONE continuous image split in half.
Product DRAMATICALLY LARGE, filling full height of both modules combined.
Module 0: Top portion (50-60% of product visible, cropped at bottom).
Module 1: Reveals the rest + brand/product name as text.
Together: "wow" moment — not information, pure visual impact.

Modules 2-5 = INDEPENDENT editorial compositions. Each one:
- SHORT EVOCATIVE HEADLINE (2-5 words) — feeling, not feature
- Supporting body copy that creates DESIRE, not description
- Optional spec callouts (only if they feel impressive, not just informative)
- Product from a DIFFERENT angle each time
- Clean background (solid or subtle gradient — NOT busy scenes)

HEADLINE EXAMPLES:
- WRONG: "Water-Tight Interior" → RIGHT: "Every Morning, Fresh"
- WRONG: "Premium Ceramic Material" → RIGHT: "Made to Last"
- WRONG: "8 inches tall" → RIGHT: "A Quiet Presence"

BACKGROUND RHYTHM — Alternate using ONLY framework palette colors:
- Modules 0+1 (hero): Framework primary color
- Module 2: Lightest palette color
- Module 3: Darkest palette color (drama beat)
- Module 4: Light again
- Module 5: Return to primary/secondary (bookend)

Every background MUST be from the framework palette or a tint/shade of one.
The palette IS the brand identity.

LAYOUT ALTERNATION — Ping-pong composition:
- Module 2: Product LEFT, text RIGHT
- Module 3: Text LEFT, product RIGHT
- Module 4: Product LEFT, text RIGHT
- Module 5: Text LEFT, product RIGHT

PRODUCT ANGLE PROGRESSION:
- Modules 0+1: Dramatic tilt, close-up, HUGE
- Module 2: 3/4 angle, inviting exploration
- Module 3: Detail close-up, reveals craft
- Module 4: In context, shows belonging
- Module 5: Final beauty shot, confident

MODULE EMOTIONAL ROLES (pick best for THIS audience):
- "hero_reveal": Pure visual impact — "Wow" (always modules 0+1)
- "intrigue": Draw them deeper — "Tell me more"
- "trust": Prove quality through craft — "This is well-made"
- "belonging": Show their life with it — "This fits me"
- "desire": Create longing — "I want this feeling"
- "certainty": Remove doubt — "I'm ready to buy"

═══════════════════════════════════════════════════════════════════════════════
                         TYPOGRAPHY — WORDS THAT FEEL
═══════════════════════════════════════════════════════════════════════════════

HERO PAIR (modules 0+1):
- Module 0: NO text. Pure visual impact. Let the product speak.
- Module 1: Brand name (smaller) + Product name (large, bold). Nothing else.

FEATURE MODULES (2-5):
- HEADLINE: 2-5 words that create FEELING, not describe features
- BODY COPY: 1-2 sentences that paint a moment, not list specs
- SPEC CALLOUTS: Only if impressive — "4,900 mAh" with "All-day confidence"

COPYWRITING RULES:
- Headlines should feel like a whisper, not a shout
- Body copy should create a scene, not explain a feature
- Every word should make them want the product MORE

WRONG COPY:
- "Water-Tight Interior"
- "Premium ceramic material ensures durability"
- "Perfect for fresh flowers"

RIGHT COPY:
- "Every Morning, Fresh"
- "The quiet ritual of arranging flowers in something beautiful"
- (No feature explanation needed — the image shows it)

Typography uses framework fonts. Headlines bold, body regular.
Keep text to ONE SIDE — never scatter across image.

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
- `PREVIOUS_MODULE` — banner above (modules 1+ only)

Your prompts MUST reference PRODUCT_PHOTO and STYLE_REFERENCE by name.

═══════════════════════════════════════════════════════════════════════════════
                         OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

Respond with ONLY valid JSON:
{{
  "narrative_theme": "Single sentence capturing the EMOTIONAL journey",
  "color_flow": "How palette evolves — which module gets which color",
  "background_strategy": "Rhythm pattern",
  "hero_pair_prompt": "COMPLETE 200-350 word prompt for tall 4:3 hero image — FEELING first",
  "modules": [
    {{
      "index": 0,
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
      "role": "hero_reveal",
      "emotional_beat": "awe",
      "viewer_thought": "I want to know more",
      "headline": "Brand + Product Name",
      "mood": "Feeling",
      "scene_description": "50-100 words: bottom half",
      "render_text": {{"headline": null, "body_copy": null, "spec_callouts": null, "text_position": "left or right"}}
    }},
    {{
      "index": 2,
      "role": "intrigue | trust | belonging | desire | certainty",
      "emotional_beat": "intrigue",
      "viewer_thought": "What the viewer unconsciously thinks",
      "mood": "...",
      "scene_description": "OPTIONAL — only for continuity",
      "render_text": {{"headline": "2-5 evocative words", "body_copy": "1-2 sentences that create a scene", "spec_callouts": [], "text_position": "left or right"}},
      "generation_prompt": "COMPLETE 200-350 word prompt — FEELING first, then visuals..."
    }}
  ]
}}

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
Headline: "{module_headline}"
Product treatment: {module_product_angle}
Background: {module_background}
Visual elements: {module_elements}
THE FEELING: {module_mood}
What the viewer thinks: {module_content_focus}

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
- Use product reference for REAL product. Honor materials and proportions.
- Style reference = visual direction. Match mood, lighting, sophistication.
- Brand colors in scene naturally — lighting, surfaces, atmosphere
- Frame from a premium brand film, not a template
- NEVER include website UI, Amazon navigation, browser chrome
- Do NOT render text, headlines, logos in the image

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
- Text in lower third only, integrated naturally
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
) -> str:
    """Build the Art Director visual script prompt."""
    return VISUAL_SCRIPT_PROMPT.format(
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
        module_headline=mod.get("headline", ""),
        module_product_angle=mod.get("product_angle", ""),
        module_background=mod.get("background_description", ""),
        module_elements=", ".join(mod.get("key_elements", [])),
        module_mood=mod.get("mood", ""),
        module_content_focus=mod.get("content_focus", ""),
        top_edge=mod.get("top_edge", "Clean start"),
        bottom_edge=mod.get("bottom_edge", "Flows downward"),
        module_position=module_position,
        position_instruction=position_instruction,
        continuity_instruction=continuity_instruction,
    )

    if custom_instructions:
        prompt += f"\n\nCLIENT NOTE:\n{custom_instructions}"

    return prompt

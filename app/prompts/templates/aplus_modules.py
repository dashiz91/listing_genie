"""
A+ Content Module Prompt Templates - Principle-Based Creative Direction

These templates power the Art Director visual script system for generating
Premium A+ Content images. Uses the same vocabulary triggers and product
protection philosophy as listing images for consistent quality.

Philosophy: Great A+ content feels like one seamless scroll — a visual story
that pulls the customer deeper into the brand world with every banner.
"""
import json
from typing import Optional

from ..vocabulary import get_aplus_quality_standard
from ..product_protection import PRODUCT_PROTECTION_DIRECTIVE


# ============================================================================
# LEGACY PROMPTS (fallback when no visual script exists)
# ============================================================================

APLUS_FULL_IMAGE_BASE = """Sotheby's catalog. Campaign imagery. Cinematic.

You're creating a premium A+ Content banner for {product_title}.
Brand "{brand_name}" needs a wide frame that stops the scroll.

The audience — {target_audience} — should feel something instantly.
This isn't a product photo. This is a brand moment.

PRODUCT DNA:
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
OPENING MOVE:
First thing they see in your A+ section. Design with downward momentum.
Gradients pulling south, surfaces receding, light inviting further scroll.
Plant visual seeds that modules below will grow.
"""

APLUS_FULL_IMAGE_CHAINED = APLUS_FULL_IMAGE_BASE + APLUS_CONTINUITY_ADDITION

APLUS_FULL_IMAGE_LAST = APLUS_FULL_IMAGE_BASE + APLUS_CONTINUITY_ADDITION + """
CLOSING FRAME:
Final banner. Visual story resolves. Background settles.
Gradients reach destination, compositions find rest.
Customer feels: "I've seen enough. I want this."
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
Today: Amazon Premium A+ Content — {module_count} full-width banners (1464×600) stacking into one editorial scroll.

Sotheby's catalog quality. Campaign imagery standards.

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
                         THE EDITORIAL DESIGN SYSTEM
═══════════════════════════════════════════════════════════════════════════════

STRUCTURE — THE {module_count}-MODULE ARC:

Modules 0+1 = HERO PAIR. ONE continuous image split in half.
Product DRAMATICALLY LARGE, filling full height of both modules combined.
Module 0: Top portion (50-60% of product visible, cropped at bottom).
Module 1: Reveals the rest + brand/product name as text.
Together: "wow" moment like Samsung's Galaxy hero banners.

Modules 2-5 = INDEPENDENT editorial compositions. Each one:
- SHORT PUNCHY HEADLINE (2-5 words) — "Big. Bright. Smooth."
- Supporting body copy (1-2 sentences)
- Optional spec callouts (large numbers + units)
- Product from a DIFFERENT angle each time
- Clean background (solid or subtle gradient — NOT busy scenes)

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
- Module 2: 3/4 angle, feature callouts
- Module 3: Front-facing or detail close-up
- Module 4: Multiple angles or product in context
- Module 5: Lifestyle/ecosystem or final beauty angle

MODULE ROLES (pick best for THIS audience):
- "hero_reveal": Dramatic intro (always modules 0+1)
- "feature_specs": Technical callouts — "What am I getting?"
- "craftsmanship": Close-up details — "Is this well-made?"
- "lifestyle_context": Real environment — "Will this fit my life?"
- "versatility": Multiple uses — "Is it flexible?"
- "comparison": Before/after — "Why not the cheaper one?"
- "social_proof": Awards, certifications — "Do others trust this?"
- "ecosystem": Related products — "What else should I get?"

═══════════════════════════════════════════════════════════════════════════════
                         TYPOGRAPHY IN THE IMAGE
═══════════════════════════════════════════════════════════════════════════════

HERO PAIR (modules 0+1):
- Module 0: NO text. Pure dramatic product photography.
- Module 1: Brand name (smaller) + Product name (large, bold).

FEATURE MODULES (2-5):
- HEADLINE: 2-5 words, BOLD, large. "Big. Bright. Smooth."
- BODY COPY: 1-2 sentences, smaller, lighter weight.
- SPEC CALLOUTS: Large numbers + small units. "4,900 mAh"

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
  "narrative_theme": "Single sentence capturing the visual story",
  "color_flow": "How palette evolves — which module gets which color",
  "background_strategy": "Rhythm pattern",
  "hero_pair_prompt": "COMPLETE 200-350 word prompt for tall 4:3 hero image",
  "modules": [
    {{
      "index": 0,
      "role": "hero_reveal",
      "headline": "NO TEXT",
      "mood": "Feeling this evokes",
      "scene_description": "50-100 words: top half",
      "render_text": null
    }},
    {{
      "index": 1,
      "role": "hero_reveal",
      "headline": "Brand + Product Name",
      "mood": "Feeling",
      "scene_description": "50-100 words: bottom half",
      "render_text": {{"headline": null, "body_copy": null, "spec_callouts": null, "text_position": "left or right"}}
    }},
    {{
      "index": 2,
      "role": "feature_specs | craftsmanship | etc.",
      "mood": "...",
      "scene_description": "OPTIONAL — only for continuity",
      "render_text": {{"headline": "2-5 words", "body_copy": "1-2 sentences", "spec_callouts": [], "text_position": "left or right"}},
      "generation_prompt": "COMPLETE 200-350 word prompt..."
    }}
  ]
}}

Generate exactly {module_count} modules. Each earns its place — no filler.
"""


APLUS_MODULE_WITH_SCRIPT = """Sotheby's catalog. Campaign imagery. Cinematic.

You're executing a premium A+ banner for {product_title}.
The Art Director scripted the entire section as one continuous visual world.
Bring THIS frame to life — faithful to the script, with craft and instinct.

PRODUCT:
- Brand: {brand_name}
- What matters: {features}
- Audience: {target_audience}

VISUAL IDENTITY ({framework_name}):
{design_philosophy}
Anchor color: {primary_color} | Palette: {color_palette}
Mood: {framework_mood}

THE ART DIRECTOR'S VISION:
"{narrative_theme}"
Color journey: {color_flow}
Background world: {background_strategy}
Seam technique: {edge_connection_strategy}

YOUR FRAME — Module {module_index} of {module_count} ({module_role}):
Headline: "{module_headline}"
Product treatment: {module_product_angle}
Background: {module_background}
Visual elements: {module_elements}
Emotional beat: {module_mood}
Story purpose: {module_content_focus}

EDGE CONTRACTS:
- Top edge resolves to: {top_edge}
- Bottom edge sets up: {bottom_edge}

POSITION: {module_position}
{position_instruction}

CRAFT NOTES:
- Wide format (2.4:1) — cinematic, not square
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

RULES:
- Keep top half intact — do NOT change it
- Replace ONLY the bottom green half
- Transition must be seamless — ONE continuous image, no visible seam
- Same lighting direction, perspective, surfaces continuing
- Use PRODUCT_PHOTO for real product reference
- Use STYLE_REFERENCE for visual style and mood
"""


HERO_PAIR_PROMPT = """Generate ONE single tall portrait photograph — NOT two separate panels.
This image will later be cropped into two halves. Must look like one seamless photo top to bottom.

CRITICAL: Do NOT compose as "top section" and "bottom section."
Think: ONE tall editorial magazine photograph that happens to be cropped later.
The viewer should NOT be able to tell where the crop line is.

REFERENCE IMAGES:
- PRODUCT_PHOTO: The actual product — honor materials, proportions, character
- STYLE_REFERENCE: Match this visual style, mood, and color treatment

═══ ART DIRECTOR'S CREATIVE BRIEF ═══

{hero_pair_brief}

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

    # Position instructions
    if module_index == 0:
        position_instruction = (
            "Opening frame. Design with downward momentum — eye should want to scroll. "
            "Plant visual seeds that pay off in later modules."
        )
        module_position = "FIRST (the opening)"
    elif module_index == module_count - 1:
        position_instruction = (
            "Closing frame. Visual story resolves — gradients settle, compositions rest, "
            "customer feels confident and ready to buy."
        )
        module_position = "LAST (the close)"
    else:
        position_instruction = (
            "Middle frame. Seamlessly receive flow from above, pass it below. "
            "Deepen the story — reveal something new."
        )
        module_position = f"{module_index + 1} of {module_count} (middle)"

    # Continuity instruction
    if is_chained and module_index > 0:
        continuity_instruction = (
            "CONTINUITY NON-NEGOTIABLE:\n"
            "Reference image = banner above. Look at its BOTTOM EDGE — exact colors, gradient, lighting. "
            "Your TOP EDGE starts with those same colors, then transitions into your background. "
            "Top 20% of your image = natural extension of previous banner."
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

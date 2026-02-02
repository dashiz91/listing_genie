"""
A+ Content Module Prompt Templates

These templates power the Art Director visual script system for generating
Premium A+ Content images. The Art Director plans the entire A+ section as
one continuous visual narrative, then guides each module's generation with
rich creative direction.

Philosophy: Great A+ content feels like one seamless scroll — a visual story
that pulls the customer deeper into the brand world with every banner.
"""
import json
from typing import Optional


# ============================================================================
# LEGACY PROMPTS (fallback when no visual script exists)
# ============================================================================

APLUS_FULL_IMAGE_BASE = """You are an award-winning commercial photographer and art director shooting a premium
Amazon A+ Content banner for {product_title}.

THE BRIEF:
Brand "{brand_name}" needs a wide cinematic banner that stops the scroll. The audience —
{target_audience} — should feel something the instant they see it. This isn't a product photo.
This is a brand moment.

PRODUCT DNA:
The product's standout qualities: {features}

CREATIVE DIRECTION ({framework_name}):
Visual identity: {framework_style}
Hero color: {primary_color} — use this to anchor the composition, not flood it.
Supporting palette: {color_palette}
Emotional register: {framework_mood}

WHAT TO CREATE:
A wide-format banner (roughly 2.4:1) that feels like a frame from a luxury brand film.
The product must be the undeniable star, but the environment around it should whisper
the brand story. Think editorial, not catalog.

Use the product reference photos to capture the REAL product — its materials, proportions,
colors, and character. Don't invent a different product.

Let the brand colors live in the background, lighting, and atmosphere — not as flat graphic
blocks. The palette should feel like it belongs to the scene, not painted on top.

Leave breathing room at the top and bottom edges. The design should feel like it extends
beyond the frame — as if this banner is a window into a larger world.

ABSOLUTE RULES:
- NEVER include any website UI, Amazon navigation, search bars, browser chrome, or page elements. This is a standalone product image.
- Do NOT render any text, headlines, logos, or typography in the image. Produce a purely photographic/visual composition.
"""

APLUS_CONTINUITY_ADDITION = """
CONTINUITY DIRECTIVE:
This banner sits DIRECTLY below another banner. The reference image is what appears above you.

Your job: make the seam disappear. The viewer should never notice where one banner ends
and the next begins. Match the background's gradient direction, color temperature, lighting
angle, shadow behavior, and any decorative rhythms. If there's a surface, continue it.
If there's a gradient, extend it. If there's a pattern, let it flow.

Both banners are one continuous canvas that happened to be split in two.
"""

APLUS_FULL_IMAGE_FIRST = APLUS_FULL_IMAGE_BASE + """
OPENING MOVE:
This is the first thing they see when they scroll to your A+ section.
Design the background with downward momentum — gradients that pull the eye south,
surfaces that recede toward the bottom edge, light that invites further scrolling.
Plant visual seeds that the modules below will grow.
"""

APLUS_FULL_IMAGE_CHAINED = APLUS_FULL_IMAGE_BASE + APLUS_CONTINUITY_ADDITION

APLUS_FULL_IMAGE_LAST = APLUS_FULL_IMAGE_BASE + APLUS_CONTINUITY_ADDITION + """
CLOSING FRAME:
This is the final banner. The visual story resolves here. The background should settle —
gradients reaching their destination, surfaces finding rest, the composition achieving
a sense of quiet confidence. The customer should feel: "I've seen enough. I want this."
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

VISUAL_SCRIPT_PROMPT = """You are an Art Director at a top-tier e-commerce creative agency. You've directed
campaigns for Samsung, Dyson, Apple, Glossier, and Aesop. Today you're planning an Amazon Premium A+ Content
section — {module_count} full-width banners (1464×600 each) that stack vertically into one editorial scroll.

You design like Samsung's Galaxy A+ pages: each module is a carefully composed editorial frame with bold
typography, clean backgrounds, and product photography that tells a story through RHYTHM and CONTRAST.

THE PRODUCT:
- {product_title}
- Brand: {brand_name}
- What makes it special: {features}
- Who it's for: {target_audience}

THE DESIGN LANGUAGE (selected framework):
- Identity: {framework_name}
- Philosophy: {design_philosophy}
- Palette: {color_palette}
- Typography: {typography}
- Story arc: {story_arc}
- Visual treatment: {visual_treatment}

I've attached the actual product photos. STUDY THEM. Notice the materials, the finish, the scale,
the color. Your script must reflect the REAL product, not an imagined one.

═══════════════════════════════════════════════════════════════════════
THE EDITORIAL DESIGN SYSTEM
═══════════════════════════════════════════════════════════════════════

STRUCTURE — THE {module_count}-MODULE ARC:

Modules 0+1 are the HERO PAIR. They form ONE continuous image that gets split in half.
The product should be DRAMATICALLY LARGE, filling the full height of both modules combined,
shot at a dynamic angle. Module 0 shows the top portion (intentionally cropped at the bottom —
we only see 50-60% of the product). Module 1 reveals the rest of the product plus the brand/product
name as text. Together they create a "wow" moment like Samsung's Galaxy hero banners.

Modules 2-5 are INDEPENDENT editorial compositions. Each one is its own frame with:
- A SHORT PUNCHY HEADLINE (2-5 words, bold, large) — e.g. "Big. Bright. Smooth." or "Built to Last."
- Supporting body copy (1-2 sentences explaining the feature)
- Optional spec callouts (large numbers + units, e.g. "4,900 mAh" or "6.7 inches")
- The product shown from a DIFFERENT angle each time
- Clean background (solid color or subtle gradient — NOT busy scenes)

BACKGROUND RHYTHM — You MUST alternate backgrounds using ONLY colors from the framework palette above.
NEVER default to generic white or generic black — always pick a specific hex from the palette.
- Modules 0+1 (hero): Framework primary color as background (e.g. {color_palette} — pick the primary)
- Module 2: The lightest color from the palette (or the text_light color). If the palette has no
  near-white, use a very light tint of the primary color.
- Module 3: The darkest color from the palette (text_dark, or the deepest secondary/accent).
  This is the "drama beat" — use a DARK shade from the palette, NOT generic black.
- Module 4: Light palette color again (same as module 2, or another light palette entry)
- Module 5: Return to framework primary/secondary color — bookend the section

⚠️ EVERY background MUST be a color from the framework palette or a tint/shade of one.
The palette IS the brand identity. Using generic white (#FFFFFF) is ONLY acceptable if #FFFFFF
is explicitly in the palette. Same for black.

This palette-driven rhythm creates visual chapters while maintaining brand consistency.

LAYOUT ALTERNATION — Ping-pong the composition:
- Module 2: Product on LEFT, text on RIGHT
- Module 3: Text on LEFT, product on RIGHT
- Module 4: Product on LEFT, text on RIGHT
- Module 5: Text on LEFT, product on RIGHT
(Or vice versa — just alternate consistently.)

PRODUCT ANGLE PROGRESSION — Show the product differently every time:
- Module 0+1 hero: Dramatic tilt, close-up, product HUGE
- Module 2: 3/4 angle, feature callout lines pointing to details
- Module 3: Front-facing or detail close-up, moody lighting
- Module 4: Multiple angles or sizes side-by-side, or product in context
- Module 5: Lifestyle/ecosystem shot, or final beauty angle

MODULE ROLE MENU — Pick the best role for each module based on what would persuade THIS audience:
- "hero_reveal": Dramatic product intro (always modules 0+1)
- "feature_specs": Technical callout lines, dimensions, materials — "What am I getting?"
- "craftsmanship": Close-up details, materials, texture — "Is this well-made?"
- "lifestyle_context": Product in a real environment — "Will this fit my life/space?"
- "versatility": Multiple uses, sizes, configurations — "Is it flexible enough?"
- "comparison": Before/after or vs. alternatives — "Why not the cheaper one?"
- "social_proof": Ratings, awards, certifications — "Do others trust this?"
- "ecosystem": Related products, bundles, accessories — "What else should I get?"

Choose roles for modules 2-5 that would most effectively persuade {target_audience} to buy {product_title}.
Don't repeat roles. Each module must earn its place.

═══════════════════════════════════════════════════════════════════════
TYPOGRAPHY IN THE IMAGE
═══════════════════════════════════════════════════════════════════════

Text IS rendered in the image. This is a key part of the design. For each module:

HERO PAIR (modules 0+1):
- Module 0: NO text. Pure dramatic product photography.
- Module 1: Brand name (smaller, above) + Product name (large, bold). Placed in the open space
  beside or below the revealed product. Clean and confident.

FEATURE MODULES (2-5):
- HEADLINE: 2-5 words, BOLD, large. Punchy and benefit-driven. Think Samsung style:
  "Big. Bright. Smooth." / "More power. Less plugging in." / "Built to outlast."
- BODY COPY: 1-2 sentences, smaller, lighter weight. Explains the headline. Conversational tone.
- SPEC CALLOUTS (optional): Large numbers + small units. e.g. "4,900 mAh" or "12 MP"
  with a small label underneath like "Battery capacity" or "Wide-angle Camera"

Typography should use the framework's font choices. Headlines in headline font (bold),
body in body font (regular weight). Keep text to ONE SIDE of the composition — never scatter
text across the image. Leave breathing room around text blocks.

⚠️ CRITICAL: When writing prompts, describe fonts and colors SEPARATELY from the text strings.
The image model renders everything near a quoted string as visible text. NEVER write font names
or hex codes adjacent to the text content.
  BAD:  «"BRAND NAME" in Quicksand Bold #544381»  (model renders "Quicksand Bold #544381" as text)
  GOOD: «The text "BRAND NAME" appears large and bold in a rounded sans-serif font, colored #544381.»

═══════════════════════════════════════════════════════════════════════
CONTINUITY SYSTEM
═══════════════════════════════════════════════════════════════════════

Modules 0+1 use our HERO PAIR technique: We generate ONE tall 4:3 image covering both modules,
then split it at the exact horizontal midpoint. Both halves come from the same pixel output —
guaranteed perfect alignment, zero seam.

You must write a single `hero_pair_prompt` (300-500 words) at the top level of your JSON output.
This is the COMPLETE prompt sent directly to the image generation model for generating the tall image.
Do NOT write `generation_prompt` for modules 0 or 1 — they share the hero_pair_prompt.

The `hero_pair_prompt` must include:
1. Format: "Single tall 4:3 image (~1464×1098). Split at horizontal midpoint into two 1464×600 banners."
2. Product placement: THE SAME SINGLE PRODUCT must cross the midline — dramatically large, dynamic
   angle, spanning from top half into bottom half as one continuous object. Do NOT introduce packaging,
   boxes, or a second/smaller copy of the product. The bottom half reveals the REST of the same product.
3. Background: exact hex from palette, continuous top to bottom
4. Typography: bottom half only — specify the EXACT TEXT STRINGS to render (brand name and product name).
   Describe the font style in natural language (e.g. "clean sans-serif, bold, large") and the text color
   as a hex code. ⚠️ NEVER put font names, font weights, or hex codes next to the text strings in a way
   that could be read as part of the visible text. BAD: «"BRAND NAME" in Quicksand Bold #544381»
   GOOD: «The text "BRAND NAME" appears in a bold rounded sans-serif font, colored #544381.»
5. Top half: NO text, pure product photography
6. Reference images: "Use PRODUCT_PHOTO for exact product. Match STYLE_REFERENCE mood/style."
7. Lighting setup description
8. Rules: no website UI, no Amazon navigation, no product packaging/boxes unless the product IS packaging

For modules 2-5: scene_description is OPTIONAL. Only include it if you want canvas continuity
between consecutive modules (e.g. modules 2→3 sharing a background). For contrast breaks
(like white→dark), do NOT provide scene_description — let each module generate independently.

═══════════════════════════════════════════════════════════════════════
REFERENCE IMAGES
═══════════════════════════════════════════════════════════════════════

When generating each banner, the model receives these named reference images:
- `PRODUCT_PHOTO` — the actual product (always present)
- `STYLE_REFERENCE` — the visual style direction (if available)
- `PREVIOUS_MODULE` — the banner directly above this one (modules 1+ only)

Your prompts MUST reference PRODUCT_PHOTO and STYLE_REFERENCE by name.
For the hero pair (modules 0+1), the PREVIOUS_MODULE reference is handled automatically by the
canvas continuity system — you do NOT need to reference it in module 1's prompt.

═══════════════════════════════════════════════════════════════════════
YOUR OUTPUT
═══════════════════════════════════════════════════════════════════════

Write a `hero_pair_prompt` at the TOP LEVEL of your JSON — this is the single prompt for the
tall 4:3 hero image (modules 0+1). See CONTINUITY SYSTEM above for what it must contain.
Do NOT write `generation_prompt` for modules 0 or 1.

For modules 2-5, write a `generation_prompt` — the COMPLETE, ready-to-use prompt (300-500 words)
that will be sent directly to the image generation model.

Each module 2-5 prompt must include:
1. Role statement ("You are a commercial photographer and typographer...")
2. Format ("wide 2.4:1 banner, 1464×600")
3. Reference images ("Use PRODUCT_PHOTO as reference for the real product. Match the visual style of STYLE_REFERENCE.")
4. Background — MUST specify the EXACT hex color from the framework palette. e.g. "The background is solid #E6DFF7 (Soft Lilac)." NEVER say "pure white" or "black" unless that exact hex is in the palette.
5. Product placement (position, angle, scale, what part is visible)
6. Typography — use the framework's font names. e.g. "Headlines in Quicksand Bold, body in Montserrat Regular." Use text colors from the palette.
7. Layout (which side has product, which side has text)
8. Rules: NEVER include website UI, Amazon navigation, or browser chrome.
9. Style continuity: "Match the color palette, mood, and visual language of STYLE_REFERENCE throughout."

Respond with ONLY valid JSON (no markdown, no code fences):
{{
  "narrative_theme": "The single sentence that captures the whole visual story",
  "color_flow": "How the palette evolves — which module gets which background color",
  "background_strategy": "The rhythm pattern: [color] → [color] → white → dark → white → [color]",
  "hero_pair_prompt": "The COMPLETE 300-500 word prompt for ONE tall 4:3 image that will be split into modules 0+1. Must include format spec, product crossing midline, background hex, typography in bottom half only, reference image names, lighting, and rules.",
  "modules": [
    {{
      "index": 0,
      "role": "hero_reveal",
      "headline": "NO TEXT — pure product drama",
      "mood": "The feeling this banner evokes",
      "scene_description": "50-100 words describing the top half of the hero pair — product angle, background, lighting.",
      "render_text": null
    }},
    {{
      "index": 1,
      "role": "hero_reveal",
      "headline": "Brand + Product Name",
      "mood": "The feeling this banner evokes",
      "scene_description": "50-100 words describing the bottom half — revealed product, text placement, same background.",
      "render_text": {{
        "headline": null,
        "body_copy": null,
        "spec_callouts": null,
        "text_position": "left or right"
      }}
    }},
    {{
      "index": 2,
      "role": "feature_specs | craftsmanship | lifestyle_context | etc.",
      "mood": "...",
      "scene_description": "OPTIONAL — only if you want continuity with the previous module.",
      "render_text": {{
        "headline": "The exact headline text to render (2-5 words)",
        "body_copy": "The exact body copy (1-2 sentences)",
        "spec_callouts": ["Optional array of spec strings like '4,900 mAh' or '12 MP'"],
        "text_position": "left or right — which side of the banner the text block goes on"
      }},
      "generation_prompt": "The COMPLETE 300-500 word prompt..."
    }}
  ]
}}

Generate exactly {module_count} modules. Make each one earn its place — no filler, no repetition.
The customer already saw the listing photos. This A+ section must close the deal.
"""


APLUS_MODULE_WITH_SCRIPT = """You are a commercial photographer executing a premium Amazon A+ banner for {product_title}.

The Art Director has scripted the entire A+ section as one continuous visual world. Your job is to bring
THIS specific frame to life — faithful to the script, but with the craft and instinct of someone who
understands light, composition, and what makes people stop scrolling.

PRODUCT:
- Brand: {brand_name}
- What matters: {features}
- Audience: {target_audience}

VISUAL IDENTITY ({framework_name}):
{design_philosophy}
Anchor color: {primary_color} | Full palette: {color_palette}
Emotional tone: {framework_mood}

THE ART DIRECTOR'S VISION FOR THE FULL SECTION:
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
- Wide format, roughly 2.4:1 — think cinematic, not square.
- Use the product reference photos for the REAL product. Honor its actual materials and proportions.
- The style reference image shows the visual direction — match its mood, lighting quality, and sophistication level.
- Let brand colors live in the scene naturally — through lighting, surfaces, and atmosphere, not flat graphic overlays.
- This should feel like a frame from a premium brand film, not a design template.
- NEVER include any website UI, Amazon navigation, search bars, browser chrome, or page elements. This is a standalone product image.
- Do NOT render any text, headlines, logos, or typography in the image. Produce a purely photographic/visual composition.

{continuity_instruction}"""


# ============================================================================
# IMAGE LABEL CONSTANTS (used in both prompt template and backend generation)
# ============================================================================

IMAGE_LABEL_PRODUCT = "PRODUCT_PHOTO"
IMAGE_LABEL_STYLE = "STYLE_REFERENCE"
IMAGE_LABEL_PREVIOUS = "PREVIOUS_MODULE"


CANVAS_INPAINTING_PROMPT = """CANVAS_TO_COMPLETE is split into two halves:
- TOP HALF: A finished photograph showing {previous_scene_description}
- BOTTOM HALF: Solid bright green (#00FF00) — this is a placeholder that must be replaced.

YOUR TASK: Replace the bottom green half with new content to create ONE seamless continuous photograph.
The bottom half should show: {current_scene_description}

CRITICAL RULES:
- Keep the top half photograph intact — do NOT change it.
- Replace ONLY the bottom green half with the new scene content.
- The transition between the existing top photograph and the new bottom must be seamless — ONE continuous image, no visible seam, edge, or line.
- Same lighting direction, same perspective, same surfaces continuing from top into bottom.
- Use PRODUCT_PHOTO as reference for what the real product looks like.
- Use STYLE_REFERENCE to match the visual style and mood.
"""


HERO_PAIR_PROMPT = """Generate ONE single tall portrait photograph — NOT two separate panels or compositions.
This image will later be cropped into two halves, so it MUST look like one seamless photo from top to bottom.

CRITICAL: Do NOT compose this as "top section" and "bottom section". Think of it as ONE tall editorial magazine photograph that happens to be cropped later. The viewer should NOT be able to tell where the crop line is.

REFERENCE IMAGES:
- PRODUCT_PHOTO: The actual product — honor its materials, proportions, and character.
- STYLE_REFERENCE: Match this visual style, mood, and color treatment throughout.

═══ ART DIRECTOR'S CREATIVE BRIEF ═══

{hero_pair_brief}

═══ COMPOSITION RULES (NON-NEGOTIABLE) ═══
- This is ONE continuous photograph, NOT two stacked panels
- The product should be positioned so it naturally spans the vertical center of the image
- Background must be one continuous color, gradient, or environment from top edge to bottom edge — no dividing lines, no color shifts at the midpoint
- Place any brand name or product title text in the lower third only, integrated naturally into the scene
- NEVER include website UI, Amazon navigation, search bars, or browser chrome
- Do NOT duplicate the product — show it ONCE, large, crossing through the center of the frame

{custom_instructions_block}"""


def build_hero_pair_prompt(
    visual_script: dict,
    product_title: str,
    brand_name: str,
    custom_instructions: str = "",
) -> str:
    """
    Build a unified prompt for the hero pair (modules 0+1).

    New path: use hero_pair_prompt from visual script (single unified brief).
    Fallback: merge per-module generation_prompts from old visual scripts.
    """
    # New path: use hero_pair_prompt from visual script
    hero_brief = visual_script.get("hero_pair_prompt")

    # Fallback for old visual scripts that have per-module generation_prompts
    if not hero_brief:
        modules = visual_script.get("modules", [])
        parts = []
        if len(modules) > 0 and modules[0].get("generation_prompt"):
            parts.append(f"TOP HALF:\n{modules[0]['generation_prompt']}")
        if len(modules) > 1 and modules[1].get("generation_prompt"):
            parts.append(f"BOTTOM HALF:\n{modules[1]['generation_prompt']}")
        hero_brief = "\n\n".join(parts) if parts else (
            f"Dramatic product hero for {product_title} by {brand_name}. "
            f"Single tall 4:3 image (~1464×1098). Product crosses the midline, dramatically large. "
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
    Look up the pre-written generation prompt for a module from the visual script.

    Returns the full prompt string if the visual script contains a `generation_prompt`
    for this module index. Returns None if not found (caller should fall back to legacy).
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
    """
    Build a rich per-module prompt using the Art Director's visual script.
    """
    modules = visual_script.get("modules", [])
    if module_index >= len(modules):
        # Fallback if script doesn't cover this module
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
            "This is the opening frame. Design with downward momentum — the eye should want to keep scrolling. "
            "Plant visual seeds that pay off in later modules."
        )
        module_position = "FIRST (the opening)"
    elif module_index == module_count - 1:
        position_instruction = (
            "This is the closing frame. The visual story resolves here — gradients settle, compositions find rest, "
            "the customer feels confident and ready to buy."
        )
        module_position = "LAST (the close)"
    else:
        position_instruction = (
            "This is a middle frame. It must seamlessly receive the flow from above and pass it below. "
            "Deepen the story — reveal something new about the product."
        )
        module_position = f"{module_index + 1} of {module_count} (middle)"

    # Continuity instruction
    if is_chained and module_index > 0:
        continuity_instruction = (
            "CONTINUITY IS NON-NEGOTIABLE:\n"
            "The reference image shows the banner directly above yours. Look at the BOTTOM EDGE of that reference — "
            "its exact colors, gradient direction, lighting, and surface. Your image's TOP EDGE must start with those "
            "same colors and tones, then gradually transition into your module's own background. The top 20% of your "
            "image should feel like a natural extension of the previous banner. Do NOT start with a completely different "
            "color or scene — ease into yours."
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

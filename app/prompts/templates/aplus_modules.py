"""
A+ Content Module Prompt Templates — Clean Scene Description System

Philosophy: The Visual Script does the thinking (scene descriptions).
Per-module delivery just wraps them lightly — same architecture as listing images.
"""
import json
from typing import Optional


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
SAFE ZONE: Keep ALL text and important content at least 10% away from ALL edges. Content near edges WILL be cropped.

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

VISUAL_SCRIPT_PROMPT = """You are an Art Director writing generation prompts for {module_count} Amazon A+ Content banners.

These banners stack below the listing images as one emotional buyer journey.
By the time shoppers reach A+ content, they've already seen the listing images and are interested.
A+ deepens desire into certainty. Each module has a specific JOB in the conversion funnel.

THE PRODUCT:
- {product_title}
- Brand: {brand_name}
- What makes it special: {features}
- Who it's for: {target_audience}

DESIGN SYSTEM (must match listing images exactly):
- Framework: {framework_name} — {design_philosophy}
- Colors (3 ONLY): {color_palette}
  Use ONLY these 3 hex colors + black/white for contrast. No invented hues.
- Typography: {typography}
  Use these EXACT font names in every text description — no substitutes.
- Visual treatment: {visual_treatment}

{listing_context}

Study the attached product photos. Notice materials, finish, scale, color.
Your prompts must reflect the REAL product, not an imagined one.

YOUR JOB: Write {module_count} scene descriptions that form an emotional buyer journey.
Each description should be 150-250 words — a complete prompt for Gemini image generation.
Write like listing image prompts — one vivid, specific scene per module. No boilerplate.

MODULE JOBS (each serves a different purpose in the funnel):

Modules 0+1 (HERO PAIR): Brand desire — "This is a REAL brand."
  Immediate visual impact. Product hero + brand identity.
  The viewer thinks: "Wow, this looks premium."

Module 2: Quality depth — prove craftsmanship.
  Extreme close-ups, material details, construction quality.
  The viewer thinks: "Look at that detail."

Module 3: Authority — social proof and trust signals.
  Stats, awards, trust badges, credibility.
  The viewer thinks: "Others trust this."

Module 4: Lifestyle — show the life with a real person.
  Product in authentic real-world use, genuine emotion.
  The viewer thinks: "I can see myself using this."

Module 5: Confidence — close the deal.
  Final dramatic product shot. Quiet certainty.
  The viewer thinks: "I'm ready to buy."

WRITING YOUR SCENE DESCRIPTIONS:
- Write one vivid, specific scene per module — paint a cinematographer's shot brief
- Include EXACT hex colors and font names from the design system INLINE in the description
- Include any text to render (headlines, brand name, labels) naturally in the description
- Reference PRODUCT_PHOTO, STYLE_REFERENCE, BRAND_LOGO by name where relevant
- Keep rendered text SHORT (2-5 words per element) — Gemini renders short text well
- At least 2 modules must include a real person with face visible, genuine emotion
- Each module should look visually DIFFERENT (variety of compositions, angles, environments)
- Format: wide 2.4:1 cinematic banners (think editorial magazine, not catalog)
- Specify lighting direction (never flat), camera angle, and background for each
- SAFE ZONE: remind to keep text/content 10% from edges (will be cropped)

DON'T REPEAT LISTING CONTENT:
- Listings already showed product beauty, features, lifestyle, transformation
- A+ goes DEEPER: details they couldn't see, objections they still have, new contexts
- If listings showed a lifestyle context, A+ shows DIFFERENT lifestyle contexts

HERO PAIR SPECIAL:
Write one 200-300 word prompt for a SINGLE tall 4:3 photograph (~1464x1098) that will be split at the midpoint into two A+ banners.
Compose as ONE seamless photo — the viewer should NOT see the crop line.
Top half: product photography with dramatic lighting. Bottom half: brand name + product name as bold text.
Do NOT compose as two separate sections. No website UI or browser chrome.
Reference PRODUCT_PHOTO, STYLE_REFERENCE, and BRAND_LOGO by name.

OUTPUT — respond with ONLY valid JSON:
{{
  "hero_pair_prompt": "200-300 word complete prompt for tall 4:3 hero image...",
  "modules": [
    {{
      "index": 0,
      "role": "hero_reveal",
      "scene_prompt": null,
      "text_elements": []
    }},
    {{
      "index": 1,
      "role": "hero_reveal",
      "scene_prompt": null,
      "text_elements": ["Brand Name", "Product Name"]
    }},
    {{
      "index": 2,
      "role": "quality_depth",
      "scene_prompt": "150-250 word vivid scene description with hex colors, font names, lighting, camera angle, text elements inline...",
      "text_elements": ["Detail Label", "Feature Name"]
    }},
    {{
      "index": 3,
      "role": "authority",
      "scene_prompt": "150-250 word scene description...",
      "text_elements": ["#1 Brand", "6.5M+ Users"]
    }},
    {{
      "index": 4,
      "role": "lifestyle",
      "scene_prompt": "150-250 word scene description with a real person...",
      "text_elements": ["Aspirational Headline"]
    }},
    {{
      "index": 5,
      "role": "confidence",
      "scene_prompt": "150-250 word scene description...",
      "text_elements": ["Brand Name"]
    }}
  ]
}}

IMPORTANT:
- Modules 0 and 1 have scene_prompt: null — the hero_pair_prompt covers both.
- Modules 2-5 each have a complete scene_prompt (the full generation prompt).
- text_elements lists the short text strings that should appear in the image.
- Generate exactly {module_count} modules.
"""


# ============================================================================
# PER-MODULE PROMPT DELIVERY (clean header + scene description)
# ============================================================================

APLUS_MODULE_HEADER = """=== REFERENCE IMAGES ===
{reference_images_desc}
Channel the style reference's mood, lighting, and atmosphere.

Amazon A+ Content banner. Wide 2.4:1 format.
SAFE ZONE: Keep all text and important content at least 10% from edges (will be cropped).
NEVER include website UI, Amazon navigation, or browser chrome.

"""

APLUS_CONTINUITY_NOTE = """

VISUAL CONTINUITY: This banner sits directly below the previous one. Your top edge should naturally flow from the previous banner's bottom edge — match colors and gradient direction at the seam."""

APLUS_HERO_HEADER = """=== REFERENCE IMAGES ===
{reference_images_desc}
Channel the style reference's mood, lighting, and atmosphere.

Single tall 4:3 photograph (~1464x1098), later split at midpoint into two A+ banners.
Compose as ONE seamless photo — the viewer should not see the crop line.
Top half: product photography. Bottom half: brand name + product name as bold text.
Do NOT compose as two separate sections. Never include website UI or browser chrome.

"""


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


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _ref_desc(has_style_ref: bool, has_logo: bool, is_chained: bool) -> str:
    """Build reference images description matching listing prompt style."""
    lines = ["- PRODUCT_PHOTO: The actual product — honor its materials, proportions, character"]
    if has_style_ref:
        lines.append("- STYLE_REFERENCE: Match this visual style, mood, and color treatment")
    if has_logo:
        lines.append("- BRAND_LOGO: Reproduce this logo where appropriate")
    if is_chained:
        lines.append("- PREVIOUS_MODULE: The banner directly above — match its bottom edge for seamless flow")
    return "\n".join(lines)


def _default_hero_brief(product_title: str, brand_name: str) -> str:
    """Fallback hero brief when visual script has no hero_pair_prompt."""
    return (
        f"Dramatic product hero for {product_title} by {brand_name}. "
        f"Single tall 4:3 image (~1464x1098). Product crosses midline, dramatically large. "
        f"CINEMATIC textured background (marble, fabric, atmospheric haze) — not a flat solid color. "
        f"Dramatic directional lighting — side light with rim separation. "
        f"Typography in bottom half only — brand name smaller, product name large and bold. "
        f"Top half is pure product photography, no text. "
        f"Use PRODUCT_PHOTO for the real product. Match STYLE_REFERENCE mood. "
        f"If BRAND_LOGO provided, place logo in bottom half near brand name."
    )


# ============================================================================
# BUILD FUNCTIONS
# ============================================================================

def build_hero_pair_prompt(
    visual_script: dict,
    product_title: str,
    brand_name: str,
    custom_instructions: str = "",
    *,
    has_style_ref: bool = True,
    has_logo: bool = False,
) -> str:
    """Build clean prompt for hero pair (modules 0+1)."""
    hero_brief = visual_script.get("hero_pair_prompt")

    # Fallback for old visual scripts that have per-module generation_prompts
    if not hero_brief:
        modules = visual_script.get("modules", [])
        parts = []
        if len(modules) > 0 and modules[0].get("generation_prompt"):
            parts.append(f"TOP HALF:\n{modules[0]['generation_prompt']}")
        if len(modules) > 1 and modules[1].get("generation_prompt"):
            parts.append(f"BOTTOM HALF:\n{modules[1]['generation_prompt']}")
        hero_brief = "\n\n".join(parts) if parts else _default_hero_brief(product_title, brand_name)

    header = APLUS_HERO_HEADER.format(
        reference_images_desc=_ref_desc(has_style_ref, has_logo, False),
    )
    prompt = header + hero_brief

    if custom_instructions:
        prompt += f"\n\nCLIENT NOTE:\n{custom_instructions}"

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
    *,
    has_style_ref: bool = True,
    has_logo: bool = False,
) -> str:
    """Build clean per-module prompt using scene description from visual script."""
    modules = visual_script.get("modules", [])

    # Out-of-range: fall back to legacy prompt
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

    # New format: scene_prompt. Old format: generation_prompt.
    scene_prompt = mod.get("scene_prompt") or mod.get("generation_prompt")

    # If neither exists, build a minimal fallback from available fields
    if not scene_prompt:
        scene_desc = mod.get("scene_description", "")
        mood = mod.get("mood", "premium and cinematic")
        role = mod.get("role", "editorial")
        scene_prompt = (
            f"Create a {role} composition for {product_title} by {brand_name or 'Premium Brand'}. "
            f"{scene_desc} "
            f"The mood is {mood}. Use PRODUCT_PHOTO for the real product — honor its materials, "
            f"proportions, and character. Match STYLE_REFERENCE visual style. "
            f"Dramatic directional lighting. Cinematic color grading. "
            f"Wide 2.4:1 format. Keep text 10% from edges."
        )

    # Build the clean prompt: header + scene description
    header = APLUS_MODULE_HEADER.format(
        reference_images_desc=_ref_desc(has_style_ref, has_logo, is_chained),
    )
    prompt = header + scene_prompt

    # Add continuity note for chained modules
    if is_chained and module_index > 0:
        prompt += APLUS_CONTINUITY_NOTE

    if custom_instructions:
        prompt += f"\n\nCLIENT NOTE:\n{custom_instructions}"

    return prompt


def build_canvas_inpainting_prompt(
    previous_scene_description: str,
    current_scene_description: str,
) -> str:
    """Build the inpainting prompt for canvas extension."""
    return CANVAS_INPAINTING_PROMPT.format(
        previous_scene_description=previous_scene_description,
        current_scene_description=current_scene_description,
    )


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

        listing_context = (
            "WHAT LISTINGS ALREADY COVERED (do not repeat):\n"
            + "\n".join(listing_summary)
            + "\n\nA+ must NOT duplicate these concepts. Go deeper, not wider.\n"
        )

    prompt = VISUAL_SCRIPT_PROMPT.format(
        module_count=module_count,
        product_title=product_title,
        brand_name=brand_name or "Premium Brand",
        features=", ".join(features) if features else "Quality craftsmanship",
        target_audience=target_audience or "Discerning customers",
        framework_name=framework.get("framework_name", "Professional"),
        design_philosophy=framework.get("design_philosophy", "Clean and modern"),
        color_palette=", ".join(
            c.get("hex", "") for c in framework.get("colors", [])[:3]
        ) or "#C85A35",
        typography=json.dumps(framework.get("typography", {})),
        visual_treatment=json.dumps(framework.get("visual_treatment", {})),
        listing_context=listing_context,
    )

    return prompt

"""
A+ Content Module Prompt Templates — Clean Scene Description System

Philosophy: The Visual Script does the thinking (scene descriptions).
Per-module delivery just wraps them lightly — same architecture as listing images.
"""
import json
import re
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

ABSOLUTE RULES:
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

    resolved_brand = (brand_name or "").strip()

    prompt = template.format(
        product_title=product_title,
        brand_name=resolved_brand or "Unspecified Brand",
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

    return strip_aplus_banner_boilerplate(prompt)


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
- Colors: {color_palette}
  Use ONLY these hex colors + black/white for contrast. No invented hues.
- Typography: Headlines in {headline_font_desc}, body text in {body_font_desc}
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
  BRAND TEXT: YES — brand name or logo in one corner. This establishes identity.

Module 2: Quality depth — prove WHY this product is worth it.
  Create a BRAND NEW composition (NEVER crop or zoom the reference photo).
  Pick the best approach for this product category:
  • Crafted/tactile goods → A still life where a key detail fills the frame as its own subject
  • Consumables/formulas/chemicals → Ingredients, purity, the science visualized
  • Simple/commodity items → Design choices, testing, engineering made visible
  IMPORTANT: Generate a fresh scene with dramatic lighting, don't crop or enlarge the product photo.
  The viewer thinks: "There's real substance here."
  BRAND TEXT: NO — zero brand name or logo. Let the quality speak for itself.

Module 3: Authority — social proof and trust signals.
  Stats, awards, trust badges, credibility.
  The viewer thinks: "Others trust this."
  BRAND TEXT: NO — no brand name. Use stats and proof, not branding.

Module 4: Lifestyle — show the life with a real person.
  Product in authentic real-world use, genuine emotion.
  The viewer thinks: "I can see myself using this."
  BRAND TEXT: NO — no brand name or logo. Pure experience, no branding.

Module 5: Confidence — close the deal.
  Final dramatic product shot. Quiet certainty.
  The viewer thinks: "I'm ready to buy."
  BRAND TEXT: YES — brand name or logo returns. Bookend the experience.

WRITING YOUR SCENE DESCRIPTIONS:
- Write one vivid, specific scene per module — paint a cinematographer's shot brief
- Include EXACT hex colors INLINE in the description (e.g., "deep navy #1A1D21 background")
- Describe text rendering in plain visual language: "bold serif headline" or "clean sans-serif label"
- NEVER include pixel sizes (42px), font-weight numbers (700), CSS properties, or technical formatting
- Include any text to render (headlines, labels) naturally in the description
- If Brand is "NOT_SPECIFIED", do NOT render any typed brand-name text; if BRAND_LOGO exists, place logo only
- When rendering brand name text (only when Brand is provided), use EXACTLY "{brand_name}" - never "Premium Brand" or any generic placeholder
- BRAND PLACEMENT RULE: Only include brand name/logo in the HERO PAIR and the LAST module (bookends). Modules 2-4 must have ZERO brand text or logo — let the content speak for itself. This prevents the repetitive, amateur look of stamping brand on every banner.
- Reference PRODUCT_PHOTO, STYLE_REFERENCE, BRAND_LOGO by name where relevant
- Keep rendered text SHORT (2-5 words per element) — Gemini renders short text well
- At least 2 modules must include a real person with face visible, genuine emotion
- Each module should look visually DIFFERENT (variety of compositions, angles, environments)
- Specify lighting direction (never flat), camera angle, and background for each
- Do NOT include delivery boilerplate like "Amazon A+ Content banner", "Wide 2.4:1 format", margin-safe-zone notes, or browser/UI exclusion rules

DON'T REPEAT LISTING CONTENT:
- Listings already showed product beauty, features, lifestyle, transformation
- A+ goes DEEPER: details they couldn't see, objections they still have, new contexts
- If listings showed a lifestyle context, A+ shows DIFFERENT lifestyle contexts

HERO PAIR SPECIAL:
Write one 200-300 word prompt for a SINGLE tall 4:3 photograph (~1464x1098).
Photography-first: the product should dominate the frame (60-70% of composition).
Cinematic, dramatic lighting. Rich textured or solid brand-color background.

Text rules (STRICT):
- Brand name or logo in ONE corner — small, tasteful, not competing with the product
- Optionally ONE bold word (2-3 words max) as a product name or tagline
- NO font names, font sizes, px values, or CSS styling in the prompt
- NO paragraphs, feature text, descriptions, or sentences
- Think Bose, Apple, Stanley hero banners — the image IS the message

Describe: the product pose/angle, lighting direction, background material/color, mood.
Reference PRODUCT_PHOTO, STYLE_REFERENCE, and BRAND_LOGO by name.
Do NOT mention banner splitting, safe zones, midpoints, or composition sections.

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
      "text_elements": ["#1 Rated", "6.5M+ Users"]
    }},
    {{
      "index": 4,
      "role": "lifestyle",
      "scene_prompt": "150-250 word scene description with a real person...",
      "text_elements": ["Aspirational Headline (NO brand name)"]
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

"""

APLUS_CONTINUITY_NOTE = """

VISUAL CONTINUITY: This banner sits directly below the previous one. Your top edge should naturally flow from the previous banner's bottom edge — match colors and gradient direction at the seam."""

APLUS_HERO_HEADER = """=== REFERENCE IMAGES ===
{reference_images_desc}
Channel the style reference's mood, lighting, and atmosphere.

Single tall 4:3 photograph (~1464x1098). Product dominates the frame.
Photography-first: cinematic lighting, rich background, editorial quality.
Brand name or logo small in one corner. No feature text, no descriptions.

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

def strip_aplus_banner_boilerplate(text: str) -> str:
    """Remove recurring A+ delivery boilerplate so it never reaches Gemini."""
    if not text:
        return text

    # Normalize common punctuation variants to make matching robust.
    cleaned = (
        text.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("—", "-")
        .replace("–", "-")
    )

    # Remove the exact legacy 3-line block first.
    for legacy_block in [
        (
            "Amazon A+ Content banner. Wide 2.4:1 format.\n"
            "Center your composition with generous margins on all sides.\n"
            "NEVER include website UI, Amazon navigation, or browser chrome.\n"
        ),
        (
            "Amazon A+ Content banner. Wide 2.4:1 format.\n"
            "Center your composition with generous margins on all sides.\n"
            "NEVER include website UI, Amazon navigation, or browser chrome."
        ),
    ]:
        cleaned = cleaned.replace(legacy_block, "")

    # Remove common sentence-level boilerplate variants.
    sentence_patterns = [
        r'Amazon\s*A\+\s*Content\s*banner\.?\s*',
        r'Wide\s*2\.4\s*:\s*1\s*format\.?\s*',
        r'Wide\s*cinematic\s*banner\s*\(\s*2\.4\s*:\s*1\s*\)\.?\s*',
        r'Center(?:\s+your)?\s+composition(?:s)?\s+with\s+generous\s+margins(?:\s+on\s+all\s+sides)?\.?\s*',
        r'NEVER\s+include\s+website\s+UI,\s*Amazon\s+navigation,\s*(?:or\s*)?browser\s+chrome\.?\s*',
        r'Never\s+include\s+website\s+UI,\s*Amazon\s+navigation,\s*(?:or\s*)?browser\s+chrome\.?\s*',
    ]
    for pattern in sentence_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Drop any leftover line that still contains boilerplate concepts.
    blocked_line_patterns = [
        r'amazon\s*a\+\s*content\s*banner',
        r'wide\s*2\.4\s*:\s*1',
        r'center\s+.*composition.*margin',
        r'website\s+ui.*amazon\s+navigation',
        r'browser\s+chrome',
    ]
    kept_lines = []
    for line in cleaned.splitlines():
        normalized = re.sub(r'\s+', ' ', line.strip().lower())
        if normalized and any(re.search(pat, normalized, flags=re.IGNORECASE) for pat in blocked_line_patterns):
            continue
        kept_lines.append(line)

    cleaned = "\n".join(kept_lines)
    cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def strip_brand_name_text_when_missing(text: str) -> str:
    """Remove explicit brand-name rendering instructions when brand is unknown."""
    if not text:
        return text

    cleaned = text
    patterns = [
        r'(?i)\s*(?:in\s+the\s+[^,.\n]+,\s*)?render\s+the\s+brand\s+name\s+["\'][^"\']+["\'][^.\n]*\.?',
        r'(?i)\s*brand\s+name\s+["\'][^"\']+["\'][^.\n]*\.?',
        r'(?i)\s*brand\s+name\s+`[^`]+`[^.\n]*\.?',
    ]
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned)

    cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def _strip_brand_text_from_prompt(text: str, brand_name: str) -> str:
    """Remove brand name rendering instructions from middle A+ module prompts.

    Middle modules (2-4) should NOT display brand text — only the hero pair
    and the closing module get branding (bookend strategy, like Bose/Apple).
    """
    if not text or not brand_name:
        return text

    cleaned = text
    bn = re.escape(brand_name)

    # Remove sentences/phrases that instruct rendering the brand name
    patterns = [
        # "render the brand name 'X' in the top-left corner"
        rf'(?i)[^.]*\brender\b[^.]*\b{bn}\b[^.]*\.?\s*',
        # "brand name 'X' sits in the corner" / "place 'X' logo"
        rf'(?i)[^.]*\bplace\b[^.]*\b{bn}\b[^.]*\.?\s*',
        # "the brand name 'X' appears small in ..."
        rf'(?i)[^.]*\bbrand\s*name\b[^.]*\b{bn}\b[^.]*\.?\s*',
        # "'X' logo in the bottom-right"
        rf'(?i)[^.]*\b{bn}\b[^.]*\blogo\b[^.]*\.?\s*',
        # "logo ... 'X'"
        rf'(?i)[^.]*\blogo\b[^.]*\b{bn}\b[^.]*\.?\s*',
        # Standalone brand mention as text element: "Bold 'X' text" or "'X' in corner"
        rf'(?i)[^.]*\b{bn}\b[^.]*\b(?:corner|bottom|top|left|right|small|tasteful)\b[^.]*\.?\s*',
    ]
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned)

    # Clean up leftover artifacts
    cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def _strip_css_specs(text: str) -> str:
    """Remove CSS-like typography specs that image models render as garbled text.

    Strips patterns like:
      - "using headline_font Playfair Display, headline_weight Bold, headline_size 42px"
      - "letter_spacing 0.5px"
      - standalone "42px", "24px"
    """
    # Remove "using <css_property> <value>, <css_property> <value>, ..." blocks
    # Matches: "using headline_font X, headline_weight Y, headline_size Z"
    text = re.sub(
        r'\s*using\s+(?:(?:headline|subhead|body)_(?:font|weight|size)|letter_spacing)'
        r'[\s\S]*?(?=(?:,\s*and\b|\.|\n|$))',
        '', text
    )
    # Remove any remaining standalone CSS property references
    text = re.sub(
        r',?\s*(?:headline|subhead|body)_(?:font|weight|size|spacing)\s+[^,\n.]*',
        '', text
    )
    text = re.sub(r',?\s*letter_spacing\s+[^,\n.]*', '', text)
    # Remove standalone px/pt values like "42px" or "0.5px"
    text = re.sub(r'\s*\b\d+(?:\.\d+)?px\b', '', text)
    # Clean up leftover artifacts
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r',\s*\.', '.', text)
    text = re.sub(r'\s*,\s*and\b', ' and', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def _ref_desc(
    has_style_ref: bool,
    has_logo: bool,
    *,
    has_product_ref: bool = True,
) -> str:
    """Build reference images description matching listing prompt style."""
    lines = []
    if has_product_ref:
        lines.append("- PRODUCT_PHOTO: The actual product — honor its materials, proportions, character")
    if has_style_ref:
        lines.append("- STYLE_REFERENCE: Match this visual style, mood, and color treatment")
    if has_logo:
        lines.append("- BRAND_LOGO: Reproduce this logo where appropriate")
    if not lines:
        lines.append("- Use the supplied reference images exactly as provided")
    return "\n".join(lines)


def _default_hero_brief(product_title: str, brand_name: str) -> str:
    """Fallback hero brief when visual script has no hero_pair_prompt."""
    resolved_brand = (brand_name or "").strip()
    brand_byline = f" by {resolved_brand}" if resolved_brand else ""
    brand_text_rule = (
        f"Brand name '{resolved_brand}' small in bottom-right corner - tasteful, not competing with product. "
        if resolved_brand
        else "If BRAND_LOGO is provided, place logo small in one corner - tasteful, not competing with product. "
    )
    return (
        f"Dramatic product hero photograph for {product_title}{brand_byline}. "
        f"Product dominates 60-70% of the frame, dramatically large, slightly angled. "
        f"CINEMATIC textured background (marble, fabric, atmospheric haze) - not a flat solid color. "
        f"Dramatic directional lighting - side light with rim separation, professional studio quality. "
        f"{brand_text_rule}"
        f"Use PRODUCT_PHOTO for the real product. Match STYLE_REFERENCE mood and atmosphere."
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
    has_product_ref: bool = True,
) -> str:
    """Build clean prompt for hero pair (modules 0+1)."""
    resolved_brand = (brand_name or "").strip()
    hero_brief = visual_script.get("hero_pair_prompt")

    # Fallback for old visual scripts that have per-module generation_prompts
    if not hero_brief:
        modules = visual_script.get("modules", [])
        parts = []
        if len(modules) > 0 and modules[0].get("generation_prompt"):
            parts.append(f"TOP HALF:\n{modules[0]['generation_prompt']}")
        if len(modules) > 1 and modules[1].get("generation_prompt"):
            parts.append(f"BOTTOM HALF:\n{modules[1]['generation_prompt']}")
        hero_brief = "\n\n".join(parts) if parts else _default_hero_brief(product_title, resolved_brand)

    # Replace generic "Premium Brand" with actual brand/product name in AI-generated text
    replacement = resolved_brand
    if replacement:
        hero_brief = hero_brief.replace("Premium Brand", replacement)
    else:
        hero_brief = strip_brand_name_text_when_missing(hero_brief)

    header = APLUS_HERO_HEADER.format(
        reference_images_desc=_ref_desc(
            has_style_ref, has_logo,
            has_product_ref=has_product_ref,
        ),
    )
    prompt = header + hero_brief

    if custom_instructions:
        prompt += f"\n\nCLIENT NOTE:\n{custom_instructions}"

    return strip_aplus_banner_boilerplate(prompt)


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
    *,
    has_style_ref: bool = True,
    has_logo: bool = False,
    has_product_ref: bool = True,
) -> str:
    """Build clean per-module prompt using scene description from visual script."""
    resolved_brand = (brand_name or "").strip()
    modules = visual_script.get("modules", [])

    # Out-of-range: fall back to legacy prompt
    if module_index >= len(modules):
        position = "first" if module_index == 0 else "middle"
        colors = framework.get("colors", [])
        return get_aplus_prompt(
            module_type="full_image",
            position=position,
            product_title=product_title,
            brand_name=resolved_brand,
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
        brand_byline = f" by {resolved_brand}" if resolved_brand else ""
        scene_prompt = (
            f"Create a {role} composition for {product_title}{brand_byline}. "
            f"{scene_desc} "
            f"The mood is {mood}. Use PRODUCT_PHOTO for the real product — honor its materials, "
            f"proportions, and character. Match STYLE_REFERENCE visual style. "
            f"Dramatic directional lighting. Cinematic color grading."
        )

    # Replace generic "Premium Brand" with actual brand/product name in AI-generated text
    replacement = resolved_brand
    if replacement:
        scene_prompt = scene_prompt.replace("Premium Brand", replacement)
    else:
        scene_prompt = strip_brand_name_text_when_missing(scene_prompt)

    # Strip CSS-like specs that image models render as garbled text.
    # Catches patterns like "headline_size 42px", "letter_spacing 0.5px",
    # "headline_weight Bold", "subhead_font Inter" from older visual scripts.
    scene_prompt = _strip_css_specs(scene_prompt)

    # Brand bookend rule: only hero (0-1) and last module get brand text.
    # Middle modules (2 through second-to-last) should have no brand name.
    is_middle_module = 2 <= module_index < module_count - 1
    if is_middle_module and resolved_brand:
        scene_prompt = _strip_brand_text_from_prompt(scene_prompt, resolved_brand)

    # Build the clean prompt: header + scene description
    # Suppress logo reference for middle modules (no branding needed)
    effective_has_logo = has_logo and not is_middle_module
    header = APLUS_MODULE_HEADER.format(
        reference_images_desc=_ref_desc(
            has_style_ref, effective_has_logo,
            has_product_ref=has_product_ref,
        ),
    )
    prompt = header + scene_prompt

    if custom_instructions:
        prompt += f"\n\nCLIENT NOTE:\n{custom_instructions}"

    return strip_aplus_banner_boilerplate(prompt)


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

    # Extract clean font descriptions — never send raw JSON/CSS specs to image models
    typo = framework.get("typography", {})
    headline_font = typo.get("headline_font", "bold serif")
    body_font = typo.get("body_font", "clean sans-serif")
    headline_weight = typo.get("headline_weight", "Bold")
    # Describe fonts visually, not technically
    headline_font_desc = f"{headline_weight.lower()} {headline_font} lettering" if headline_weight else headline_font
    body_font_desc = f"{body_font}"

    resolved_brand = (brand_name or "").strip()

    prompt = VISUAL_SCRIPT_PROMPT.format(
        module_count=module_count,
        product_title=product_title,
        brand_name=resolved_brand or "NOT_SPECIFIED",
        features=", ".join(features) if features else "Quality craftsmanship",
        target_audience=target_audience or "Discerning customers",
        framework_name=framework.get("framework_name", "Professional"),
        design_philosophy=framework.get("design_philosophy", "Clean and modern"),
        color_palette=", ".join(
            c.get("hex", "") for c in framework.get("colors", [])[:3]
        ) or "#C85A35",
        headline_font_desc=headline_font_desc,
        body_font_desc=body_font_desc,
        visual_treatment=json.dumps(framework.get("visual_treatment", {})),
        listing_context=listing_context,
    )

    return prompt


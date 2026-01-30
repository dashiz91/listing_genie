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
campaigns for Dyson, Apple, Glossier, and Aesop. Today you're planning an Amazon Premium A+ Content
section — {module_count} full-width banners (1464×600 each) that stack vertically into one seamless scroll.

Your signature move: you never design banners. You design one continuous visual world, then slice it
into frames. When a customer scrolls through your A+ section, they should feel like they're sinking
deeper into the brand universe — each banner revealing another layer of the story.

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

CRITICAL RULES:
- These banners are STANDALONE product images. They are NOT screenshots of a website.
- NEVER reference Amazon UI, navigation bars, search bars, browser chrome, or any website elements.
- Edge descriptions should only describe the visual design (colors, gradients, textures) — never mention
  "blending into" any UI or page element.
- Do NOT include any text, logos, headlines, or typography in the image itself. The headline field is for
  internal reference only — it should NOT appear rendered in the image.

YOUR KEY OUTPUT: COMPLETE GENERATION PROMPTS

For each module, you must write a `generation_prompt` — the COMPLETE, ready-to-use prompt that will be
sent directly to an image generation model. This is NOT metadata. This is the actual photographer's brief.

When generating each banner, the model will receive these named reference images:
- `PRODUCT_PHOTO` — the actual product (always present)
- `STYLE_REFERENCE` — the visual style direction (if available)
- `PREVIOUS_MODULE` — the banner directly above this one (modules 1+ only)

Your prompts MUST reference these by name. For modules 1+, include an instruction like:
"Study PREVIOUS_MODULE. Your top edge must seamlessly continue from its bottom edge."

Write the COMPLETE generation prompt for each module. The prompts must describe backgrounds that
physically connect — if module 0 ends with "warm amber fading to deep bronze at the bottom 50px",
then module 1 MUST begin with "the top 50px continues from PREVIOUS_MODULE's bottom edge — deep
bronze, same gradient, same lighting." Bake the transitions directly into the prompt text.

Each prompt should be ~300-500 words and include:
1. Role statement ("You are a commercial photographer shooting a premium A+ banner")
2. Format note ("wide 2.4:1 format, 1464×600")
3. Reference image instructions ("Use PRODUCT_PHOTO as reference for the real product...")
4. Full scene description (background, lighting, product placement, atmosphere)
5. Edge descriptions (top 50px and bottom 50px — what colors/gradients they resolve to)
6. Absolute rules (no text, no UI, no logos)

YOUR TASK:
Write a visual script that treats these {module_count} banners as one continuous composition.
Think about the scroll as a journey:
- Where does the eye enter? Where does it rest?
- How does the palette shift from top to bottom — warming, cooling, deepening?
- What's the emotional arc? Intrigue → desire → trust → action?
- How do backgrounds flow across banner boundaries with zero visible seams?

Respond with ONLY valid JSON (no markdown, no code fences):
{{
  "narrative_theme": "The single sentence that captures the whole visual story",
  "color_flow": "How the palette evolves from first banner to last — be specific about which colors dominate where",
  "background_strategy": "The continuous background concept",
  "modules": [
    {{
      "index": 0,
      "role": "The role this banner plays in the story (e.g., 'The Reveal', 'Deep Craft')",
      "headline": "Internal reference headline (NOT rendered in image)",
      "mood": "The feeling this banner evokes in one phrase",
      "scene_description": "A 50-100 word description of the PHYSICAL SCENE as if a camera is pulling back to reveal more of the same space. Describe surfaces, backgrounds, and objects as EXTENSIONS of one continuous environment — same table/surface extending further, same wall continuing, same lighting. NEVER describe a different camera angle, zoom level, or scene change. Instead describe what new objects appear in the foreground of the SAME space as the camera reveals more. Include connecting elements (scattered items, draped fabric, etc.) that span the transition zone.",
      "generation_prompt": "The COMPLETE generation prompt for this module. ~300-500 words. References PRODUCT_PHOTO, STYLE_REFERENCE. Describes full scene, background, edges. For module 0: top opens clean, bottom settles into a specific color/gradient. For modules 1+: references PREVIOUS_MODULE, top continues from previous bottom edge."
    }}
  ]
}}

Generate exactly {module_count} modules. Make each one earn its place — no filler, no repetition.
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


CANVAS_INPAINTING_PROMPT = """Edit this image to complete it as ONE single continuous photograph.
The top portion shows {previous_scene_description}. The bottom portion is blank and needs to be filled.

IMPORTANT: This must look like ONE single photograph taken with a camera pulled back to show a wider view. {current_scene_description} NO edge, NO shelf, NO line, NO break. Single continuous perspective, single light source, one unified scene.

Do NOT render any text, headlines, logos, or typography in the image.
"""


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

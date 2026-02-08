"""
A+ Prompt Compiler — pure functions that assemble prompts for A+ generation.

Extracts all prompt assembly logic from generation.py endpoints into testable,
reusable compile functions. Endpoints become thin: auth + compile + execute + return.
"""
import json as json_module
import logging
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any

from app.models.database import GenerationSession, DesignContext
from app.prompts.templates.aplus_modules import (
    build_aplus_module_prompt,
    build_hero_pair_prompt,
    get_aplus_prompt,
    get_visual_script_prompt,
    get_module_config,
    strip_aplus_banner_boilerplate,
    _ref_desc,
    ModuleConfig,
    APLUS_MODULE_HEADER,
    APLUS_HERO_HEADER,
)
from app.services.generation_utils import (
    ReferenceImageSet,
    assemble_reference_images,
    get_enhancement_context,
    strip_json_fences,
)
from app.services.gemini_service import append_lighting_override_once
from app.services.prompt_builder import get_structural_context

logger = logging.getLogger(__name__)


# ============================================================================
# Result dataclass
# ============================================================================

@dataclass(frozen=True)
class AplusPromptResult:
    """Output of a compile function — everything needed to execute generation."""
    prompt: str
    reference_images: ReferenceImageSet
    use_named: bool
    module_config: ModuleConfig
    change_summary: Optional[str] = None


# ============================================================================
# Shared helpers (moved from generation.py)
# ============================================================================

def _has_legacy_aplus_boilerplate(text: str) -> bool:
    """Detect the legacy A+ banner boilerplate block in a normalization-tolerant way."""
    if not text:
        return False
    normalized = re.sub(r"\s+", " ", text.lower())
    return (
        "amazon a+ content banner" in normalized
        and ("wide 2.4:1 format" in normalized or "wide 2.4 : 1 format" in normalized)
        and "amazon navigation" in normalized
        and "browser chrome" in normalized
    )


def _ensure_reference_images_header(prompt: str, header_template: str) -> str:
    """
    Ensure prompt includes the leading '=== REFERENCE IMAGES ===' block.

    AI rewrites can sometimes drop this block on regeneration. We force it back
    to keep named image ingestion consistent between first generation and regen.
    """
    prompt_text = (prompt or "").lstrip()
    if prompt_text.startswith("=== REFERENCE IMAGES ==="):
        return prompt_text
    return f"{header_template}{prompt_text}"


def _finalize_prompt(prompt: str, header_template: str) -> str:
    """
    Apply the shared finalization pipeline to a compiled A+ prompt.

    1. Ensure reference images header is present
    2. Strip known A+ boilerplate (seatbelt)
    3. Double-check for legacy boilerplate leaks
    4. Append lighting override
    """
    prompt = _ensure_reference_images_header(prompt, header_template)

    # Seatbelt: strip known A+ boilerplate before sending to Gemini
    prompt = strip_aplus_banner_boilerplate(prompt)
    if _has_legacy_aplus_boilerplate(prompt):
        prompt = strip_aplus_banner_boilerplate(prompt)
    if _has_legacy_aplus_boilerplate(prompt):
        raise ValueError(
            "Legacy A+ boilerplate leak detected before Gemini call. Please retry after backend restart."
        )

    # Prevent amateur lighting bleed from reference photos
    prompt = append_lighting_override_once(prompt)
    return prompt


async def _apply_ai_rewrite(
    prompt: str,
    custom_instructions: str,
    image_type_key: str,
    session: GenerationSession,
    design_context: Optional[DesignContext],
    vision_service: Any,
    *,
    has_canvas: bool = False,
) -> tuple[str, Optional[str]]:
    """
    Run AI-enhanced prompt rewriting when user provides feedback.

    Returns (enhanced_prompt, change_summary).
    Raises on AI failure so the caller can map to HTTP 502.
    """
    structural_ctx = get_structural_context(image_type_key, has_canvas=has_canvas)
    fw_dict, analysis_text = get_enhancement_context(session, design_context)

    enhancement = await vision_service.enhance_prompt_with_feedback(
        original_prompt=prompt,
        user_feedback=custom_instructions,
        image_type=image_type_key,
        framework=fw_dict,
        product_analysis=analysis_text,
        structural_context=structural_ctx,
    )
    enhanced_prompt = enhancement["enhanced_prompt"]
    change_summary = enhancement.get("interpretation", "AI-enhanced based on feedback")
    return enhanced_prompt, change_summary


# ============================================================================
# Module compiler
# ============================================================================

async def compile_aplus_module(
    session: GenerationSession,
    module_index: int,
    module_count: int,
    module_type_value: str,
    visual_script: Optional[Dict] = None,
    custom_instructions: Optional[str] = None,
    brand_name: str = "",
    design_context: Optional[DesignContext] = None,
    vision_service: Any = None,
    image_model: Optional[str] = None,
) -> AplusPromptResult:
    """
    Compile the full prompt + reference images for a single A+ module.

    All prompt logic lives here — the endpoint just calls this then executes.
    """
    config = get_module_config(module_index, module_count)
    features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]
    framework = session.design_framework_json or {}
    has_product_ref = bool(session.upload_path)
    has_style_ref = bool(session.style_reference_path)
    has_logo_ref = bool(session.logo_path)

    # === Build base prompt ===
    prompt = None
    use_named = False

    # Tier 1: Visual script scene description (clean header + scene)
    if visual_script:
        prompt = build_aplus_module_prompt(
            product_title=session.product_title,
            brand_name=brand_name,
            features=features,
            target_audience=session.target_audience or "",
            framework=framework,
            visual_script=visual_script,
            module_index=module_index,
            module_count=len(visual_script.get("modules", [])),
            custom_instructions="",  # handled by AI enhancement below
            has_style_ref=has_style_ref,
            has_logo=has_logo_ref,
            has_product_ref=has_product_ref,
        )
        if prompt:
            use_named = True
            logger.info(f"Using visual script prompt for module {module_index}, {len(prompt)} chars")

    # Tier 2: No visual script fallback
    if not prompt:
        prompt = _build_legacy_module_prompt(
            session=session,
            module_index=module_index,
            module_type_value=module_type_value,
            brand_name=brand_name,
            features=features,
            framework=framework,
            design_context=design_context,
        )

    # === AI-enhanced rewrite when user provides feedback ===
    change_summary = None
    if custom_instructions and vision_service:
        image_type_key = f"aplus_{module_index}"
        prompt, change_summary = await _apply_ai_rewrite(
            prompt=prompt,
            custom_instructions=custom_instructions,
            image_type_key=image_type_key,
            session=session,
            design_context=design_context,
            vision_service=vision_service,
        )
        logger.info(f"AI Designer enhanced module {module_index} prompt: {change_summary[:100]}")

    # === Finalize: header + boilerplate strip + lighting ===
    module_header = APLUS_MODULE_HEADER.format(
        reference_images_desc=_ref_desc(
            has_style_ref, (has_logo_ref and config.send_logo),
            has_product_ref=has_product_ref,
        )
    )
    prompt = _finalize_prompt(prompt, module_header)

    # === Assemble reference images ===
    ref_images = assemble_reference_images(
        session, f"aplus_{module_index}",
        use_named=use_named,
        module_index=module_index,
        module_count=module_count,
    )

    return AplusPromptResult(
        prompt=prompt,
        reference_images=ref_images,
        use_named=use_named,
        module_config=config,
        change_summary=change_summary,
    )


def _build_legacy_module_prompt(
    session: GenerationSession,
    module_index: int,
    module_type_value: str,
    brand_name: str,
    features: list,
    framework: dict,
    design_context: Optional[DesignContext],
) -> str:
    """Build A+ module prompt when no visual script exists (legacy fallback)."""
    if module_index == 0:
        position = "first"
    elif module_index > 0:
        position = "middle"
    else:
        position = "only"

    framework_name = "Professional"
    framework_style = "Clean and modern premium design"
    framework_mood = "Professional and engaging"
    primary_color = "#C85A35"
    color_palette = [primary_color]

    if framework:
        framework_name = framework.get('framework_name', framework_name)
        framework_style = framework.get('design_philosophy', framework_style)
        framework_mood = framework.get('brand_voice', framework_mood)
        colors = framework.get('colors', [])
        if colors:
            color_palette = [c.get('hex', '#C85A35') for c in colors if c.get('hex')]
            primary_color = next(
                (c.get('hex') for c in colors if c.get('role') == 'primary'),
                colors[0].get('hex', '#C85A35') if colors else '#C85A35'
            )

    if design_context:
        if design_context.selected_framework_name:
            framework_name = design_context.selected_framework_name
        if design_context.locked_colors:
            color_palette = design_context.locked_colors
            primary_color = design_context.locked_colors[0]

    return get_aplus_prompt(
        module_type=module_type_value,
        position=position,
        product_title=session.product_title,
        brand_name=brand_name,
        features=features,
        target_audience=session.target_audience or "",
        framework_name=framework_name,
        framework_style=framework_style,
        primary_color=primary_color,
        color_palette=color_palette,
        framework_mood=framework_mood,
        custom_instructions="",  # handled by AI enhancement in caller
    )


# ============================================================================
# Hero pair compiler
# ============================================================================

async def compile_aplus_hero(
    session: GenerationSession,
    visual_script: Optional[Dict],
    custom_instructions: Optional[str],
    brand_name: str,
    design_context: Optional[DesignContext],
    vision_service: Any,
    gemini_service: Any,
    db: Any,
    image_model: Optional[str] = None,
) -> AplusPromptResult:
    """
    Compile the full prompt + reference images for the A+ hero pair.

    Handles auto-generating visual script if missing, building the hero prompt,
    AI rewriting on custom instructions, and assembling reference images.
    """
    config = get_module_config(0)  # hero pair = module 0
    has_product_ref = bool(session.upload_path)
    has_style_ref = bool(session.style_reference_path)
    has_logo_ref = bool(session.logo_path)

    # Auto-generate visual script if missing
    if not visual_script:
        logger.info("No visual script found, generating one for hero pair...")
        visual_script = await _auto_generate_visual_script(
            session, brand_name, gemini_service, db,
        )

    # Build the hero pair prompt
    prompt = build_hero_pair_prompt(
        visual_script=visual_script,
        product_title=session.product_title,
        brand_name=brand_name,
        custom_instructions="",  # handled by AI enhancement below
        has_style_ref=has_style_ref,
        has_logo=has_logo_ref,
        has_product_ref=has_product_ref,
    )

    # AI-enhanced prompt rewriting when user provides feedback
    change_summary = None
    if custom_instructions and vision_service:
        prompt, change_summary = await _apply_ai_rewrite(
            prompt=prompt,
            custom_instructions=custom_instructions,
            image_type_key="aplus_hero",
            session=session,
            design_context=design_context,
            vision_service=vision_service,
        )
        logger.info(f"AI Designer enhanced hero pair prompt: {change_summary[:100]}")

    # === Finalize: header + boilerplate strip + lighting ===
    hero_header = APLUS_HERO_HEADER.format(
        reference_images_desc=_ref_desc(
            has_style_ref, has_logo_ref,
            has_product_ref=has_product_ref,
        )
    )
    prompt = _finalize_prompt(prompt, hero_header)

    # Assemble reference images
    ref_images = assemble_reference_images(
        session, "aplus_hero",
        module_index=0,
    )

    return AplusPromptResult(
        prompt=prompt,
        reference_images=ref_images,
        use_named=True,
        module_config=config,
        change_summary=change_summary,
    )


async def _auto_generate_visual_script(
    session: GenerationSession,
    brand_name: str,
    gemini_service: Any,
    db: Any,
) -> Dict:
    """Auto-generate a visual script when one doesn't exist yet."""
    from app.api.endpoints.generation import _sanitize_aplus_visual_script

    features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]
    framework = session.design_framework_json or {}
    listing_prompts = framework.get("generation_prompts", [])

    script_prompt = get_visual_script_prompt(
        product_title=session.product_title,
        brand_name=brand_name,
        features=features,
        target_audience=session.target_audience or "",
        framework=framework,
        module_count=6,
        listing_prompts=listing_prompts,
    )

    image_paths = []
    if session.upload_path:
        image_paths.append(session.upload_path)
    if session.additional_upload_paths:
        image_paths.extend(session.additional_upload_paths)

    raw_text = await gemini_service.generate_text_with_images(
        prompt=script_prompt,
        image_paths=image_paths,
        max_tokens=5000,
        temperature=0.7,
    )
    visual_script = _sanitize_aplus_visual_script(
        json_module.loads(strip_json_fences(raw_text))
    )
    session.aplus_visual_script = visual_script
    db.commit()

    return visual_script

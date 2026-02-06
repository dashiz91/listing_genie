"""
Shared utilities for the generation pipeline.

Extracts duplicated patterns from generation.py endpoints into reusable functions.
"""
import logging
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Any

from sqlalchemy.orm import Session as DBSession
from PIL import Image

from app.models.database import (
    GenerationSession,
    DesignContext,
    PromptHistory,
    ImageTypeEnum,
)
from app.services.supabase_storage_service import SupabaseStorageService

logger = logging.getLogger(__name__)


def get_enhancement_context(
    session: GenerationSession,
    design_context: Optional[DesignContext] = None,
) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Extract framework dict + product analysis text for AI-enhanced prompt rewriting.

    Returns (framework_dict, product_analysis_text) — shared by listing and A+ regen paths.
    """
    framework_dict = session.design_framework_json

    product_analysis_text = None
    if design_context and design_context.product_analysis:
        analysis = design_context.product_analysis
        if isinstance(analysis, dict):
            parts = []
            for key in (
                "what_i_see", "visual_characteristics", "product_category",
                "natural_mood", "ideal_customer",
            ):
                if analysis.get(key):
                    label = key.replace("_", " ").title()
                    parts.append(f"{label}: {analysis[key]}")
            product_analysis_text = "\n".join(parts) if parts else str(analysis)
        else:
            product_analysis_text = str(analysis)

    return framework_dict, product_analysis_text


def get_next_version(
    storage: SupabaseStorageService,
    session_id: str,
    storage_key: str,
) -> int:
    """
    Scan storage for existing versioned files and return the next version number.

    Looks for files matching `{storage_key}_v{N}.png` and returns max(N) + 1.
    Returns 1 if no versions exist.
    """
    version = 1
    try:
        all_files = storage.client.storage.from_(storage.generated_bucket).list(session_id)
        for f in all_files:
            name = f.get("name", "")
            m = re.match(rf'^{re.escape(storage_key)}_v(\d+)\.png$', name)
            if m:
                v = int(m.group(1))
                if v >= version:
                    version = v + 1
    except Exception:
        pass
    return version


def ensure_design_context(
    db: DBSession,
    session: GenerationSession,
    gemini=None,
    storage=None,
) -> DesignContext:
    """
    Get existing DesignContext for a session, or create one if missing.

    This replaces the repeated get-or-create pattern across A+ endpoints.
    """
    from app.services.generation_service import GenerationService

    ctx = db.query(DesignContext).filter(
        DesignContext.session_id == session.id
    ).first()
    if ctx:
        return ctx

    # Need to create one — requires a GenerationService instance
    gen_service = GenerationService(db=db, gemini=gemini, storage=storage)
    return gen_service.create_design_context(session)


def strip_json_fences(text: str) -> str:
    """
    Remove markdown code fences from JSON text returned by LLMs.

    Handles ```json ... ``` and ``` ... ``` patterns.
    """
    clean = text.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
    return clean


def build_reference_images_for_history(
    session: GenerationSession,
    *,
    include_canvas: bool = False,
    canvas_path: Optional[str] = None,
    include_previous: bool = False,
    previous_module_path: Optional[str] = None,
    previous_module_index: Optional[int] = None,
) -> List[Dict]:
    """
    Build the reference_images list for PromptHistory storage.

    Centralizes the repeated pattern of assembling ref image dicts for history.
    """
    refs = []
    if include_canvas and canvas_path:
        refs.append({"type": "gradient_canvas", "path": canvas_path})

    if session.upload_path:
        refs.append({"type": "primary", "path": session.upload_path})
    if session.style_reference_path:
        refs.append({"type": "style_reference", "path": session.style_reference_path})

    if include_previous and previous_module_path and previous_module_index is not None:
        refs.append({
            "type": f"previous_module_{previous_module_index}",
            "path": previous_module_path,
        })
    return refs


# ============================================================================
# Reference Image Assembly
# ============================================================================

@dataclass
class ReferenceImageSet:
    """
    Standardized set of reference images for any generation type.

    named_images: list of (label, path_or_pil_image) tuples for Gemini named image API
    unnamed_paths: list of paths for Gemini reference_image_paths API (legacy)
    history_meta: list of dicts for PromptHistory storage
    """
    named_images: List[Tuple[str, Any]] = field(default_factory=list)
    unnamed_paths: List[str] = field(default_factory=list)
    history_meta: List[Dict] = field(default_factory=list)


def assemble_reference_images(
    session: GenerationSession,
    image_type: str,
    *,
    focus_overrides: Optional[List[str]] = None,
    previous_module_path: Optional[str] = None,
    canvas_image: Optional[Any] = None,
    canvas_debug_path: Optional[str] = None,
    use_named: bool = True,
) -> ReferenceImageSet:
    """
    Centralized reference image assembly for ALL generation types.

    Encodes all rules about which images to include for each type:
    - Listing (non-main): upload + additional + style_ref + logo
    - Listing (main): upload + additional + style_ref (no logo)
    - A+ hero: upload + style_ref + logo (as BRAND_LOGO)
    - A+ module: upload + style_ref + logo (as BRAND_LOGO) + previous (if chained)
    - A+ canvas: canvas + upload + style_ref
    - Any with focus_overrides: only those images
    - Mobile transform: source desktop only (handled externally)
    """
    from app.prompts.templates.aplus_modules import (
        IMAGE_LABEL_PRODUCT, IMAGE_LABEL_STYLE, IMAGE_LABEL_PREVIOUS,
    )

    result = ReferenceImageSet()
    is_aplus = image_type.startswith("aplus_")
    use_focus = bool(focus_overrides)

    # ── Structural images (always included — canvas + previous module) ──
    if canvas_image is not None:
        result.named_images.append(("CANVAS_TO_COMPLETE", canvas_image))
        if canvas_debug_path:
            result.history_meta.append({"type": "gradient_canvas", "path": canvas_debug_path})

    # ── Content images (focus overrides OR default product/style/logo) ──
    if use_focus:
        # Listing focus: only focus images, no defaults
        # A+ focus: focus images replace product/style, structural images above still included
        for i, path in enumerate(focus_overrides):
            result.unnamed_paths.append(path)
            result.history_meta.append({"type": f"focus_reference_{i}", "path": path})
    else:
        # Default content images
        if session.upload_path:
            if use_named:
                result.named_images.append((IMAGE_LABEL_PRODUCT, session.upload_path))
            result.unnamed_paths.append(session.upload_path)
            result.history_meta.append({"type": "primary", "path": session.upload_path})

        # Additional product photos (listing images only, not A+)
        if not is_aplus and session.additional_upload_paths:
            for i, path in enumerate(session.additional_upload_paths):
                result.unnamed_paths.append(path)
                result.history_meta.append({"type": f"additional_product_{i+1}", "path": path})

        # Style reference (all types)
        if session.style_reference_path:
            if use_named:
                result.named_images.append((IMAGE_LABEL_STYLE, session.style_reference_path))
            result.unnamed_paths.append(session.style_reference_path)
            result.history_meta.append({"type": "style_reference", "path": session.style_reference_path})

    # Logo (listing non-main + all A+ modules, skip when focus overrides active)
    if not use_focus and image_type != "main" and session.logo_path:
        if is_aplus and use_named:
            result.named_images.append(("BRAND_LOGO", session.logo_path))
        result.unnamed_paths.append(session.logo_path)
        result.history_meta.append({"type": "logo", "path": session.logo_path})

    # ── Previous module (A+ chaining) ──
    # When focus overrides are active, only include if user explicitly selected it.
    # When no focus overrides, always include (default canvas continuity behavior).
    if previous_module_path and is_aplus:
        include_prev = not use_focus or previous_module_path in focus_overrides
        if include_prev:
            if use_named:
                result.named_images.append((IMAGE_LABEL_PREVIOUS, previous_module_path))
            result.unnamed_paths.append(previous_module_path)
            try:
                idx = int(image_type.split("_")[1])
                result.history_meta.append({
                    "type": f"previous_module_{idx - 1}",
                    "path": previous_module_path,
                })
            except (IndexError, ValueError):
                result.history_meta.append({"type": "previous_module", "path": previous_module_path})

    return result


# ============================================================================
# GenerationContext — unified context for any generation operation
# ============================================================================

@dataclass
class GenerationContext:
    """
    Unified context for any generation operation.

    Replaces 6+ separate code paths that each build prompt + images → Gemini → save
    with slightly different logic. Every endpoint builds a GenerationContext, then
    calls GenerationService.execute(ctx).
    """
    session: GenerationSession
    image_type: str                           # "main", "aplus_0", "aplus_hero"
    operation: str                            # "generate" | "edit" | "mobile_transform"
    prompt: str
    reference_images: ReferenceImageSet
    aspect_ratio: str = "1:1"                 # "1:1", "4:3", "21:9"
    image_size: str = "1K"
    target_dimensions: Optional[Tuple[int, int]] = None  # post-gen resize
    source_image_path: Optional[str] = None   # for edits
    module_index: Optional[int] = None        # A+ specific
    canvas_image: Optional[Any] = None        # canvas extension PIL Image
    storage_key: Optional[str] = None         # override storage key
    user_feedback: Optional[str] = None       # for prompt history
    change_summary: Optional[str] = None      # for prompt history
    model_name: Optional[str] = None          # which AI model generated this
    model_override: Optional[str] = None      # override default gemini model for this call

    @classmethod
    def for_aplus_module(
        cls,
        session: GenerationSession,
        module_index: int,
        prompt: str,
        reference_images: ReferenceImageSet,
        module_type: str = "full_image",
        custom_storage_key: Optional[str] = None,
    ) -> "GenerationContext":
        from app.services.image_utils import APLUS_DIMENSIONS
        dims = APLUS_DIMENSIONS.get(module_type, (1464, 600))
        return cls(
            session=session,
            image_type=f"aplus_{module_index}",
            operation="generate",
            prompt=prompt,
            reference_images=reference_images,
            aspect_ratio="21:9" if module_type == "full_image" else "1:1",
            target_dimensions=dims,
            module_index=module_index,
            storage_key=custom_storage_key or f"aplus_{module_type}_{module_index}",
        )

    @classmethod
    def for_aplus_hero(
        cls,
        session: GenerationSession,
        prompt: str,
        reference_images: ReferenceImageSet,
    ) -> "GenerationContext":
        return cls(
            session=session,
            image_type="aplus_hero",
            operation="generate",
            prompt=prompt,
            reference_images=reference_images,
            aspect_ratio="4:3",
        )

    @classmethod
    def for_mobile_transform(
        cls,
        session: GenerationSession,
        module_index: int,
        prompt: str,
        source_image_path: str,
    ) -> "GenerationContext":
        return cls(
            session=session,
            image_type=f"aplus_{module_index}",
            operation="mobile_transform",
            prompt=prompt,
            reference_images=ReferenceImageSet(),
            aspect_ratio="4:3",
            target_dimensions=(600, 450),
            source_image_path=source_image_path,
            module_index=module_index,
        )

    @classmethod
    def for_edit(
        cls,
        session: GenerationSession,
        image_type: str,
        edit_instructions: str,
        source_image_path: str,
        reference_images: ReferenceImageSet,
        aspect_ratio: str = "1:1",
        target_dimensions: Optional[Tuple[int, int]] = None,
    ) -> "GenerationContext":
        return cls(
            session=session,
            image_type=image_type,
            operation="edit",
            prompt=edit_instructions,
            reference_images=reference_images,
            aspect_ratio=aspect_ratio,
            source_image_path=source_image_path,
            target_dimensions=target_dimensions,
            user_feedback=edit_instructions,
            change_summary="Image edit",
        )

    @classmethod
    def for_canvas_extension(
        cls,
        session: GenerationSession,
        module_index: int,
        prompt: str,
        reference_images: ReferenceImageSet,
        canvas_image: Any,
    ) -> "GenerationContext":
        return cls(
            session=session,
            image_type=f"aplus_{module_index}",
            operation="canvas_extension",
            prompt=prompt,
            reference_images=reference_images,
            aspect_ratio="4:3",
            module_index=module_index,
            canvas_image=canvas_image,
            storage_key=f"aplus_full_image_{module_index}",
        )

"""
Image Generation API Endpoints

MASTER Level: Now includes Principal Designer AI for dynamic framework generation.
"""
import asyncio
import io
import json as json_module
import logging
import re
import time
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Optional
from PIL import Image

from app.core.auth import User, get_current_user
from app.db.session import get_db
from app.services.gemini_service import (
    GeminiService,
    _load_image_from_path,
    append_lighting_override_once,
    get_gemini_service,
)
from app.services.supabase_storage_service import SupabaseStorageService
from app.services.generation_service import GenerationService
from app.services.vision_service import VisionService, get_vision_service as get_unified_vision_service
from app.services.credits_service import CreditsService, MODEL_COSTS
from app.dependencies import get_storage_service, get_credits_service
from app.services.generation_utils import (
    GenerationContext, ReferenceImageSet, assemble_reference_images,
    get_next_version, ensure_design_context, strip_json_fences,
    build_reference_images_for_history, get_enhancement_context,
)
from app.services.prompt_builder import get_structural_context
from app.services.image_utils import resize_for_aplus_module, APLUS_DIMENSIONS
from app.config import settings


def _get_image_url(relative_path: str) -> str:
    """
    Convert a relative API path to an absolute URL.
    Uses backend_url setting if configured, otherwise returns relative path.
    """
    if settings.backend_url:
        return f"{settings.backend_url.rstrip('/')}{relative_path}"
    return relative_path
from app.services.canvas_compositor import CanvasCompositor
from app.models.database import (
    GenerationSession, DesignContext,
    PromptHistory as PromptHistoryModel,
    ImageTypeEnum as DBImageType, ImageTypeEnum as DBImageTypeEnum,
    ColorModeEnum, UserSettings,
)
from app.prompts.templates.aplus_modules import (
    get_aplus_prompt, build_aplus_module_prompt,
    build_canvas_inpainting_prompt, build_hero_pair_prompt,
    get_visual_script_prompt, strip_aplus_banner_boilerplate,
    APLUS_MODULE_HEADER, APLUS_HERO_HEADER,
)

logger = logging.getLogger(__name__)

from app.schemas.generation import (
    GenerationRequest,
    GenerationResponse,
    SessionStatusResponse,
    SingleImageRequest,
    SingleImageResponse,
    StylePreviewRequest,
    StylePreviewResponse,
    SelectStyleRequest,
    ImageResult,
    GenerationStatusEnum,
    ImageTypeEnum,
    ColorMode,
    FrameworkGenerationRequest,
    FrameworkGenerationResponse,
    FrameworkGenerationWithImageRequest,
    GenerateWithFrameworkRequest,
    PromptHistoryResponse,
    EditImageRequest,
    AplusModuleType,
    AplusModuleRequest,
    RefinedModule,
    AplusModuleResponse,
    AplusVisualScriptRequest,
    AplusVisualScriptResponse,
    ReplanRequest,
    ReplanResponse,
    HeroPairRequest,
    HeroPairModuleResult,
    HeroPairResponse,
    AplusMobileRequest,
    AltTextRequest,
    AltTextResponse,
    AplusMobileResponse,
    AplusAllMobileRequest,
    ImageGenerationPrompt,
    DesignFramework,
)
from app.prompts import get_all_styles, generate_random_framework, get_all_presets

router = APIRouter()


def _sanitize_aplus_visual_script(visual_script: dict) -> dict:
    """Strip known A+ boilerplate from generated visual scripts before persistence."""
    if not isinstance(visual_script, dict):
        return visual_script

    cleaned = dict(visual_script)

    hero_prompt = cleaned.get("hero_pair_prompt")
    if isinstance(hero_prompt, str):
        cleaned["hero_pair_prompt"] = strip_aplus_banner_boilerplate(hero_prompt)

    modules = cleaned.get("modules")
    if isinstance(modules, list):
        sanitized_modules = []
        for module in modules:
            if not isinstance(module, dict):
                sanitized_modules.append(module)
                continue

            module_clean = dict(module)
            for key in ("scene_prompt", "generation_prompt", "scene_description"):
                value = module_clean.get(key)
                if isinstance(value, str):
                    module_clean[key] = strip_aplus_banner_boilerplate(value)
            sanitized_modules.append(module_clean)
        cleaned["modules"] = sanitized_modules

    return cleaned


def _resolve_effective_brand_name(
    session: GenerationSession,
    db: Session,
    user_id: Optional[str] = None,
) -> str:
    """
    Resolve the brand name used in prompt generation.

    Priority:
    1) Session brand_name
    2) UserSettings.default_brand_name (if available)
    """
    session_brand = (session.brand_name or "").strip()
    product_title = (session.product_title or "").strip()
    session_brand_matches_title = (
        bool(session_brand)
        and bool(product_title)
        and session_brand.casefold() == product_title.casefold()
    )
    if session_brand and not session_brand_matches_title:
        return session_brand

    lookup_user_id = user_id or getattr(session, "user_id", None)
    if lookup_user_id:
        settings = db.query(UserSettings).filter(
            UserSettings.user_id == lookup_user_id
        ).first()
        if settings and settings.default_brand_name:
            return settings.default_brand_name.strip()

    # If brand appears to be just the product title, treat as unspecified.
    # In that case prompts should prefer logo rendering instead of typing
    # product title as a fake brand name.
    if session_brand_matches_title:
        return ""

    if session_brand:
        return session_brand

    return ""


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


def _build_aplus_reference_images_desc(
    *,
    has_product_ref: bool,
    has_style_ref: bool,
    has_logo: bool,
) -> str:
    """Build A+ reference image description header lines."""
    lines = []
    if has_product_ref:
        lines.append("- PRODUCT_PHOTO: The actual product - honor its materials, proportions, character")
    if has_style_ref:
        lines.append("- STYLE_REFERENCE: Match this visual style, mood, and color treatment")
    if has_logo:
        lines.append("- BRAND_LOGO: Reproduce this logo where appropriate")
    if not lines:
        lines.append("- Use the supplied reference images exactly as provided")
    return "\n".join(lines)


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


def get_generation_service(
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
) -> GenerationService:
    """Dependency injection for GenerationService"""
    return GenerationService(db=db, gemini=gemini, storage=storage)


def get_vision_service() -> VisionService:
    """
    Dependency injection for Vision Service (Principal Designer AI).

    Uses Gemini by default.
    OpenAI vision is deprecated and disabled unless
    ALLOW_OPENAI_VISION=true is explicitly set for emergency use.
    """
    return get_unified_vision_service()


def _get_owned_session(service: GenerationService, session_id: str, user: User) -> GenerationSession:
    """Resolve a session only if it belongs to the authenticated user."""
    session = service.get_session_status(session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/", response_model=GenerationResponse)
async def start_generation(
    request: GenerationRequest,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Start a new image generation session.

    Creates a session and generates all 5 listing images:
    - Main product image
    - Infographic 1 (feature 1)
    - Infographic 2 (feature 2)
    - Lifestyle image
    - Comparison chart

    Returns session ID and initial status.
    """
    try:
        # Create session
        session = service.create_session(request, user_id=user.id)

        # Generate all images
        results = await service.generate_all_images(session)

        return GenerationResponse(
            session_id=session.id,
            status=GenerationStatusEnum(session.status.value),
            images=results,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/async", response_model=GenerationResponse)
async def start_generation_async(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Start an async image generation session.

    Creates a session and queues image generation in the background.
    Returns immediately with session ID to poll for status.
    """
    try:
        # Create session
        session = service.create_session(request, user_id=user.id)

        # Queue background generation
        background_tasks.add_task(
            service.generate_all_images,
            session,
        )

        # Return pending status
        results = service.get_session_results(session)

        return GenerationResponse(
            session_id=session.id,
            status=GenerationStatusEnum.PROCESSING,
            images=results,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start generation: {str(e)}")


@router.get("/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Get status of a generation session.

    Returns current status and results for all images.
    """
    session = _get_owned_session(service, session_id, user)

    results = service.get_session_results(session)

    return SessionStatusResponse(
        session_id=session.id,
        status=GenerationStatusEnum(session.status.value),
        product_title=session.product_title,
        created_at=session.created_at.isoformat(),
        completed_at=session.completed_at.isoformat() if session.completed_at else None,
        images=results,
    )


@router.post("/single", response_model=SingleImageResponse)
async def generate_single_image(
    request: SingleImageRequest,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
    credits: CreditsService = Depends(get_credits_service),
):
    """
    Generate or regenerate a single image type for an existing session.

    Useful for retrying failed generations or regenerating specific images.
    Accepts an optional note/instructions to customize the regeneration.
    """
    session = _get_owned_session(service, request.session_id, user)

    # === CREDIT CHECK ===
    if user:
        model = request.image_model or "gemini-3-pro-image-preview"
        cost = credits.get_credit_cost("listing_image", model, 1)
        has_credits, balance, msg = credits.check_credits(user.id, cost, user.email)
        if not has_credits:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Need {cost}, have {balance}. Please upgrade your plan."
            )

    try:
        # Convert schema enum to DB enum
        db_image_type = DBImageType(request.image_type.value)

        # Pass the optional note and reference images to generate_single_image
        result = await service.generate_single_image(
            session, db_image_type,
            note=request.note,
            reference_image_paths=request.reference_image_paths,
            model_override=request.image_model,
        )

        # Update session status based on image statuses
        service._update_session_status(session)

        # === DEDUCT CREDITS ===
        if user and result.status == "complete":
            model = request.image_model or "gemini-3-pro-image-preview"
            cost = credits.get_credit_cost("listing_image", model, 1)
            credits.deduct_credits(user.id, cost, "listing_image", email=user.email)

        return SingleImageResponse(
            session_id=session.id,
            image_type=request.image_type,
            status=result.status,
            storage_path=result.storage_path,
            error_message=result.error_message,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/edit", response_model=SingleImageResponse)
async def edit_single_image(
    request: EditImageRequest,
    service: GenerationService = Depends(get_generation_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
    user: User = Depends(get_current_user),
    credits: CreditsService = Depends(get_credits_service),
):
    """
    Edit an existing generated image with specific instructions.

    This is DIFFERENT from regeneration:
    - Regenerate: Creates a NEW image using original product photos
    - Edit: MODIFIES the existing generated image based on instructions

    Use edit for:
    - "Change the headline to 'New Text'"
    - "Make the background color lighter"
    - "Remove the icon in the corner"
    - "Fill the empty area with the gradient"

    Use regenerate for:
    - "Try a completely different style"
    - "This doesn't look right, try again"

    Mobile mode:
    - Set mobile=True to edit the mobile version of an A+ module
    - For A+ modules 0/1, edits the hero mobile image
    - For A+ modules 2+, edits the individual mobile image
    """
    session = _get_owned_session(service, request.session_id, user)

    # === CREDIT CHECK ===
    if user:
        cost = credits.get_credit_cost("edit_image", count=1)
        has_credits, balance, msg = credits.check_credits(user.id, cost, user.email)
        if not has_credits:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Need {cost}, have {balance}. Please upgrade your plan."
            )

    try:
        # Handle mobile A+ edit separately
        if request.mobile:
            image_type_str = request.image_type.value
            if not image_type_str.startswith("aplus_"):
                raise HTTPException(status_code=400, detail="Mobile edit is only supported for A+ modules")

            try:
                module_index = int(image_type_str.split("_")[1])
            except (IndexError, ValueError):
                raise HTTPException(status_code=400, detail=f"Invalid A+ image type format: {image_type_str}")

            mobile_key = "aplus_full_image_hero_mobile" if module_index in [0, 1] else f"aplus_full_image_{module_index}_mobile"
            mobile_path = f"supabase://{storage.generated_bucket}/{request.session_id}/{mobile_key}.png"

            try:
                storage.get_generated_url(request.session_id, mobile_key, expires_in=60)
            except Exception:
                raise HTTPException(status_code=400, detail=f"Mobile image doesn't exist for module {module_index}. Generate mobile version first.")

            logger.info(f"Editing mobile A+ module {module_index} with instructions: {request.edit_instructions}")


            ref_images = ReferenceImageSet(unnamed_paths=list(request.reference_image_paths or []))
            ctx = GenerationContext.for_edit(
                session=session,
                image_type=f"aplus_{module_index}",
                edit_instructions=request.edit_instructions,
                source_image_path=mobile_path,
                reference_images=ref_images,
                aspect_ratio="4:3",
                target_dimensions=(600, 450),
            )
            ctx.storage_key = mobile_key
            if request.image_model:
                ctx.model_override = request.image_model

            result = await service.execute(ctx)

            logger.info(f"Mobile A+ module {module_index} edited and saved: {result.primary_path}")

            # === DEDUCT CREDITS ===
            if user:
                cost = credits.get_credit_cost("edit_image", count=1)
                credits.deduct_credits(user.id, cost, "edit_image", email=user.email)

            return SingleImageResponse(
                session_id=request.session_id,
                image_type=request.image_type,
                status="complete",
                storage_path=result.primary_path,
                error_message=None,
            )

        # Standard desktop edit flow
        # Convert schema enum to DB enum
        db_image_type = DBImageType(request.image_type.value)

        # Call the edit method
        result = await service.edit_single_image(
            session,
            db_image_type,
            edit_instructions=request.edit_instructions,
            reference_image_paths=request.reference_image_paths,
            model_override=request.image_model,
        )

        # === DEDUCT CREDITS ===
        if user and result.status == "complete":
            cost = credits.get_credit_cost("edit_image", count=1)
            credits.deduct_credits(user.id, cost, "edit_image", email=user.email)

        return SingleImageResponse(
            session_id=session.id,
            image_type=request.image_type,
            status=result.status,
            storage_path=result.storage_path,
            error_message=result.error_message,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Edit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Edit failed: {str(e)}")


@router.post("/main", response_model=SingleImageResponse)
async def generate_main_image(
    session_id: str,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Generate just the main product image.

    Convenience endpoint for generating only the main image.
    """
    session = _get_owned_session(service, session_id, user)

    try:
        result = await service.generate_single_image(
            session,
            DBImageType.MAIN,
        )

        return SingleImageResponse(
            session_id=session.id,
            image_type=ImageTypeEnum.MAIN,
            status=result.status,
            storage_path=result.storage_path,
            error_message=result.error_message,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/{session_id}/retry", response_model=GenerationResponse)
async def retry_failed_images(
    session_id: str,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Retry generation of all failed images in a session.

    Only retries images with status='failed'. Returns updated results.
    """
    session = _get_owned_session(service, session_id, user)

    try:
        results = await service.retry_failed_images(session)

        # Get all current results
        all_results = service.get_session_results(session)

        return GenerationResponse(
            session_id=session.id,
            status=GenerationStatusEnum(session.status.value),
            images=all_results,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retry failed: {str(e)}")


@router.get("/{session_id}/stats")
async def get_generation_stats(
    session_id: str,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Get generation statistics for a session.

    Returns retry counts and status breakdown.
    """
    session = _get_owned_session(service, session_id, user)

    return service.get_generation_stats(session)


# ============== Prompt History Endpoints ==============

@router.get("/{session_id}/prompts", response_model=List[PromptHistoryResponse])
async def get_session_prompts(
    session_id: str,
    response: Response,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Get all prompts used for image generation in this session.

    Returns prompt history for each image type, including:
    - The actual prompt sent to Gemini
    - Version number (for regenerations)
    - User feedback that triggered regeneration (if any)
    - AI's interpretation of changes made
    """
    session = _get_owned_session(service, session_id, user)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    context = service.get_design_context(session.id)
    if not context:
        return []  # No prompts stored yet

    # Get all prompt history entries for all image types (listing + A+)
    all_types = list(service.IMAGE_TYPES) + [
        DBImageType.APLUS_0, DBImageType.APLUS_1, DBImageType.APLUS_2,
        DBImageType.APLUS_3, DBImageType.APLUS_4, DBImageType.APLUS_5,
    ]

    results = []
    for image_type in all_types:
        history = service.get_prompt_history(context, image_type)
        for h in history:
            results.append(PromptHistoryResponse(
                image_type=h.image_type.value,
                version=h.version,
                prompt_text=h.prompt_text,
                user_feedback=h.user_feedback,
                change_summary=h.change_summary,
                model_name=getattr(h, 'model_name', None),
                created_at=h.created_at.isoformat() if h.created_at else "",
            ))

    return results


@router.get("/{session_id}/prompts/{image_type}", response_model=PromptHistoryResponse)
async def get_image_prompt(
    session_id: str,
    image_type: str,
    response: Response,
    version: Optional[int] = None,
    track: Optional[str] = None,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Get a prompt for a specific image type.

    Args:
        version: Optional version number (1-based). If omitted, returns the latest version.

    Returns the prompt used to generate this image version,
    including any user feedback and AI's interpretation of changes.
    """
    session = _get_owned_session(service, session_id, user)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    context = service.get_design_context(session.id)
    if not context:
        raise HTTPException(status_code=404, detail="No design context found - image may not have been generated yet")

    try:
        db_image_type = DBImageType(image_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid image type: {image_type}")

    requested_track = (track or "").strip().lower()
    if requested_track and requested_track not in ("desktop", "mobile", "all"):
        raise HTTPException(status_code=400, detail=f"Invalid prompt track: {track}")
    prompt_track = requested_track or ("desktop" if image_type.startswith("aplus_") else "all")

    filtered_history: List[PromptHistoryModel]
    if prompt_track == "desktop":
        filtered_history = service.get_prompt_history(
            context,
            db_image_type,
            include_mobile=False,
        )
        if version is not None:
            latest = filtered_history[version - 1] if 1 <= version <= len(filtered_history) else None
        else:
            latest = filtered_history[-1] if filtered_history else None
    elif prompt_track == "mobile":
        filtered_history = service.get_prompt_history(
            context,
            db_image_type,
            include_mobile=True,
            mobile_only=True,
        )
        if version is not None:
            latest = filtered_history[version - 1] if 1 <= version <= len(filtered_history) else None
        else:
            latest = filtered_history[-1] if filtered_history else None
    else:
        filtered_history = service.get_prompt_history(context, db_image_type)
        if version is not None:
            latest = service.get_prompt_by_version(context, db_image_type, version)
        else:
            latest = service.get_latest_prompt(context, db_image_type)

    if not latest:
        track_detail = f" ({prompt_track})" if prompt_track != "all" else ""
        raise HTTPException(
            status_code=404,
            detail=f"No prompt found for image type: {image_type}{track_detail}" + (f" version {version}" if version else ""),
        )

    resolved_version = latest.version
    if prompt_track in ("desktop", "mobile"):
        for idx, item in enumerate(filtered_history, start=1):
            if item.id == latest.id:
                resolved_version = idx
                break

    # Build reference images list
    # If the prompt has stored reference_image_paths (A+ modules), use those
    # Otherwise fall back to deriving from session data (listing images)
    if latest.reference_image_paths:
        reference_images = latest.reference_image_paths
    else:
        reference_images = []
        if session.upload_path:
            reference_images.append({
                "type": "primary",
                "path": session.upload_path,
                "label": "PRODUCT_PHOTO",
            })
        if session.additional_upload_paths:
            for i, path in enumerate(session.additional_upload_paths):
                reference_images.append({
                    "type": f"additional_{i+1}",
                    "path": path,
                    "label": f"ADDITIONAL_PRODUCT_{i+1}",
                })
        if session.style_reference_path:
            reference_images.append({
                "type": "style_reference",
                "path": session.style_reference_path,
                "label": "STYLE_REFERENCE",
            })
        # Logo only for non-main images
        if session.logo_path and image_type != "main":
            reference_images.append({
                "type": "logo",
                "path": session.logo_path,
                "label": "BRAND_LOGO",
            })

    # Build designer context - everything that was fed to the AI Designer
    effective_brand_name = _resolve_effective_brand_name(session, service.db)
    designer_context = {
        "product_info": {
            "title": session.product_title,
            "brand_name": effective_brand_name or None,
            "features": [session.feature_1, session.feature_2, session.feature_3] if hasattr(session, 'feature_1') else [],
            "target_audience": session.target_audience if hasattr(session, 'target_audience') else None,
        },
        "framework": session.design_framework_json if session.design_framework_json else None,
        "global_note": session.global_note if session.global_note else None,
        "product_analysis": context.product_analysis if context and context.product_analysis else None,
    }

    # Extract key framework elements for easy viewing
    if session.design_framework_json:
        fw = session.design_framework_json
        designer_context["framework_summary"] = {
            "name": fw.get("framework_name"),
            "philosophy": fw.get("design_philosophy"),
            "brand_voice": fw.get("brand_voice"),
            "colors": fw.get("colors", []),
            "typography": fw.get("typography", {}),
            "story_arc": fw.get("story_arc", {}),
            "visual_treatment": fw.get("visual_treatment", {}),
        }
        # Get image-specific copy if available
        image_copy = fw.get("image_copy", [])
        for ic in image_copy:
            if ic.get("image_type") == image_type:
                designer_context["image_copy"] = ic
                break

    # For A+ modules, include the visual script in designer context
    if image_type.startswith("aplus_") and session.aplus_visual_script:
        designer_context["visual_script"] = session.aplus_visual_script
        # Extract this module's section
        try:
            module_idx = int(image_type.split("_")[1])
            script_modules = session.aplus_visual_script.get("modules", [])
            if module_idx < len(script_modules):
                designer_context["module_script"] = script_modules[module_idx]
        except (ValueError, IndexError):
            pass

    return PromptHistoryResponse(
        image_type=latest.image_type.value,
        version=resolved_version,
        prompt_text=latest.prompt_text,
        user_feedback=latest.user_feedback,
        change_summary=latest.change_summary,
        model_name=getattr(latest, 'model_name', None),
        created_at=latest.created_at.isoformat() if latest.created_at else "",
        reference_images=reference_images,
        designer_context=designer_context,
    )


# ============== Style Endpoints ==============

@router.get("/styles/list")
async def list_styles():
    """
    Get all available style presets.

    Returns list of styles with id, name, description, colors, and mood.
    """
    return get_all_styles()


@router.get("/styles/presets")
async def list_design_presets():
    """
    Get all professional design framework presets.

    Returns presets like tech_minimal, bold_energetic, luxury_elegant, etc.
    Each preset is a complete, professionally-designed style system.
    """
    return get_all_presets()


@router.post("/styles/generate-random")
async def generate_random_style(
    mood: str = None,
    energy: str = None,
):
    """
    Generate a random but cohesive design framework.

    Optionally constrain by mood (sophisticated, exciting, luxurious, etc.)
    or energy level (calm, moderate, energetic).

    Returns a complete design framework with all visual parameters
    that work together harmoniously.
    """
    framework = generate_random_framework(mood=mood, energy=energy)

    return {
        "framework": {
            "layout": {
                "grid": framework.layout_grid.value,
                "balance": framework.balance,
                "whitespace": framework.whitespace,
            },
            "colors": {
                "harmony": framework.color_harmony.value,
                "temperature": framework.color_temperature.value,
                "saturation": framework.saturation.value,
                "primary": framework.primary_color,
                "secondary": framework.secondary_color,
                "accent": framework.accent_color,
            },
            "typography": {
                "style": framework.typography_style.value,
                "letter_spacing": framework.letter_spacing,
            },
            "elements": {
                "shadow_style": framework.shadow_style.value,
                "background": framework.background_style.value,
                "shape_language": framework.shape_language.value,
                "icon_style": framework.icon_style.value,
                "badge_style": framework.badge_style.value,
            },
            "lighting": framework.lighting_mood.value,
            "mood": framework.mood,
            "energy": framework.energy,
            "formality": framework.formality,
        },
        "prompt_modifier": framework.to_prompt_section(),
    }


@router.post("/styles/preview", response_model=StylePreviewResponse)
async def generate_style_previews(
    request: StylePreviewRequest,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Generate preview images for multiple styles.

    Creates a main product image in each requested style so user
    can compare and select their preferred aesthetic.
    """
    try:
        # Create preview session
        session = service.create_preview_session(request, user_id=user.id)

        # Generate all style previews
        results = await service.generate_all_style_previews(
            session,
            request.style_ids,
        )

        return StylePreviewResponse(
            session_id=session.id,
            previews=results,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Style preview failed: {str(e)}")


@router.post("/styles/select")
async def select_style(
    request: SelectStyleRequest,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Select a style for the session.

    After user reviews style previews, they select one style
    that will be applied to all 5 listing images.
    """
    _get_owned_session(service, request.session_id, user)
    session = service.select_style(request.session_id, request.style_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.id,
        "style_id": session.style_id,
        "message": f"Style '{request.style_id}' selected. Ready for full generation."
    }


@router.post("/styles/generate-all", response_model=GenerationResponse)
async def generate_with_style(
    request: GenerationRequest,
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
):
    """
    Generate all 5 listing images with the selected style.

    Requires style_id in request. All images will follow the same
    visual style for a cohesive listing appearance.
    """
    if not request.style_id:
        raise HTTPException(
            status_code=400,
            detail="style_id is required. Use /styles/preview first to select a style."
        )

    try:
        session = service.create_session(request, user_id=user.id)
        results = await service.generate_all_images(session)

        return GenerationResponse(
            session_id=session.id,
            status=GenerationStatusEnum(session.status.value),
            images=results,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# ============================================================================
# MASTER LEVEL: Principal Designer AI - Dynamic Framework Generation
# ============================================================================

@router.post("/frameworks/analyze", response_model=FrameworkGenerationResponse)
async def analyze_and_generate_frameworks(
    request: FrameworkGenerationWithImageRequest,
    vision: VisionService = Depends(get_vision_service),
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
    credits: CreditsService = Depends(get_credits_service),
):
    """
    MASTER LEVEL: Analyze product image, generate design frameworks, and create preview images.

    This is the main entry point for the MASTER level design flow:

    1. User uploads product image (via /upload endpoint)
    2. User calls THIS endpoint with the upload_path
    3. AI Vision SEES the product and generates design frameworks:
       - WITHOUT style reference: 4 different framework options
       - WITH style reference: 1 framework that matches the style reference
    4. We generate a PREVIEW IMAGE for each framework using the product
    5. User reviews previews and selects their preferred framework
    6. The selected preview image is used as STYLE REFERENCE for all 5 images

    Each framework includes:
    - Preview image URL (so user can SEE the style)
    - Color palette with exact hex codes (from style ref or product colors)
    - Typography with specific font names, weights, sizes
    - Headlines tailored to THIS specific product
    - Story arc across 5 images
    - Layout and visual treatment specs

    Framework Types (when no style reference - 4 options):
    - Framework 1: "Safe Excellence" - Most likely to convert, professional
    - Framework 2: "Bold Creative" - Unexpected but compelling design risk
    - Framework 3: "Emotional Story" - Feelings and lifestyle focus
    - Framework 4: "Premium Elevation" - Makes product feel luxurious

    With style reference: Single "Style Match" framework that extracts styling from the reference.
    """
    try:
        # === API ENDPOINT LOGGING ===
        logger.info("=" * 60)
        logger.info("[API ENDPOINT] /frameworks/analyze called")
        logger.info(f"[API ENDPOINT] Request upload_path: {request.upload_path}")
        logger.info(f"[API ENDPOINT] Request additional_upload_paths: {request.additional_upload_paths}")
        logger.info(f"[API ENDPOINT] Request color_mode: {request.color_mode}")
        logger.info(f"[API ENDPOINT] Request locked_colors: {request.locked_colors}")
        logger.info(f"[API ENDPOINT] Request style_reference_path: {request.style_reference_path}")
        logger.info("=" * 60)

        # === CREDIT CHECK ===
        # Framework analysis: 2 credits (analysis) + 1 credit per preview
        num_previews = 0 if request.skip_preview_generation else request.framework_count
        analysis_cost = credits.get_credit_cost("framework_analysis", count=1)
        preview_cost = credits.get_credit_cost("framework_preview", count=num_previews)
        total_cost = analysis_cost + preview_cost

        has_credits, balance, msg = credits.check_credits(user.id, total_cost, user.email)
        if not has_credits:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Need {total_cost}, have {balance}. Please upgrade your plan."
            )

        # Step 1: AI Vision analyzes product and generates framework(s)
        # - Without style reference: 4 different framework options
        # - With style reference: 1 framework that matches the style
        # Color mode determines how AI handles colors
        result = await vision.generate_frameworks(
            product_image_path=request.upload_path,
            product_name=request.product_title,
            brand_name=request.brand_name,
            features=request.features,
            target_audience=request.target_audience,
            primary_color=request.primary_color,
            additional_image_paths=request.additional_upload_paths if request.additional_upload_paths else None,
            color_mode=request.color_mode.value,
            locked_colors=request.locked_colors if request.locked_colors else None,
            style_reference_path=request.style_reference_path,  # NEW: Pass style ref so AI can see it
        )

        frameworks = result.get('frameworks', [])

        # Limit to requested framework count (saves preview generation time/cost)
        if request.framework_count < len(frameworks):
            frameworks = frameworks[:request.framework_count]
            logger.info(f"Limited to {request.framework_count} framework(s) as requested")

        # Step 2: Create a session for storing preview images
        preview_request = StylePreviewRequest(
            product_title=request.product_title,
            feature_1=request.features[0] if request.features else None,
            upload_path=request.upload_path,
            style_ids=[f"framework_{i+1}" for i in range(len(frameworks))],
        )
        session = service.create_preview_session(
            preview_request,
            user_id=user.id,
        )
        # Store additional form data on the session so it appears in projects
        session.brand_name = request.brand_name
        session.feature_2 = request.features[1] if request.features and len(request.features) > 1 else None
        session.feature_3 = request.features[2] if request.features and len(request.features) > 2 else None
        session.target_audience = request.target_audience
        session.additional_upload_paths = request.additional_upload_paths or []
        session.style_reference_path = request.style_reference_path
        service.db.commit()

        # Store original style reference in DesignContext AND copy to generated bucket with versioning
        if request.style_reference_path:
            logger.info(f"Creating DesignContext with original_style_reference_path: {request.style_reference_path}")
            service.create_design_context(
                session=session,
                product_analysis=result,
                original_style_reference_path=request.style_reference_path,
            )

            # Copy style reference to generated bucket with version 1
            try:
                storage = get_storage_service()
                versioned_path = storage.copy_upload_to_generated_versioned(
                    upload_path=request.style_reference_path,
                    session_id=session.id,
                    image_type="style_reference",
                    version=1,
                )
                logger.info(f"Saved versioned style reference: {versioned_path}")
            except Exception as e:
                logger.warning(f"Failed to save versioned style reference: {e}")
                # Non-fatal - continue with original path

        # Step 3: Generate preview images (or skip if using original style ref)
        logger.info(f"skip_preview_generation={request.skip_preview_generation}, style_reference_path={request.style_reference_path}")
        if request.skip_preview_generation and request.style_reference_path:
            # Use the original style reference image as the preview for all frameworks
            logger.info("Skipping preview generation — using original style reference image")
            storage = get_storage_service()
            # Build a preview URL from the style reference path
            style_ref_url = _get_image_url(f"/api/images/file?path={request.style_reference_path}")
            for fw in frameworks:
                fw['preview_url'] = style_ref_url
                fw['preview_path'] = request.style_reference_path
            frameworks_with_previews = frameworks
        else:

            gemini = get_gemini_service()
            storage = get_storage_service()

            async def generate_preview(i: int, framework: dict) -> dict:
                """Generate a single preview image for a framework"""
                try:
                    preview_prompt = vision.framework_to_prompt(framework, 'main')
                    preview_image = await gemini.generate_image(
                        prompt=preview_prompt,
                        reference_image_paths=[request.upload_path],
                        aspect_ratio="1:1",
                        max_retries=2,
                    )

                    if preview_image:
                        storage_path = storage.save_generated_image(
                            session_id=session.id,
                            image_type=f"framework_preview_{i+1}",
                            image=preview_image,
                        )
                        framework['preview_url'] = _get_image_url(f"/api/images/{session.id}/framework_preview_{i+1}")
                        framework['preview_path'] = storage_path
                        logger.info(f"Preview {i+1} generated successfully")
                    else:
                        framework['preview_url'] = None
                        framework['preview_path'] = None
                except Exception as e:
                    logger.warning(f"Failed to generate preview for framework {i+1}: {e}")
                    framework['preview_url'] = None
                    framework['preview_path'] = None
                return framework

            # Generate all previews in parallel
            num_frameworks = len(frameworks)
            logger.info(f"Generating {num_frameworks} framework preview(s) in parallel...")
            frameworks_with_previews = await asyncio.gather(
                *[generate_preview(i, fw) for i, fw in enumerate(frameworks)]
            )
            logger.info(f"All {num_frameworks} preview(s) generated")

        # Handle nested product_analysis structure
        product_analysis = result.get('product_analysis', {})
        if isinstance(product_analysis, dict):
            analysis_text = product_analysis.get('what_i_see', 'Product analyzed successfully')
            product_analysis_raw = product_analysis  # Keep the full dict for regeneration
        else:
            analysis_text = str(product_analysis)
            product_analysis_raw = None

        # === DEDUCT CREDITS ===
        num_previews = len(frameworks_with_previews)
        analysis_cost = credits.get_credit_cost("framework_analysis", count=1)
        preview_cost = credits.get_credit_cost("framework_preview", count=num_previews)
        total_cost = analysis_cost + preview_cost
        credits.deduct_credits(user.id, total_cost, "framework_analysis", email=user.email)

        return FrameworkGenerationResponse(
            session_id=session.id,
            product_analysis=analysis_text,
            product_analysis_raw=product_analysis_raw,  # Include raw for regeneration context
            frameworks=frameworks_with_previews,
            generation_notes=result.get('generation_notes', ''),
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Product image not found. Please upload the image first."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Framework generation failed: {str(e)}")


@router.post("/frameworks/generate", response_model=GenerationResponse)
async def generate_with_framework(
    request: GenerateWithFrameworkRequest,
    vision: VisionService = Depends(get_vision_service),
    service: GenerationService = Depends(get_generation_service),
    user: User = Depends(get_current_user),
    credits: CreditsService = Depends(get_credits_service),
):
    """
    MASTER LEVEL - STEP 2: Generate all 5 listing images with the selected framework.

    This is the TWO-STEP flow:

    STEP 1 (already done): User called /frameworks/analyze which:
      - Analyzed the product with GPT-4o Vision
      - Generated 4 style frameworks
      - Created preview images for each

    STEP 2 (THIS ENDPOINT): User selected a framework, now we:
      1. Generate 5 DETAILED image prompts specific to the product + framework
      2. Use those prompts to generate 5 RADICALLY DIFFERENT images:
         - Image 1: Pure product on white (no text)
         - Image 2: Technical infographic with callouts
         - Image 3: Benefits grid with icons
         - Image 4: Lifestyle with real person
         - Image 5: Multiple uses / package contents

    The selected framework's preview image is used as style reference.
    """
    try:
        framework = request.framework

        # === CREDIT CHECK ===
        # Determine how many images will be generated
        model = request.image_model or "gemini-3-pro-image-preview"
        if request.create_only:
            num_images = 0
        elif request.single_image_type:
            num_images = 1
        else:
            num_images = 6  # 6 listing images (main + 5 variants)

        if num_images > 0:
            cost = credits.get_credit_cost("listing_image", model, num_images)
            has_credits, balance, msg = credits.check_credits(user.id, cost, user.email)
            if not has_credits:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"Insufficient credits. Need {cost}, have {balance}. Please upgrade your plan."
                )

        # STEP 1: Generate 5 detailed image prompts for this framework
        logger.info(f"Generating 5 image prompts for framework: {framework.get('framework_name')}")

        generation_prompts = await vision.generate_image_prompts(
            framework=framework,
            product_name=request.product_title,
            product_description=request.product_title,
            features=request.features,
            target_audience=request.target_audience,
            global_note=request.global_note,  # AI Designer interprets for each image
            has_style_reference=bool(request.style_reference_path),  # Tell AI Designer about style ref
            brand_name=request.brand_name,
        )

        logger.info(f"Generated {len(generation_prompts)} prompts")

        # Add prompts to the framework
        framework['generation_prompts'] = generation_prompts

        # STEP 2: Create the generation request with the framework (including prompts)

        # Convert framework dict to DesignFramework model
        # First, convert generation_prompts to proper format
        prompt_models = []
        for gp in generation_prompts:
            prompt_models.append(ImageGenerationPrompt(
                image_number=gp.get('image_number', 1),
                image_type=gp.get('image_type', 'main'),
                prompt=gp.get('prompt', ''),
                composition_notes=gp.get('composition_notes', ''),
                key_elements=gp.get('key_elements', []),
            ))

        # Build the full DesignFramework
        design_framework = DesignFramework(
            framework_id=framework.get('framework_id', 'selected'),
            framework_name=framework.get('framework_name', 'Selected Framework'),
            framework_type=framework.get('framework_type'),
            design_philosophy=framework.get('design_philosophy', ''),
            colors=[
                {
                    'hex': c.get('hex', '#000000'),
                    'name': c.get('name', 'Color'),
                    'role': c.get('role', 'primary'),
                    'usage': c.get('usage', ''),
                }
                for c in framework.get('colors', [])
            ],
            typography=framework.get('typography', {}),
            story_arc=framework.get('story_arc', {}),
            image_copy=framework.get('image_copy', []),
            brand_voice=framework.get('brand_voice', ''),
            layout=framework.get('layout', {}),
            visual_treatment=framework.get('visual_treatment', {}),
            rationale=framework.get('rationale', ''),
            target_appeal=framework.get('target_appeal', ''),
            generation_prompts=prompt_models,
        )

        # Create the generation request
        gen_request = GenerationRequest(
            product_title=request.product_title,
            upload_path=request.upload_path,
            additional_upload_paths=request.additional_upload_paths or [],
            feature_1=request.features[0] if len(request.features) > 0 else None,
            feature_2=request.features[1] if len(request.features) > 1 else None,
            feature_3=request.features[2] if len(request.features) > 2 else None,
            target_audience=request.target_audience,
            brand_name=request.brand_name,
            logo_path=request.logo_path,
            style_reference_path=request.style_reference_path or framework.get('preview_path'),
            design_framework=design_framework,
            global_note=request.global_note,
        )

        # STEP 3: Generate images (all 5 or just 1 if single_image_type specified)
        session = service.create_session(gen_request, user_id=user.id)

        # Create DesignContext with product_analysis and/or original_style_reference for restoration support
        if request.product_analysis or request.original_style_reference_path:
            logger.info("Creating DesignContext for regeneration/restoration support")
            service.create_design_context(
                session=session,
                product_analysis=request.product_analysis,
                original_style_reference_path=request.original_style_reference_path,
            )

        # Check if we should create only, generate one, or generate all
        if request.create_only:
            # Just create session, no generation
            logger.info("Session created (create_only mode), skipping generation")
            results = service.get_session_results(session)
        elif request.single_image_type:
            # Generate only the specified image type
            logger.info(f"Generating SINGLE image: {request.single_image_type}")
            try:
                db_image_type = DBImageType(request.single_image_type)
                result = await service.generate_single_image(
                    session, db_image_type, model_override=request.image_model
                )
                # Get all image statuses (4 pending + 1 generated)
                results = service.get_session_results(session)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid image type: {request.single_image_type}")
        else:
            # Generate all 5 images sequentially
            logger.info("Starting generation of all 5 images...")
            results = await service.generate_all_images(session, model_override=request.image_model)

        # === DEDUCT CREDITS ===
        if not request.create_only:
            model = request.image_model or "gemini-3-pro-image-preview"
            # Count how many images were actually generated (complete status)
            completed_count = sum(1 for r in results if r.status == "complete")
            if completed_count > 0:
                cost = credits.get_credit_cost("listing_image", model, completed_count)
                credits.deduct_credits(user.id, cost, "listing_image", email=user.email)

        return GenerationResponse(
            session_id=session.id,
            status=GenerationStatusEnum(session.status.value),
            images=results,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Generation with framework failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/aplus/hero-pair", response_model=HeroPairResponse)
async def generate_aplus_hero_pair(
    request: HeroPairRequest,
    service: GenerationService = Depends(get_generation_service),
    vision: VisionService = Depends(get_vision_service),
    user: User = Depends(get_current_user),
    gemini: GeminiService = Depends(get_gemini_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
    db: Session = Depends(get_db),
    credits: CreditsService = Depends(get_credits_service),
):
    """
    Generate the A+ hero pair (modules 0+1) as a single tall image, then split it in half.

    This produces two perfectly aligned banners from one Gemini call — zero seam possible.
    """
    start_time = time.time()
    logger.info(f"Hero pair request: session={request.session_id}, custom_instructions={request.custom_instructions!r}, ref_images={request.reference_image_paths}")

    # === CREDIT CHECK ===
    # Hero pair = 1 image generation (results in 2 modules)
    model = request.image_model or "gemini-3-pro-image-preview"
    cost = credits.get_credit_cost("aplus_module", model, 1)
    has_credits, balance, msg = credits.check_credits(user.id, cost, user.email)
    if not has_credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Need {cost}, have {balance}. Please upgrade your plan."
        )

    try:
        session = _get_owned_session(service, request.session_id, user)
        effective_brand_name = _resolve_effective_brand_name(
            session, db, user.id
        )
        has_product_ref = bool(session.upload_path)
        has_style_ref = bool(session.style_reference_path)
        has_logo_ref = bool(session.logo_path)

        # Auto-generate visual script if missing
        visual_script = session.aplus_visual_script
        if not visual_script:
            logger.info("No visual script found, generating one for hero pair...")
            features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]
            framework = session.design_framework_json or {}
            # Get listing prompts so A+ knows what NOT to repeat
            listing_prompts = framework.get("generation_prompts", [])
            script_prompt = get_visual_script_prompt(
                product_title=session.product_title,
                brand_name=effective_brand_name,
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

            raw_text = await gemini.generate_text_with_images(
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

        # Build the hero pair prompt
        prompt = build_hero_pair_prompt(
            visual_script=visual_script,
            product_title=session.product_title,
            brand_name=effective_brand_name,
            custom_instructions="",  # handled by AI enhancement below
            has_style_ref=has_style_ref,
            has_logo=has_logo_ref,
            has_product_ref=has_product_ref,
        )

        # AI-enhanced prompt rewriting when user provides feedback
        hero_change_summary = None
        if request.custom_instructions:
            design_context = db.query(DesignContext).filter(
                DesignContext.session_id == request.session_id
            ).first()
            structural_ctx = get_structural_context("aplus_hero")
            fw_dict, analysis_text = get_enhancement_context(session, design_context)
            try:
                enhancement = await vision.enhance_prompt_with_feedback(
                    original_prompt=prompt,
                    user_feedback=request.custom_instructions,
                    image_type="aplus_hero",
                    framework=fw_dict,
                    product_analysis=analysis_text,
                    structural_context=structural_ctx,
                )
                prompt = enhancement["enhanced_prompt"]
                hero_change_summary = enhancement.get("interpretation", "AI-enhanced based on feedback")
                logger.info(f"AI Designer enhanced hero pair prompt: {hero_change_summary[:100]}")
            except Exception as e:
                logger.error(f"AI enhancement failed for hero pair rewrite: {e}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI Designer could not rewrite hero feedback into a valid prompt. Please retry.",
                )

        hero_header = APLUS_HERO_HEADER.format(
            reference_images_desc=_build_aplus_reference_images_desc(
                has_product_ref=has_product_ref,
                has_style_ref=has_style_ref,
                has_logo=has_logo_ref,
            )
        )
        prompt = _ensure_reference_images_header(prompt, hero_header)

        # Final guardrail: strip known A+ boilerplate before sending to Gemini
        prompt = strip_aplus_banner_boilerplate(prompt)
        if _has_legacy_aplus_boilerplate(prompt):
            prompt = strip_aplus_banner_boilerplate(prompt)
        if _has_legacy_aplus_boilerplate(prompt):
            raise HTTPException(
                status_code=500,
                detail="Legacy A+ boilerplate leak detected before Gemini call. Please retry after backend restart.",
            )

        # Append lighting override (prevents amateur lighting bleed from reference photos)
        prompt = append_lighting_override_once(prompt)

        # Assemble reference images and execute via unified pipeline
        ref_images = assemble_reference_images(
            session, "aplus_hero",
            module_index=0,
        )
        ctx = GenerationContext.for_aplus_hero(
            session=session,
            prompt=prompt,
            reference_images=ref_images,
        )

        # Store feedback metadata for prompt history
        if request.custom_instructions:
            ctx.user_feedback = request.custom_instructions
            ctx.change_summary = hero_change_summary

        # Apply model override if specified
        if request.image_model:
            ctx.model_override = request.image_model

        logger.info(f"Generating hero pair with {len(ref_images.named_images)} named images, prompt={len(prompt)} chars")

        result = await service.execute(ctx)

        generation_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Hero pair generated in {generation_time_ms}ms")

        top_path, top_url, _ = result.saved.get("aplus_full_image_0", ("", "", 1))
        bottom_path, bottom_url, _ = result.saved.get("aplus_full_image_1", ("", "", 1))

        # === DEDUCT CREDITS ===
        if top_path and bottom_path:
            model = request.image_model or "gemini-3-pro-image-preview"
            cost = credits.get_credit_cost("aplus_module", model, 1)
            credits.deduct_credits(user.id, cost, "aplus_hero", email=user.email)

        return HeroPairResponse(
            session_id=request.session_id,
            module_0=HeroPairModuleResult(
                image_path=top_path,
                image_url=top_url,
                prompt_text=prompt,
            ),
            module_1=HeroPairModuleResult(
                image_path=bottom_path,
                image_url=bottom_url,
                prompt_text=prompt,
            ),
            generation_time_ms=generation_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hero pair generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hero pair generation failed: {str(e)}")


@router.post("/aplus/generate", response_model=AplusModuleResponse)
async def generate_aplus_module(
    request: AplusModuleRequest,
    service: GenerationService = Depends(get_generation_service),
    vision: VisionService = Depends(get_vision_service),
    user: User = Depends(get_current_user),
    gemini: GeminiService = Depends(get_gemini_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
    db: Session = Depends(get_db),
    credits: CreditsService = Depends(get_credits_service),
):
    """
    Generate a single A+ Content module image.

    Each module is generated independently with product photo + style reference.
    Logo is included only for bookend modules (hero pair and last module).
    """
    start_time = time.time()

    # === CREDIT CHECK ===
    model = request.image_model or "gemini-3-pro-image-preview"
    cost = credits.get_credit_cost("aplus_module", model, 1)
    has_credits, balance, msg = credits.check_credits(user.id, cost, user.email)
    if not has_credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Need {cost}, have {balance}. Please upgrade your plan."
        )

    try:
        session = _get_owned_session(service, request.session_id, user)

        design_context = db.query(DesignContext).filter(
            DesignContext.session_id == request.session_id
        ).first()

        features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]
        effective_brand_name = _resolve_effective_brand_name(
            session, db, user.id
        )
        framework = session.design_framework_json or {}
        visual_script = session.aplus_visual_script
        has_product_ref = bool(session.upload_path)
        has_style_ref = bool(session.style_reference_path)
        has_logo_ref = bool(session.logo_path)
        module_count = len(visual_script.get("modules", [])) if visual_script else 6

        # === Build prompt ===
        prompt = None
        use_named_images = False

        # Build prompt from visual script scene description (clean header + scene)
        if visual_script:
            prompt = build_aplus_module_prompt(
                product_title=session.product_title,
                brand_name=effective_brand_name,
                features=features,
                target_audience=session.target_audience or "",
                framework=framework,
                visual_script=visual_script,
                module_index=request.module_index,
                module_count=len(visual_script.get("modules", [])),
                custom_instructions="",  # handled by AI enhancement below
                has_style_ref=has_style_ref,
                has_logo=has_logo_ref,
                has_product_ref=has_product_ref,
            )
            if prompt:
                use_named_images = True
                logger.info(f"Using visual script prompt for module {request.module_index}, {len(prompt)} chars")

        # Tier 3: No visual script fallback
        if not prompt:
            if request.module_index == 0:
                position = "first"
            elif request.module_index > 0:
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

            prompt = get_aplus_prompt(
                module_type=request.module_type.value,
                position=position,
                product_title=session.product_title,
                brand_name=effective_brand_name,
                features=features,
                target_audience=session.target_audience or "",
                framework_name=framework_name,
                framework_style=framework_style,
                primary_color=primary_color,
                color_palette=color_palette,
                framework_mood=framework_mood,
                custom_instructions="",  # handled by AI enhancement below
            )

        # === Canvas extension DISABLED ===
        # Was causing all modules to look like variations of the same image
        # Each module is now generated independently for more variety
        use_canvas_extension = False
        canvas_image = None
        debug_canvas_path = None

        # === AI-enhanced prompt rewriting when user provides feedback ===
        ai_change_summary = None
        if request.custom_instructions:
            image_type_key = f"aplus_{request.module_index}"
            structural_ctx = get_structural_context(image_type_key, has_canvas=use_canvas_extension)
            fw_dict, analysis_text = get_enhancement_context(session, design_context)
            try:
                enhancement = await vision.enhance_prompt_with_feedback(
                    original_prompt=prompt,
                    user_feedback=request.custom_instructions,
                    image_type=image_type_key,
                    framework=fw_dict,
                    product_analysis=analysis_text,
                    structural_context=structural_ctx,
                )
                prompt = enhancement["enhanced_prompt"]
                ai_change_summary = enhancement.get("interpretation", "AI-enhanced based on feedback")
                logger.info(f"AI Designer enhanced module {request.module_index} prompt: {ai_change_summary[:100]}")
            except Exception as e:
                logger.error(f"AI enhancement failed for module {request.module_index} rewrite: {e}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI Designer could not rewrite module feedback into a valid prompt. Please retry.",
                )

        is_middle_module = 2 <= request.module_index < module_count - 1
        module_header = APLUS_MODULE_HEADER.format(
            reference_images_desc=_build_aplus_reference_images_desc(
                has_product_ref=has_product_ref,
                has_style_ref=has_style_ref,
                has_logo=(has_logo_ref and not is_middle_module),
            )
        )
        prompt = _ensure_reference_images_header(prompt, module_header)

        # Final guardrail: strip known A+ boilerplate before sending to Gemini
        prompt = strip_aplus_banner_boilerplate(prompt)
        if _has_legacy_aplus_boilerplate(prompt):
            prompt = strip_aplus_banner_boilerplate(prompt)
        if _has_legacy_aplus_boilerplate(prompt):
            raise HTTPException(
                status_code=500,
                detail="Legacy A+ boilerplate leak detected before Gemini call. Please retry after backend restart.",
            )

        # Append lighting override (prevents amateur lighting bleed from reference photos)
        prompt = append_lighting_override_once(prompt)

        # === Build GenerationContext and execute ===
        logger.info(f"Generating A+ {request.module_type.value} module (index={request.module_index}, canvas_ext={use_canvas_extension})")

        if use_canvas_extension:
            ref_images = assemble_reference_images(
                session, f"aplus_{request.module_index}",
                canvas_image=canvas_image, canvas_debug_path=debug_canvas_path,
                module_index=request.module_index, module_count=module_count,
            )
            ctx = GenerationContext.for_canvas_extension(
                session=session,
                module_index=request.module_index,
                prompt=prompt,
                reference_images=ref_images,
                canvas_image=canvas_image,
            )
        else:
            ref_images = assemble_reference_images(
                session, f"aplus_{request.module_index}",
                use_named=use_named_images,
                module_index=request.module_index, module_count=module_count,
            )
            ctx = GenerationContext.for_aplus_module(
                session=session,
                module_index=request.module_index,
                prompt=prompt,
                reference_images=ref_images,
                module_type=request.module_type.value,
            )

        # Store feedback metadata for prompt history
        if request.custom_instructions:
            ctx.user_feedback = request.custom_instructions
            ctx.change_summary = ai_change_summary

        # Apply model override if specified
        if request.image_model:
            ctx.model_override = request.image_model

        result = await service.execute(ctx)

        generation_time_ms = int((time.time() - start_time) * 1000)
        target_width, target_height = APLUS_DIMENSIONS[request.module_type.value]

        # Build refined_previous info from result if canvas extension was used
        refined_previous_info = None
        if result.refined_previous_index is not None:
            refined_previous_info = RefinedModule(
                module_index=result.refined_previous_index,
                image_path=result.refined_previous_path or "",
                image_url=result.refined_previous_url or "",
            )

        logger.info(f"A+ module generated in {generation_time_ms}ms: {result.primary_path}")

        # === DEDUCT CREDITS ===
        if result.primary_path:
            model = request.image_model or "gemini-3-pro-image-preview"
            cost = credits.get_credit_cost("aplus_module", model, 1)
            credits.deduct_credits(user.id, cost, "aplus_module", email=user.email)

        return AplusModuleResponse(
            session_id=request.session_id,
            module_type=request.module_type.value,
            module_index=request.module_index,
            image_path=result.primary_path,
            image_url=result.primary_url,
            width=target_width,
            height=target_height,
            is_chained=False,
            generation_time_ms=generation_time_ms,
            prompt_text=prompt,
            refined_previous=refined_previous_info,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"A+ module generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"A+ generation failed: {str(e)}")


# ============== A+ Art Director Visual Script ==============

@router.post("/aplus/visual-script", response_model=AplusVisualScriptResponse)
async def generate_aplus_visual_script(
    request: AplusVisualScriptRequest,
    user: User = Depends(get_current_user),
    gemini: GeminiService = Depends(get_gemini_service),
    db: Session = Depends(get_db),
):
    """
    Generate an Art Director visual script that plans the entire A+ section
    as one unified visual narrative before generating any modules.
    """

    try:
        session = db.query(GenerationSession).filter(
            GenerationSession.id == request.session_id,
            GenerationSession.user_id == user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        effective_brand_name = _resolve_effective_brand_name(
            session, db, user.id
        )

        # Build framework dict from session
        framework = session.design_framework_json or {}

        # Build prompt with listing context so A+ doesn't repeat
        features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]
        listing_prompts = framework.get("generation_prompts", [])
        prompt = get_visual_script_prompt(
            product_title=session.product_title,
            brand_name=effective_brand_name,
            features=features,
            target_audience=session.target_audience or "",
            framework=framework,
            module_count=request.module_count,
            listing_prompts=listing_prompts,
        )

        # Collect product image paths for visual context
        image_paths = []
        if session.upload_path:
            image_paths.append(session.upload_path)
        if session.additional_upload_paths:
            image_paths.extend(session.additional_upload_paths)

        # Call Gemini with images so Art Director can SEE the product
        logger.info(f"Generating visual script with {len(image_paths)} product images")
        raw_text = await gemini.generate_text_with_images(
            prompt=prompt,
            image_paths=image_paths,
            max_tokens=5000,
            temperature=0.7,
        )

        # Parse JSON from response (strip markdown fences if present)
        visual_script = _sanitize_aplus_visual_script(
            json_module.loads(strip_json_fences(raw_text))
        )

        # Store on session
        session.aplus_visual_script = visual_script
        db.commit()

        logger.info(f"Visual script generated with {len(visual_script.get('modules', []))} modules")

        return AplusVisualScriptResponse(
            session_id=request.session_id,
            visual_script=visual_script,
            module_count=request.module_count,
        )

    except HTTPException:
        raise
    except json_module.JSONDecodeError as e:
        logger.error(f"Failed to parse visual script JSON: {e}")
        raise HTTPException(status_code=500, detail="Art Director returned invalid JSON")
    except Exception as e:
        logger.error(f"Visual script generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Visual script generation failed: {str(e)}")


@router.get("/aplus/{session_id}/visual-script", response_model=AplusVisualScriptResponse)
async def get_aplus_visual_script(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the stored visual script for a session."""

    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.aplus_visual_script:
        raise HTTPException(status_code=404, detail="No visual script generated yet")

    return AplusVisualScriptResponse(
        session_id=session_id,
        visual_script=session.aplus_visual_script,
        module_count=len(session.aplus_visual_script.get("modules", [])),
    )


    # A+ prompts are stored in the same PromptHistory system as listing images.
    # Use GET /generate/{session_id}/prompts/aplus_0 through aplus_4 to retrieve them.


# ============== Re-plan All Prompts (Listing + A+) ==============

@router.post("/replan", response_model=ReplanResponse)
async def replan_all_prompts(
    request: ReplanRequest,
    vision: VisionService = Depends(get_unified_vision_service),
    gemini: GeminiService = Depends(get_gemini_service),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Regenerate all prompts (listing images + A+ visual script) without regenerating
    the framework itself. This keeps the same style/colors but creates fresh prompts
    for variation.

    Use this when you want different creative direction while maintaining visual consistency.
    """
    try:
        session = db.query(GenerationSession).filter(
            GenerationSession.id == request.session_id,
            GenerationSession.user_id == user.id,
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get stored framework
        framework = session.design_framework_json
        if not framework:
            raise HTTPException(status_code=400, detail="No design framework found. Generate frameworks first.")

        features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]
        effective_brand_name = _resolve_effective_brand_name(
            session, db, user.id
        )

        # === STEP 1: Regenerate listing prompts ===
        logger.info(f"Re-planning listing prompts for session {request.session_id}")

        listing_prompts = await vision.generate_image_prompts(
            framework=framework,
            product_name=session.product_title,
            product_description=session.product_title,
            features=features,
            target_audience=session.target_audience or "",
            global_note=session.global_note,
            has_style_reference=bool(session.style_reference_path),
            brand_name=effective_brand_name,
        )

        logger.info(f"Generated {len(listing_prompts)} listing prompts")

        # Update framework with new prompts
        # IMPORTANT: Create a new dict to ensure SQLAlchemy detects the change
        updated_framework = dict(framework)
        updated_framework['generation_prompts'] = listing_prompts
        session.design_framework_json = updated_framework
        flag_modified(session, 'design_framework_json')
        db.commit()

        # Use updated framework for the rest of this request
        framework = updated_framework

        # === STEP 2: Regenerate A+ visual script ===
        logger.info(f"Re-planning A+ visual script for session {request.session_id}")

        visual_script_prompt = get_visual_script_prompt(
            product_title=session.product_title,
            brand_name=effective_brand_name,
            features=features,
            target_audience=session.target_audience or "",
            framework=framework,
            module_count=request.module_count,
            listing_prompts=listing_prompts,  # Pass so A+ knows what NOT to repeat
        )

        # Collect product image paths for visual context
        image_paths = []
        if session.upload_path:
            image_paths.append(session.upload_path)
        if session.additional_upload_paths:
            image_paths.extend(session.additional_upload_paths)

        # Call Gemini with images so Art Director can SEE the product
        raw_text = await gemini.generate_text_with_images(
            prompt=visual_script_prompt,
            image_paths=image_paths,
            max_tokens=5000,
            temperature=0.7,
        )

        visual_script = _sanitize_aplus_visual_script(
            json_module.loads(strip_json_fences(raw_text))
        )

        # Store on session (flag_modified ensures SQLAlchemy detects JSON change)
        session.aplus_visual_script = visual_script
        flag_modified(session, 'aplus_visual_script')
        db.commit()

        logger.info(f"Visual script regenerated with {len(visual_script.get('modules', []))} modules")

        return ReplanResponse(
            session_id=request.session_id,
            listing_prompts=listing_prompts,
            visual_script=visual_script,
            module_count=request.module_count,
        )

    except HTTPException:
        raise
    except json_module.JSONDecodeError as e:
        logger.error(f"Failed to parse visual script JSON: {e}")
        raise HTTPException(status_code=500, detail="Art Director returned invalid JSON")
    except Exception as e:
        logger.error(f"Replan failed: {e}")
        raise HTTPException(status_code=500, detail=f"Replan failed: {str(e)}")


@router.post("/aplus/generate-mobile", response_model=AplusMobileResponse)
async def generate_aplus_mobile(
    request: AplusMobileRequest,
    service: GenerationService = Depends(get_generation_service),
    vision: VisionService = Depends(get_vision_service),
    user: User = Depends(get_current_user),
    gemini: GeminiService = Depends(get_gemini_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
    db: Session = Depends(get_db),
    credits: CreditsService = Depends(get_credits_service),
):
    """
    Generate a mobile-optimized version (600x450, 4:3) of an A+ module
    by using Gemini's edit API to intelligently recompose the desktop image.

    Special handling for hero modules:
    - module_index 0: Merges modules 0 and 1 into a single hero mobile image
    - module_index 1: Returns existing hero mobile image from module 0
    - module_index 2+: Standard individual mobile generation
    """

    # === CREDIT CHECK ===
    # Mobile transforms cost 1 credit each (skip for module 1 which just returns existing)
    if request.module_index != 1:
        cost = credits.get_credit_cost("aplus_mobile", count=1)
        has_credits, balance, msg = credits.check_credits(user.id, cost, user.email)
        if not has_credits:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Need {cost}, have {balance}. Please upgrade your plan."
            )

    try:
        session = _get_owned_session(service, request.session_id, user)

        # Special handling for module 1: return existing hero mobile
        if request.module_index == 1:
            hero_mobile_key = "aplus_full_image_hero_mobile"
            try:
                # Check if hero mobile exists
                hero_mobile_url = storage.get_generated_url(request.session_id, hero_mobile_key, expires_in=3600)
                hero_mobile_path = f"supabase://{storage.generated_bucket}/{request.session_id}/{hero_mobile_key}.png"

                logger.info(f"Returning existing hero mobile image for module 1")
                return AplusMobileResponse(
                    session_id=request.session_id,
                    module_index=request.module_index,
                    image_path=hero_mobile_path,
                    image_url=hero_mobile_url,
                )
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="Hero mobile image doesn't exist. Generate mobile for module 0 instead."
                )

        # Special handling for module 0: merge with module 1 into hero mobile
        if request.module_index == 0:
            # Load BOTH desktop hero images (modules 0 and 1)
            desktop_key_0 = "aplus_full_image_0"
            desktop_key_1 = "aplus_full_image_1"
            desktop_path_0 = f"supabase://{storage.generated_bucket}/{request.session_id}/{desktop_key_0}.png"
            desktop_path_1 = f"supabase://{storage.generated_bucket}/{request.session_id}/{desktop_key_1}.png"

            # Verify both desktop images exist
            try:
                storage.get_generated_url(request.session_id, desktop_key_0, expires_in=60)
                storage.get_generated_url(request.session_id, desktop_key_1, expires_in=60)
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="Both hero desktop images (modules 0 and 1) must exist. Generate desktop first."
                )

            # Load and stack the images vertically
            logger.info("Loading and stacking hero desktop images for mobile merge")
            img0 = _load_image_from_path(desktop_path_0)
            img1 = _load_image_from_path(desktop_path_1)

            # Create combined image (stack vertically)
            combined_width = max(img0.width, img1.width)
            combined_height = img0.height + img1.height
            combined = Image.new('RGB', (combined_width, combined_height))
            combined.paste(img0, (0, 0))
            combined.paste(img1, (0, img0.height))

            # Save combined image temporarily
            temp_key = "aplus_hero_combined_temp"
            storage.save_generated_image_versioned(
                request.session_id,
                temp_key,
                combined,
                0,  # version 0 for temp file
            )
            temp_path = f"supabase://{storage.generated_bucket}/{request.session_id}/{temp_key}.png"

            # Build hero-specific recomposition prompt
            recompose_prompt = (
                "Recompose this hero banner for mobile viewing. "
                "The original is two seamless desktop halves (top + bottom) stacked vertically. "
                "Intelligently rearrange all content to fit a single 4:3 mobile image: "
                "- Keep the product prominent and centered "
                "- Reflow text and graphics to fit the mobile format "
                "- Maintain the same visual style, colors, and brand identity "
                "- Don't crop important elements — rearrange them "
                "- Ensure text remains readable at mobile scale "
                "- Preserve the seamless brand experience from the desktop hero "
            )
            if request.custom_instructions:
                feedback_context = service.get_design_context(request.session_id)
                image_type_key = "aplus_hero"
                structural_ctx = get_structural_context(image_type_key)
                fw_dict, analysis_text = get_enhancement_context(session, feedback_context)
                try:
                    enhancement = await vision.enhance_prompt_with_feedback(
                        original_prompt=recompose_prompt,
                        user_feedback=request.custom_instructions,
                        image_type=image_type_key,
                        framework=fw_dict,
                        product_analysis=analysis_text,
                        structural_context=structural_ctx,
                    )
                    recompose_prompt = enhancement["enhanced_prompt"]
                except Exception as e:
                    logger.error(f"AI enhancement failed for hero mobile rewrite: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="AI Designer could not rewrite mobile hero feedback into a valid prompt. Please retry.",
                    )

            logger.info("Generating hero mobile from combined desktop images via edit API")

            # Use Gemini edit to recompose the combined image
            mobile_image = await gemini.edit_image(
                source_image_path=temp_path,
                edit_instructions=recompose_prompt,
                aspect_ratio="4:3",
                max_retries=3,
            )

            if not mobile_image:
                raise HTTPException(status_code=500, detail="Hero mobile image generation failed")

            # Resize to exact 600x450
            mobile_image = resize_for_aplus_module(mobile_image, "full_image", mobile=True)

            # Save as hero mobile (not module 0 mobile)
            mobile_key = "aplus_full_image_hero_mobile"

            # Get version number for hero mobile track
            mobile_version = get_next_version(storage, request.session_id, mobile_key)

            # Save with versioned copy
            image_path = storage.save_generated_image_versioned(
                request.session_id,
                mobile_key,
                mobile_image,
                mobile_version,
            )

            # Get URL
            try:
                image_url = storage.get_generated_url(request.session_id, mobile_key, expires_in=3600)
            except Exception:
                image_url = f"/api/images/file?path={image_path}"

            # Store prompt history
            try:
                design_ctx = service.get_design_context(request.session_id)
                if design_ctx:
                    service.store_prompt_in_history(
                        context=design_ctx,
                        image_type=DBImageTypeEnum("aplus_0"),
                        prompt_text=f"[HERO MOBILE MERGE] {recompose_prompt}",
                        change_summary="Hero mobile recomposition from combined desktop images (modules 0+1)",
                    )
            except Exception as e:
                logger.warning(f"Failed to store hero mobile prompt history: {e}")

            logger.info(f"Hero mobile image generated: {image_path}")

            # === DEDUCT CREDITS ===
            cost = credits.get_credit_cost("aplus_mobile", count=1)
            credits.deduct_credits(user.id, cost, "aplus_mobile", email=user.email)

            return AplusMobileResponse(
                session_id=request.session_id,
                module_index=request.module_index,
                image_path=image_path,
                image_url=image_url,
            )

        # Standard processing for modules 2+
        desktop_key = f"aplus_full_image_{request.module_index}"
        desktop_path = f"supabase://{storage.generated_bucket}/{request.session_id}/{desktop_key}.png"

        # Verify desktop image exists
        try:
            storage.get_generated_url(request.session_id, desktop_key, expires_in=60)
        except Exception:
            raise HTTPException(status_code=400, detail=f"No desktop image for module {request.module_index}. Generate desktop first.")

        # Build recomposition prompt
        recompose_prompt = (
            "Recompose this wide desktop banner image for mobile viewing. "
            "The original is a wide banner (21:9 ratio). "
            "Intelligently rearrange the content to fit a 4:3 mobile ratio: "
            "- Keep the product prominent and centered "
            "- Reflow text and graphics to fit the taller format "
            "- Maintain the same visual style, colors, and brand identity "
            "- Don't crop important elements — rearrange them "
            "- Ensure text remains readable at mobile scale "
        )
        if request.custom_instructions:
            feedback_context = service.get_design_context(request.session_id)
            image_type_key = f"aplus_{request.module_index}"
            structural_ctx = get_structural_context(image_type_key)
            fw_dict, analysis_text = get_enhancement_context(session, feedback_context)
            try:
                enhancement = await vision.enhance_prompt_with_feedback(
                    original_prompt=recompose_prompt,
                    user_feedback=request.custom_instructions,
                    image_type=image_type_key,
                    framework=fw_dict,
                    product_analysis=analysis_text,
                    structural_context=structural_ctx,
                )
                recompose_prompt = enhancement["enhanced_prompt"]
            except Exception as e:
                logger.error(f"AI enhancement failed for mobile module {request.module_index} rewrite: {e}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI Designer could not rewrite mobile feedback into a valid prompt. Please retry.",
                )

        logger.info(f"Generating mobile A+ module {request.module_index} via edit API")

        # Use unified pipeline

        ctx = GenerationContext.for_mobile_transform(
            session=session,
            module_index=request.module_index,
            prompt=recompose_prompt,
            source_image_path=desktop_path,
        )
        ctx.storage_key = f"aplus_full_image_{request.module_index}_mobile"
        ctx.change_summary = "Mobile recomposition from desktop image"

        result = await service.execute(ctx)

        logger.info(f"Mobile A+ module {request.module_index} generated: {result.primary_path}")

        # === DEDUCT CREDITS ===
        if result.primary_path:
            cost = credits.get_credit_cost("aplus_mobile", count=1)
            credits.deduct_credits(user.id, cost, "aplus_mobile", email=user.email)

        return AplusMobileResponse(
            session_id=request.session_id,
            module_index=request.module_index,
            image_path=result.primary_path,
            image_url=result.primary_url,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mobile A+ generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Mobile generation failed: {str(e)}")


@router.post("/aplus/generate-all-mobile")
async def generate_all_aplus_mobile(
    request: AplusAllMobileRequest,
    user: User = Depends(get_current_user),
    gemini: GeminiService = Depends(get_gemini_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
    db: Session = Depends(get_db),
    service: GenerationService = Depends(get_generation_service),
    credits: CreditsService = Depends(get_credits_service),
):
    """
    Generate mobile versions for all A+ modules that have desktop images.
    Returns array of results.
    """

    session = db.query(GenerationSession).filter(
        GenerationSession.id == request.session_id,
        GenerationSession.user_id == user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Count how many modules need mobile transforms (excluding module 1)
    modules_to_generate = []
    for i in range(7):
        if i == 1:  # Skip module 1 (uses hero mobile)
            continue
        desktop_key = f"aplus_full_image_{i}"
        try:
            storage.get_generated_url(request.session_id, desktop_key, expires_in=60)
            modules_to_generate.append(i)
        except Exception:
            continue

    # === CREDIT CHECK ===
    if modules_to_generate:
        cost = credits.get_credit_cost("aplus_mobile", count=len(modules_to_generate))
        has_credits, balance, msg = credits.check_credits(user.id, cost, user.email)
        if not has_credits:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Need {cost} for {len(modules_to_generate)} mobile transforms, have {balance}. Please upgrade your plan."
            )

    # Find all modules with desktop images
    results = []
    for i in range(7):  # up to 7 modules
        desktop_key = f"aplus_full_image_{i}"
        try:
            storage.get_generated_url(request.session_id, desktop_key, expires_in=60)
        except Exception:
            continue  # No desktop image for this module

        try:
            # Generate mobile for this module
            mobile_req = AplusMobileRequest(
                session_id=request.session_id,
                module_index=i,
            )
            result = await generate_aplus_mobile(
                request=mobile_req,
                service=service,
                user=user,
                gemini=gemini,
                storage=storage,
                db=db,
                credits=credits,
            )
            results.append({
                "module_index": i,
                "image_path": result.image_path,
                "image_url": result.image_url,
                "status": "complete",
            })
        except Exception as e:
            logger.error(f"Mobile generation failed for module {i}: {e}")
            results.append({
                "module_index": i,
                "image_path": "",
                "image_url": "",
                "status": "failed",
            })

    return results


# ============================================================================
# ALT TEXT GENERATION
# ============================================================================

@router.post("/alt-text", response_model=AltTextResponse)
async def generate_alt_text(
    request: AltTextRequest,
    service: GenerationService = Depends(get_generation_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
    user: User = Depends(get_current_user),
):
    """
    Generate SEO-optimized alt text for a listing image.

    Uses Gemini Vision to analyze the image and generate descriptive,
    keyword-rich alt text suitable for Amazon listings (max 125 characters).
    """
    from app.services.gemini_vision_service import get_gemini_vision_service

    session = _get_owned_session(service, request.session_id, user)

    # Get the image storage path
    storage_key = request.image_type
    if request.image_type.startswith("aplus_"):
        # A+ modules have different naming: aplus_0 -> aplus_full_image_0
        module_idx = request.image_type.replace("aplus_", "")
        storage_key = f"aplus_full_image_{module_idx}"

    try:
        # Verify image exists
        storage.get_generated_url(request.session_id, storage_key, expires_in=60)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"Image not found: {request.image_type}"
        )

    image_path = f"supabase://{storage.generated_bucket}/{request.session_id}/{storage_key}.png"

    # Get product info from session
    product_name = session.product_name or "Product"
    features = []
    if session.design_framework_json:
        framework = session.design_framework_json
        if isinstance(framework, dict):
            features = framework.get("key_features", [])

    # Generate alt text
    vision_service = get_gemini_vision_service()
    try:
        alt_text = await vision_service.generate_alt_text(
            image_path=image_path,
            product_name=product_name,
            image_type=request.image_type,
            features=features,
        )
    except Exception as e:
        logger.error(f"Alt text generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Alt text generation failed: {str(e)}"
        )

    return AltTextResponse(
        image_type=request.image_type,
        alt_text=alt_text,
        character_count=len(alt_text),
    )


@router.post("/alt-text/batch")
async def generate_alt_text_batch(
    session_id: str,
    service: GenerationService = Depends(get_generation_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
    user: User = Depends(get_current_user),
):
    """
    Generate alt text for all listing images in a session.

    Returns a dictionary of image_type -> alt_text for all complete images.
    """
    from app.services.gemini_vision_service import get_gemini_vision_service

    session = _get_owned_session(service, session_id, user)

    # Get product info
    product_name = session.product_name or "Product"
    features = []
    if session.design_framework_json:
        framework = session.design_framework_json
        if isinstance(framework, dict):
            features = framework.get("key_features", [])

    vision_service = get_gemini_vision_service()
    results = {}

    # Standard listing image types
    listing_types = ["main", "infographic_1", "infographic_2", "lifestyle", "transformation"]

    for image_type in listing_types:
        try:
            storage.get_generated_url(session_id, image_type, expires_in=60)
            image_path = f"supabase://{storage.generated_bucket}/{session_id}/{image_type}.png"

            alt_text = await vision_service.generate_alt_text(
                image_path=image_path,
                product_name=product_name,
                image_type=image_type,
                features=features,
            )
            results[image_type] = {
                "alt_text": alt_text,
                "character_count": len(alt_text),
            }
        except Exception as e:
            logger.debug(f"No image or alt text generation failed for {image_type}: {e}")
            continue

    return {"session_id": session_id, "alt_texts": results}


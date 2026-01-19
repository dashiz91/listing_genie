"""
Image Generation API Endpoints

MASTER Level: Now includes Principal Designer AI for dynamic framework generation.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

from app.db.session import get_db
from app.services.gemini_service import GeminiService, get_gemini_service
from app.services.storage_service import StorageService
from app.services.generation_service import GenerationService
from app.services.vision_service import VisionService, get_vision_service as get_unified_vision_service
from app.dependencies import get_storage_service
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
)
from app.prompts import get_all_styles, generate_random_framework, get_all_presets, DesignFramework
from app.models.database import ImageTypeEnum as DBImageType, ColorModeEnum
from enum import Enum


# ============== MASTER Level: Color Mode ==============

class ColorMode(str, Enum):
    """How colors should be determined by AI Designer"""
    AI_DECIDES = "ai_decides"           # AI picks all colors based on product
    SUGGEST_PRIMARY = "suggest_primary"  # User suggests primary, AI builds palette
    LOCKED_PALETTE = "locked_palette"    # User locks exact colors, AI must use them


# ============== MASTER Level: Framework Generation Schemas ==============

class FrameworkGenerationRequest(BaseModel):
    """Request to generate design frameworks using Principal Designer AI"""
    product_title: str = Field(..., min_length=1, max_length=200)
    brand_name: Optional[str] = Field(None, max_length=100)
    features: List[str] = Field(default_factory=list, max_length=3)
    target_audience: Optional[str] = Field(None, max_length=200)
    primary_color: Optional[str] = Field(
        None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Optional preferred primary color (hex)"
    )


class FrameworkGenerationResponse(BaseModel):
    """Response with 4 AI-generated design frameworks with preview images"""
    session_id: str  # Session for storing previews
    product_analysis: str  # Summary text for display
    product_analysis_raw: Optional[dict] = None  # Full analysis dict for regeneration context
    frameworks: list  # List of complete framework dicts with preview_url
    generation_notes: str


class PromptHistoryResponse(BaseModel):
    """Response with prompt history for an image"""
    image_type: str
    version: int
    prompt_text: str
    user_feedback: Optional[str] = None
    change_summary: Optional[str] = None
    created_at: str
    # Reference images used for this generation
    reference_images: List[dict] = []  # [{type: "primary", path: "..."}, ...]
    # Full context injected into AI Designer (for transparency)
    designer_context: Optional[dict] = None  # Framework, colors, typography, global_note, etc.

router = APIRouter()


def get_generation_service(
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini_service),
    storage: StorageService = Depends(get_storage_service),
) -> GenerationService:
    """Dependency injection for GenerationService"""
    return GenerationService(db=db, gemini=gemini, storage=storage)


def get_vision_service() -> VisionService:
    """
    Dependency injection for Vision Service (Principal Designer AI).

    Uses Gemini by default (10x cheaper than GPT-4o).
    Set VISION_PROVIDER=openai in .env to use OpenAI instead.
    """
    return get_unified_vision_service()


@router.post("/", response_model=GenerationResponse)
async def start_generation(
    request: GenerationRequest,
    service: GenerationService = Depends(get_generation_service),
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
        session = service.create_session(request)

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
):
    """
    Start an async image generation session.

    Creates a session and queues image generation in the background.
    Returns immediately with session ID to poll for status.
    """
    try:
        # Create session
        session = service.create_session(request)

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
):
    """
    Get status of a generation session.

    Returns current status and results for all images.
    """
    session = service.get_session_status(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

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
):
    """
    Generate or regenerate a single image type for an existing session.

    Useful for retrying failed generations or regenerating specific images.
    Accepts an optional note/instructions to customize the regeneration.
    """
    session = service.get_session_status(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Convert schema enum to DB enum
        db_image_type = DBImageType(request.image_type.value)

        # Pass the optional note to generate_single_image
        result = await service.generate_single_image(session, db_image_type, note=request.note)

        return SingleImageResponse(
            session_id=session.id,
            image_type=request.image_type,
            status=result.status,
            storage_path=result.storage_path,
            error_message=result.error_message,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# ============== Edit Image Endpoint ==============

class EditImageRequest(BaseModel):
    """Request to edit an existing generated image"""
    session_id: str
    image_type: ImageTypeEnum
    edit_instructions: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Specific edit instructions (e.g., 'Change the headline to New Text')"
    )


@router.post("/edit", response_model=SingleImageResponse)
async def edit_single_image(
    request: EditImageRequest,
    service: GenerationService = Depends(get_generation_service),
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
    """
    session = service.get_session_status(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Convert schema enum to DB enum
        db_image_type = DBImageType(request.image_type.value)

        # Call the edit method
        result = await service.edit_single_image(
            session,
            db_image_type,
            edit_instructions=request.edit_instructions
        )

        return SingleImageResponse(
            session_id=session.id,
            image_type=request.image_type,
            status=result.status,
            storage_path=result.storage_path,
            error_message=result.error_message,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Edit failed: {str(e)}")


@router.post("/main", response_model=SingleImageResponse)
async def generate_main_image(
    session_id: str,
    service: GenerationService = Depends(get_generation_service),
):
    """
    Generate just the main product image.

    Convenience endpoint for generating only the main image.
    """
    session = service.get_session_status(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

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
):
    """
    Retry generation of all failed images in a session.

    Only retries images with status='failed'. Returns updated results.
    """
    session = service.get_session_status(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

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
):
    """
    Get generation statistics for a session.

    Returns retry counts and status breakdown.
    """
    session = service.get_session_status(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return service.get_generation_stats(session)


# ============== Prompt History Endpoints ==============

@router.get("/{session_id}/prompts", response_model=List[PromptHistoryResponse])
async def get_session_prompts(
    session_id: str,
    service: GenerationService = Depends(get_generation_service),
):
    """
    Get all prompts used for image generation in this session.

    Returns prompt history for each image type, including:
    - The actual prompt sent to Gemini
    - Version number (for regenerations)
    - User feedback that triggered regeneration (if any)
    - AI's interpretation of changes made
    """
    session = service.get_session_status(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    context = service.get_design_context(session.id)
    if not context:
        return []  # No prompts stored yet

    # Get all prompt history entries for all image types
    results = []
    for image_type in service.IMAGE_TYPES:
        history = service.get_prompt_history(context, image_type)
        for h in history:
            results.append(PromptHistoryResponse(
                image_type=h.image_type.value,
                version=h.version,
                prompt_text=h.prompt_text,
                user_feedback=h.user_feedback,
                change_summary=h.change_summary,
                created_at=h.created_at.isoformat() if h.created_at else "",
            ))

    return results


@router.get("/{session_id}/prompts/{image_type}", response_model=PromptHistoryResponse)
async def get_image_prompt(
    session_id: str,
    image_type: str,
    service: GenerationService = Depends(get_generation_service),
):
    """
    Get the latest prompt for a specific image type.

    Returns the most recent prompt used to generate this image,
    including any user feedback and AI's interpretation of changes.
    """
    session = service.get_session_status(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    context = service.get_design_context(session.id)
    if not context:
        raise HTTPException(status_code=404, detail="No design context found - image may not have been generated yet")

    try:
        db_image_type = DBImageType(image_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid image type: {image_type}")

    latest = service.get_latest_prompt(context, db_image_type)
    if not latest:
        raise HTTPException(status_code=404, detail=f"No prompt found for image type: {image_type}")

    # Build reference images list from session data
    reference_images = []
    if session.upload_path:
        reference_images.append({"type": "primary", "path": session.upload_path})
    if session.additional_upload_paths:
        for i, path in enumerate(session.additional_upload_paths):
            reference_images.append({"type": f"additional_{i+1}", "path": path})
    if session.style_reference_path:
        reference_images.append({"type": "style_reference", "path": session.style_reference_path})
    # Logo only for non-main images
    if session.logo_path and image_type != "main":
        reference_images.append({"type": "logo", "path": session.logo_path})

    # Build designer context - everything that was fed to the AI Designer
    designer_context = {
        "product_info": {
            "title": session.product_title,
            "brand_name": session.brand_name,
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

    return PromptHistoryResponse(
        image_type=latest.image_type.value,
        version=latest.version,
        prompt_text=latest.prompt_text,
        user_feedback=latest.user_feedback,
        change_summary=latest.change_summary,
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
):
    """
    Generate preview images for multiple styles.

    Creates a main product image in each requested style so user
    can compare and select their preferred aesthetic.
    """
    try:
        # Create preview session
        session = service.create_preview_session(request)

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
):
    """
    Select a style for the session.

    After user reviews style previews, they select one style
    that will be applied to all 5 listing images.
    """
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
        session = service.create_session(request)
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

class FrameworkGenerationWithImageRequest(BaseModel):
    """Request with upload path for framework generation"""
    product_title: str = Field(..., min_length=1, max_length=200)
    upload_path: str = Field(..., description="Path to uploaded primary product image")
    additional_upload_paths: List[str] = Field(
        default_factory=list,
        max_length=4,
        description="Additional product images (up to 4) for better AI context"
    )
    brand_name: Optional[str] = Field(None, max_length=100)
    features: List[str] = Field(default_factory=list, max_length=3)
    target_audience: Optional[str] = Field(None, max_length=200)
    primary_color: Optional[str] = Field(
        None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Optional preferred primary color (hex)"
    )
    # Style reference image - AI will extract colors/style from this
    style_reference_path: Optional[str] = Field(
        None,
        description="Path to style reference image - AI extracts colors and style from this"
    )
    # Color Mode - controls how AI Designer handles colors
    color_mode: ColorMode = Field(
        default=ColorMode.AI_DECIDES,
        description="How colors should be determined: AI_DECIDES (default), SUGGEST_PRIMARY, or LOCKED_PALETTE"
    )
    locked_colors: List[str] = Field(
        default_factory=list,
        max_length=6,
        description="Hex colors to lock when color_mode is LOCKED_PALETTE (e.g., ['#FF5733', '#2E86AB'])"
    )


@router.post("/frameworks/analyze", response_model=FrameworkGenerationResponse)
async def analyze_and_generate_frameworks(
    request: FrameworkGenerationWithImageRequest,
    vision: VisionService = Depends(get_vision_service),
    service: GenerationService = Depends(get_generation_service),
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
        logger.info(f"[API ENDPOINT] Request color_mode: {request.color_mode}")
        logger.info(f"[API ENDPOINT] Request color_mode.value: {request.color_mode.value}")
        logger.info(f"[API ENDPOINT] Request locked_colors: {request.locked_colors}")
        logger.info(f"[API ENDPOINT] Request primary_color: {request.primary_color}")
        logger.info(f"[API ENDPOINT] Request style_reference_path: {request.style_reference_path}")
        logger.info("=" * 60)

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

        # Step 2: Create a session for storing preview images
        from app.schemas.generation import StylePreviewRequest
        preview_request = StylePreviewRequest(
            product_title=request.product_title,
            feature_1=request.features[0] if request.features else None,
            upload_path=request.upload_path,
            style_ids=[f"framework_{i+1}" for i in range(len(frameworks))],
        )
        session = service.create_preview_session(preview_request)

        # Step 3: Generate preview images for all frameworks IN PARALLEL
        import asyncio
        from app.services.gemini_service import get_gemini_service
        from app.dependencies import get_storage_service

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
                    framework['preview_url'] = f"/api/images/{session.id}/framework_preview_{i+1}"
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


class GenerateWithFrameworkRequest(BaseModel):
    """Request to generate all 5 images with a selected framework"""
    product_title: str = Field(..., min_length=1, max_length=200)
    upload_path: str = Field(..., description="Path to primary product image")
    additional_upload_paths: List[str] = Field(
        default_factory=list,
        max_length=4,
        description="Additional product images for better AI context"
    )
    framework: dict = Field(..., description="The selected design framework")
    brand_name: Optional[str] = Field(None, max_length=100)
    features: List[str] = Field(default_factory=list, max_length=3)
    target_audience: Optional[str] = Field(None, max_length=200)
    logo_path: Optional[str] = Field(None, description="Path to logo image")
    style_reference_path: Optional[str] = Field(None, description="Path to style reference (preview image)")
    global_note: Optional[str] = Field(None, max_length=2000, description="Global instructions for all images")
    # AI's analysis from framework generation - used for context during regeneration
    product_analysis: Optional[dict] = Field(None, description="AI's product analysis from framework generation")


@router.post("/frameworks/generate", response_model=GenerationResponse)
async def generate_with_framework(
    request: GenerateWithFrameworkRequest,
    vision: VisionService = Depends(get_vision_service),
    service: GenerationService = Depends(get_generation_service),
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
        )

        logger.info(f"Generated {len(generation_prompts)} prompts")

        # Add prompts to the framework
        framework['generation_prompts'] = generation_prompts

        # STEP 2: Create the generation request with the framework (including prompts)
        from app.schemas.generation import DesignFramework, ImageGenerationPrompt

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

        # STEP 3: Generate all 5 images
        logger.info("Starting generation of all 5 images...")
        session = service.create_session(gen_request)

        # Create DesignContext with product_analysis for regeneration support
        if request.product_analysis:
            logger.info("Creating DesignContext with product_analysis for regeneration support")
            service.create_design_context(
                session=session,
                product_analysis=request.product_analysis,
            )

        results = await service.generate_all_images(session)

        return GenerationResponse(
            session_id=session.id,
            status=GenerationStatusEnum(session.status.value),
            images=results,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Generation with framework failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

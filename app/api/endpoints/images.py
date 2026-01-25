"""
Image Serving Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, RedirectResponse, Response
from app.services.supabase_storage_service import SupabaseStorageService
from app.services.generation_service import GenerationService
from app.services.gemini_service import GeminiService, get_gemini_service
from app.dependencies import get_storage_service
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()


def get_generation_service(
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
) -> GenerationService:
    """Dependency injection for GenerationService"""
    return GenerationService(db=db, gemini=gemini, storage=storage)


@router.get("/{session_id}")
async def get_session_images(
    session_id: str,
    service: GenerationService = Depends(get_generation_service),
):
    """
    Get all images for a generation session.

    Returns URLs and status for each image type.
    """
    session = service.get_session_status(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    images = []
    for img in session.images:
        image_data = {
            "type": img.image_type.value,
            "status": img.status.value,
            "label": _get_image_label(img.image_type.value),
        }

        if img.storage_path:
            # Serve via API endpoint
            image_data["url"] = f"/api/images/{session_id}/{img.image_type.value}"

        if img.error_message:
            image_data["error"] = img.error_message

        images.append(image_data)

    return {
        "session_id": session_id,
        "status": session.status.value,
        "images": images,
    }


@router.get("/{session_id}/{image_type}")
async def get_image_file(
    session_id: str,
    image_type: str,
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    Serve a generated image file.
    Redirects to a signed Supabase URL.
    """
    try:
        signed_url = storage.get_generated_url(session_id, image_type, expires_in=3600)
        return RedirectResponse(url=signed_url, status_code=302)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image not found")


@router.get("/upload/{upload_id}")
async def get_upload_file(
    upload_id: str,
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    Serve an uploaded image file.
    Redirects to a signed Supabase URL.
    """
    try:
        signed_url = storage.get_upload_url(upload_id, expires_in=3600)
        return RedirectResponse(url=signed_url, status_code=302)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Upload not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/file")
async def get_file_by_path(
    path: str,
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    Serve a file by its storage path (for reference image previews).
    Handles Supabase paths (supabase://bucket/path format).
    """
    try:
        if path.startswith("supabase://"):
            # Parse supabase:// URL and create signed URL
            parts = path[len("supabase://"):].split("/", 1)
            bucket = parts[0]
            file_path = parts[1] if len(parts) > 1 else ""

            # Create signed URL
            response = storage.client.storage.from_(bucket).create_signed_url(
                path=file_path,
                expires_in=3600
            )
            signed_url = response.get('signedURL', '')
            if signed_url:
                return RedirectResponse(url=signed_url, status_code=302)
            else:
                raise HTTPException(status_code=404, detail="File not found")
        else:
            # Legacy local file path - not supported anymore
            raise HTTPException(status_code=400, detail="Local file paths not supported. Use Supabase storage.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {str(e)}")


def _get_image_label(image_type: str) -> str:
    """Convert image type to display label"""
    labels = {
        "main": "Main Image",
        "infographic_1": "Infographic 1",
        "infographic_2": "Infographic 2",
        "lifestyle": "Lifestyle",
        "comparison": "Comparison",
    }
    return labels.get(image_type, image_type.title())

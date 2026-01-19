"""
Image Serving Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from app.services.storage_service import StorageService
from app.services.generation_service import GenerationService
from app.services.gemini_service import GeminiService, get_gemini_service
from app.dependencies import get_storage_service
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()


def get_generation_service(
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini_service),
    storage: StorageService = Depends(get_storage_service),
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
    storage: StorageService = Depends(get_storage_service),
):
    """
    Serve a generated image file.
    """
    try:
        file_path = storage.get_generated_path(session_id, image_type)
        return FileResponse(
            file_path,
            media_type="image/png",
            filename=f"{image_type}.png"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image not found")


@router.get("/upload/{upload_id}")
async def get_upload_file(
    upload_id: str,
    storage: StorageService = Depends(get_storage_service),
):
    """
    Serve an uploaded image file.
    """
    try:
        file_path = storage.get_upload_path(upload_id)
        return FileResponse(
            file_path,
            media_type="image/png",
            filename=f"{upload_id}.png"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Upload not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/file")
async def get_file_by_path(
    path: str,
    storage: StorageService = Depends(get_storage_service),
):
    """
    Serve a file by its storage path (for reference image previews).
    Only serves files within the storage directory for security.
    """
    import os
    from pathlib import Path

    # Security: Resolve to absolute path and verify it's within storage
    try:
        requested_path = Path(path).resolve()
        storage_root = Path(storage.base_path).resolve()

        # Check if file is within our storage directory
        if not str(requested_path).startswith(str(storage_root)):
            raise HTTPException(status_code=403, detail="Access denied")

        if not requested_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Determine media type from extension
        ext = requested_path.suffix.lower()
        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        media_type = media_types.get(ext, 'application/octet-stream')

        return FileResponse(
            str(requested_path),
            media_type=media_type,
            filename=requested_path.name
        )
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

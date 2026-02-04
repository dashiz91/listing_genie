"""
Image Serving Endpoints

Supports two modes:
1. Redirect mode (default): Returns 302 redirect to Supabase signed URL
2. Proxy mode (?proxy=true): Fetches image server-side and serves directly
   - Bypasses CORS issues when frontend domain not in Supabase CORS config
   - Slightly higher latency but works from any domain
"""
import logging
import re
from fastapi import APIRouter, HTTPException, Depends, Query

logger = logging.getLogger(__name__)
from fastapi.responses import FileResponse, RedirectResponse, Response
from app.services.supabase_storage_service import SupabaseStorageService
from app.services.generation_service import GenerationService
from app.services.gemini_service import GeminiService, get_gemini_service
from app.dependencies import get_storage_service
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()


def _get_content_type(path: str) -> str:
    """Determine content type from file extension"""
    path_lower = path.lower()
    if path_lower.endswith('.png'):
        return 'image/png'
    elif path_lower.endswith('.jpg') or path_lower.endswith('.jpeg'):
        return 'image/jpeg'
    elif path_lower.endswith('.webp'):
        return 'image/webp'
    elif path_lower.endswith('.gif'):
        return 'image/gif'
    return 'image/png'  # Default to PNG


def get_generation_service(
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
) -> GenerationService:
    """Dependency injection for GenerationService"""
    return GenerationService(db=db, gemini=gemini, storage=storage)


# --- Static routes MUST be declared before parameterized /{session_id} ---

@router.get("/file")
async def get_file_by_path(
    path: str,
    proxy: bool = Query(default=True, description="Proxy image through backend (bypasses CORS)"),
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    Serve a file by its storage path (for reference image previews).
    Handles Supabase paths (supabase://bucket/path format) and legacy local paths.

    Args:
        path: Storage path (supabase://bucket/file or legacy storage/bucket/file)
        proxy: If True (default), fetches image server-side and serves directly.
               If False, redirects to Supabase signed URL (may hit CORS issues).
    """
    try:
        # Normalise legacy local paths (storage\uploads\UUID.png or storage/uploads/UUID.png)
        # into supabase:// URIs so older sessions still resolve.
        normalised = path.replace("\\", "/")
        if not normalised.startswith("supabase://"):
            m = re.match(r"^storage/(uploads|generated)/(.+)$", normalised)
            if m:
                normalised = f"supabase://{m.group(1)}/{m.group(2)}"
            else:
                raise HTTPException(status_code=400, detail="Unrecognised storage path format.")

        # Parse supabase:// URL
        parts = normalised[len("supabase://"):].split("/", 1)
        bucket = parts[0]
        file_path = parts[1] if len(parts) > 1 else ""

        if proxy:
            # Proxy mode: fetch image server-side and serve directly (bypasses CORS)
            try:
                image_data = storage.client.storage.from_(bucket).download(file_path)
                content_type = _get_content_type(file_path)
                return Response(
                    content=image_data,
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=3600",
                        "Content-Disposition": f"inline; filename={file_path.split('/')[-1]}",
                    }
                )
            except Exception as e:
                logger.error(f"Failed to proxy image from {bucket}/{file_path}: {e}")
                raise HTTPException(status_code=404, detail="File not found")
        else:
            # Redirect mode: return signed URL (may hit CORS on some domains)
            response = storage.client.storage.from_(bucket).create_signed_url(
                path=file_path,
                expires_in=3600
            )
            signed_url = response.get('signedURL') or response.get('signedUrl') or ''
            if signed_url:
                return RedirectResponse(url=signed_url, status_code=302)
            else:
                logger.warning(f"No signed URL in response keys: {list(response.keys())}")
                raise HTTPException(status_code=404, detail="File not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {str(e)}")


@router.get("/upload/{upload_id}")
async def get_upload_file(
    upload_id: str,
    proxy: bool = Query(default=True, description="Proxy image through backend (bypasses CORS)"),
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    Serve an uploaded image file.

    Args:
        upload_id: The upload ID (filename without extension)
        proxy: If True (default), fetches image server-side and serves directly.
               If False, redirects to Supabase signed URL (may hit CORS issues).
    """
    try:
        if proxy:
            # Proxy mode: fetch image server-side and serve directly
            # Try common extensions
            for ext in ['.png', '.jpg', '.jpeg', '.webp']:
                file_path = f"{upload_id}{ext}"
                try:
                    image_data = storage.client.storage.from_('uploads').download(file_path)
                    content_type = _get_content_type(file_path)
                    return Response(
                        content=image_data,
                        media_type=content_type,
                        headers={
                            "Cache-Control": "public, max-age=3600",
                            "Content-Disposition": f"inline; filename={file_path}",
                        }
                    )
                except Exception:
                    continue
            raise HTTPException(status_code=404, detail="Upload not found")
        else:
            # Redirect mode
            signed_url = storage.get_upload_url(upload_id, expires_in=3600)
            return RedirectResponse(url=signed_url, status_code=302)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Upload not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Parameterized routes after static ones ---

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
    proxy: bool = Query(default=True, description="Proxy image through backend (bypasses CORS)"),
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    Serve a generated image file.

    Args:
        session_id: The generation session ID
        image_type: Type of image (main, infographic_1, etc.)
        proxy: If True (default), fetches image server-side and serves directly.
               If False, redirects to Supabase signed URL (may hit CORS issues).
    """
    try:
        if proxy:
            # Proxy mode: fetch image server-side and serve directly
            file_path = f"{session_id}/{image_type}.png"
            try:
                image_data = storage.client.storage.from_('generated').download(file_path)
                return Response(
                    content=image_data,
                    media_type='image/png',
                    headers={
                        "Cache-Control": "public, max-age=3600",
                        "Content-Disposition": f"inline; filename={image_type}.png",
                    }
                )
            except Exception as e:
                logger.error(f"Failed to proxy generated image {file_path}: {e}")
                raise HTTPException(status_code=404, detail="Image not found")
        else:
            # Redirect mode
            signed_url = storage.get_generated_url(session_id, image_type, expires_in=3600)
            return RedirectResponse(url=signed_url, status_code=302)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image not found")


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

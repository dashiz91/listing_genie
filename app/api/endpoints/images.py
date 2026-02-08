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
from fastapi.responses import RedirectResponse, Response
from app.services.supabase_storage_service import SupabaseStorageService
from app.services.generation_service import GenerationService
from app.services.gemini_service import GeminiService, get_gemini_service
from app.dependencies import get_storage_service
from app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.auth import User, get_current_user_from_header_or_cookie
from app.models.database import GenerationSession, DesignContext
from app.config import settings

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


def _normalize_storage_path(path: str) -> str:
    """Normalize legacy storage paths to supabase:// URIs."""
    normalised = path.replace("\\", "/")
    if normalised.startswith("supabase://"):
        return normalised

    m = re.match(r"^storage/(uploads|generated)/(.+)$", normalised)
    if m:
        return f"supabase://{m.group(1)}/{m.group(2)}"

    raise HTTPException(status_code=400, detail="Unrecognised storage path format.")


def _split_supabase_path(storage_path: str) -> tuple[str, str]:
    parts = storage_path[len("supabase://"):].split("/", 1)
    bucket = parts[0]
    file_path = parts[1] if len(parts) > 1 else ""
    return bucket, file_path


def _session_belongs_to_user(db: Session, user_id: str, session_id: str) -> bool:
    return (
        db.query(GenerationSession.id)
        .filter(GenerationSession.id == session_id, GenerationSession.user_id == user_id)
        .first()
        is not None
    )


def _user_can_access_storage_path(db: Session, user: User, storage_path: str) -> bool:
    """Authorize access to a storage object based on session ownership."""
    if not storage_path.startswith("supabase://"):
        return False

    bucket, file_path = _split_supabase_path(storage_path)
    if not file_path:
        return False

    # Generated images are namespaced by session_id/<file>.
    if bucket == settings.supabase_generated_bucket:
        session_id = file_path.split("/", 1)[0]
        return bool(session_id) and _session_belongs_to_user(db, user.id, session_id)

    # Uploads are only accessible if referenced by one of the user's sessions.
    if bucket == settings.supabase_uploads_bucket:
        direct_match = (
            db.query(GenerationSession.id)
            .filter(GenerationSession.user_id == user.id)
            .filter(
                or_(
                    GenerationSession.upload_path == storage_path,
                    GenerationSession.logo_path == storage_path,
                    GenerationSession.style_reference_path == storage_path,
                )
            )
            .first()
        )
        if direct_match:
            return True

        sessions = db.query(GenerationSession).filter(GenerationSession.user_id == user.id).all()
        for session in sessions:
            paths = session.additional_upload_paths or []
            if isinstance(paths, list) and storage_path in paths:
                return True

        contexts = (
            db.query(DesignContext)
            .join(GenerationSession, GenerationSession.id == DesignContext.session_id)
            .filter(GenerationSession.user_id == user.id)
            .all()
        )
        for context in contexts:
            inventory = context.image_inventory or []
            if not isinstance(inventory, list):
                continue
            for item in inventory:
                if isinstance(item, dict) and item.get("path") == storage_path:
                    return True

    return False


# --- Static routes MUST be declared before parameterized /{session_id} ---

@router.get("/file")
async def get_file_by_path(
    path: str,
    proxy: bool = Query(default=True, description="Proxy image through backend (bypasses CORS)"),
    storage: SupabaseStorageService = Depends(get_storage_service),
    user: User = Depends(get_current_user_from_header_or_cookie),
    db: Session = Depends(get_db),
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
        normalised = _normalize_storage_path(path)
        if not _user_can_access_storage_path(db, user, normalised):
            raise HTTPException(status_code=404, detail="File not found")

        bucket, file_path = _split_supabase_path(normalised)

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
    user: User = Depends(get_current_user_from_header_or_cookie),
    db: Session = Depends(get_db),
):
    """
    Serve an uploaded image file.

    Args:
        upload_id: The upload ID (filename without extension)
        proxy: If True (default), fetches image server-side and serves directly.
               If False, redirects to Supabase signed URL (may hit CORS issues).
    """
    try:
        owned_candidate_paths = []
        for ext in ['.png', '.jpg', '.jpeg', '.webp']:
            candidate = f"supabase://{settings.supabase_uploads_bucket}/{upload_id}{ext}"
            if _user_can_access_storage_path(db, user, candidate):
                owned_candidate_paths.append(candidate)

        if not owned_candidate_paths:
            raise HTTPException(status_code=404, detail="Upload not found")

        if proxy:
            # Proxy mode: fetch image server-side and serve directly
            for candidate in owned_candidate_paths:
                bucket, file_path = _split_supabase_path(candidate)
                try:
                    image_data = storage.client.storage.from_(bucket).download(file_path)
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
            bucket, file_path = _split_supabase_path(owned_candidate_paths[0])
            response = storage.client.storage.from_(bucket).create_signed_url(
                path=file_path,
                expires_in=3600,
            )
            signed_url = response.get('signedURL') or response.get('signedUrl') or ''
            if not signed_url:
                raise HTTPException(status_code=404, detail="Upload not found")
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
    user: User = Depends(get_current_user_from_header_or_cookie),
):
    """
    Get all images for a generation session.

    Returns URLs and status for each image type.
    """
    session = service.get_session_status(session_id)

    if not session or session.user_id != user.id:
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
    service: GenerationService = Depends(get_generation_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
    user: User = Depends(get_current_user_from_header_or_cookie),
):
    """
    Serve a generated image file.

    Args:
        session_id: The generation session ID
        image_type: Type of image (main, infographic_1, etc.)
        proxy: If True (default), fetches image server-side and serves directly.
               If False, redirects to Supabase signed URL (may hit CORS issues).
    """
    session = service.get_session_status(session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Image not found")

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
        "transformation": "Transformation",
        "comparison": "Comparison",
    }
    return labels.get(image_type, image_type.title())

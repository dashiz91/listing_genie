"""
File Upload API Endpoints
"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.storage_service import StorageService
from app.dependencies import get_storage_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Allowed image types (including WebP for style references)
# Note: Some browsers may send non-standard MIME types
ALLOWED_TYPES = {
    'image/png',
    'image/jpeg',
    'image/jpg',  # Non-standard but sometimes sent
    'image/webp',
    'image/gif',  # Allow GIFs too
}
# Also allow by file extension as fallback
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/")
async def upload_product_image(
    file: UploadFile = File(...),
    storage: StorageService = Depends(get_storage_service),
):
    """
    Upload a product image for processing.

    Returns the upload ID and path for use in generation requests.
    """
    logger.info(f"[UPLOAD] Received file: {file.filename}, content_type: {file.content_type}")

    # Validate content type (with fallback to file extension)
    import os
    file_ext = os.path.splitext(file.filename or "")[1].lower() if file.filename else ""

    content_type_ok = file.content_type in ALLOWED_TYPES
    extension_ok = file_ext in ALLOWED_EXTENSIONS

    if not content_type_ok and not extension_ok:
        logger.warning(f"[UPLOAD] Rejected file: content_type={file.content_type}, extension={file_ext}, filename={file.filename}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}' (extension: {file_ext}). Allowed: PNG, JPEG, WebP, GIF"
        )

    if not content_type_ok and extension_ok:
        logger.info(f"[UPLOAD] Accepting file by extension ({file_ext}) despite content_type: {file.content_type}")

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    if len(content) == 0:
        logger.warning(f"[UPLOAD] Empty file received: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail="Empty file uploaded"
        )

    logger.info(f"[UPLOAD] File validated: {file.filename} ({len(content)} bytes)")

    try:
        # Save the upload
        upload_id, file_path = storage.save_upload(content, file.filename or "upload.png")

        return {
            "upload_id": upload_id,
            "file_path": file_path,
            "filename": file.filename,
            "size": len(content),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save upload: {str(e)}"
        )


@router.delete("/{upload_id}")
async def delete_upload(
    upload_id: str,
    storage: StorageService = Depends(get_storage_service),
):
    """
    Delete an uploaded file.
    """
    try:
        storage.delete_upload(upload_id)
        return {"status": "deleted", "upload_id": upload_id}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Upload not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

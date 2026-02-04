"""
Projects API Endpoints

CRUD operations for user's generation sessions (projects).
"""
import re
import logging
from typing import Optional, List, Dict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies import get_db, get_storage_service
from app.core.auth import User, get_current_user
from app.models.database import GenerationSession, ImageRecord, GenerationStatusEnum, DesignContext
from app.services.supabase_storage_service import SupabaseStorageService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class ProjectListItem(BaseModel):
    """Project item for list view"""
    session_id: str
    product_title: str
    status: str
    created_at: str
    image_count: int
    complete_count: int
    thumbnail_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Paginated list of projects"""
    projects: List[ProjectListItem]
    total: int
    page: int
    total_pages: int


class ImageVersionDetail(BaseModel):
    """Single version of a listing image"""
    version: int
    image_url: str
    image_path: str


class ProjectImageDetail(BaseModel):
    """Image detail for project view"""
    image_type: str
    status: str
    storage_path: Optional[str] = None
    image_url: Optional[str] = None
    error_message: Optional[str] = None
    versions: Optional[List[ImageVersionDetail]] = None


class AplusModuleVersionDetail(BaseModel):
    """Single version of an A+ module image"""
    version: int
    image_url: str
    image_path: str


class AplusModuleDetail(BaseModel):
    """A+ module info for project restoration"""
    module_index: int
    module_type: str
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    versions: Optional[List[AplusModuleVersionDetail]] = None
    mobile_image_url: Optional[str] = None
    mobile_image_path: Optional[str] = None
    mobile_versions: Optional[List[AplusModuleVersionDetail]] = None


class ProjectDetailResponse(BaseModel):
    """Full project detail with all session fields for state restoration"""
    session_id: str
    product_title: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    brand_name: Optional[str] = None
    images: List[ProjectImageDetail]
    # Form fields
    feature_1: Optional[str] = None
    feature_2: Optional[str] = None
    feature_3: Optional[str] = None
    target_audience: Optional[str] = None
    global_note: Optional[str] = None
    # Upload paths
    upload_path: Optional[str] = None
    additional_upload_paths: Optional[List[str]] = None
    # Brand & style
    brand_colors: Optional[List[str]] = None
    color_palette: Optional[List[str]] = None
    color_count: Optional[int] = None
    logo_path: Optional[str] = None
    style_reference_path: Optional[str] = None
    style_reference_url: Optional[str] = None  # Signed URL for current style reference
    style_reference_versions: Optional[List[ImageVersionDetail]] = None  # Version history
    original_style_reference_path: Optional[str] = None  # User's original upload (if different from framework preview)
    # Design framework (full JSON)
    design_framework: Optional[dict] = None
    # Product analysis from DesignContext
    product_analysis: Optional[dict] = None
    product_analysis_summary: Optional[str] = None
    # A+ Content
    aplus_visual_script: Optional[dict] = None
    aplus_modules: Optional[List[AplusModuleDetail]] = None


class RenameRequest(BaseModel):
    """Request body for renaming a project"""
    new_title: str


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(12, ge=1, le=50, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    List all projects for the authenticated user.

    Returns paginated list of generation sessions with thumbnail URLs.
    """
    # Build base query
    query = db.query(GenerationSession).filter(
        GenerationSession.user_id == user.id
    )

    # Apply status filter if provided
    if status_filter and status_filter != "all":
        try:
            status_enum = GenerationStatusEnum(status_filter)
            query = query.filter(GenerationSession.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter}"
            )

    # Get total count
    total = query.count()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    # Paginate and order by most recent
    sessions = query.order_by(GenerationSession.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()

    # Build response with image counts and thumbnails
    projects = []
    for session in sessions:
        # Count images
        total_images = len(session.images) if session.images else 0
        complete_images = sum(
            1 for img in session.images
            if img.status == GenerationStatusEnum.COMPLETE
        ) if session.images else 0

        # Get thumbnail URL (main image)
        thumbnail_url = None
        main_image = next(
            (img for img in session.images if img.image_type.value == "main" and img.status == GenerationStatusEnum.COMPLETE),
            None
        )
        if main_image and main_image.storage_path:
            try:
                thumbnail_url = storage.get_generated_url(session.id, "main", expires_in=3600)
            except Exception as e:
                logger.warning(f"Failed to get thumbnail URL for session {session.id}: {e}")

        projects.append(ProjectListItem(
            session_id=session.id,
            product_title=session.product_title,
            status=session.status.value,
            created_at=session.created_at.isoformat() if session.created_at else "",
            image_count=total_images,
            complete_count=complete_images,
            thumbnail_url=thumbnail_url,
        ))

    return ProjectListResponse(
        projects=projects,
        total=total,
        page=page,
        total_pages=total_pages,
    )


@router.get("/{session_id}", response_model=ProjectDetailResponse)
async def get_project_detail(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    Get detailed information about a specific project.

    Includes all images with signed URLs.
    """
    # Get session with authorization check
    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == user.id,
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # List ALL files in session folder once to build a version map
    version_map: Dict[str, List[int]] = {}  # base_key -> sorted list of version numbers
    try:
        all_files = storage.client.storage.from_(storage.generated_bucket).list(session.id, {"limit": 1000})
        logger.info(f"[VERSION DEBUG] Session {session.id}: Found {len(all_files)} files in storage")
        for f in all_files:
            name = f.get("name", "")
            logger.info(f"[VERSION DEBUG]   File: {name}")
            # Match pattern: {base_key}_v{number}.png
            m = re.match(r'^(.+)_v(\d+)\.png$', name)
            if m:
                base_key = m.group(1)
                version_num = int(m.group(2))
                version_map.setdefault(base_key, []).append(version_num)
        # Sort each version list
        for key in version_map:
            version_map[key].sort()
        logger.info(f"[VERSION DEBUG] Version map: {version_map}")
    except Exception as e:
        logger.warning(f"Failed to list session files for version discovery: {e}")

    # Helper to build version details for a given storage key
    def _build_versions(base_key: str) -> List[ImageVersionDetail]:
        versions = []
        for v in version_map.get(base_key, []):
            versioned_key = f"{base_key}_v{v}"
            try:
                v_url = storage.get_generated_url(session.id, versioned_key, expires_in=3600)
                v_path = f"supabase://generated/{session.id}/{versioned_key}.png"
                versions.append(ImageVersionDetail(version=v, image_url=v_url, image_path=v_path))
            except Exception:
                pass
        return versions

    # Build image details with signed URLs and versions
    images = []
    for img in session.images:
        image_url = None
        if img.storage_path and img.status == GenerationStatusEnum.COMPLETE:
            try:
                image_url = storage.get_generated_url(
                    session.id,
                    img.image_type.value,
                    expires_in=3600
                )
            except Exception as e:
                logger.warning(f"Failed to get URL for {img.image_type}: {e}")

        img_versions = _build_versions(img.image_type.value) if img.status == GenerationStatusEnum.COMPLETE else []

        images.append(ProjectImageDetail(
            image_type=img.image_type.value,
            status=img.status.value,
            storage_path=img.storage_path,
            image_url=image_url,
            error_message=img.error_message,
            versions=img_versions if img_versions else None,
        ))

    # Load DesignContext for product analysis
    design_context = db.query(DesignContext).filter(
        DesignContext.session_id == session_id
    ).first()

    # Build product analysis summary text from raw analysis
    product_analysis_summary = None
    if design_context and design_context.product_analysis:
        pa = design_context.product_analysis
        if isinstance(pa, dict):
            product_analysis_summary = pa.get("summary") or pa.get("product_category", "")

    # Extract original style reference path from DesignContext image_inventory
    original_style_reference_path = None
    if design_context and design_context.image_inventory:
        for item in design_context.image_inventory:
            if item.get("type") == "original_style_reference":
                original_style_reference_path = item.get("path")
                break

    # Load A+ modules — use version_map + storage probing
    aplus_modules_list = None
    aplus_slot_count = 0
    if session.aplus_visual_script:
        aplus_slot_count = len(session.aplus_visual_script.get("modules", []))
    if aplus_slot_count == 0:
        aplus_slot_count = 5

    aplus_modules_list = []
    for i in range(aplus_slot_count):
        storage_key = f"aplus_full_image_{i}"
        versions = _build_versions(storage_key)

        # Get latest (unversioned) URL for backward compat
        latest_url = None
        latest_path = None
        try:
            latest_url = storage.get_generated_url(session.id, storage_key, expires_in=3600)
            latest_path = f"supabase://generated/{session.id}/{storage_key}.png"
        except Exception:
            pass

        # Probe mobile versions - special handling for hero modules
        mobile_url = None
        mobile_path = None
        mobile_versions = None

        if i == 0:
            # Module 0: use hero mobile image
            mobile_key = "aplus_full_image_hero_mobile"
            mobile_versions = _build_versions(mobile_key)
            try:
                mobile_url = storage.get_generated_url(session.id, mobile_key, expires_in=3600)
                mobile_path = f"supabase://generated/{session.id}/{mobile_key}.png"
            except Exception:
                pass
        elif i == 1:
            # Module 1: skip mobile probing (shares hero mobile with module 0)
            pass
        else:
            # Modules 2+: standard individual mobile images
            mobile_key = f"aplus_full_image_{i}_mobile"
            mobile_versions = _build_versions(mobile_key)
            try:
                mobile_url = storage.get_generated_url(session.id, mobile_key, expires_in=3600)
                mobile_path = f"supabase://generated/{session.id}/{mobile_key}.png"
            except Exception:
                pass

        if latest_url:
            aplus_modules_list.append(AplusModuleDetail(
                module_index=i,
                module_type="full_image",
                image_url=latest_url,
                image_path=latest_path,
                versions=[AplusModuleVersionDetail(version=v.version, image_url=v.image_url, image_path=v.image_path) for v in versions] if versions else None,
                mobile_image_url=mobile_url,
                mobile_image_path=mobile_path,
                mobile_versions=[AplusModuleVersionDetail(version=v.version, image_url=v.image_url, image_path=v.image_path) for v in mobile_versions] if mobile_versions else None,
            ))
        else:
            aplus_modules_list.append(AplusModuleDetail(
                module_index=i,
                module_type="full_image",
                mobile_image_url=mobile_url,
                mobile_image_path=mobile_path,
                mobile_versions=[AplusModuleVersionDetail(version=v.version, image_url=v.image_url, image_path=v.image_path) for v in mobile_versions] if mobile_versions else None,
            ))

    # Only return A+ data if at least one module has an image
    if not any(m.image_url for m in aplus_modules_list):
        aplus_modules_list = None

    # Build style reference URL and versions
    style_reference_url = None
    style_reference_versions = None

    # First check for versioned style references in generated bucket
    style_ref_versions_list = _build_versions("style_reference")
    if style_ref_versions_list:
        style_reference_versions = style_ref_versions_list
        # Get the latest version URL
        try:
            style_reference_url = storage.get_generated_url(session.id, "style_reference", expires_in=3600)
            logger.info(f"[STYLE REF] Found versioned style ref, URL: {style_reference_url[:50]}...")
        except Exception as e:
            logger.warning(f"[STYLE REF] Failed to get versioned URL: {e}")

    # Fallback chain if no versioned style reference found
    if not style_reference_url:
        # Try original_style_reference_path from DesignContext
        if original_style_reference_path:
            style_reference_url = f"/api/images/file?path={original_style_reference_path}"
            logger.info(f"[STYLE REF] Using original_style_reference_path: {original_style_reference_path}")
        # Try session.style_reference_path if not a framework preview
        elif session.style_reference_path and 'framework_preview' not in session.style_reference_path:
            style_reference_url = f"/api/images/file?path={session.style_reference_path}"
            logger.info(f"[STYLE REF] Using session.style_reference_path: {session.style_reference_path}")
        else:
            logger.info(f"[STYLE REF] No style reference found for session {session.id}")

    return ProjectDetailResponse(
        session_id=session.id,
        product_title=session.product_title,
        status=session.status.value,
        created_at=session.created_at.isoformat() if session.created_at else "",
        completed_at=session.completed_at.isoformat() if session.completed_at else None,
        brand_name=session.brand_name,
        images=images,
        # Form fields
        feature_1=session.feature_1,
        feature_2=session.feature_2,
        feature_3=session.feature_3,
        target_audience=session.target_audience,
        global_note=session.global_note,
        # Upload paths
        upload_path=session.upload_path,
        additional_upload_paths=session.additional_upload_paths or [],
        # Brand & style
        brand_colors=session.brand_colors or [],
        color_palette=session.color_palette or [],
        color_count=session.color_count,
        logo_path=session.logo_path,
        style_reference_path=session.style_reference_path,
        style_reference_url=style_reference_url,
        style_reference_versions=style_reference_versions,
        original_style_reference_path=original_style_reference_path,
        # Design framework
        design_framework=session.design_framework_json,
        # Product analysis
        product_analysis=design_context.product_analysis if design_context else None,
        product_analysis_summary=product_analysis_summary,
        # A+ Content
        aplus_visual_script=session.aplus_visual_script,
        aplus_modules=aplus_modules_list,
    )


@router.patch("/{session_id}")
async def rename_project(
    session_id: str,
    request: RenameRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rename a project (update product title).
    """
    # Get session with authorization check
    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == user.id,
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Validate new title
    new_title = request.new_title.strip()
    if not new_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    if len(new_title) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be 200 characters or less"
        )

    # Update title
    session.product_title = new_title
    db.commit()

    logger.info(f"Renamed project {session_id} to: {new_title}")

    return {"status": "success", "product_title": new_title}


@router.delete("/{session_id}")
async def delete_project(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    Delete a project and all associated images from storage.
    """
    # Get session with authorization check
    session = db.query(GenerationSession).filter(
        GenerationSession.id == session_id,
        GenerationSession.user_id == user.id,
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Delete images from Supabase storage
    try:
        storage.delete_session_images(session_id)
        logger.info(f"Deleted storage images for session {session_id}")
    except Exception as e:
        logger.warning(f"Failed to delete storage images for {session_id}: {e}")
        # Continue with database deletion even if storage fails

    # Delete session from database (cascade deletes images, keywords, context)
    db.delete(session)
    db.commit()

    logger.info(f"Deleted project {session_id} for user {user.id}")

    return {"status": "success", "deleted": session_id}

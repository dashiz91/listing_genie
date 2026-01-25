"""
Projects API Endpoints

CRUD operations for user's generation sessions (projects).
"""
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies import get_db, get_storage_service
from app.core.auth import User, get_current_user
from app.models.database import GenerationSession, ImageRecord, GenerationStatusEnum
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


class ProjectImageDetail(BaseModel):
    """Image detail for project view"""
    image_type: str
    status: str
    storage_path: Optional[str] = None
    image_url: Optional[str] = None
    error_message: Optional[str] = None


class ProjectDetailResponse(BaseModel):
    """Full project detail"""
    session_id: str
    product_title: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    brand_name: Optional[str] = None
    images: List[ProjectImageDetail]


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

    # Build image details with signed URLs
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

        images.append(ProjectImageDetail(
            image_type=img.image_type.value,
            status=img.status.value,
            storage_path=img.storage_path,
            image_url=image_url,
            error_message=img.error_message,
        ))

    return ProjectDetailResponse(
        session_id=session.id,
        product_title=session.product_title,
        status=session.status.value,
        created_at=session.created_at.isoformat() if session.created_at else "",
        completed_at=session.completed_at.isoformat() if session.completed_at else None,
        brand_name=session.brand_name,
        images=images,
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

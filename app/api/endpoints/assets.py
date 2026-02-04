"""
Assets API Endpoints

List and manage reusable assets (logos, style references, product photos, generated images).
"""
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from pydantic import BaseModel

from app.dependencies import get_db, get_storage_service
from app.core.auth import User, get_current_user
from app.models.database import GenerationSession, ImageRecord, GenerationStatusEnum
from app.services.supabase_storage_service import SupabaseStorageService
from app.config import settings

logger = logging.getLogger(__name__)


def _get_image_url(relative_path: str) -> str:
    """Convert a relative API path to an absolute URL."""
    if settings.backend_url:
        return f"{settings.backend_url.rstrip('/')}{relative_path}"
    return relative_path


router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class AssetItem(BaseModel):
    """Single asset item"""
    id: str
    name: str
    url: str
    type: str  # logos, style-refs, products, generated
    created_at: str
    session_id: Optional[str] = None  # For generated images
    image_type: Optional[str] = None  # For generated images (main, infographic_1, etc.)


class AssetsListResponse(BaseModel):
    """List of assets"""
    assets: List[AssetItem]
    total: int


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/", response_model=AssetsListResponse)
async def list_assets(
    asset_type: str = Query("all", description="Asset type: logos, style-refs, products, generated, all"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    List all assets for the authenticated user by category.

    Categories:
    - logos: Brand logos uploaded across all projects
    - style-refs: Style reference images uploaded across all projects
    - products: Product photos uploaded across all projects
    - generated: AI-generated listing images from all projects
    - all: All assets combined
    """
    assets = []
    seen_paths = set()  # Deduplicate by storage path

    # Get all user's sessions
    sessions = db.query(GenerationSession).filter(
        GenerationSession.user_id == user.id
    ).order_by(GenerationSession.created_at.desc()).all()

    # Collect Logos
    if asset_type in ["logos", "all"]:
        for session in sessions:
            if session.logo_path and session.logo_path not in seen_paths:
                seen_paths.add(session.logo_path)
                # Extract upload_id from path like "supabase://uploads/uuid.png"
                upload_id = session.logo_path.split("/")[-1].replace(".png", "")
                assets.append(AssetItem(
                    id=upload_id,
                    name=f"Logo - {session.product_title[:30]}..." if len(session.product_title) > 30 else f"Logo - {session.product_title}",
                    url=_get_image_url(f"/api/images/file?path={session.logo_path}"),
                    type="logos",
                    created_at=session.created_at.isoformat() if session.created_at else "",
                    session_id=session.id,
                ))

    # Collect Style References
    if asset_type in ["style-refs", "all"]:
        for session in sessions:
            if session.style_reference_path and session.style_reference_path not in seen_paths:
                # Skip framework preview images (they're generated, not user uploads)
                if "framework_preview" in session.style_reference_path:
                    continue
                seen_paths.add(session.style_reference_path)
                upload_id = session.style_reference_path.split("/")[-1].replace(".png", "")
                assets.append(AssetItem(
                    id=upload_id,
                    name=f"Style - {session.product_title[:30]}..." if len(session.product_title) > 30 else f"Style - {session.product_title}",
                    url=_get_image_url(f"/api/images/file?path={session.style_reference_path}"),
                    type="style-refs",
                    created_at=session.created_at.isoformat() if session.created_at else "",
                    session_id=session.id,
                ))

    # Collect Product Photos
    if asset_type in ["products", "all"]:
        for session in sessions:
            # Main upload
            if session.upload_path and session.upload_path not in seen_paths:
                seen_paths.add(session.upload_path)
                upload_id = session.upload_path.split("/")[-1].replace(".png", "")
                assets.append(AssetItem(
                    id=upload_id,
                    name=f"Product - {session.product_title[:25]}..." if len(session.product_title) > 25 else f"Product - {session.product_title}",
                    url=_get_image_url(f"/api/images/file?path={session.upload_path}"),
                    type="products",
                    created_at=session.created_at.isoformat() if session.created_at else "",
                    session_id=session.id,
                ))

            # Additional uploads
            if session.additional_upload_paths:
                for i, path in enumerate(session.additional_upload_paths):
                    if path and path not in seen_paths:
                        seen_paths.add(path)
                        upload_id = path.split("/")[-1].replace(".png", "")
                        assets.append(AssetItem(
                            id=upload_id,
                            name=f"Product {i+2} - {session.product_title[:20]}..." if len(session.product_title) > 20 else f"Product {i+2} - {session.product_title}",
                            url=_get_image_url(f"/api/images/file?path={path}"),
                            type="products",
                            created_at=session.created_at.isoformat() if session.created_at else "",
                            session_id=session.id,
                        ))

    # Collect Generated Images
    if asset_type in ["generated", "all"]:
        # Query completed images from all sessions
        for session in sessions:
            for img in session.images:
                if img.status == GenerationStatusEnum.COMPLETE and img.storage_path:
                    storage_path = img.storage_path
                    if storage_path not in seen_paths:
                        seen_paths.add(storage_path)
                        assets.append(AssetItem(
                            id=f"{session.id}_{img.image_type.value}",
                            name=f"{img.image_type.value.replace('_', ' ').title()} - {session.product_title[:20]}...",
                            url=_get_image_url(f"/api/images/{session.id}/{img.image_type.value}"),
                            type="generated",
                            created_at=session.created_at.isoformat() if session.created_at else "",
                            session_id=session.id,
                            image_type=img.image_type.value,
                        ))

    return AssetsListResponse(
        assets=assets,
        total=len(assets),
    )

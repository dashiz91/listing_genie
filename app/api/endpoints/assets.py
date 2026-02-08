"""
Assets API Endpoints

List and manage reusable assets (logos, style references, product photos, generated images).
"""
import logging
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies import get_db, get_storage_service
from app.core.auth import User, get_current_user
from app.models.database import GenerationSession
from app.services.supabase_storage_service import SupabaseStorageService
from app.config import settings

logger = logging.getLogger(__name__)


def _get_image_url(relative_path: str) -> str:
    """Convert a relative API path to an absolute URL."""
    if settings.backend_url:
        return f"{settings.backend_url.rstrip('/')}{relative_path}"
    return relative_path


router = APIRouter()

LISTING_KEYS = {
    "main",
    "infographic_1",
    "infographic_2",
    "lifestyle",
    "transformation",
    "comparison",
}

LISTING_LABELS = {
    "main": "Main",
    "infographic_1": "Infographic 1",
    "infographic_2": "Infographic 2",
    "lifestyle": "Lifestyle",
    "transformation": "Transformation",
    "comparison": "Comparison",
}


def _trim_title(title: str, limit: int = 28) -> str:
    if len(title) <= limit:
        return title
    return f"{title[:limit]}..."


def _strip_generated_version_suffix(name_without_ext: str) -> tuple[str, Optional[int]]:
    """
    Convert "main_v3" -> ("main", 3), or "main" -> ("main", None).
    """
    match = re.match(r"^(.*)_v(\d+)$", name_without_ext)
    if not match:
        return name_without_ext, None
    return match.group(1), int(match.group(2))


def _generated_category_from_key(base_key: str) -> str:
    if base_key in LISTING_KEYS:
        return "listing"
    if base_key.startswith("aplus_") or base_key.startswith("aplus_full_image_"):
        return "aplus"
    return "other"


def _generated_display_name(base_key: str, version: Optional[int], product_title: str) -> str:
    category = _generated_category_from_key(base_key)
    base_product = _trim_title(product_title, 22)
    version_suffix = f" v{version}" if version is not None else ""

    if category == "listing":
        label = LISTING_LABELS.get(base_key, base_key.replace("_", " ").title())
        return f"{label}{version_suffix} - {base_product}"

    if category == "aplus":
        label = base_key.replace("_", " ").title()
        return f"{label}{version_suffix} - {base_product}"

    label = base_key.replace("_", " ").title()
    return f"{label}{version_suffix} - {base_product}"


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
    generated_category: Optional[str] = None  # listing, aplus, other
    storage_path: Optional[str] = None


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
    assets: List[AssetItem] = []
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
        # Include every generated file for each session, including versioned regenerations
        # and A+ desktop/mobile artifacts (not just the latest DB image record).
        for session in sessions:
            try:
                files = storage.client.storage.from_(storage.generated_bucket).list(
                    session.id,
                    {"limit": 1000},
                )
            except Exception as exc:
                logger.warning("Failed to list generated assets for session %s: %s", session.id, exc)
                continue

            for file_entry in files:
                filename = file_entry.get("name") or ""
                if not filename:
                    continue

                lower_name = filename.lower()
                if not (lower_name.endswith(".png") or lower_name.endswith(".jpg") or lower_name.endswith(".jpeg") or lower_name.endswith(".webp")):
                    continue

                name_without_ext = filename.rsplit(".", 1)[0]
                base_key, version = _strip_generated_version_suffix(name_without_ext)
                generated_category = _generated_category_from_key(base_key)

                full_storage_path = f"supabase://{storage.generated_bucket}/{session.id}/{filename}"
                created_at = file_entry.get("created_at") or (
                    session.created_at.isoformat() if session.created_at else ""
                )

                assets.append(
                    AssetItem(
                        id=f"{session.id}:{filename}",
                        name=_generated_display_name(base_key, version, session.product_title),
                        url=_get_image_url(f"/api/images/file?path={full_storage_path}"),
                        type="generated",
                        created_at=created_at,
                        session_id=session.id,
                        image_type=base_key,
                        generated_category=generated_category,
                        storage_path=full_storage_path,
                    )
                )

    assets.sort(key=lambda a: a.created_at or "", reverse=True)

    return AssetsListResponse(
        assets=assets,
        total=len(assets),
    )

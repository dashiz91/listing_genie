"""
Amazon SP-API integration endpoints.

Phase 1:
- OAuth connection status/url/callback/disconnect
- Async listing images push + job status polling
"""
from __future__ import annotations

import logging
from typing import Optional, Literal
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.core.auth import User, get_current_user
from app.db.session import get_db, SessionLocal
from app.services.amazon_auth_service import AmazonAuthService
from app.services.amazon_push_service import AmazonPushService

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class AmazonAuthStatusResponse(BaseModel):
    connected: bool
    seller_id: Optional[str]
    marketplace_id: str
    connection_mode: Literal["env", "oauth", "manual", "none"]
    last_connected_at: Optional[str]


class AmazonAuthUrlRequest(BaseModel):
    marketplace_id: Optional[str] = None
    return_to: Optional[str] = "/app/settings"


class AmazonAuthUrlResponse(BaseModel):
    auth_url: str
    state: str
    expires_in_seconds: int


class AmazonDisconnectResponse(BaseModel):
    disconnected: bool


class PushListingImagesRequest(BaseModel):
    session_id: str = Field(min_length=1)
    asin: str = Field(min_length=10, max_length=20)
    sku: str = Field(min_length=1, max_length=80)
    marketplace_id: Optional[str] = None
    image_paths: Optional[list[str]] = None


class PushListingImagesResponse(BaseModel):
    job_id: str
    status: Literal["queued"]


class PushJobStatusResponse(BaseModel):
    job_id: str
    kind: str
    status: Literal["queued", "preparing", "submitting", "processing", "completed", "failed"]
    progress: int
    step: str
    asin: Optional[str]
    sku: Optional[str]
    session_id: Optional[str]
    submission_id: Optional[str]
    error_message: Optional[str]
    created_at: str
    updated_at: Optional[str]
    completed_at: Optional[str]


class SellerSku(BaseModel):
    sku: str
    asin: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None


class SellerSkusResponse(BaseModel):
    skus: list[SellerSku]
    count: int


def _frontend_redirect(return_to: Optional[str], **params: str) -> str:
    safe_path = return_to or "/app/settings"
    if not safe_path.startswith("/"):
        safe_path = "/app/settings"
    base = settings.frontend_url.rstrip("/")
    query = urlencode(params)
    sep = "&" if "?" in safe_path else "?"
    return f"{base}{safe_path}{sep}{query}"


async def _run_listing_push_job(job_id: str) -> None:
    """Background worker wrapper with its own DB session."""
    db = SessionLocal()
    try:
        service = AmazonPushService(db)
        await service.process_listing_images_job(job_id)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------
@router.get("/auth/status", response_model=AmazonAuthStatusResponse)
async def get_auth_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AmazonAuthService(db)
    return AmazonAuthStatusResponse(**service.get_auth_status(user.id))


@router.post("/auth/url", response_model=AmazonAuthUrlResponse)
async def create_auth_url(
    request: AmazonAuthUrlRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AmazonAuthService(db)
    try:
        payload = service.build_authorization_url(
            user_id=user.id,
            marketplace_id=request.marketplace_id,
            return_to=request.return_to,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AmazonAuthUrlResponse(**payload)


@router.get("/auth/callback")
async def auth_callback(
    spapi_oauth_code: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    selling_partner_id: Optional[str] = Query(default=None),
    error: Optional[str] = Query(default=None),
    error_description: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    service = AmazonAuthService(db)

    # State is required to identify the user/session.
    if not state:
        return RedirectResponse(
            _frontend_redirect("/app/settings", amazon_connect="error", reason="missing_state"),
            status_code=302,
        )

    try:
        state_payload = service.verify_signed_state(state)
    except Exception:
        return RedirectResponse(
            _frontend_redirect("/app/settings", amazon_connect="error", reason="invalid_state"),
            status_code=302,
        )

    user_id = state_payload.get("uid")
    return_to = state_payload.get("rt") or "/app/settings"
    marketplace_id = state_payload.get("mp") or settings.amazon_default_marketplace_id
    if not user_id:
        return RedirectResponse(
            _frontend_redirect(return_to, amazon_connect="error", reason="missing_user"),
            status_code=302,
        )

    if error:
        reason = error_description or error
        return RedirectResponse(
            _frontend_redirect(return_to, amazon_connect="error", reason=reason),
            status_code=302,
        )

    if not spapi_oauth_code:
        return RedirectResponse(
            _frontend_redirect(return_to, amazon_connect="error", reason="missing_oauth_code"),
            status_code=302,
        )

    try:
        token_payload = await service.exchange_code_for_refresh_token(spapi_oauth_code)
        service.save_connection(
            user_id=user_id,
            refresh_token=token_payload["refresh_token"],
            seller_id=selling_partner_id,
            marketplace_id=marketplace_id,
        )
    except Exception as exc:
        logger.error(f"Amazon OAuth callback failed: {exc}")
        return RedirectResponse(
            _frontend_redirect(return_to, amazon_connect="error", reason="token_exchange_failed"),
            status_code=302,
        )

    return RedirectResponse(
        _frontend_redirect(return_to, amazon_connect="success"),
        status_code=302,
    )


@router.delete("/auth/disconnect", response_model=AmazonDisconnectResponse)
async def disconnect_auth(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AmazonAuthService(db)
    service.disconnect(user.id)
    return AmazonDisconnectResponse(disconnected=True)


@router.get("/skus", response_model=SellerSkusResponse)
async def list_skus(
    query: Optional[str] = Query(default=None, description="Optional keyword/SKU search"),
    limit: int = Query(default=20, ge=1, le=100),
    marketplace_id: Optional[str] = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AmazonPushService(db)
    try:
        skus = await service.list_seller_skus(
            user_id=user.id,
            query=query,
            limit=limit,
            marketplace_id=marketplace_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Failed to list seller SKUs: {exc}")
        raise HTTPException(status_code=502, detail="Failed to fetch SKUs from Amazon") from exc
    return SellerSkusResponse(
        skus=[SellerSku(**s) for s in skus],
        count=len(skus),
    )


# ---------------------------------------------------------------------------
# Push endpoints
# ---------------------------------------------------------------------------
@router.post("/push/listing-images", response_model=PushListingImagesResponse)
async def push_listing_images(
    request: PushListingImagesRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AmazonPushService(db)

    # Ensure account is connected before creating a job.
    connection = service.auth.get_connection(user.id)
    if not connection:
        raise HTTPException(status_code=400, detail="Amazon account is not connected")

    job = service.create_listing_images_job(
        user_id=user.id,
        session_id=request.session_id,
        asin=request.asin,
        sku=request.sku,
        marketplace_id=request.marketplace_id or connection.marketplace_id,
        image_paths=request.image_paths,
    )
    background_tasks.add_task(_run_listing_push_job, job.id)
    return PushListingImagesResponse(job_id=job.id, status="queued")


@router.get("/push/status/{job_id}", response_model=PushJobStatusResponse)
async def get_push_status(
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AmazonPushService(db)
    job = service.get_job_for_user(job_id, user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Push job not found")

    updated_at = None
    if job.updated_at:
        updated_at = job.updated_at.isoformat()

    return PushJobStatusResponse(
        job_id=job.id,
        kind=job.kind,
        status=job.status,
        progress=job.progress,
        step=job.step or "",
        asin=job.asin,
        sku=job.sku,
        session_id=job.session_id,
        submission_id=job.submission_id,
        error_message=job.error_message,
        created_at=job.created_at.isoformat(),
        updated_at=updated_at,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
    )

"""
Amazon push orchestration service.

Owns:
- Job creation/status
- Session image resolution
- Public URL conversion for SP-API ingestion
- Listing image submission orchestration
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from urllib.parse import quote

from sqlalchemy.orm import Session

from app.config import settings
from app.models.database import (
    AmazonPushJob,
    ImageRecord,
    ImageTypeEnum,
    GenerationStatusEnum,
)
from app.services.amazon_auth_service import AmazonAuthService
from app.services.amazon_sp_api_service import AmazonSPAPIService, AmazonSPAPIError

logger = logging.getLogger(__name__)


LISTING_IMAGE_TYPES = [
    ImageTypeEnum.MAIN,
    ImageTypeEnum.INFOGRAPHIC_1,
    ImageTypeEnum.INFOGRAPHIC_2,
    ImageTypeEnum.LIFESTYLE,
    ImageTypeEnum.TRANSFORMATION,
    ImageTypeEnum.COMPARISON,
]


class AmazonPushService:
    """Coordinates SP-API push operations and persistent job state."""

    def __init__(self, db: Session):
        self.db = db
        self.auth = AmazonAuthService(db)
        self.sp_api = AmazonSPAPIService()

    def create_listing_images_job(
        self,
        *,
        user_id: str,
        session_id: str,
        asin: str,
        sku: str,
        marketplace_id: Optional[str],
        image_paths: Optional[List[str]] = None,
    ) -> AmazonPushJob:
        job = AmazonPushJob(
            user_id=user_id,
            kind="listing_images",
            status="queued",
            progress=0,
            step="Queued",
            session_id=session_id,
            asin=asin,
            sku=sku,
            marketplace_id=marketplace_id or settings.amazon_default_marketplace_id,
            payload_json={"image_paths": image_paths or []},
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job_for_user(self, job_id: str, user_id: str) -> Optional[AmazonPushJob]:
        return (
            self.db.query(AmazonPushJob)
            .filter(AmazonPushJob.id == job_id, AmazonPushJob.user_id == user_id)
            .first()
        )

    def _update_job(
        self,
        job: AmazonPushJob,
        *,
        status: str,
        progress: int,
        step: str,
        error_message: Optional[str] = None,
        submission_id: Optional[str] = None,
        response_json: Optional[Dict[str, Any]] = None,
        completed: bool = False,
    ) -> None:
        job.status = status
        job.progress = max(0, min(100, progress))
        job.step = step
        job.error_message = error_message
        if submission_id:
            job.submission_id = submission_id
        if response_json is not None:
            job.response_json = response_json
        if completed:
            job.completed_at = datetime.now(timezone.utc)
        self.db.commit()

    def _collect_session_listing_paths(self, session_id: str) -> List[str]:
        paths: List[str] = []
        for image_type in LISTING_IMAGE_TYPES:
            record = (
                self.db.query(ImageRecord)
                .filter(
                    ImageRecord.session_id == session_id,
                    ImageRecord.image_type == image_type,
                    ImageRecord.status == GenerationStatusEnum.COMPLETE,
                    ImageRecord.storage_path.isnot(None),
                )
                .order_by(ImageRecord.created_at.desc(), ImageRecord.id.desc())
                .first()
            )
            if record and record.storage_path:
                paths.append(record.storage_path)
        return paths

    @staticmethod
    def _to_public_image_url(storage_path: str) -> str:
        if not settings.backend_url:
            raise ValueError("backend_url must be configured to generate public image URLs")
        return f"{settings.backend_url.rstrip('/')}/api/images/file?path={quote(storage_path, safe='')}"

    async def process_listing_images_job(self, job_id: str) -> None:
        job = self.db.query(AmazonPushJob).filter(AmazonPushJob.id == job_id).first()
        if not job:
            logger.error(f"Amazon push job not found: {job_id}")
            return

        try:
            self._update_job(job, status="preparing", progress=10, step="Resolving Amazon credentials")
            connection = self.auth.get_connection(job.user_id)
            if not connection:
                raise ValueError("Amazon account is not connected")
            if not connection.seller_id:
                raise ValueError("Missing seller ID for connected Amazon account")

            self._update_job(job, status="preparing", progress=25, step="Preparing listing images")
            requested_paths = ((job.payload_json or {}).get("image_paths") or [])
            image_paths = [p for p in requested_paths if isinstance(p, str) and p.strip()]
            if not image_paths:
                image_paths = self._collect_session_listing_paths(job.session_id or "")
            image_paths = image_paths[:7]
            if not image_paths:
                raise ValueError("No generated listing images found for this session")

            image_urls = [self._to_public_image_url(path) for path in image_paths]

            self._update_job(job, status="submitting", progress=55, step="Submitting to Amazon SP-API")
            access_token = await self.auth.refresh_access_token(connection.refresh_token)
            patch_result = await self.sp_api.patch_listing_images(
                access_token=access_token,
                seller_id=connection.seller_id,
                sku=job.sku or "",
                marketplace_id=job.marketplace_id or connection.marketplace_id,
                image_urls=image_urls,
            )

            self._update_job(
                job,
                status="completed",
                progress=100,
                step="Completed",
                submission_id=patch_result.get("submission_id"),
                response_json=patch_result,
                completed=True,
            )
        except AmazonSPAPIError as exc:
            logger.error(f"Amazon SP-API error for job {job_id}: {exc}")
            self._update_job(
                job,
                status="failed",
                progress=100,
                step="Failed",
                error_message=str(exc),
                response_json={"details": exc.details},
                completed=True,
            )
        except Exception as exc:
            logger.error(f"Amazon push failed for job {job_id}: {exc}")
            self._update_job(
                job,
                status="failed",
                progress=100,
                step="Failed",
                error_message=str(exc),
                completed=True,
            )

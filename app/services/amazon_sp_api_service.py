"""
Amazon SP-API client service.

Implements AWS SigV4 signing for SP-API requests and exposes
the Listings Items PATCH call used by Phase 1 image push.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from urllib.parse import quote, urlparse, parse_qsl

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AmazonSPAPIError(Exception):
    """Raised when SP-API returns an error."""

    def __init__(self, message: str, *, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class AmazonSPAPIService:
    """Minimal SP-API client for Listings Items image patch operations."""

    def __init__(self):
        self.endpoint = settings.amazon_spapi_endpoint.rstrip("/")
        self.region = settings.amazon_spapi_region
        self.service = "execute-api"
        self.aws_access_key = settings.amazon_aws_access_key_id
        self.aws_secret_key = settings.amazon_aws_secret_access_key
        self.aws_session_token = settings.amazon_aws_session_token

    # ------------------------------------------------------------------
    # SigV4 helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _sha256_hex(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _hmac_sha256(key: bytes, data: str) -> bytes:
        return hmac.new(key, data.encode("utf-8"), hashlib.sha256).digest()

    def _signature_key(self, date_stamp: str) -> bytes:
        k_date = self._hmac_sha256(("AWS4" + self.aws_secret_key).encode("utf-8"), date_stamp)
        k_region = self._hmac_sha256(k_date, self.region)
        k_service = self._hmac_sha256(k_region, self.service)
        return self._hmac_sha256(k_service, "aws4_request")

    @staticmethod
    def _canonical_query(query: str) -> str:
        parts = parse_qsl(query, keep_blank_values=True)
        encoded = [
            (quote(k, safe="-_.~"), quote(v, safe="-_.~"))
            for k, v in parts
        ]
        encoded.sort()
        return "&".join(f"{k}={v}" for k, v in encoded)

    @staticmethod
    def _normalize_header_value(value: str) -> str:
        return " ".join(value.strip().split())

    def _sign_headers(
        self,
        *,
        method: str,
        url: str,
        headers: Dict[str, str],
        payload: bytes,
    ) -> Dict[str, str]:
        if not self.aws_access_key or not self.aws_secret_key:
            raise AmazonSPAPIError(
                "AWS credentials for SP-API signing are not configured",
                status_code=500,
            )

        parsed = urlparse(url)
        now = datetime.now(timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")

        canonical_uri = quote(parsed.path or "/", safe="/-_.~")
        canonical_query = self._canonical_query(parsed.query)

        canonical_headers_map = {k.lower(): self._normalize_header_value(v) for k, v in headers.items()}
        canonical_headers_map["host"] = parsed.netloc
        canonical_headers_map["x-amz-date"] = amz_date
        if self.aws_session_token:
            canonical_headers_map["x-amz-security-token"] = self.aws_session_token

        signed_header_names = sorted(canonical_headers_map.keys())
        signed_headers = ";".join(signed_header_names)
        canonical_headers = "".join(f"{name}:{canonical_headers_map[name]}\n" for name in signed_header_names)

        payload_hash = self._sha256_hex(payload)
        canonical_request = "\n".join(
            [
                method.upper(),
                canonical_uri,
                canonical_query,
                canonical_headers,
                signed_headers,
                payload_hash,
            ]
        )

        credential_scope = f"{date_stamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = "\n".join(
            [
                "AWS4-HMAC-SHA256",
                amz_date,
                credential_scope,
                self._sha256_hex(canonical_request.encode("utf-8")),
            ]
        )

        signing_key = self._signature_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        authorization = (
            "AWS4-HMAC-SHA256 "
            f"Credential={self.aws_access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )

        out = dict(headers)
        out["x-amz-date"] = amz_date
        out["Authorization"] = authorization
        if self.aws_session_token:
            out["x-amz-security-token"] = self.aws_session_token
        return out

    # ------------------------------------------------------------------
    # Listings API
    # ------------------------------------------------------------------
    @staticmethod
    def build_listing_image_attributes(image_urls: List[str]) -> List[Dict[str, Any]]:
        """Create Listings Items patches for main + other image locators."""
        attributes = []
        for idx, image_url in enumerate(image_urls):
            if idx == 0:
                attr = "main_product_image_locator"
            else:
                attr = f"other_product_image_locator_{idx}"
            attributes.append(
                {
                    "op": "replace",
                    "path": f"/attributes/{attr}",
                    "value": [{"media_location": image_url}],
                }
            )
        return attributes

    async def patch_listing_images(
        self,
        *,
        access_token: str,
        seller_id: str,
        sku: str,
        marketplace_id: str,
        image_urls: List[str],
    ) -> Dict[str, Any]:
        if not image_urls:
            raise AmazonSPAPIError("No image URLs provided for listing patch", status_code=400)

        path = f"/listings/2021-08-01/items/{seller_id}/{quote(sku, safe='')}"
        query = f"marketplaceIds={quote(marketplace_id, safe='')}&issueLocale=en_US"
        url = f"{self.endpoint}{path}?{query}"

        payload_obj = {
            "productType": "PRODUCT",
            "patches": self.build_listing_image_attributes(image_urls),
        }
        payload_bytes = json.dumps(payload_obj, separators=(",", ":")).encode("utf-8")

        headers = {
            "content-type": "application/json",
            "x-amz-access-token": access_token,
            "user-agent": "reddstudio-ai/1.0 (SP-API Listings Push)",
            "accept": "application/json",
        }
        signed_headers = self._sign_headers(
            method="PATCH",
            url=url,
            headers=headers,
            payload=payload_bytes,
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.patch(url, content=payload_bytes, headers=signed_headers)

        response_data: Any
        try:
            response_data = response.json()
        except Exception:
            response_data = {"raw": response.text}

        if response.status_code >= 400:
            logger.error(f"SP-API listing patch failed {response.status_code}: {response_data}")
            raise AmazonSPAPIError(
                "SP-API listing patch failed",
                status_code=response.status_code,
                details={"response": response_data},
            )

        submission_id = None
        if isinstance(response_data, dict):
            submission_id = (
                response_data.get("submissionId")
                or response_data.get("submission_id")
                or (response_data.get("payload") or {}).get("submissionId")
            )

        return {
            "status_code": response.status_code,
            "submission_id": submission_id,
            "response": response_data,
        }

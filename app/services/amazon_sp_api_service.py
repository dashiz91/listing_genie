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
from urllib.parse import quote, urlparse, parse_qsl, urlencode

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

    async def _signed_request(
        self,
        *,
        method: str,
        path: str,
        query_params: Optional[Dict[str, str]],
        access_token: str,
        payload_obj: Optional[Dict[str, Any]] = None,
        timeout_seconds: float = 60.0,
    ) -> Dict[str, Any]:
        query_string = urlencode(query_params or {}, doseq=True)
        url = f"{self.endpoint}{path}"
        if query_string:
            url = f"{url}?{query_string}"

        payload_bytes = b""
        headers: Dict[str, str] = {
            "x-amz-access-token": access_token,
            "user-agent": "reddstudio-ai/1.0 (SP-API)",
            "accept": "application/json",
        }
        if payload_obj is not None:
            payload_bytes = json.dumps(payload_obj, separators=(",", ":")).encode("utf-8")
            headers["content-type"] = "application/json"

        signed_headers = self._sign_headers(
            method=method,
            url=url,
            headers=headers,
            payload=payload_bytes,
        )

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.request(
                method.upper(),
                url,
                content=payload_bytes if payload_obj is not None else None,
                headers=signed_headers,
            )

        try:
            response_data: Any = response.json()
        except Exception:
            response_data = {"raw": response.text}

        if response.status_code >= 400:
            logger.error(f"SP-API request failed {response.status_code} {method} {path}: {response_data}")
            raise AmazonSPAPIError(
                "SP-API request failed",
                status_code=response.status_code,
                details={"response": response_data, "method": method.upper(), "path": path},
            )

        return {
            "status_code": response.status_code,
            "response": response_data,
        }

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
        payload_obj = {
            "productType": "PRODUCT",
            "patches": self.build_listing_image_attributes(image_urls),
        }
        result = await self._signed_request(
            method="PATCH",
            path=path,
            query_params={
                "marketplaceIds": marketplace_id,
                "issueLocale": "en_US",
            },
            access_token=access_token,
            payload_obj=payload_obj,
            timeout_seconds=60.0,
        )
        response_data = result["response"]

        submission_id = None
        if isinstance(response_data, dict):
            submission_id = (
                response_data.get("submissionId")
                or response_data.get("submission_id")
                or (response_data.get("payload") or {}).get("submissionId")
            )

        return {
            "status_code": result["status_code"],
            "submission_id": submission_id,
            "response": response_data,
        }

    async def search_listing_skus(
        self,
        *,
        access_token: str,
        seller_id: str,
        marketplace_id: str,
        query: Optional[str] = None,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        safe_page_size = max(1, min(page_size, 20))
        params: Dict[str, str] = {
            "marketplaceIds": marketplace_id,
            "includedData": "summaries",
            "issueLocale": "en_US",
            "pageSize": str(safe_page_size),
        }
        if query and query.strip():
            params["keywords"] = query.strip()

        result = await self._signed_request(
            method="GET",
            path=f"/listings/2021-08-01/items/{seller_id}",
            query_params=params,
            access_token=access_token,
            payload_obj=None,
            timeout_seconds=45.0,
        )
        payload = result["response"] if isinstance(result.get("response"), dict) else {}
        raw_items = payload.get("items") or []

        skus: List[Dict[str, Any]] = []
        seen = set()
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            sku = item.get("sku")
            if not sku or sku in seen:
                continue
            summaries = item.get("summaries") or []
            summary = summaries[0] if summaries and isinstance(summaries[0], dict) else {}
            asin = summary.get("asin")
            title = summary.get("itemName")
            status_value = summary.get("status")
            status = None
            if isinstance(status_value, list) and status_value:
                status = status_value[0]
            elif isinstance(status_value, str):
                status = status_value

            skus.append(
                {
                    "sku": sku,
                    "asin": asin,
                    "title": title,
                    "status": status,
                }
            )
            seen.add(sku)

        return {
            "skus": skus,
            "next_token": payload.get("nextToken"),
        }

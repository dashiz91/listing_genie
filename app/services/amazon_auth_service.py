"""
Amazon OAuth/LWA auth service.

Handles:
- OAuth authorization URL + state signing
- OAuth code -> refresh token exchange (LWA)
- Refresh token -> access token exchange (LWA)
- Per-user token storage and encryption
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from app.config import settings
from app.models.database import UserSettings

logger = logging.getLogger(__name__)


@dataclass
class AmazonConnection:
    refresh_token: str
    seller_id: Optional[str]
    marketplace_id: str
    mode: str  # env | oauth | manual
    connected_at: Optional[datetime]


class AmazonAuthService:
    """Amazon OAuth token orchestration and secure storage."""

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------------------
    # Token encryption helpers
    # ---------------------------------------------------------------------
    @staticmethod
    def _derive_fernet_key(source: str) -> bytes:
        digest = hashlib.sha256(source.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    def _get_fernet(self) -> Fernet:
        key_source = (settings.amazon_token_encryption_key or "").strip()
        if key_source:
            try:
                # Accept raw 44-char Fernet key if provided.
                return Fernet(key_source.encode("utf-8"))
            except Exception:
                logger.warning("amazon_token_encryption_key is not a valid Fernet key, deriving from provided value")
                return Fernet(self._derive_fernet_key(key_source))

        # Fallback: derive from app secret key.
        return Fernet(self._derive_fernet_key(settings.secret_key))

    def encrypt_refresh_token(self, refresh_token: str) -> str:
        token = self._get_fernet().encrypt(refresh_token.encode("utf-8"))
        return token.decode("utf-8")

    def decrypt_refresh_token(self, encrypted_token: str) -> str:
        plain = self._get_fernet().decrypt(encrypted_token.encode("utf-8"))
        return plain.decode("utf-8")

    # ---------------------------------------------------------------------
    # OAuth state signing
    # ---------------------------------------------------------------------
    @staticmethod
    def _b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    @staticmethod
    def _b64url_decode(data: str) -> bytes:
        padding = "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + padding)

    def create_signed_state(
        self,
        *,
        user_id: str,
        marketplace_id: str,
        return_to: str,
        expires_in_seconds: int = 600,
    ) -> str:
        now = int(time.time())
        payload = {
            "uid": user_id,
            "mp": marketplace_id,
            "rt": return_to,
            "iat": now,
            "exp": now + expires_in_seconds,
        }
        payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        payload_b64 = self._b64url_encode(payload_bytes)
        sig = hmac.new(
            settings.secret_key.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        sig_b64 = self._b64url_encode(sig)
        return f"{payload_b64}.{sig_b64}"

    def verify_signed_state(self, state: str) -> Dict[str, Any]:
        try:
            payload_b64, sig_b64 = state.split(".", 1)
        except ValueError as exc:
            raise ValueError("Invalid state format") from exc

        expected_sig = hmac.new(
            settings.secret_key.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        actual_sig = self._b64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Invalid state signature")

        payload_raw = self._b64url_decode(payload_b64)
        payload = json.loads(payload_raw.decode("utf-8"))
        now = int(time.time())
        if payload.get("exp", 0) < now:
            raise ValueError("State expired")
        return payload

    # ---------------------------------------------------------------------
    # Connection storage
    # ---------------------------------------------------------------------
    def _get_or_create_settings(self, user_id: str) -> UserSettings:
        row = self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if not row:
            row = UserSettings(user_id=user_id)
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
        return row

    def save_connection(
        self,
        *,
        user_id: str,
        refresh_token: str,
        seller_id: Optional[str],
        marketplace_id: Optional[str],
        email: Optional[str] = None,
    ) -> None:
        row = self._get_or_create_settings(user_id)
        row.amazon_refresh_token_encrypted = self.encrypt_refresh_token(refresh_token)
        row.amazon_seller_id = seller_id
        row.amazon_marketplace_id = marketplace_id or settings.amazon_default_marketplace_id
        row.amazon_connected_at = datetime.now(timezone.utc)
        if email and not row.email:
            row.email = email.lower().strip()
        self.db.commit()

    def disconnect(self, user_id: str) -> None:
        row = self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if not row:
            return
        row.amazon_refresh_token_encrypted = None
        row.amazon_seller_id = None
        row.amazon_marketplace_id = None
        row.amazon_connected_at = None
        self.db.commit()

    def get_connection(self, user_id: str) -> Optional[AmazonConnection]:
        # Highest precedence: env-configured connection (fast internal testing path).
        env_refresh = (settings.amazon_spapi_refresh_token or "").strip()
        if env_refresh:
            return AmazonConnection(
                refresh_token=env_refresh,
                seller_id=(settings.amazon_spapi_seller_id or "").strip() or None,
                marketplace_id=(settings.amazon_spapi_marketplace_id or "").strip() or settings.amazon_default_marketplace_id,
                mode="env",
                connected_at=None,
            )

        row = self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if not row or not row.amazon_refresh_token_encrypted:
            return None

        try:
            refresh_token = self.decrypt_refresh_token(row.amazon_refresh_token_encrypted)
        except Exception as exc:
            logger.error(f"Failed to decrypt Amazon refresh token for user {user_id}: {exc}")
            return None

        return AmazonConnection(
            refresh_token=refresh_token,
            seller_id=row.amazon_seller_id,
            marketplace_id=row.amazon_marketplace_id or settings.amazon_default_marketplace_id,
            mode="oauth",
            connected_at=row.amazon_connected_at,
        )

    def get_auth_status(self, user_id: str) -> Dict[str, Any]:
        conn = self.get_connection(user_id)
        if not conn:
            return {
                "connected": False,
                "seller_id": None,
                "marketplace_id": settings.amazon_default_marketplace_id,
                "connection_mode": "none",
                "last_connected_at": None,
            }
        return {
            "connected": True,
            "seller_id": conn.seller_id,
            "marketplace_id": conn.marketplace_id,
            "connection_mode": conn.mode,
            "last_connected_at": conn.connected_at.isoformat() if conn.connected_at else None,
        }

    # ---------------------------------------------------------------------
    # OAuth/LWA network calls
    # ---------------------------------------------------------------------
    def build_authorization_url(
        self,
        *,
        user_id: str,
        marketplace_id: Optional[str],
        return_to: Optional[str],
    ) -> Dict[str, Any]:
        if not settings.amazon_spapi_app_id:
            raise ValueError("amazon_spapi_app_id is not configured")
        if not settings.amazon_oauth_redirect_uri:
            raise ValueError("amazon_oauth_redirect_uri is not configured")

        chosen_marketplace = marketplace_id or settings.amazon_default_marketplace_id
        safe_return_to = return_to or "/app/settings"
        state = self.create_signed_state(
            user_id=user_id,
            marketplace_id=chosen_marketplace,
            return_to=safe_return_to,
            expires_in_seconds=600,
        )

        params = {
            "application_id": settings.amazon_spapi_app_id,
            "state": state,
            "redirect_uri": settings.amazon_oauth_redirect_uri,
        }
        if settings.amazon_oauth_version:
            params["version"] = settings.amazon_oauth_version

        auth_url = f"{settings.amazon_authorization_base_url}?{urlencode(params)}"
        return {
            "auth_url": auth_url,
            "state": state,
            "expires_in_seconds": 600,
        }

    async def exchange_code_for_refresh_token(self, oauth_code: str) -> Dict[str, Any]:
        if not settings.amazon_lwa_client_id or not settings.amazon_lwa_client_secret:
            raise ValueError("Amazon LWA client credentials are not configured")
        if not settings.amazon_oauth_redirect_uri:
            raise ValueError("amazon_oauth_redirect_uri is not configured")

        form = {
            "grant_type": "authorization_code",
            "code": oauth_code,
            "client_id": settings.amazon_lwa_client_id,
            "client_secret": settings.amazon_lwa_client_secret,
            "redirect_uri": settings.amazon_oauth_redirect_uri,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.amazon_lwa_token_url,
                data=form,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        if response.status_code >= 400:
            raise ValueError(f"LWA token exchange failed ({response.status_code}): {response.text}")

        payload = response.json()
        refresh_token = payload.get("refresh_token")
        access_token = payload.get("access_token")
        if not refresh_token:
            raise ValueError("LWA response did not include refresh_token")
        return {
            "refresh_token": refresh_token,
            "access_token": access_token,
            "expires_in": payload.get("expires_in"),
            "token_type": payload.get("token_type"),
            "scope": payload.get("scope"),
        }

    async def refresh_access_token(self, refresh_token: str) -> str:
        if not settings.amazon_lwa_client_id or not settings.amazon_lwa_client_secret:
            raise ValueError("Amazon LWA client credentials are not configured")

        form = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.amazon_lwa_client_id,
            "client_secret": settings.amazon_lwa_client_secret,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.amazon_lwa_token_url,
                data=form,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        if response.status_code >= 400:
            raise ValueError(f"LWA refresh failed ({response.status_code}): {response.text}")

        payload = response.json()
        access_token = payload.get("access_token")
        if not access_token:
            raise ValueError("LWA refresh response did not include access_token")
        return access_token

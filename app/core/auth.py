"""
Supabase JWT Authentication for FastAPI

Validates JWTs issued by Supabase Auth using JWKS (JSON Web Key Set) verification.
Supports both modern ES256 (ECC) and legacy HS256 tokens.
"""
import logging
from typing import Optional
from functools import lru_cache
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)

# Cache for JWKS client (refreshes keys every 5 minutes)
_jwks_client: Optional[PyJWKClient] = None
_jwks_client_created_at: float = 0
JWKS_CACHE_TTL = 300  # 5 minutes


class User(BaseModel):
    """Authenticated user from Supabase JWT"""
    id: str  # Supabase user UUID
    email: Optional[str] = None
    role: str = "authenticated"


def get_jwks_client() -> Optional[PyJWKClient]:
    """
    Get or create a cached JWKS client for Supabase token verification.
    The client automatically fetches and caches public keys from Supabase.
    """
    global _jwks_client, _jwks_client_created_at

    if not settings.supabase_url:
        return None

    # Refresh client if cache expired
    now = time.time()
    if _jwks_client is None or (now - _jwks_client_created_at) > JWKS_CACHE_TTL:
        jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
        try:
            # Supabase JWKS endpoint requires apikey header
            headers = {"apikey": settings.supabase_anon_key} if settings.supabase_anon_key else {}
            _jwks_client = PyJWKClient(jwks_url, cache_keys=True, headers=headers)
            _jwks_client_created_at = now
            logger.info(f"JWKS client initialized from {jwks_url}")
        except Exception as e:
            logger.error(f"Failed to initialize JWKS client: {e}")
            return None

    return _jwks_client


def verify_supabase_token(token: str) -> Optional[dict]:
    """
    Verify a Supabase JWT token using JWKS (recommended) or legacy HS256 secret.

    Verification order:
    1. Try JWKS verification (ES256/RS256) - modern Supabase default
    2. Fall back to HS256 with JWT secret if configured
    3. Development only: decode without verification if nothing configured
    """
    # First, try JWKS verification (modern approach)
    jwks_client = get_jwks_client()
    if jwks_client:
        try:
            # Get the signing key from JWKS
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # Verify and decode the token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "RS256"],  # Support both ECC and RSA
                audience="authenticated",
            )
            logger.debug("Token verified successfully via JWKS")
            return payload
        except jwt.exceptions.PyJWKClientError as e:
            logger.debug(f"JWKS verification failed, trying fallback: {e}")
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.debug(f"JWKS token validation failed: {e}")

    # Fallback: try HS256 with legacy JWT secret
    if settings.supabase_jwt_secret:
        try:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
            logger.debug("Token verified successfully via HS256 secret")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"HS256 token validation failed: {e}")
            return None

    # Development fallback: decode without verification
    if settings.app_env == "development":
        logger.warning("No JWKS or JWT secret - decoding without verification (dev only)")
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token decode failed: {e}")
            return None

    logger.error("No verification method available and not in development mode")
    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    FastAPI dependency to get the current authenticated user.

    Usage:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_supabase_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user info from Supabase JWT payload
    user_id = payload.get("sub")  # Supabase uses 'sub' for user ID
    email = payload.get("email")
    role = payload.get("role", "authenticated")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check email whitelist (if configured)
    # "*" means allow all, empty string means allow all
    if settings.allowed_emails and settings.allowed_emails.strip() != "*":
        allowed_list = [e.strip().lower() for e in settings.allowed_emails.split(",") if e.strip()]
        if allowed_list and (not email or email.lower() not in allowed_list):
            logger.warning(f"Access denied for email: {email} (not in whitelist)")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access restricted. Your account is not authorized.",
            )

    return User(id=user_id, email=email, role=role)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[User]:
    """
    FastAPI dependency to get the current user if authenticated, None otherwise.

    Use this for endpoints that work for both authenticated and anonymous users.
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

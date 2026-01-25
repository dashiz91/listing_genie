"""
Supabase JWT Authentication for FastAPI

Validates JWTs issued by Supabase Auth and extracts user information.
"""
import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


class User(BaseModel):
    """Authenticated user from Supabase JWT"""
    id: str  # Supabase user UUID
    email: Optional[str] = None
    role: str = "authenticated"


def verify_supabase_token(token: str) -> Optional[dict]:
    """
    Verify a Supabase JWT token.

    Supabase uses RS256 by default, but for simplicity we can use the JWT secret
    with HS256 if configured. In production, you should verify against Supabase's
    public key.
    """
    try:
        # Supabase JWTs can be verified with the JWT secret
        if not settings.supabase_jwt_secret:
            # Fallback: decode without verification (development only)
            logger.warning("No SUPABASE_JWT_SECRET configured - decoding without verification")
            payload = jwt.decode(token, options={"verify_signature": False})
        else:
            # Verify with the JWT secret
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )

        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
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

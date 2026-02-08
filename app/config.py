from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "listing-genie"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = "dev-secret-key-change-in-production"

    # API
    api_prefix: str = "/api"
    # Backend URL for generating absolute image URLs (set in production/staging)
    # If empty, relative URLs are used (works for same-origin setups)
    backend_url: str = ""  # e.g., "https://reddstudio-staging-backend-staging.up.railway.app"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        # Production
        "https://reddstudio.ai",
        "https://www.reddstudio.ai",
        "https://frontend-weld-kappa-94.vercel.app",
        # Staging
        "https://staging.reddstudio.ai",
        # Vercel preview deployments
        "https://frontend-*-redds-projects-be5739a8.vercel.app",
    ]

    # Account lockdown - comma-separated list of allowed emails
    # Empty = allow all (for when credits system is ready)
    allowed_emails: str = ""  # e.g., "robertoxma@hotmail.com,another@email.com"

    # Admin emails - comma-separated list of emails with unlimited credits
    # These users bypass all credit checks
    admin_emails: str = ""

    # Gemini (Story 2.1)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-pro-image-preview"  # For image GENERATION
    gemini_vision_model: str = "gemini-3-flash-preview"  # For vision ANALYSIS (Principal Designer)

    # Vision Provider Selection:
    # - "gemini" (default and recommended)
    # - "openai" (deprecated; requires allow_openai_vision=true)
    vision_provider: str = "gemini"
    # Emergency override: enable deprecated OpenAI vision provider only when needed
    allow_openai_vision: bool = False

    # OpenAI Vision (deprecated emergency backup only)
    openai_api_key: str = ""
    openai_vision_model: str = "gpt-4o"  # Latest vision model

    # Storage (Story 1.3)
    storage_type: str = "local"  # "local" or "supabase"
    storage_path: str = "./storage"  # For local storage

    # Supabase Storage buckets
    supabase_uploads_bucket: str = "uploads"
    supabase_generated_bucket: str = "generated"

    # Database (Story 1.2)
    database_url: str = "sqlite:///./listing_genie.db"

    # Feature Flags
    enable_payment: bool = False  # Deferred to Phase 2

    # Logging
    log_level: str = "INFO"

    # Supabase Auth
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""  # For server-side operations
    supabase_jwt_secret: str = ""  # For JWT verification

    # Frontend URL (used for OAuth callback redirects)
    frontend_url: str = "http://localhost:5173"

    # Amazon Selling Partner API (SP-API)
    amazon_lwa_client_id: str = ""
    amazon_lwa_client_secret: str = ""
    amazon_oauth_redirect_uri: str = ""
    amazon_spapi_app_id: str = ""  # amzn1.sellerapps.app.*
    amazon_authorization_base_url: str = "https://sellercentral.amazon.com/apps/authorize/consent"
    amazon_lwa_token_url: str = "https://api.amazon.com/auth/o2/token"
    amazon_oauth_version: str = ""  # e.g. "beta" for draft app auth flow

    # SP-API endpoint/region + AWS signing credentials
    amazon_spapi_endpoint: str = "https://sellingpartnerapi-na.amazon.com"
    amazon_spapi_region: str = "us-east-1"
    amazon_aws_access_key_id: str = ""
    amazon_aws_secret_access_key: str = ""
    amazon_aws_session_token: str = ""

    # Default marketplace (US)
    amazon_default_marketplace_id: str = "ATVPDKIKX0DER"

    # Optional env-based direct connection (for rapid internal testing).
    # Disabled by default so each user must connect their own Seller Central account.
    amazon_allow_env_connection: bool = False
    amazon_spapi_refresh_token: str = ""
    amazon_spapi_seller_id: str = ""
    amazon_spapi_marketplace_id: str = ""

    # Optional encryption key for stored refresh tokens (Fernet key preferred)
    amazon_token_encryption_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

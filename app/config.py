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

    # Gemini (Story 2.1)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-pro-image-preview"  # For image GENERATION
    gemini_vision_model: str = "gemini-3-flash-preview"  # For vision ANALYSIS (Principal Designer)

    # Vision Provider Selection: "gemini" (recommended - 10x cheaper) or "openai"
    vision_provider: str = "gemini"

    # OpenAI (Fallback for Vision Analysis)
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

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

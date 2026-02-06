from fastapi import APIRouter
from app.api.endpoints import health, generation, upload, images, projects, assets, settings, asin, admin, styles, amazon

api_router = APIRouter(prefix="/api")

# Health check endpoints
api_router.include_router(health.router, tags=["health"])

# Generation endpoints
api_router.include_router(
    generation.router,
    prefix="/generate",
    tags=["generation"]
)

# Upload endpoints
api_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["upload"]
)

# Image serving endpoints
api_router.include_router(
    images.router,
    prefix="/images",
    tags=["images"]
)

# Projects endpoints
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"]
)

# Assets endpoints
api_router.include_router(
    assets.router,
    prefix="/assets",
    tags=["assets"]
)

# Settings endpoints
api_router.include_router(
    settings.router,
    prefix="/settings",
    tags=["settings"]
)

# ASIN import endpoints
api_router.include_router(
    asin.router,
    prefix="/asin",
    tags=["asin"]
)

# Admin endpoints (credit management, user lookup)
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)

# Style library endpoints (free, no auth required)
api_router.include_router(
    styles.router,
    tags=["styles"]
)

# Amazon SP-API endpoints
api_router.include_router(
    amazon.router,
    prefix="/amazon",
    tags=["amazon"]
)

from fastapi import APIRouter
from app.api.endpoints import health, generation, upload, images, projects

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

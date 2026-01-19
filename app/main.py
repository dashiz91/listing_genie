from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.middleware import LoggingMiddleware, ErrorHandlerMiddleware, SecurityHeadersMiddleware
from app.config import settings
from app.db.session import init_db
import logging

# Initialize logging
from app.core import logging_config  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="Listing Genie API",
    description="AI-powered Amazon listing image generator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware (order matters - first added = outermost)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Include API routes
app.include_router(api_router)


@app.get("/health")
async def root_health_check():
    """
    Basic health check at root level.
    Used by container orchestrators and load balancers.
    """
    return {
        "status": "healthy",
        "service": "listing-genie",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint - redirect to docs or serve frontend in production"""
    return {
        "message": "Welcome to Listing Genie API",
        "docs": "/docs",
        "health": "/health"
    }

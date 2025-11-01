"""
FastAPI application for OCR and document parsing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.routers import ocr, document_parser, corroboration, alerts
from backend.config import settings

# Import infrastructure components
from backend.database import init_db, close_db
from backend.cache import init_cache, close_cache
from backend.logging import configure_logging, LoggingMiddleware, get_logger

# Configure logging before any other imports
configure_logging(
    level=getattr(settings, "LOG_LEVEL", "INFO"),
    json_output=not settings.TESTING,  # Console output for testing
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("application_starting", version=settings.VERSION)

    # Initialize database connection pool
    logger.info("database_initializing")
    try:
        await init_db()
        logger.info("database_connected")
    except Exception as e:
        logger.warning(
            "database_connection_failed",
            error=str(e),
            fallback="continuing_without_database",
        )

    # Initialize cache (Redis or in-memory fallback)
    logger.info("cache_initializing")
    try:
        await init_cache()
        logger.info("cache_connected")
    except Exception as e:
        logger.warning(
            "cache_initialization_failed",
            error=str(e),
            fallback="continuing_without_cache",
        )

    logger.info("application_ready", version=settings.VERSION)

    yield

    # Shutdown
    logger.info("application_shutting_down")

    # Close cache connections
    try:
        await close_cache()
        logger.info("cache_closed")
    except Exception as e:
        logger.error("cache_close_error", error=str(e))

    # Close database connections
    try:
        await close_db()
        logger.info("database_closed")
    except Exception as e:
        logger.error("database_close_error", error=str(e))

    logger.info("application_shutdown_complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API for OCR and document parsing operations",
    lifespan=lifespan,
)

# Add logging middleware (first, to log all requests)
app.add_middleware(LoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(document_parser.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(corroboration.router, prefix="/api/v1/corroboration", tags=["Corroboration"])
app.include_router(alerts.router)  # Alert router has its own prefix defined


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FastAPI OCR and Document Parsing API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint with infrastructure status.

    Returns status of database, cache, and overall application health.
    """
    from backend.database.connection import check_db_health
    from backend.cache import cache_manager

    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "database": "unknown",
        "cache": "unknown",
    }

    # Check database health
    try:
        db_healthy = await check_db_health()
        health_status["database"] = "connected" if db_healthy else "disconnected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"

    # Check cache health
    try:
        cache_healthy = await cache_manager.health_check()
        health_status["cache"] = "connected" if cache_healthy else "disconnected"
    except Exception as e:
        health_status["cache"] = f"error: {str(e)}"

    # Overall status
    if health_status["database"] != "connected" or health_status["cache"] != "connected":
        health_status["status"] = "degraded"

    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

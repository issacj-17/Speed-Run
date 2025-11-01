"""
FastAPI application for OCR and document parsing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.routers import ocr, document_parser, corroboration
from backend.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("🚀 Starting FastAPI application...")
    yield
    # Shutdown
    print("👋 Shutting down FastAPI application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API for OCR and document parsing operations",
    lifespan=lifespan,
)

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
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

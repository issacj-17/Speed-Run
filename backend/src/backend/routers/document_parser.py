"""Document parsing API endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any

from backend.services.document_service import DocumentService
from backend.schemas.document import DocumentParseResponse
from backend.config import settings

router = APIRouter()
document_service = DocumentService()


@router.post("/parse", response_model=DocumentParseResponse)
async def parse_document(
    file: UploadFile = File(..., description="Document file to parse"),
):
    """
    Parse a document and extract text, tables, and metadata.

    Supports formats: PDF, DOCX, images (PNG, JPG, etc.)

    Args:
        file: Document file to process

    Returns:
        DocumentParseResponse with extracted content and metadata
    """
    # Validate file extension
    file_ext = f".{file.filename.split('.')[-1].lower()}"
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )

    try:
        result = await document_service.parse_document_bytes(
            file_bytes=contents,
            filename=file.filename,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-tables", response_model=List[Dict[str, Any]])
async def extract_tables(
    file: UploadFile = File(..., description="Document file to extract tables from"),
):
    """
    Extract only tables from a document.

    Supports formats: PDF, DOCX

    Args:
        file: Document file to process

    Returns:
        List of tables as JSON objects
    """
    # Validate file extension
    file_ext = f".{file.filename.split('.')[-1].lower()}"
    if file_ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type for table extraction. Allowed: ['.pdf', '.docx']"
        )

    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )

    try:
        # Create temporary file for processing
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(contents)
            tmp_path = Path(tmp_file.name)

        try:
            tables = await document_service.extract_tables(tmp_path)
            return tables
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def document_parser_health_check():
    """Check if document parsing service is operational."""
    return {
        "status": "healthy",
        "service": "Document Parser",
        "engine": "docling",
        "supported_formats": settings.ALLOWED_EXTENSIONS
    }

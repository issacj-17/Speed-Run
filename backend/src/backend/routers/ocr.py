"""OCR API endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.services.ocr_service import OCRService
from backend.schemas.ocr import OCRResponse
from backend.config import settings

router = APIRouter()
ocr_service = OCRService()


@router.post("/extract", response_model=OCRResponse)
async def extract_text_from_image(
    file: UploadFile = File(..., description="Image file for OCR"),
):
    """
    Extract text from an image using OCR.

    Assumes all documents are in English.
    Supports formats: PNG, JPG, JPEG, TIFF, BMP

    Args:
        file: Image file to process

    Returns:
        OCRResponse with extracted text and metadata
    """
    # Validate file extension
    file_ext = f".{file.filename.split('.')[-1].lower()}"
    if file_ext not in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {['.png', '.jpg', '.jpeg', '.tiff', '.bmp']}"
        )

    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )

    try:
        result = await ocr_service.process_image_bytes(
            file_bytes=contents,
            filename=file.filename,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def ocr_health_check():
    """Check if OCR service is operational."""
    return {
        "status": "healthy",
        "service": "OCR",
        "engine": "docling"
    }

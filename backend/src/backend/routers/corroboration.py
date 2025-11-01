"""Document and image corroboration API endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import PlainTextResponse
from typing import Optional, List, Dict, Any
import json

from backend.services.corroboration_service import CorroborationService
from backend.schemas.validation import (
    CorroborationReport,
    CorroborationRequest,
    ImageAnalysisResult,
)
from backend.config import settings

router = APIRouter()
corroboration_service = CorroborationService()


@router.post("/analyze", response_model=CorroborationReport)
async def analyze_document(
    file: UploadFile = File(..., description="Document or image file to analyze"),
    perform_format_validation: bool = Form(default=True, description="Enable format validation"),
    perform_structure_validation: bool = Form(default=True, description="Enable structure validation"),
    perform_content_validation: bool = Form(default=True, description="Enable content validation"),
    perform_image_analysis: bool = Form(default=True, description="Enable image analysis"),
    expected_document_type: Optional[str] = Form(default=None, description="Expected document type (e.g., 'invoice', 'contract')"),
    enable_reverse_image_search: bool = Form(default=False, description="Enable reverse image search"),
    risk_threshold: float = Form(default=50.0, description="Risk score threshold for flagging (0-100)"),
):
    """
    Perform comprehensive document corroboration analysis.

    Supports:
    - Format validation (spelling, spacing, formatting)
    - Structure validation (completeness, template matching)
    - Content validation (quality, PII detection)
    - Image analysis (authenticity, AI detection, tampering)

    Returns detailed risk assessment and recommendations.
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

    # Create request object
    request = CorroborationRequest(
        perform_format_validation=perform_format_validation,
        perform_structure_validation=perform_structure_validation,
        perform_content_validation=perform_content_validation,
        perform_image_analysis=perform_image_analysis,
        expected_document_type=expected_document_type,
        enable_reverse_image_search=enable_reverse_image_search,
        risk_threshold=risk_threshold,
    )

    try:
        report = await corroboration_service.analyze_document(
            file_bytes=contents,
            filename=file.filename,
            request=request,
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-image", response_model=ImageAnalysisResult)
async def analyze_image_only(
    file: UploadFile = File(..., description="Image file to analyze"),
    enable_reverse_search: bool = Form(default=False, description="Enable reverse image search"),
):
    """
    Perform image-only analysis for authenticity verification.

    Checks:
    - AI-generated detection
    - Tampering detection (ELA analysis)
    - EXIF metadata validation
    - Forensic analysis
    - Reverse image search (optional)

    Returns detailed image analysis results.
    """
    # Validate file extension
    file_ext = f".{file.filename.split('.')[-1].lower()}"
    if file_ext not in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type. Allowed: ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']"
        )

    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )

    try:
        result = await corroboration_service.analyze_image_only(
            file_bytes=contents,
            filename=file.filename,
            enable_reverse_search=enable_reverse_search,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")


@router.get("/report/{document_id}", response_model=CorroborationReport)
async def get_report(document_id: str):
    """
    Retrieve a previously generated corroboration report.

    Args:
        document_id: Unique document identifier from analysis

    Returns:
        Complete corroboration report with all findings
    """
    report = await corroboration_service.get_report(document_id)

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report not found for document_id: {document_id}"
        )

    return report


@router.get("/report/{document_id}/markdown", response_class=PlainTextResponse)
async def get_report_markdown(document_id: str):
    """
    Retrieve a report in markdown format.

    Args:
        document_id: Unique document identifier

    Returns:
        Markdown formatted report
    """
    markdown = await corroboration_service.export_report_markdown(document_id)

    if not markdown:
        raise HTTPException(
            status_code=404,
            detail=f"Report not found for document_id: {document_id}"
        )

    return markdown


@router.get("/reports", response_model=List[Dict[str, Any]])
async def list_reports(
    limit: int = 100,
    risk_level: Optional[str] = None,
    requires_manual_review: Optional[bool] = None,
):
    """
    List corroboration reports with optional filtering.

    Args:
        limit: Maximum number of reports to return (default: 100)
        risk_level: Filter by risk level (low, medium, high, critical)
        requires_manual_review: Filter by manual review requirement (true/false)

    Returns:
        List of report summaries
    """
    if risk_level and risk_level.lower() not in ['low', 'medium', 'high', 'critical']:
        raise HTTPException(
            status_code=400,
            detail="Invalid risk_level. Must be one of: low, medium, high, critical"
        )

    try:
        reports = await corroboration_service.list_reports(
            limit=limit,
            risk_level=risk_level,
            requires_manual_review=requires_manual_review,
        )
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@router.post("/validate-format")
async def validate_format_only(
    file: UploadFile = File(..., description="Document file to validate"),
):
    """
    Perform format validation only (quick check).

    Checks for:
    - Double spacing issues
    - Font inconsistencies
    - Indentation problems
    - Spelling errors

    Faster than full analysis, useful for pre-screening.
    """
    file_ext = f".{file.filename.split('.')[-1].lower()}"

    if file_ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type for format validation"
        )

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )

    # Create minimal request for format validation only
    request = CorroborationRequest(
        perform_format_validation=True,
        perform_structure_validation=False,
        perform_content_validation=False,
        perform_image_analysis=False,
    )

    try:
        report = await corroboration_service.analyze_document(
            file_bytes=contents,
            filename=file.filename,
            request=request,
        )
        return {"format_validation": report.format_validation, "risk_score": report.risk_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Format validation failed: {str(e)}")


@router.post("/validate-structure")
async def validate_structure_only(
    file: UploadFile = File(..., description="Document file to validate"),
    expected_document_type: Optional[str] = Form(default=None, description="Expected document type"),
):
    """
    Perform structure validation only (quick check).

    Checks for:
    - Document completeness
    - Missing sections
    - Template matching
    - Header formatting

    Useful for verifying document structure before full analysis.
    """
    file_ext = f".{file.filename.split('.')[-1].lower()}"

    if file_ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type for structure validation"
        )

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )

    # Create minimal request for structure validation only
    request = CorroborationRequest(
        perform_format_validation=False,
        perform_structure_validation=True,
        perform_content_validation=False,
        perform_image_analysis=False,
        expected_document_type=expected_document_type,
    )

    try:
        report = await corroboration_service.analyze_document(
            file_bytes=contents,
            filename=file.filename,
            request=request,
        )
        return {"structure_validation": report.structure_validation, "risk_score": report.risk_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Structure validation failed: {str(e)}")


@router.get("/health")
async def corroboration_health_check():
    """Check if corroboration service is operational."""
    return {
        "status": "healthy",
        "service": "Document Corroboration",
        "features": [
            "format_validation",
            "structure_validation",
            "content_validation",
            "image_analysis",
            "risk_scoring",
            "audit_trails"
        ]
    }

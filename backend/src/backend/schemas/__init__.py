"""Pydantic schemas for request/response models."""

from backend.schemas.ocr import OCRResponse, OCRRequest
from backend.schemas.document import DocumentParseResponse, DocumentMetadata
from backend.schemas.validation import (
    CorroborationReport,
    CorroborationRequest,
    ValidationIssue,
    ValidationSeverity,
    FormatValidationResult,
    StructureValidationResult,
    ContentValidationResult,
    ImageAnalysisResult,
    RiskScore,
)

__all__ = [
    "OCRResponse",
    "OCRRequest",
    "DocumentParseResponse",
    "DocumentMetadata",
    "CorroborationReport",
    "CorroborationRequest",
    "ValidationIssue",
    "ValidationSeverity",
    "FormatValidationResult",
    "StructureValidationResult",
    "ContentValidationResult",
    "ImageAnalysisResult",
    "RiskScore",
]

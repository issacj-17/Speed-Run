"""Document and image validation schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationIssue(BaseModel):
    """Individual validation issue found in document."""

    category: str = Field(description="Category of the issue (e.g., 'formatting', 'content', 'structure')")
    severity: ValidationSeverity = Field(description="Severity level of the issue")
    description: str = Field(description="Human-readable description of the issue")
    location: Optional[str] = Field(None, description="Location in document where issue was found")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details about the issue")


class FormatValidationResult(BaseModel):
    """Results from format validation checks."""

    has_double_spacing: bool = Field(description="Whether document has irregular double spacing")
    has_font_inconsistencies: bool = Field(description="Whether fonts are inconsistent")
    has_indentation_issues: bool = Field(description="Whether indentation is irregular")
    has_spelling_errors: bool = Field(description="Whether spelling errors were detected")
    spelling_error_count: int = Field(default=0, description="Number of spelling errors")
    issues: List[ValidationIssue] = Field(default=[], description="List of formatting issues found")


class StructureValidationResult(BaseModel):
    """Results from document structure validation."""

    is_complete: bool = Field(description="Whether document appears complete")
    missing_sections: List[str] = Field(default=[], description="List of expected sections that are missing")
    has_correct_headers: bool = Field(description="Whether headers match expected format")
    template_match_score: float = Field(
        ge=0.0, le=1.0,
        description="How well document matches expected template (0-1)"
    )
    issues: List[ValidationIssue] = Field(default=[], description="List of structure issues found")


class ImageAnalysisResult(BaseModel):
    """Results from image authenticity analysis."""

    is_authentic: bool = Field(description="Whether image appears authentic")
    is_ai_generated: bool = Field(description="Whether image appears to be AI-generated")
    ai_detection_confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score for AI detection (0-1)"
    )
    is_tampered: bool = Field(description="Whether image shows signs of tampering")
    tampering_confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score for tampering detection (0-1)"
    )
    reverse_image_matches: int = Field(
        default=0,
        description="Number of matches found in reverse image search"
    )
    metadata_issues: List[ValidationIssue] = Field(
        default=[],
        description="Issues found in image metadata"
    )
    forensic_findings: List[ValidationIssue] = Field(
        default=[],
        description="Forensic analysis findings"
    )


class ContentValidationResult(BaseModel):
    """Results from content validation."""

    has_sensitive_data: bool = Field(description="Whether document contains sensitive/PII data")
    quality_score: float = Field(
        ge=0.0, le=1.0,
        description="Overall content quality score (0-1)"
    )
    readability_score: float = Field(
        ge=0.0, le=100.0,
        description="Flesch reading ease score"
    )
    word_count: int = Field(description="Total word count")
    issues: List[ValidationIssue] = Field(default=[], description="Content-related issues")


class RiskScore(BaseModel):
    """Risk scoring for document/image."""

    overall_score: float = Field(
        ge=0.0, le=100.0,
        description="Overall risk score (0=low risk, 100=high risk)"
    )
    risk_level: ValidationSeverity = Field(description="Categorized risk level")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in the risk assessment (0-1)"
    )
    contributing_factors: List[Dict[str, Any]] = Field(
        default=[],
        description="Factors that contributed to the risk score"
    )
    recommendations: List[str] = Field(
        default=[],
        description="Recommended actions based on risk assessment"
    )


class CorroborationReport(BaseModel):
    """Comprehensive corroboration report."""

    document_id: str = Field(description="Unique identifier for the document")
    file_name: str = Field(description="Original file name")
    file_type: str = Field(description="File type/extension")
    analysis_timestamp: datetime = Field(description="When the analysis was performed")

    # Validation results
    format_validation: Optional[FormatValidationResult] = None
    structure_validation: Optional[StructureValidationResult] = None
    content_validation: Optional[ContentValidationResult] = None
    image_analysis: Optional[ImageAnalysisResult] = None

    # Risk assessment
    risk_score: RiskScore = Field(description="Overall risk assessment")

    # Processing metadata
    processing_time: float = Field(description="Total processing time in seconds")
    engines_used: List[str] = Field(
        default=[],
        description="List of analysis engines used"
    )

    # Summary
    total_issues_found: int = Field(description="Total number of issues across all validations")
    critical_issues_count: int = Field(description="Number of critical issues")
    requires_manual_review: bool = Field(description="Whether document requires manual review")


class CorroborationRequest(BaseModel):
    """Request parameters for document corroboration."""

    perform_format_validation: bool = Field(default=True, description="Enable format validation")
    perform_structure_validation: bool = Field(default=True, description="Enable structure validation")
    perform_content_validation: bool = Field(default=True, description="Enable content validation")
    perform_image_analysis: bool = Field(default=True, description="Enable image analysis")

    expected_document_type: Optional[str] = Field(
        None,
        description="Expected document type for template matching (e.g., 'invoice', 'contract')"
    )
    enable_reverse_image_search: bool = Field(
        default=True,
        description="Enable reverse image search for authenticity verification"
    )
    risk_threshold: float = Field(
        default=50.0,
        ge=0.0, le=100.0,
        description="Risk score threshold for flagging (0-100)"
    )

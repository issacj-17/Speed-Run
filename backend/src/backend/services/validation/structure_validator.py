"""
Structure validation service.

Single Responsibility: Validate document structure (sections, headers, completeness).
"""

import re
from pathlib import Path
from typing import List, Dict, Optional

from backend.schemas.validation import (
    StructureValidationResult,
    ValidationIssue,
    ValidationSeverity,
)
from backend.logging import get_logger

logger = get_logger(__name__)


class StructureValidationService:
    """
    Service for validating document structure.

    Responsibilities:
    - Check for missing sections
    - Validate section headers
    - Verify document completeness
    - Calculate template matching scores
    """

    # Document templates with expected sections
    TEMPLATES: Dict[str, List[str]] = {
        "invoice": ["Invoice", "Date", "Amount", "Description", "Total"],
        "contract": ["Parties", "Terms", "Conditions", "Signatures", "Date"],
        "report": ["Executive Summary", "Introduction", "Methodology", "Results", "Conclusion"],
        "letter": ["Date", "Recipient", "Body", "Signature"],
        "financial_statement": ["Balance Sheet", "Income Statement", "Cash Flow"],
        "kyc_document": ["Personal Information", "Address", "Identification", "Source of Funds"],
    }

    # Minimum word count for completeness
    MIN_WORD_COUNT = 100

    def __init__(self):
        """Initialize structure validation service."""
        logger.info("structure_validation_service_initialized", template_count=len(self.TEMPLATES))

    async def validate(
        self,
        text: str,
        file_path: Path,
        expected_document_type: Optional[str] = None,
    ) -> StructureValidationResult:
        """
        Validate document structure.

        Args:
            text: Extracted text from document
            file_path: Path to the document file
            expected_document_type: Expected type for template matching

        Returns:
            StructureValidationResult with structure analysis
        """
        logger.info(
            "structure_validation_started",
            file_name=file_path.name,
            expected_type=expected_document_type,
        )

        issues: List[ValidationIssue] = []

        # Check for missing sections
        section_result = await self._check_sections(text, expected_document_type)
        issues.extend(section_result["issues"])

        # Check for proper headers
        header_result = await self._check_headers(text)
        issues.extend(header_result["issues"])

        # Check document completeness
        completeness_result = await self._check_completeness(text)
        issues.extend(completeness_result["issues"])

        result = StructureValidationResult(
            is_complete=completeness_result["is_complete"],
            missing_sections=section_result["missing_sections"],
            has_correct_headers=header_result["has_correct_headers"],
            template_match_score=section_result["template_match_score"],
            issues=issues,
        )

        logger.info(
            "structure_validation_completed",
            file_name=file_path.name,
            is_complete=result.is_complete,
            missing_sections_count=len(result.missing_sections),
            template_match_score=result.template_match_score,
        )

        return result

    async def _check_sections(self, text: str, document_type: Optional[str]) -> dict:
        """Check for missing expected sections."""
        expected_sections = self._get_expected_sections(document_type)
        missing_sections = []

        for section in expected_sections:
            # Case-insensitive search for section headers
            pattern = re.compile(rf"\b{re.escape(section)}\b", re.IGNORECASE)
            if not pattern.search(text):
                missing_sections.append(section)

        issues = []
        if missing_sections:
            severity = ValidationSeverity.HIGH if len(missing_sections) > 2 else ValidationSeverity.MEDIUM
            issues.append(
                ValidationIssue(
                    category="structure",
                    severity=severity,
                    description=f"Document is missing {len(missing_sections)} expected sections",
                    details={"missing_sections": missing_sections},
                )
            )

        # Calculate template match score
        sections_found = len(expected_sections) - len(missing_sections)
        template_match_score = (
            sections_found / len(expected_sections) if expected_sections else 1.0
        )

        return {
            "missing_sections": missing_sections,
            "template_match_score": template_match_score,
            "issues": issues,
        }

    async def _check_headers(self, text: str) -> dict:
        """Check for proper section headers."""
        # Pattern for proper headers: Start with capital letter, 3-50 chars
        header_pattern = re.compile(r"^[A-Z][A-Za-z\s]{3,50}$", re.MULTILINE)
        headers = header_pattern.findall(text)
        has_correct_headers = len(headers) >= 2  # At least 2 proper headers

        issues = []
        if not has_correct_headers:
            issues.append(
                ValidationIssue(
                    category="structure",
                    severity=ValidationSeverity.MEDIUM,
                    description="Document appears to lack proper section headers",
                    details={"header_count": len(headers)},
                )
            )

        return {"has_correct_headers": has_correct_headers, "issues": issues}

    async def _check_completeness(self, text: str) -> dict:
        """Check if document appears complete."""
        word_count = len(text.split())
        is_complete = word_count >= self.MIN_WORD_COUNT

        issues = []
        if not is_complete:
            issues.append(
                ValidationIssue(
                    category="structure",
                    severity=ValidationSeverity.CRITICAL,
                    description=f"Document appears incomplete (only {word_count} words)",
                    details={"word_count": word_count, "minimum_required": self.MIN_WORD_COUNT},
                )
            )

        return {"is_complete": is_complete, "issues": issues}

    def _get_expected_sections(self, document_type: Optional[str]) -> List[str]:
        """Get expected sections based on document type."""
        if document_type and document_type.lower() in self.TEMPLATES:
            return self.TEMPLATES[document_type.lower()]

        # Default generic sections
        return ["Introduction", "Body", "Conclusion"]


__all__ = ["StructureValidationService"]

"""
Format validation service.

Single Responsibility: Validate document formatting (spacing, indentation, spelling).
"""

import re
from pathlib import Path
from typing import List, Optional

from backend.adapters.nlp import NLPProcessorProtocol
from backend.schemas.validation import (
    FormatValidationResult,
    ValidationIssue,
    ValidationSeverity,
)
from backend.logging import get_logger

logger = get_logger(__name__)


class FormatValidationService:
    """
    Service for validating document formatting.

    Responsibilities:
    - Check for irregular spacing
    - Detect indentation inconsistencies
    - Perform spell checking
    - Validate font consistency (placeholder)
    """

    def __init__(self, nlp_processor: Optional[NLPProcessorProtocol] = None):
        """
        Initialize format validation service.

        Args:
            nlp_processor: NLP processor for spell checking (injected)
        """
        self.nlp_processor = nlp_processor
        logger.info("format_validation_service_initialized", has_nlp=nlp_processor is not None)

    async def validate(self, text: str, file_path: Path) -> FormatValidationResult:
        """
        Validate document formatting.

        Args:
            text: Extracted text from document
            file_path: Path to the document file

        Returns:
            FormatValidationResult with formatting analysis
        """
        logger.info("format_validation_started", file_name=file_path.name)

        issues: List[ValidationIssue] = []

        # Check spacing issues
        spacing_result = await self._check_spacing(text)
        issues.extend(spacing_result["issues"])

        # Check indentation issues
        indentation_result = await self._check_indentation(text)
        issues.extend(indentation_result["issues"])

        # Check spelling (if NLP processor available)
        spelling_result = await self._check_spelling(text)
        issues.extend(spelling_result["issues"])

        # Font consistency (placeholder)
        font_result = await self._check_font_consistency(text)

        # Calculate has_formatting_issues (True if any issues found)
        has_formatting_issues = (
            spacing_result["has_double_spacing"]
            or indentation_result["has_issues"]
            or spelling_result["has_errors"]
            or font_result["has_inconsistencies"]
            or len(issues) > 0
        )

        result = FormatValidationResult(
            has_double_spacing=spacing_result["has_double_spacing"],
            has_font_inconsistencies=font_result["has_inconsistencies"],
            has_indentation_issues=indentation_result["has_issues"],
            has_spelling_errors=spelling_result["has_errors"],
            spelling_error_count=spelling_result["error_count"],
            issues=issues,
            # Additional fields
            has_formatting_issues=has_formatting_issues,
            double_spacing_count=spacing_result["double_spacing_count"],
            trailing_whitespace_count=spacing_result["trailing_whitespace_count"],
            spelling_errors=spelling_result["spelling_errors"],
        )

        logger.info(
            "format_validation_completed",
            file_name=file_path.name,
            issue_count=len(issues),
            has_spacing_issues=result.has_double_spacing,
            has_spelling_errors=result.has_spelling_errors,
        )

        return result

    async def _check_spacing(self, text: str) -> dict:
        """Check for irregular spacing issues."""
        # Count double spacing occurrences (2 or more consecutive spaces)
        double_spacing_count = len(re.findall(r' {2,}', text))
        has_double_spacing = double_spacing_count > 0
        issues = []

        if has_double_spacing:
            issues.append(
                ValidationIssue(
                    category="formatting",
                    severity=ValidationSeverity.LOW,
                    description=f"Found {double_spacing_count} instances of irregular spacing (double/triple spaces)",
                    details={"spacing_issues_count": double_spacing_count},
                )
            )

        # Check for irregular line breaks (3+ consecutive newlines)
        has_irregular_breaks = bool(re.search(r'\n{3,}', text))
        if has_irregular_breaks:
            issues.append(
                ValidationIssue(
                    category="formatting",
                    severity=ValidationSeverity.LOW,
                    description="Document has irregular line breaks (3+ consecutive newlines)",
                )
            )

        # Check for mixed line break styles (\n vs \r\n)
        # Count occurrences of each type
        unix_breaks = text.count('\n') - text.count('\r\n')  # Pure \n (not part of \r\n)
        windows_breaks = text.count('\r\n')

        # Mixed if both types exist
        if unix_breaks > 0 and windows_breaks > 0:
            issues.append(
                ValidationIssue(
                    category="formatting",
                    severity=ValidationSeverity.LOW,
                    description="Document has inconsistent line breaks (mix of Unix \\n and Windows \\r\\n)",
                )
            )

        # Check for trailing whitespace
        lines = text.split('\n')
        trailing_whitespace_count = sum(1 for line in lines if line and re.search(r'\s+$', line))

        if trailing_whitespace_count > 0:
            issues.append(
                ValidationIssue(
                    category="formatting",
                    severity=ValidationSeverity.LOW,
                    description=f"Found {trailing_whitespace_count} lines with trailing whitespace",
                    details={"trailing_whitespace_count": trailing_whitespace_count},
                )
            )

        return {
            "has_double_spacing": has_double_spacing or has_irregular_breaks,
            "double_spacing_count": double_spacing_count,
            "trailing_whitespace_count": trailing_whitespace_count,
            "issues": issues
        }

    async def _check_indentation(self, text: str) -> dict:
        """Check for mixed indentation (tabs vs spaces)."""
        lines = text.split("\n")
        tab_lines = sum(1 for line in lines if line.startswith("\t"))
        space_indent_lines = sum(1 for line in lines if re.match(r"^\s{2,}", line))
        has_issues = tab_lines > 0 and space_indent_lines > 0

        issues = []
        if has_issues:
            issues.append(
                ValidationIssue(
                    category="formatting",
                    severity=ValidationSeverity.MEDIUM,
                    description="Document has mixed indentation (both tabs and spaces)",
                    details={"tab_lines": tab_lines, "space_indent_lines": space_indent_lines},
                )
            )

        return {"has_issues": has_issues, "issues": issues}

    async def _check_spelling(self, text: str) -> dict:
        """Check spelling using NLP processor."""
        has_errors = False
        error_count = 0
        spelling_errors = []
        issues = []

        if self.nlp_processor:
            try:
                # Limit text for performance
                text_sample = text[:10000]

                # Use NLP adapter's spell checking
                unknown_words = await self.nlp_processor.check_spelling(text_sample, threshold=10)

                spelling_errors = unknown_words
                error_count = len(unknown_words)
                has_errors = error_count > 5  # Threshold

                if has_errors:
                    issues.append(
                        ValidationIssue(
                            category="content",
                            severity=ValidationSeverity.MEDIUM,
                            description=f"Detected {error_count} potential spelling errors or unknown words",
                            details={"sample_errors": unknown_words[:10]},
                        )
                    )

                logger.debug("spell_check_completed", unknown_word_count=error_count)

            except Exception as e:
                logger.warning("spell_check_failed", error=str(e))
        else:
            logger.debug("spell_check_skipped", reason="no_nlp_processor")

        return {
            "has_errors": has_errors,
            "error_count": error_count,
            "spelling_errors": spelling_errors,
            "issues": issues
        }

    async def _check_font_consistency(self, text: str) -> dict:
        """Check font consistency (placeholder for PDF metadata analysis)."""
        # This is a placeholder - in a real system, you'd analyze PDF metadata
        # using a PDF library and check for font changes, sizes, etc.
        return {"has_inconsistencies": False}


__all__ = ["FormatValidationService"]

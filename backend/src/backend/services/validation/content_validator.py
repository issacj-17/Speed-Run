"""
Content validation service.

Single Responsibility: Validate document content quality (PII, readability, quality scoring).
"""

import re
from typing import List

from backend.schemas.validation import (
    ContentValidationResult,
    ValidationIssue,
    ValidationSeverity,
)
from backend.logging import get_logger

logger = get_logger(__name__)


class ContentValidationService:
    """
    Service for validating document content quality.

    Responsibilities:
    - Detect sensitive data (PII)
    - Calculate readability scores
    - Assess overall content quality
    - Check for repetitive content
    """

    # Sensitive data patterns
    SSN_PATTERN = r"\b\d{3}-\d{2}-\d{4}\b"
    CREDIT_CARD_PATTERN = r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    PHONE_PATTERN = r"\b(\+?1[-.]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"

    # Thresholds
    LOW_READABILITY_THRESHOLD = 30.0  # Flesch score below this is very difficult

    def __init__(self):
        """Initialize content validation service."""
        logger.info("content_validation_service_initialized")

    async def validate(
        self,
        text: str,
        min_length: int = None,
        max_length: int = None
    ) -> ContentValidationResult:
        """
        Validate document content quality.

        Args:
            text: Extracted text from document
            min_length: Minimum allowed text length in characters (optional)
            max_length: Maximum allowed text length in characters (optional)

        Returns:
            ContentValidationResult with content analysis
        """
        logger.info("content_validation_started", text_length=len(text))

        issues: List[ValidationIssue] = []

        # Check length constraints
        text_length = len(text)
        if min_length is not None and text_length < min_length:
            issues.append(
                ValidationIssue(
                    category="content",
                    severity=ValidationSeverity.MEDIUM,
                    description=f"Document is too short (min: {min_length}, actual: {text_length})",
                    details={"min_length": min_length, "actual_length": text_length},
                )
            )
        if max_length is not None and text_length > max_length:
            issues.append(
                ValidationIssue(
                    category="content",
                    severity=ValidationSeverity.MEDIUM,
                    description=f"Document is too long (max: {max_length}, actual: {text_length})",
                    details={"max_length": max_length, "actual_length": text_length},
                )
            )

        # Check for sensitive data
        sensitive_result = await self._check_sensitive_data(text)
        issues.extend(sensitive_result["issues"])

        # Calculate readability
        readability_result = await self._calculate_readability(text)
        issues.extend(readability_result["issues"])

        # Calculate quality score
        word_count = len(text.split())
        quality_result = await self._calculate_quality(text, readability_result["score"], word_count)

        result = ContentValidationResult(
            has_sensitive_data=sensitive_result["has_sensitive_data"],
            quality_score=quality_result["score"],
            readability_score=readability_result["score"],
            word_count=word_count,
            issues=issues,
        )

        logger.info(
            "content_validation_completed",
            has_sensitive_data=result.has_sensitive_data,
            quality_score=result.quality_score,
            readability_score=result.readability_score,
            word_count=result.word_count,
        )

        return result

    async def _check_sensitive_data(self, text: str) -> dict:
        """Detect potential PII or sensitive data."""
        has_sensitive_data = False
        issues = []

        # Check for SSN
        if re.search(self.SSN_PATTERN, text):
            has_sensitive_data = True
            issues.append(
                ValidationIssue(
                    category="content",
                    severity=ValidationSeverity.HIGH,
                    description="Document contains SSN (Social Security Number)",
                    details={"pii_type": "SSN"},
                )
            )

        # Check for credit card numbers
        if re.search(self.CREDIT_CARD_PATTERN, text):
            has_sensitive_data = True
            issues.append(
                ValidationIssue(
                    category="content",
                    severity=ValidationSeverity.HIGH,
                    description="Document contains credit card number",
                    details={"pii_type": "credit card"},
                )
            )

        # Check for email addresses
        if re.search(self.EMAIL_PATTERN, text):
            has_sensitive_data = True
            issues.append(
                ValidationIssue(
                    category="content",
                    severity=ValidationSeverity.HIGH,
                    description="Document contains email address",
                    details={"pii_type": "email"},
                )
            )

        # Check for phone numbers
        if re.search(self.PHONE_PATTERN, text):
            has_sensitive_data = True
            issues.append(
                ValidationIssue(
                    category="content",
                    severity=ValidationSeverity.HIGH,
                    description="Document contains phone number",
                    details={"pii_type": "phone"},
                )
            )

        return {"has_sensitive_data": has_sensitive_data, "issues": issues}

    async def _calculate_readability(self, text: str) -> dict:
        """Calculate Flesch Reading Ease score."""
        words = text.split()
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        syllables = sum(self._count_syllables(word) for word in words)

        if len(sentences) == 0 or len(words) == 0:
            score = 0.0
        else:
            # Flesch Reading Ease formula
            score = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))
            score = max(0.0, min(100.0, score))

        issues = []
        if score < self.LOW_READABILITY_THRESHOLD:
            issues.append(
                ValidationIssue(
                    category="content",
                    severity=ValidationSeverity.LOW,
                    description="Document has low readability score (very difficult to read)",
                    details={"readability_score": round(score, 2)},
                )
            )

        return {"score": round(score, 2), "issues": issues}

    async def _calculate_quality(self, text: str, readability: float, word_count: int) -> dict:
        """Calculate overall content quality score."""
        # Normalize components to 0-1 scale
        readability_norm = readability / 100.0
        length_norm = min(word_count / 500.0, 1.0)  # Normalize to 500 words

        # Check for repetitive content (unique word ratio)
        words = text.lower().split()
        unique_ratio = len(set(words)) / len(words) if words else 0

        # Composite score (weighted)
        quality = readability_norm * 0.4 + length_norm * 0.3 + unique_ratio * 0.3

        return {"score": round(quality, 2)}

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simple heuristic)."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith("e") and syllable_count > 1:
            syllable_count -= 1

        return max(1, syllable_count)


__all__ = ["ContentValidationService"]

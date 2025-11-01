"""Document validation service for format, structure, and content checks."""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import spacy
from docling.document_converter import DocumentConverter

from backend.schemas.validation import (
    FormatValidationResult,
    StructureValidationResult,
    ContentValidationResult,
    ValidationIssue,
    ValidationSeverity,
)


class DocumentValidator:
    """Service for validating document format, structure, and content."""

    def __init__(self):
        """Initialize the document validator."""
        self.converter = DocumentConverter()

        # Try to load spaCy model, fallback to basic validation if not available
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
            print("Warning: spaCy model not found. Some validation features will be limited.")

    async def validate_format(self, text: str, file_path: Path) -> FormatValidationResult:
        """
        Validate document formatting.

        Args:
            text: Extracted text from document
            file_path: Path to the document file

        Returns:
            FormatValidationResult with formatting analysis
        """
        issues: List[ValidationIssue] = []

        # Check for double spacing issues
        has_double_spacing = bool(re.search(r'\s{2,}', text))
        if has_double_spacing:
            count = len(re.findall(r'\s{2,}', text))
            issues.append(ValidationIssue(
                category="formatting",
                severity=ValidationSeverity.LOW,
                description=f"Found {count} instances of irregular spacing (double/triple spaces)",
                details={"spacing_issues_count": count}
            ))

        # Check for inconsistent line breaks
        has_irregular_breaks = bool(re.search(r'\n{3,}', text))
        if has_irregular_breaks:
            issues.append(ValidationIssue(
                category="formatting",
                severity=ValidationSeverity.LOW,
                description="Document has irregular line breaks (3+ consecutive newlines)",
            ))

        # Check for mixed indentation (tabs vs spaces in structured content)
        lines = text.split('\n')
        tab_lines = sum(1 for line in lines if line.startswith('\t'))
        space_indent_lines = sum(1 for line in lines if re.match(r'^\s{2,}', line))
        has_indentation_issues = tab_lines > 0 and space_indent_lines > 0

        if has_indentation_issues:
            issues.append(ValidationIssue(
                category="formatting",
                severity=ValidationSeverity.MEDIUM,
                description="Document has mixed indentation (both tabs and spaces)",
                details={"tab_lines": tab_lines, "space_indent_lines": space_indent_lines}
            ))

        # Spell check using spaCy if available
        spelling_error_count = 0
        has_spelling_errors = False

        if self.nlp:
            doc = self.nlp(text[:10000])  # Limit to first 10k chars for performance
            # Simple spell check: look for unknown words
            unknown_words = [token.text for token in doc if not token.is_alpha or (token.is_alpha and not token.is_stop and token.pos_ == 'X')]
            spelling_error_count = len(unknown_words)
            has_spelling_errors = spelling_error_count > 5  # Threshold

            if has_spelling_errors:
                issues.append(ValidationIssue(
                    category="content",
                    severity=ValidationSeverity.MEDIUM,
                    description=f"Detected {spelling_error_count} potential spelling errors or unknown words",
                    details={"sample_errors": unknown_words[:10]}
                ))

        # Font consistency check (basic heuristic based on formatting markers)
        has_font_inconsistencies = False
        # This is a placeholder - in a real system, you'd analyze PDF metadata

        return FormatValidationResult(
            has_double_spacing=has_double_spacing,
            has_font_inconsistencies=has_font_inconsistencies,
            has_indentation_issues=has_indentation_issues,
            has_spelling_errors=has_spelling_errors,
            spelling_error_count=spelling_error_count,
            issues=issues,
        )

    async def validate_structure(
        self,
        text: str,
        file_path: Path,
        expected_document_type: Optional[str] = None
    ) -> StructureValidationResult:
        """
        Validate document structure and completeness.

        Args:
            text: Extracted text from document
            file_path: Path to the document file
            expected_document_type: Expected type of document for template matching

        Returns:
            StructureValidationResult with structure analysis
        """
        issues: List[ValidationIssue] = []

        # Define expected sections based on document type
        expected_sections = self._get_expected_sections(expected_document_type)

        # Check for missing sections
        missing_sections = []
        for section in expected_sections:
            # Case-insensitive search for section headers
            pattern = re.compile(rf'\b{re.escape(section)}\b', re.IGNORECASE)
            if not pattern.search(text):
                missing_sections.append(section)

        if missing_sections:
            issues.append(ValidationIssue(
                category="structure",
                severity=ValidationSeverity.HIGH if len(missing_sections) > 2 else ValidationSeverity.MEDIUM,
                description=f"Document is missing {len(missing_sections)} expected sections",
                details={"missing_sections": missing_sections}
            ))

        # Check for proper headers (basic heuristic)
        header_pattern = re.compile(r'^[A-Z][A-Za-z\s]{3,50}$', re.MULTILINE)
        headers = header_pattern.findall(text)
        has_correct_headers = len(headers) >= 2  # At least 2 proper headers

        if not has_correct_headers:
            issues.append(ValidationIssue(
                category="structure",
                severity=ValidationSeverity.MEDIUM,
                description="Document appears to lack proper section headers",
            ))

        # Calculate template match score
        sections_found = len(expected_sections) - len(missing_sections)
        template_match_score = sections_found / len(expected_sections) if expected_sections else 1.0

        # Check document completeness (length heuristic)
        word_count = len(text.split())
        is_complete = word_count > 100  # Basic threshold

        if not is_complete:
            issues.append(ValidationIssue(
                category="structure",
                severity=ValidationSeverity.CRITICAL,
                description=f"Document appears incomplete (only {word_count} words)",
                details={"word_count": word_count}
            ))

        return StructureValidationResult(
            is_complete=is_complete,
            missing_sections=missing_sections,
            has_correct_headers=has_correct_headers,
            template_match_score=template_match_score,
            issues=issues,
        )

    async def validate_content(self, text: str) -> ContentValidationResult:
        """
        Validate document content quality.

        Args:
            text: Extracted text from document

        Returns:
            ContentValidationResult with content analysis
        """
        issues: List[ValidationIssue] = []

        # Check for sensitive data patterns (PII)
        has_sensitive_data = self._detect_sensitive_data(text)

        if has_sensitive_data:
            issues.append(ValidationIssue(
                category="content",
                severity=ValidationSeverity.HIGH,
                description="Document may contain sensitive personal information (PII)",
            ))

        # Calculate readability score (Flesch Reading Ease)
        readability_score = self._calculate_readability(text)

        if readability_score < 30:  # Very difficult to read
            issues.append(ValidationIssue(
                category="content",
                severity=ValidationSeverity.LOW,
                description="Document has low readability score",
                details={"readability_score": readability_score}
            ))

        # Word count
        word_count = len(text.split())

        # Quality score (composite metric)
        quality_score = self._calculate_quality_score(text, readability_score, word_count)

        return ContentValidationResult(
            has_sensitive_data=has_sensitive_data,
            quality_score=quality_score,
            readability_score=readability_score,
            word_count=word_count,
            issues=issues,
        )

    def _get_expected_sections(self, document_type: Optional[str]) -> List[str]:
        """Get expected sections based on document type."""
        templates = {
            "invoice": ["Invoice", "Date", "Amount", "Description", "Total"],
            "contract": ["Parties", "Terms", "Conditions", "Signatures", "Date"],
            "report": ["Executive Summary", "Introduction", "Methodology", "Results", "Conclusion"],
            "letter": ["Date", "Recipient", "Body", "Signature"],
        }
        return templates.get(document_type, ["Introduction", "Body", "Conclusion"])

    def _detect_sensitive_data(self, text: str) -> bool:
        """Detect potential PII or sensitive data."""
        # SSN pattern
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        # Credit card pattern
        cc_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        return bool(
            re.search(ssn_pattern, text) or
            re.search(cc_pattern, text) or
            len(re.findall(email_pattern, text)) > 5  # More than 5 emails might be unusual
        )

    def _calculate_readability(self, text: str) -> float:
        """Calculate Flesch Reading Ease score."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        syllables = sum(self._count_syllables(word) for word in words)

        if len(sentences) == 0 or len(words) == 0:
            return 0.0

        # Flesch Reading Ease formula
        score = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))
        return max(0.0, min(100.0, score))

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simple heuristic)."""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1

        return max(1, syllable_count)

    def _calculate_quality_score(self, text: str, readability: float, word_count: int) -> float:
        """Calculate overall content quality score."""
        # Normalize components to 0-1 scale
        readability_norm = readability / 100.0
        length_norm = min(word_count / 500.0, 1.0)  # Normalize to 500 words

        # Check for repetitive content
        words = text.lower().split()
        unique_ratio = len(set(words)) / len(words) if words else 0

        # Composite score
        quality = (readability_norm * 0.4 + length_norm * 0.3 + unique_ratio * 0.3)
        return round(quality, 2)

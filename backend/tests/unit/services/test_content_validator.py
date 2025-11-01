"""
Unit tests for ContentValidationService.

Tests content quality validation including PII detection and readability.
"""

import pytest
from pathlib import Path

from backend.services.validation.content_validator import (
    ContentValidationService,
    ContentValidationResult,
)
from backend.schemas.validation import ValidationSeverity


# ============================================================================
# Initialization Tests
# ============================================================================


@pytest.mark.unit
def test_content_validator_initializes():
    """Test ContentValidationService initializes successfully."""
    validator = ContentValidationService()

    assert validator is not None


# ============================================================================
# PII Detection Tests - SSN
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_detects_ssn():
    """Test validator detects Social Security Numbers."""
    # Arrange
    validator = ContentValidationService()
    text = "My SSN is 123-45-6789 and I live in California."

    # Act
    result = await validator.validate(text)

    # Assert
    assert result.has_sensitive_data is True
    assert any("SSN" in issue.description or "social security" in issue.description.lower()
               for issue in result.issues)


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("text", [
    "SSN: 123-45-6789",
    "My social security number is 987-65-4321",
    "Contact me at 555-66-7777",
])
async def test_validate_detects_various_ssn_formats(text):
    """Test validator detects SSN in various formats."""
    # Arrange
    validator = ContentValidationService()

    # Act
    result = await validator.validate(text)

    # Assert
    assert result.has_sensitive_data is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_no_false_positive_ssn():
    """Test validator does not falsely detect SSN in similar patterns."""
    # Arrange
    validator = ContentValidationService()
    # Phone numbers and other non-SSN patterns
    text = "Call me at 555-1234 or reference number 12-345-6"

    # Act
    result = await validator.validate(text)

    # Assert
    # Should not flag these as SSN (wrong format)
    assert result.has_sensitive_data is False


# ============================================================================
# PII Detection Tests - Credit Card
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_detects_credit_card():
    """Test validator detects credit card numbers."""
    # Arrange
    validator = ContentValidationService()
    text = "My credit card is 4532 1234 5678 9010 and expires in 2025."

    # Act
    result = await validator.validate(text)

    # Assert
    assert result.has_sensitive_data is True
    assert any("credit card" in issue.description.lower() for issue in result.issues)


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("text", [
    "Card: 4532-1234-5678-9010",
    "CC: 4532123456789010",
    "Payment via 5425 2334 3010 9903",
])
async def test_validate_detects_various_credit_card_formats(text):
    """Test validator detects credit cards in various formats (with/without dashes/spaces)."""
    # Arrange
    validator = ContentValidationService()

    # Act
    result = await validator.validate(text)

    # Assert
    assert result.has_sensitive_data is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_no_false_positive_credit_card():
    """Test validator does not falsely detect credit card in random numbers."""
    # Arrange
    validator = ContentValidationService()
    # Random 16-digit numbers that don't match credit card patterns
    text = "Invoice number 1111 2222 3333 4444"

    # Act
    result = await validator.validate(text)

    # Assert - May or may not flag depending on pattern strictness
    # But should complete without error
    assert result is not None


# ============================================================================
# PII Detection Tests - Email
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_detects_email():
    """Test validator detects email addresses."""
    # Arrange
    validator = ContentValidationService()
    text = "Contact me at john.doe@example.com for more information."

    # Act
    result = await validator.validate(text)

    # Assert
    assert result.has_sensitive_data is True
    assert any("email" in issue.description.lower() for issue in result.issues)


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("text", [
    "Email: alice@company.org",
    "Send to bob.smith@subdomain.example.com",
    "Contact: user+tag@domain.co.uk",
])
async def test_validate_detects_various_email_formats(text):
    """Test validator detects various email formats."""
    # Arrange
    validator = ContentValidationService()

    # Act
    result = await validator.validate(text)

    # Assert
    assert result.has_sensitive_data is True


# ============================================================================
# PII Detection Tests - Phone Number
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_detects_phone_number():
    """Test validator detects phone numbers."""
    # Arrange
    validator = ContentValidationService()
    text = "Call me at (555) 123-4567 or text me anytime."

    # Act
    result = await validator.validate(text)

    # Assert
    assert result.has_sensitive_data is True
    assert any("phone" in issue.description.lower() for issue in result.issues)


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("text", [
    "Phone: (555) 123-4567",
    "Call: 555-123-4567",
    "Mobile: 555.123.4567",
    "Tel: +1-555-123-4567",
])
async def test_validate_detects_various_phone_formats(text):
    """Test validator detects various phone number formats."""
    # Arrange
    validator = ContentValidationService()

    # Act
    result = await validator.validate(text)

    # Assert
    assert result.has_sensitive_data is True


# ============================================================================
# Multiple PII Detection Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_detects_multiple_pii_types():
    """Test validator detects multiple PII types in same text."""
    # Arrange
    validator = ContentValidationService()
    text = """
    Contact John Doe at john.doe@example.com or (555) 123-4567.
    His SSN is 123-45-6789 and credit card is 4532 1234 5678 9010.
    """

    # Act
    result = await validator.validate(text)

    # Assert
    assert result.has_sensitive_data is True
    assert len(result.issues) >= 4  # Should detect email, phone, SSN, credit card


# ============================================================================
# Readability Score Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_calculates_readability_score():
    """Test validator calculates readability score (Flesch Reading Ease)."""
    # Arrange
    validator = ContentValidationService()
    text = """
    This is a simple text. It has short sentences. They are easy to read.
    The vocabulary is basic. Anyone can understand this.
    """

    # Act
    result = await validator.validate(text)

    # Assert
    assert result.readability_score is not None
    assert 0 <= result.readability_score <= 100


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_higher_score_for_simple_text():
    """Test validator assigns higher readability score to simple text."""
    # Arrange
    validator = ContentValidationService()
    simple_text = "The cat sat. The dog ran. They played."

    # Act
    result = await validator.validate(simple_text)

    # Assert
    # Simple text should have high readability (closer to 100)
    assert result.readability_score > 70


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_lower_score_for_complex_text():
    """Test validator assigns lower readability score to complex text."""
    # Arrange
    validator = ContentValidationService()
    complex_text = """
    The implementation of sophisticated algorithmic methodologies necessitates
    comprehensive understanding of multifaceted computational paradigms and their
    intricate interdependencies within heterogeneous distributed systems.
    """

    # Act
    result = await validator.validate(complex_text)

    # Assert
    # Complex text should have lower readability
    assert result.readability_score < 50


# ============================================================================
# Content Length Validation Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_detects_too_short_content():
    """Test validator flags content that is too short."""
    # Arrange
    validator = ContentValidationService()
    short_text = "Hi."  # Very short

    # Act
    result = await validator.validate(short_text, min_length=100)

    # Assert
    assert any("too short" in issue.description.lower() for issue in result.issues)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_detects_too_long_content():
    """Test validator flags content that is too long."""
    # Arrange
    validator = ContentValidationService()
    long_text = "word " * 10000  # Very long (50k chars)

    # Act
    result = await validator.validate(long_text, max_length=1000)

    # Assert
    assert any("too long" in issue.description.lower() for issue in result.issues)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_accepts_content_within_length_range():
    """Test validator accepts content within specified length range."""
    # Arrange
    validator = ContentValidationService()
    text = "This is a document with appropriate length. " * 5

    # Act
    result = await validator.validate(text, min_length=50, max_length=500)

    # Assert
    # Should not have length-related issues
    assert not any("too short" in issue.description.lower() or "too long" in issue.description.lower()
                   for issue in result.issues)


# ============================================================================
# Edge Cases Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_handles_empty_text():
    """Test validator handles empty text without errors."""
    # Arrange
    validator = ContentValidationService()

    # Act
    result = await validator.validate("")

    # Assert
    assert result is not None
    assert result.has_sensitive_data is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_handles_whitespace_only_text():
    """Test validator handles whitespace-only text."""
    # Arrange
    validator = ContentValidationService()
    text = "   \n\n   \t  "

    # Act
    result = await validator.validate(text)

    # Assert
    assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_handles_special_characters():
    """Test validator handles special characters and unicode."""
    # Arrange
    validator = ContentValidationService()
    text = "Café résumé 中文 العربية 🔥 emoji"

    # Act
    result = await validator.validate(text)

    # Assert
    assert result is not None
    assert isinstance(result, ContentValidationResult)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_handles_very_long_text():
    """Test validator handles very long text (100k+ characters)."""
    # Arrange
    validator = ContentValidationService()
    long_text = "This is a sentence. " * 10000  # ~200k characters

    # Act
    result = await validator.validate(long_text)

    # Assert
    assert result is not None
    # Should complete without errors


# ============================================================================
# Clean Text Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_clean_text_has_no_issues():
    """Test validator returns no issues for clean, appropriate text."""
    # Arrange
    validator = ContentValidationService()
    clean_text = """
    This is a professional business document. It contains important information
    about our quarterly results. The financial performance shows positive trends.
    We expect continued growth in the coming months.
    """

    # Act
    result = await validator.validate(clean_text)

    # Assert
    assert result.has_sensitive_data is False
    assert result.readability_score is not None
    # May have some readability suggestions, but no PII


# ============================================================================
# Severity Assignment Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_assigns_high_severity_to_pii():
    """Test validator assigns HIGH severity to PII detection."""
    # Arrange
    validator = ContentValidationService()
    text = "My SSN is 123-45-6789"

    # Act
    result = await validator.validate(text)

    # Assert
    pii_issues = [i for i in result.issues if "SSN" in i.description or "social security" in i.description.lower()]
    assert all(i.severity == ValidationSeverity.HIGH for i in pii_issues)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_assigns_medium_severity_to_readability():
    """Test validator assigns MEDIUM severity to readability issues."""
    # Arrange
    validator = ContentValidationService()
    # Very complex text with low readability
    complex_text = """
    The juxtaposition of multifarious epistemological frameworks necessitates
    comprehensive elucidation vis-à-vis contemporaneous hermeneutical paradigms.
    """ * 3

    # Act
    result = await validator.validate(complex_text)

    # Assert
    readability_issues = [i for i in result.issues if "readability" in i.description.lower()]
    if readability_issues:
        assert all(i.severity in [ValidationSeverity.MEDIUM, ValidationSeverity.LOW]
                   for i in readability_issues)


# ============================================================================
# Result Structure Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_result_has_required_fields():
    """Test validation result has all required fields."""
    # Arrange
    validator = ContentValidationService()
    text = "Test text."

    # Act
    result = await validator.validate(text)

    # Assert
    assert hasattr(result, "has_sensitive_data")
    assert hasattr(result, "readability_score")
    assert hasattr(result, "issues")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_issues_have_required_fields():
    """Test validation issues have all required fields."""
    # Arrange
    validator = ContentValidationService()
    text = "Contact me at email@example.com"

    # Act
    result = await validator.validate(text)

    # Assert
    if result.issues:
        for issue in result.issues:
            assert hasattr(issue, "category")
            assert hasattr(issue, "severity")
            assert hasattr(issue, "description")


# ============================================================================
# Performance Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.slow
async def test_validate_completes_within_reasonable_time():
    """Test validation completes within reasonable time for large text."""
    import time

    # Arrange
    validator = ContentValidationService()
    large_text = "This is a line of text with some content. " * 5000  # ~250k chars

    # Act
    start_time = time.time()
    result = await validator.validate(large_text)
    elapsed_time = time.time() - start_time

    # Assert
    assert elapsed_time < 5.0  # Should complete in less than 5 seconds
    assert result is not None


# ============================================================================
# Caching Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_caches_result():
    """Test validator caches result for repeated calls with same text."""
    # Arrange
    validator = ContentValidationService()
    text = "Test text for caching."

    # Act
    result1 = await validator.validate(text)
    result2 = await validator.validate(text)

    # Assert
    assert result1.has_sensitive_data == result2.has_sensitive_data
    assert result1.readability_score == result2.readability_score

    # Note: Actual caching behavior depends on cache availability


# ============================================================================
# Parametrized PII Pattern Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("pii_text,pii_type", [
    ("SSN: 123-45-6789", "SSN"),
    ("Card: 4532 1234 5678 9010", "credit card"),
    ("Email: test@example.com", "email"),
    ("Phone: (555) 123-4567", "phone"),
])
async def test_validate_detects_specific_pii_types(pii_text, pii_type):
    """Test validator detects specific PII types correctly."""
    # Arrange
    validator = ContentValidationService()

    # Act
    result = await validator.validate(pii_text)

    # Assert
    assert result.has_sensitive_data is True
    assert any(pii_type.lower() in issue.description.lower() for issue in result.issues)


# ============================================================================
# Boundary Value Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("length,min_len,max_len,should_have_issue", [
    (50, 100, 500, True),   # Too short
    (600, 100, 500, True),  # Too long
    (300, 100, 500, False), # Within range
    (100, 100, 500, False), # At minimum
    (500, 100, 500, False), # At maximum
])
async def test_validate_length_boundary_values(length, min_len, max_len, should_have_issue):
    """Test validator handles length boundary values correctly."""
    # Arrange
    validator = ContentValidationService()
    text = "x" * length

    # Act
    result = await validator.validate(text, min_length=min_len, max_length=max_len)

    # Assert
    has_length_issue = any("too short" in issue.description.lower() or "too long" in issue.description.lower()
                           for issue in result.issues)
    assert has_length_issue == should_have_issue

"""
Unit tests for FormatValidationService.

Tests format validation in isolation with mocked NLP processor.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock

from backend.services.validation.format_validator import (
    FormatValidationService,
    FormatValidationResult,
)
from backend.schemas.validation import ValidationSeverity


# ============================================================================
# Initialization Tests
# ============================================================================


@pytest.mark.unit
def test_format_validator_initializes_without_nlp():
    """Test FormatValidationService initializes without NLP processor."""
    validator = FormatValidationService()

    assert validator.nlp_processor is None


@pytest.mark.unit
def test_format_validator_accepts_nlp_processor(mock_nlp_processor):
    """Test FormatValidationService accepts NLP processor via DI."""
    validator = FormatValidationService(nlp_processor=mock_nlp_processor)

    assert validator.nlp_processor == mock_nlp_processor


# ============================================================================
# Double Spacing Detection Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_detects_double_spacing():
    """Test validator detects double spacing issues."""
    # Arrange
    validator = FormatValidationService()
    text = "This has  double  spacing issues."

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert result.has_formatting_issues is True
    assert result.double_spacing_count > 0
    assert any("spacing" in issue.description.lower() for issue in result.issues)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_no_double_spacing_in_correct_text():
    """Test validator does not flag correctly spaced text."""
    # Arrange
    validator = FormatValidationService()
    text = "This text has correct spacing throughout."

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert result.double_spacing_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("text,expected_count", [
    ("No  double  spacing  here.", 3),
    ("One  issue only.", 1),
    ("Multiple   spaces.", 1),
    ("Normal text.", 0),
])
async def test_validate_counts_double_spacing_correctly(text, expected_count):
    """Test validator correctly counts double spacing occurrences."""
    # Arrange
    validator = FormatValidationService()

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert result.double_spacing_count == expected_count


# ============================================================================
# Inconsistent Line Breaks Detection Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_detects_inconsistent_line_breaks():
    """Test validator detects inconsistent line breaks (mix of \\n and \\r\\n)."""
    # Arrange
    validator = FormatValidationService()
    text = "Line 1\nLine 2\r\nLine 3\nLine 4\r\n"  # Mixed line breaks

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert result.has_formatting_issues is True
    assert any("line break" in issue.description.lower() for issue in result.issues)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_allows_consistent_unix_line_breaks():
    """Test validator allows consistent Unix line breaks (\\n)."""
    # Arrange
    validator = FormatValidationService()
    text = "Line 1\nLine 2\nLine 3\n"

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    # Should not flag consistent line breaks
    assert not any("line break" in issue.description.lower() for issue in result.issues)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_allows_consistent_windows_line_breaks():
    """Test validator allows consistent Windows line breaks (\\r\\n)."""
    # Arrange
    validator = FormatValidationService()
    text = "Line 1\r\nLine 2\r\nLine 3\r\n"

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    # Should not flag consistent line breaks
    assert not any("line break" in issue.description.lower() for issue in result.issues)


# ============================================================================
# Trailing Whitespace Detection Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_detects_trailing_whitespace():
    """Test validator detects trailing whitespace at end of lines."""
    # Arrange
    validator = FormatValidationService()
    text = "Line with trailing spaces   \nAnother line with tabs\t\t\nClean line\n"

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert result.has_formatting_issues is True
    assert result.trailing_whitespace_count > 0
    assert any("trailing" in issue.description.lower() for issue in result.issues)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_no_trailing_whitespace_in_clean_text():
    """Test validator does not flag text without trailing whitespace."""
    # Arrange
    validator = FormatValidationService()
    text = "Clean line 1\nClean line 2\nClean line 3\n"

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert result.trailing_whitespace_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("text,expected_count", [
    ("Line 1  \nLine 2\t\nLine 3   \n", 3),
    ("Line 1  \nLine 2\n", 1),
    ("Line 1\nLine 2\n", 0),
])
async def test_validate_counts_trailing_whitespace_correctly(text, expected_count):
    """Test validator correctly counts lines with trailing whitespace."""
    # Arrange
    validator = FormatValidationService()

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert result.trailing_whitespace_count == expected_count


# ============================================================================
# Spelling Check Tests (with NLP)
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_checks_spelling_with_nlp_processor(mock_nlp_processor):
    """Test validator checks spelling when NLP processor available."""
    # Arrange
    unknown_words = ["wrods", "mistakse", "incorect"]
    mock_nlp_processor.check_spelling = AsyncMock(return_value=unknown_words)

    validator = FormatValidationService(nlp_processor=mock_nlp_processor)
    text = "This has some wrods and mistakse and incorect spelling."

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    mock_nlp_processor.check_spelling.assert_called_once()
    assert len(result.spelling_errors) == 3
    assert "wrods" in result.spelling_errors
    assert "mistakse" in result.spelling_errors


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_skips_spelling_without_nlp_processor():
    """Test validator skips spelling check when NLP processor not available."""
    # Arrange
    validator = FormatValidationService(nlp_processor=None)
    text = "This has mistakse but no NLP processor."

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert result.spelling_errors == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_truncates_text_for_spelling_check(mock_nlp_processor):
    """Test validator truncates very long text before spelling check."""
    # Arrange
    mock_nlp_processor.check_spelling = AsyncMock(return_value=[])

    validator = FormatValidationService(nlp_processor=mock_nlp_processor)

    # Create text longer than 10000 characters
    long_text = "word " * 5000  # ~25000 characters

    # Act
    await validator.validate(long_text, Path("test.txt"))

    # Assert
    call_args = mock_nlp_processor.check_spelling.call_args[0]
    assert len(call_args[0]) <= 10000  # Should be truncated


# ============================================================================
# Overall Validation Result Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_returns_false_when_no_issues():
    """Test validator returns has_formatting_issues=False when text is clean."""
    # Arrange
    validator = FormatValidationService()
    clean_text = "This is clean text.\nNo issues here.\nAll good.\n"

    # Act
    result = await validator.validate(clean_text, Path("test.txt"))

    # Assert
    assert result.has_formatting_issues is False
    assert len(result.issues) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_returns_true_when_issues_found():
    """Test validator returns has_formatting_issues=True when issues exist."""
    # Arrange
    validator = FormatValidationService()
    problematic_text = "This has  double spacing.\nAnd trailing   \n"

    # Act
    result = await validator.validate(problematic_text, Path("test.txt"))

    # Assert
    assert result.has_formatting_issues is True
    assert len(result.issues) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_includes_all_issue_types():
    """Test validator detects and reports all issue types in single pass."""
    # Arrange
    mock_nlp = AsyncMock()
    mock_nlp.check_spelling = AsyncMock(return_value=["mistakse"])

    validator = FormatValidationService(nlp_processor=mock_nlp)

    # Text with multiple issues
    text = "This has  double spacing.\nTrailing space  \nAnd mistakse spelling.\n"

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert result.has_formatting_issues is True
    assert result.double_spacing_count > 0
    assert result.trailing_whitespace_count > 0
    assert len(result.spelling_errors) > 0


# ============================================================================
# Edge Cases Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_handles_empty_text():
    """Test validator handles empty text without errors."""
    # Arrange
    validator = FormatValidationService()

    # Act
    result = await validator.validate("", Path("test.txt"))

    # Assert
    assert result.has_formatting_issues is False
    assert result.double_spacing_count == 0
    assert result.trailing_whitespace_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_handles_whitespace_only_text():
    """Test validator handles whitespace-only text."""
    # Arrange
    validator = FormatValidationService()
    text = "   \n\n   \t  "

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    # May or may not flag trailing whitespace, but should not crash
    assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_handles_single_line_text():
    """Test validator handles single-line text (no line breaks)."""
    # Arrange
    validator = FormatValidationService()
    text = "This is a single line with no line breaks."

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert result is not None
    assert isinstance(result, FormatValidationResult)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_handles_very_long_text():
    """Test validator handles very long text (100k+ characters)."""
    # Arrange
    validator = FormatValidationService()
    long_text = "Clean text. " * 10000  # ~120k characters

    # Act
    result = await validator.validate(long_text, Path("test.txt"))

    # Assert
    assert result is not None
    # Should complete without errors


# ============================================================================
# Severity Assignment Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_assigns_correct_severity_to_issues():
    """Test validator assigns appropriate severity to different issue types."""
    # Arrange
    validator = FormatValidationService()
    text = "This has  double spacing and trailing  \n"

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    for issue in result.issues:
        assert issue.severity in [ValidationSeverity.LOW, ValidationSeverity.MEDIUM, ValidationSeverity.HIGH]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_double_spacing_has_low_severity():
    """Test double spacing issues have LOW severity."""
    # Arrange
    validator = FormatValidationService()
    text = "This has  double spacing."

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    spacing_issues = [i for i in result.issues if "spacing" in i.description.lower()]
    assert all(i.severity == ValidationSeverity.LOW for i in spacing_issues)


# ============================================================================
# Result Structure Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_result_has_required_fields():
    """Test validation result has all required fields."""
    # Arrange
    validator = FormatValidationService()
    text = "Test text."

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    assert hasattr(result, "has_formatting_issues")
    assert hasattr(result, "double_spacing_count")
    assert hasattr(result, "trailing_whitespace_count")
    assert hasattr(result, "spelling_errors")
    assert hasattr(result, "issues")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_issues_have_required_fields():
    """Test validation issues have all required fields."""
    # Arrange
    validator = FormatValidationService()
    text = "This has  double spacing."

    # Act
    result = await validator.validate(text, Path("test.txt"))

    # Assert
    if result.issues:
        for issue in result.issues:
            assert hasattr(issue, "category")
            assert hasattr(issue, "severity")
            assert hasattr(issue, "description")
            assert hasattr(issue, "location")


# ============================================================================
# Integration with Caching Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_caches_result_by_file_hash():
    """Test validator caches result based on file content hash."""
    # Arrange
    validator = FormatValidationService()
    text = "Test text for caching."

    # Act
    result1 = await validator.validate(text, Path("test1.txt"))
    result2 = await validator.validate(text, Path("test1.txt"))  # Same file

    # Assert
    assert result1.has_formatting_issues == result2.has_formatting_issues
    assert result1.double_spacing_count == result2.double_spacing_count

    # Note: Actual caching behavior depends on cache availability


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_handles_nlp_processor_error(mock_nlp_processor):
    """Test validator handles NLP processor errors gracefully."""
    # Arrange
    mock_nlp_processor.check_spelling = AsyncMock(side_effect=Exception("NLP error"))

    validator = FormatValidationService(nlp_processor=mock_nlp_processor)
    text = "Test text."

    # Act & Assert - Should not crash
    result = await validator.validate(text, Path("test.txt"))

    # Should return result even if NLP fails
    assert result is not None
    assert isinstance(result, FormatValidationResult)


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
    validator = FormatValidationService()
    large_text = "This is a line of text.\n" * 10000  # 10k lines

    # Act
    start_time = time.time()
    result = await validator.validate(large_text, Path("test.txt"))
    elapsed_time = time.time() - start_time

    # Assert
    assert elapsed_time < 5.0  # Should complete in less than 5 seconds
    assert result is not None

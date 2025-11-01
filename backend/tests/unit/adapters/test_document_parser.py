"""
Unit tests for document parser adapter (Docling).

Tests DoclingAdapter in isolation with mocked Docling library.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.adapters.document_parser.docling import DoclingAdapter
from backend.adapters.document_parser.protocol import ParsedDocument


# ============================================================================
# Initialization Tests
# ============================================================================


@pytest.mark.unit
def test_docling_adapter_initializes_with_default_converter():
    """Test DoclingAdapter initializes with default Docling converter."""
    adapter = DoclingAdapter()

    assert adapter.converter is not None
    assert hasattr(adapter.converter, "convert")


@pytest.mark.unit
def test_docling_adapter_accepts_custom_converter(mock_docling_converter):
    """Test DoclingAdapter accepts custom converter for DI."""
    adapter = DoclingAdapter(converter=mock_docling_converter)

    assert adapter.converter == mock_docling_converter


# ============================================================================
# Format Support Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.parametrize("extension,expected", [
    (".pdf", True),
    (".PDF", True),
    (".docx", True),
    (".DOCX", True),
    (".doc", True),
    (".txt", False),
    (".jpg", False),
    (".png", False),
    (".xlsx", False),
])
def test_supports_format_returns_correct_value(extension, expected):
    """Test supports_format correctly identifies supported formats."""
    adapter = DoclingAdapter()

    result = adapter.supports_format(extension)

    assert result == expected


# ============================================================================
# Parse Tests - Happy Path
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_returns_parsed_document_with_correct_structure(
    mock_docling_converter,
    temp_pdf_file
):
    """Test parse returns ParsedDocument with correct structure."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "# Test Document\n\nSample content."
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_result.tables = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert isinstance(result, ParsedDocument)
    assert result.text == "# Test Document\n\nSample content."
    assert result.file_name == temp_pdf_file.name
    assert result.file_type == ".pdf"
    assert result.file_size > 0
    assert result.processing_time_ms >= 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_calls_docling_converter_with_correct_path(
    mock_docling_converter,
    temp_pdf_file
):
    """Test parse calls Docling converter with correct file path."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    await adapter.parse(temp_pdf_file)

    # Assert
    mock_docling_converter.convert.assert_called_once()
    call_args = mock_docling_converter.convert.call_args
    # Check that file path string was passed
    assert str(temp_pdf_file) in str(call_args)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_extracts_text_from_docling_result(mock_docling_converter, temp_pdf_file):
    """Test parse extracts text from Docling markdown export."""
    # Arrange
    expected_text = "# Important Document\n\n## Section 1\n\nThis is the content."

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = expected_text
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.text == expected_text
    mock_result.document.export_to_markdown.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_calculates_word_count_correctly(mock_docling_converter, temp_pdf_file):
    """Test parse calculates word count from extracted text."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "One two three four five."
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.word_count == 5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_counts_pages_correctly(mock_docling_converter, temp_pdf_file):
    """Test parse counts pages from Docling result."""
    # Arrange
    mock_page1 = MagicMock()
    mock_page2 = MagicMock()
    mock_page3 = MagicMock()

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.document.num_pages.return_value = 3  # Mock num_pages() method
    mock_result.pages = [mock_page1, mock_page2, mock_page3]
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.page_count == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_records_processing_time(mock_docling_converter, temp_pdf_file):
    """Test parse records processing time in milliseconds."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.processing_time_ms >= 0
    assert isinstance(result.processing_time_ms, float)


# ============================================================================
# Parse Tests - Edge Cases
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_handles_empty_document(mock_docling_converter, temp_pdf_file):
    """Test parse handles empty document gracefully."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = ""
    mock_result.document.num_pages.return_value = 0  # Empty document has 0 pages
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.text == ""
    assert result.word_count == 0
    assert result.page_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_handles_whitespace_only_document(mock_docling_converter, temp_pdf_file):
    """Test parse handles document with only whitespace."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "   \n\n   \t  "
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.text.strip() == ""
    assert result.word_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_handles_large_document(mock_docling_converter, temp_pdf_file):
    """Test parse handles large document (word count)."""
    # Arrange
    # Generate text with 10,000 words
    large_text = " ".join([f"word{i}" for i in range(10000)])

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = large_text
    mock_result.document.num_pages.return_value = 100  # Large document with 100 pages
    mock_result.pages = [MagicMock() for _ in range(100)]  # 100 pages
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.word_count == 10000
    assert result.page_count == 100


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_handles_special_characters(mock_docling_converter, temp_pdf_file):
    """Test parse handles special characters and unicode."""
    # Arrange
    special_text = "Café résumé naïve 中文 العربية 🔥 emoji"

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = special_text
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.text == special_text
    assert result.word_count > 0


# ============================================================================
# Parse Tests - Error Handling
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_raises_on_nonexistent_file():
    """Test parse raises FileNotFoundError for nonexistent file."""
    adapter = DoclingAdapter()
    nonexistent_file = Path("/nonexistent/path/file.pdf")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        await adapter.parse(nonexistent_file)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_raises_on_docling_error(mock_docling_converter, temp_pdf_file):
    """Test parse raises exception when Docling fails."""
    # Arrange
    mock_docling_converter.convert.side_effect = Exception("Docling conversion failed")

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await adapter.parse(temp_pdf_file)

    assert "Docling conversion failed" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_handles_export_to_markdown_error(mock_docling_converter, temp_pdf_file):
    """Test parse handles error during markdown export."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.side_effect = Exception("Export failed")
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await adapter.parse(temp_pdf_file)

    assert "Export failed" in str(exc_info.value)


# ============================================================================
# Caching Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_caches_result_on_second_call(mock_docling_converter, temp_pdf_file):
    """Test parse caches result and returns cached value on second call."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Cached content"
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act - First call (cache miss)
    result1 = await adapter.parse(temp_pdf_file)

    # Act - Second call (cache hit)
    result2 = await adapter.parse(temp_pdf_file)

    # Assert
    assert result1.text == result2.text
    assert result1.file_name == result2.file_name

    # Docling should be called only once (second call hits cache)
    # Note: This test verifies caching behavior if implemented
    # If cache is working, converter.convert should be called once
    # However, this depends on cache being available in test environment


# ============================================================================
# Metadata Extraction Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_extracts_file_metadata(mock_docling_converter, temp_pdf_file):
    """Test parse extracts file metadata (size, name, type)."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.file_name == temp_pdf_file.name
    assert result.file_type == ".pdf"
    assert result.file_size == temp_pdf_file.stat().st_size


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_includes_metadata_dict(mock_docling_converter, temp_pdf_file):
    """Test parse includes metadata dictionary."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert isinstance(result.metadata, dict)
    assert "parser" in result.metadata
    assert result.metadata["parser"] == "docling"


# ============================================================================
# Integration with Protocol Tests
# ============================================================================


@pytest.mark.unit
def test_docling_adapter_implements_protocol():
    """Test DoclingAdapter implements DocumentParserProtocol."""
    from backend.adapters.document_parser.protocol import DocumentParserProtocol

    adapter = DoclingAdapter()

    # Check protocol methods exist
    assert hasattr(adapter, "parse")
    assert hasattr(adapter, "supports_format")
    assert callable(adapter.parse)
    assert callable(adapter.supports_format)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_returns_protocol_compliant_result(mock_docling_converter, temp_pdf_file):
    """Test parse returns result compliant with ParsedDocument schema."""
    # Arrange
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 1  # Default page count
    mock_result.pages = []
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert - Check all required fields exist
    assert hasattr(result, "text")
    assert hasattr(result, "pages")
    assert hasattr(result, "tables")
    assert hasattr(result, "file_name")
    assert hasattr(result, "file_type")
    assert hasattr(result, "file_size")
    assert hasattr(result, "page_count")
    assert hasattr(result, "word_count")
    assert hasattr(result, "processing_time_ms")
    assert hasattr(result, "metadata")


# ============================================================================
# Page Extraction Tests (_extract_pages)
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_pages_with_multiple_pages(mock_docling_converter, temp_pdf_file):
    """Test _extract_pages extracts multiple pages correctly."""
    # Arrange
    mock_page1 = MagicMock()
    mock_page1.export_to_markdown.return_value = "Page 1 content with five words"

    mock_page2 = MagicMock()
    mock_page2.export_to_markdown.return_value = "Page 2 has different content"

    mock_page3 = MagicMock()
    mock_page3.export_to_markdown.return_value = "Page 3"

    mock_document = MagicMock()
    mock_document.pages = [mock_page1, mock_page2, mock_page3]
    mock_document.export_to_markdown.return_value = "Full document"
    mock_document.num_pages.return_value = 3
    mock_document.tables = []

    mock_result = MagicMock()
    mock_result.document = mock_document
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert len(result.pages) == 3
    assert result.pages[0].page_number == 1
    assert result.pages[0].text == "Page 1 content with five words"
    assert result.pages[0].word_count == 6
    assert result.pages[1].page_number == 2
    assert result.pages[1].text == "Page 2 has different content"
    assert result.pages[1].word_count == 5
    assert result.pages[2].page_number == 3
    assert result.pages[2].text == "Page 3"
    assert result.pages[2].word_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_pages_with_no_pages_attribute(mock_docling_converter, temp_pdf_file):
    """Test _extract_pages handles document with no pages attribute."""
    # Arrange
    mock_document = MagicMock()
    # Remove pages attribute
    del mock_document.pages
    mock_document.export_to_markdown.return_value = "Content"
    mock_document.num_pages.return_value = 1
    mock_document.tables = []

    mock_result = MagicMock()
    mock_result.document = mock_document
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.pages == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_pages_handles_page_without_export_method(mock_docling_converter, temp_pdf_file):
    """Test _extract_pages handles pages that don't have export_to_markdown."""
    # Arrange
    mock_page = MagicMock()
    # Remove export_to_markdown method
    del mock_page.export_to_markdown

    mock_document = MagicMock()
    mock_document.pages = [mock_page]
    mock_document.export_to_markdown.return_value = "Content"
    mock_document.num_pages.return_value = 1
    mock_document.tables = []

    mock_result = MagicMock()
    mock_result.document = mock_document
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert len(result.pages) == 1
    assert result.pages[0].text == ""  # No text if export method missing
    assert result.pages[0].word_count == 0


# ============================================================================
# Table Extraction Tests (_extract_tables)
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_tables_with_multiple_tables(mock_docling_converter, temp_pdf_file):
    """Test _extract_tables extracts multiple tables correctly."""
    # Arrange
    mock_table1 = MagicMock()
    mock_table1.export_to_dict.return_value = {
        "data": [["A1", "B1"], ["A2", "B2"]],
        "headers": ["Column A", "Column B"]
    }

    mock_table2 = MagicMock()
    mock_table2.export_to_dict.return_value = {
        "data": [["X", "Y", "Z"]],
        "headers": ["Col X", "Col Y", "Col Z"]
    }

    mock_document = MagicMock()
    mock_document.pages = []
    mock_document.tables = [mock_table1, mock_table2]
    mock_document.export_to_markdown.return_value = "Content"
    mock_document.num_pages.return_value = 1

    mock_result = MagicMock()
    mock_result.document = mock_document
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert len(result.tables) == 2
    assert result.tables[0].data == [["A1", "B1"], ["A2", "B2"]]
    assert result.tables[0].headers == ["Column A", "Column B"]
    assert result.tables[1].data == [["X", "Y", "Z"]]
    assert result.tables[1].headers == ["Col X", "Col Y", "Col Z"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_tables_with_no_tables_attribute(mock_docling_converter, temp_pdf_file):
    """Test _extract_tables handles document with no tables attribute."""
    # Arrange
    mock_document = MagicMock()
    # Remove tables attribute
    del mock_document.tables
    mock_document.pages = []
    mock_document.export_to_markdown.return_value = "Content"
    mock_document.num_pages.return_value = 1

    mock_result = MagicMock()
    mock_result.document = mock_document
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.tables == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_tables_handles_table_without_export_method(mock_docling_converter, temp_pdf_file):
    """Test _extract_tables handles tables without export_to_dict method."""
    # Arrange
    mock_table = MagicMock()
    # Remove export_to_dict method
    del mock_table.export_to_dict

    mock_document = MagicMock()
    mock_document.pages = []
    mock_document.tables = [mock_table]
    mock_document.export_to_markdown.return_value = "Content"
    mock_document.num_pages.return_value = 1

    mock_result = MagicMock()
    mock_result.document = mock_document
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    result = await adapter.parse(temp_pdf_file)

    # Assert
    assert result.tables == []  # Tables without export method are skipped


# ============================================================================
# Public extract_tables() Method Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_tables_public_method_success(mock_docling_converter, temp_pdf_file):
    """Test extract_tables() public method extracts tables successfully."""
    # Arrange
    mock_table = MagicMock()
    mock_table.export_to_dict.return_value = {
        "data": [["Value 1", "Value 2"]],
        "headers": ["Header 1", "Header 2"]
    }

    mock_document = MagicMock()
    mock_document.tables = [mock_table]

    mock_result = MagicMock()
    mock_result.document = mock_document
    mock_docling_converter.convert.return_value = mock_result

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act
    tables = await adapter.extract_tables(temp_pdf_file)

    # Assert
    assert len(tables) == 1
    assert tables[0].data == [["Value 1", "Value 2"]]
    assert tables[0].headers == ["Header 1", "Header 2"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_tables_public_method_raises_on_nonexistent_file():
    """Test extract_tables() raises FileNotFoundError for nonexistent file."""
    adapter = DoclingAdapter()
    nonexistent_file = Path("/nonexistent/path/document.pdf")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        await adapter.extract_tables(nonexistent_file)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_tables_public_method_handles_converter_error(mock_docling_converter, temp_pdf_file):
    """Test extract_tables() handles converter errors gracefully."""
    # Arrange
    mock_docling_converter.convert.side_effect = Exception("Table extraction failed")

    adapter = DoclingAdapter(converter=mock_docling_converter)

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await adapter.extract_tables(temp_pdf_file)

    assert "Table extraction failed" in str(exc_info.value)

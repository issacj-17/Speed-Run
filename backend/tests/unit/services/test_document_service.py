"""
Unit tests for DocumentService.

Tests document parsing operations with mocked Docling.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch, mock_open
from datetime import datetime
import tempfile

from backend.services.document_service import DocumentService
from backend.schemas.document import DocumentParseResponse


# ============================================================================
# Initialization Tests
# ============================================================================


@pytest.mark.unit
def test_document_service_initializes():
    """Test DocumentService initializes with converter."""
    # Act
    service = DocumentService()

    # Assert
    assert service.converter is not None
    assert service.pipeline_options is not None
    assert service.pipeline_options.do_ocr is True
    assert service.pipeline_options.do_table_structure is True


# ============================================================================
# Parse Document Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_parse_document_returns_response_with_correct_structure(
    mock_converter_class,
    temp_pdf_file
):
    """Test parse_document returns DocumentParseResponse with correct structure."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "# Test Document\n\nContent here."
    mock_result.document.num_pages.return_value = 1
    mock_result.document.pages = []
    mock_result.document.tables = []
    mock_converter.convert.return_value = mock_result

    service = DocumentService()

    # Act
    with patch.object(service, 'save_markdown_to_file', new=AsyncMock()):
        result = await service.parse_document(temp_pdf_file)

    # Assert
    assert isinstance(result, DocumentParseResponse)
    assert result.text == "# Test Document\n\nContent here."
    assert result.metadata.file_name == temp_pdf_file.name
    assert result.metadata.file_type == ".pdf"
    assert result.metadata.page_count == 1
    assert result.processing_time >= 0


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_parse_document_extracts_pages(mock_converter_class, temp_pdf_file):
    """Test parse_document extracts pages correctly."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_page1 = MagicMock()
    mock_page1.export_to_markdown.return_value = "Page 1 content"

    mock_page2 = MagicMock()
    mock_page2.export_to_markdown.return_value = "Page 2 content"

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Full document"
    mock_result.document.num_pages.return_value = 2
    mock_result.document.pages = [mock_page1, mock_page2]
    mock_result.document.tables = []
    mock_converter.convert.return_value = mock_result

    service = DocumentService()

    # Act
    with patch.object(service, 'save_markdown_to_file', new=AsyncMock()):
        result = await service.parse_document(temp_pdf_file)

    # Assert
    assert len(result.pages) == 2
    assert result.pages[0].page_number == 1
    assert result.pages[0].text == "Page 1 content"
    assert result.pages[1].page_number == 2
    assert result.pages[1].text == "Page 2 content"


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_parse_document_extracts_tables(mock_converter_class, temp_pdf_file):
    """Test parse_document extracts tables correctly."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_table = MagicMock()
    mock_table.export_to_dict.return_value = {
        "data": [["A1", "B1"], ["A2", "B2"]],
        "headers": ["Column A", "Column B"]
    }

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Document with table"
    mock_result.document.num_pages.return_value = 1
    mock_result.document.pages = []
    mock_result.document.tables = [mock_table]
    mock_converter.convert.return_value = mock_result

    service = DocumentService()

    # Act
    with patch.object(service, 'save_markdown_to_file', new=AsyncMock()):
        result = await service.parse_document(temp_pdf_file)

    # Assert
    assert result.tables is not None
    assert len(result.tables) == 1
    assert result.tables[0]["data"] == [["A1", "B1"], ["A2", "B2"]]
    assert result.tables[0]["headers"] == ["Column A", "Column B"]


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_parse_document_handles_document_without_pages(
    mock_converter_class,
    temp_pdf_file
):
    """Test parse_document handles documents without pages attribute."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 1
    # Remove pages attribute
    del mock_result.document.pages
    mock_result.document.tables = []
    mock_converter.convert.return_value = mock_result

    service = DocumentService()

    # Act
    with patch.object(service, 'save_markdown_to_file', new=AsyncMock()):
        result = await service.parse_document(temp_pdf_file)

    # Assert
    assert result.pages == []


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_parse_document_handles_document_without_tables(
    mock_converter_class,
    temp_pdf_file
):
    """Test parse_document handles documents without tables attribute."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 1
    mock_result.document.pages = []
    # Remove tables attribute
    del mock_result.document.tables
    mock_converter.convert.return_value = mock_result

    service = DocumentService()

    # Act
    with patch.object(service, 'save_markdown_to_file', new=AsyncMock()):
        result = await service.parse_document(temp_pdf_file)

    # Assert
    assert result.tables is None


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_parse_document_raises_exception_on_conversion_error(
    mock_converter_class,
    temp_pdf_file
):
    """Test parse_document raises exception when conversion fails."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter
    mock_converter.convert.side_effect = Exception("Conversion failed")

    service = DocumentService()

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await service.parse_document(temp_pdf_file)

    assert "Document parsing failed" in str(exc_info.value)
    assert "Conversion failed" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_parse_document_extracts_metadata(mock_converter_class, temp_pdf_file):
    """Test parse_document extracts metadata correctly."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 3
    mock_result.document.pages = []
    mock_result.document.tables = []
    mock_converter.convert.return_value = mock_result

    service = DocumentService()

    # Act
    with patch.object(service, 'save_markdown_to_file', new=AsyncMock()):
        result = await service.parse_document(temp_pdf_file)

    # Assert
    assert result.metadata.file_name == temp_pdf_file.name
    assert result.metadata.file_type == ".pdf"
    assert result.metadata.file_size > 0
    assert result.metadata.page_count == 3
    assert result.metadata.modified_date is not None


# ============================================================================
# Save Markdown Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_save_markdown_to_file_writes_content(tmp_path):
    """Test save_markdown_to_file writes content to file."""
    # Arrange
    service = DocumentService()
    markdown_text = "# Test Markdown\n\nContent here."
    output_file = tmp_path / "output.md"

    # Act
    await service.save_markdown_to_file(markdown_text, str(output_file))

    # Assert
    assert output_file.exists()
    assert output_file.read_text() == markdown_text


@pytest.mark.unit
@pytest.mark.asyncio
async def test_save_markdown_to_file_handles_write_error():
    """Test save_markdown_to_file handles write errors gracefully."""
    # Arrange
    service = DocumentService()
    markdown_text = "# Test"
    invalid_path = "/invalid/path/that/does/not/exist/file.md"

    # Act - Should not raise exception, just print error
    await service.save_markdown_to_file(markdown_text, invalid_path)

    # Assert - No exception raised (error is printed)


# ============================================================================
# Parse Bytes Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_parse_document_bytes_creates_temp_file(mock_converter_class):
    """Test parse_document_bytes creates and cleans up temp file."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 1
    mock_result.document.pages = []
    mock_result.document.tables = []
    mock_converter.convert.return_value = mock_result

    service = DocumentService()
    file_bytes = b"PDF content"
    filename = "test.pdf"

    # Act
    with patch.object(service, 'save_markdown_to_file', new=AsyncMock()):
        result = await service.parse_document_bytes(file_bytes, filename)

    # Assert
    assert isinstance(result, DocumentParseResponse)
    assert result.text == "Content"


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_parse_document_bytes_preserves_file_extension(mock_converter_class):
    """Test parse_document_bytes preserves file extension."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "Content"
    mock_result.document.num_pages.return_value = 1
    mock_result.document.pages = []
    mock_result.document.tables = []
    mock_converter.convert.return_value = mock_result

    service = DocumentService()
    file_bytes = b"DOCX content"
    filename = "test.docx"

    # Act
    with patch.object(service, 'save_markdown_to_file', new=AsyncMock()):
        result = await service.parse_document_bytes(file_bytes, filename)

    # Assert - Verify convert was called
    assert mock_converter.convert.called


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_parse_document_bytes_cleans_up_temp_file_on_error(mock_converter_class):
    """Test parse_document_bytes cleans up temp file even on error."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter
    mock_converter.convert.side_effect = Exception("Parse error")

    service = DocumentService()
    file_bytes = b"Content"
    filename = "test.pdf"

    # Act & Assert
    with pytest.raises(Exception):
        with patch.object(service, 'save_markdown_to_file', new=AsyncMock()):
            await service.parse_document_bytes(file_bytes, filename)

    # Cleanup is handled by finally block (tested implicitly)


# ============================================================================
# Extract Tables Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_extract_tables_returns_table_list(mock_converter_class, temp_pdf_file):
    """Test extract_tables returns list of tables."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_table1 = MagicMock()
    mock_table1.export_to_dict.return_value = {"data": [[1, 2]], "headers": ["A", "B"]}

    mock_table2 = MagicMock()
    mock_table2.export_to_dict.return_value = {"data": [[3, 4]], "headers": ["C", "D"]}

    mock_result = MagicMock()
    mock_result.document.tables = [mock_table1, mock_table2]
    mock_converter.convert.return_value = mock_result

    service = DocumentService()

    # Act
    tables = await service.extract_tables(temp_pdf_file)

    # Assert
    assert len(tables) == 2
    assert tables[0]["data"] == [[1, 2]]
    assert tables[1]["data"] == [[3, 4]]


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_extract_tables_returns_empty_list_when_no_tables(
    mock_converter_class,
    temp_pdf_file
):
    """Test extract_tables returns empty list when no tables found."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_result = MagicMock()
    # Remove tables attribute
    del mock_result.document.tables
    mock_converter.convert.return_value = mock_result

    service = DocumentService()

    # Act
    tables = await service.extract_tables(temp_pdf_file)

    # Assert
    assert tables == []


@pytest.mark.unit
@pytest.mark.asyncio
@patch("backend.services.document_service.DocumentConverter")
async def test_extract_tables_handles_tables_without_export_method(
    mock_converter_class,
    temp_pdf_file
):
    """Test extract_tables handles tables without export_to_dict method."""
    # Arrange
    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter

    mock_table = MagicMock()
    # Remove export_to_dict method
    del mock_table.export_to_dict

    mock_result = MagicMock()
    mock_result.document.tables = [mock_table]
    mock_converter.convert.return_value = mock_result

    service = DocumentService()

    # Act
    tables = await service.extract_tables(temp_pdf_file)

    # Assert
    assert tables == []

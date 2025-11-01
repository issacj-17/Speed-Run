"""
Unit test fixtures.

Provides mocks and stubs for isolated unit testing.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from PIL import Image
import numpy as np
import tempfile


# ============================================================================
# Mock Adapter Fixtures (for unit tests)
# ============================================================================


@pytest.fixture
def mock_docling_converter():
    """
    Mock Docling DocumentConverter for unit testing.

    Returns:
        MagicMock: Mocked Docling converter
    """
    mock_converter = MagicMock()

    # Mock convert result
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "# Sample Document\n\nSample text."
    mock_result.pages = []

    mock_converter.convert.return_value = mock_result

    return mock_converter


@pytest.fixture
def mock_spacy_nlp():
    """
    Mock spaCy NLP object for unit testing.

    Returns:
        MagicMock: Mocked spaCy nlp
    """
    mock_nlp = MagicMock()

    # Mock doc
    mock_doc = MagicMock()
    mock_doc.sents = [MagicMock(text="This is a sentence.")]
    mock_doc.ents = []
    mock_doc.__iter__ = MagicMock(return_value=iter([
        MagicMock(text="This", is_alpha=True),
        MagicMock(text="is", is_alpha=True),
        MagicMock(text="a", is_alpha=True),
        MagicMock(text="sentence", is_alpha=True),
    ]))

    mock_nlp.return_value = mock_doc

    return mock_nlp


@pytest.fixture
def mock_pil_image():
    """
    Mock PIL Image for unit testing.

    Returns:
        MagicMock: Mocked PIL Image
    """
    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (1920, 1080)
    mock_image.format = "JPEG"
    mock_image.mode = "RGB"
    mock_image._getexif.return_value = {
        271: "Canon",  # Make
        272: "EOS 5D",  # Model
        306: "2023:01:01 12:00:00",  # DateTime
    }

    return mock_image


# ============================================================================
# Test File Fixtures (for unit tests)
# ============================================================================


@pytest.fixture
def temp_pdf_file():
    """
    Create temporary PDF file for testing.

    Yields:
        Path: Path to temporary PDF
    """
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        # Write minimal PDF content
        f.write(b'%PDF-1.4\n%Test PDF\n')
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_jpg_file():
    """
    Create temporary JPG file for testing.

    Yields:
        Path: Path to temporary JPG
    """
    # Create a simple test image
    img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array, mode='RGB')

    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        img.save(f.name, format='JPEG')
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_text_for_validation():
    """
    Provide sample text with known formatting issues.

    Returns:
        str: Sample text with double spacing and other issues
    """
    return """
    This is a  sample document  with  double spacing.

    It has multiple paragraphs and sentences. Some text may have formatting issues.

    The document should be long enough to test various validation rules.
    """


# ============================================================================
# Data Builder Functions
# ============================================================================


def build_parsed_document_data(**overrides):
    """
    Build ParsedDocument data with sensible defaults.

    Args:
        **overrides: Fields to override

    Returns:
        dict: ParsedDocument data
    """
    from backend.adapters.document_parser.protocol import ParsedDocument

    defaults = {
        "text": "Sample parsed text.",
        "pages": [],
        "tables": [],
        "file_name": "test.pdf",
        "file_type": ".pdf",
        "file_size": 1024,
        "page_count": 1,
        "word_count": 3,
        "processing_time_ms": 100.0,
        "author": None,
        "created_date": None,
        "modified_date": None,
        "metadata": {},
    }
    defaults.update(overrides)
    return ParsedDocument(**defaults)


def build_analyzed_text_data(text: str = "Sample text", **overrides):
    """
    Build AnalyzedText data with sensible defaults.

    Args:
        text: Text content
        **overrides: Fields to override

    Returns:
        dict: AnalyzedText data
    """
    from backend.adapters.nlp.protocol import AnalyzedText

    defaults = {
        "text": text,
        "sentences": [text],
        "entities": [],
        "tokens": text.split(),
        "word_count": len(text.split()),
        "unknown_words": [],
    }
    defaults.update(overrides)
    return AnalyzedText(**defaults)


__all__ = [
    "mock_docling_converter",
    "mock_spacy_nlp",
    "mock_pil_image",
    "temp_pdf_file",
    "temp_jpg_file",
    "sample_text_for_validation",
    "build_parsed_document_data",
    "build_analyzed_text_data",
]

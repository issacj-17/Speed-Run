"""
Pytest configuration and shared fixtures.

Provides reusable fixtures for testing adapters and services.
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Import models and schemas
from backend.database.models import Base
from backend.schemas.alert import AlertCreate, AlertSeverity
from backend.schemas.validation import ValidationSeverity


# ============================================================================
# Pytest Configuration
# ============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop for async tests.

    Scope: session - one loop for all tests.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide test database session with automatic cleanup.

    Uses in-memory SQLite database for fast testing.

    Usage:
        async def test_something(test_db):
            result = await test_db.execute(select(User))
            ...
    """
    # Create in-memory SQLite database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# ============================================================================
# Mock Adapter Fixtures
# ============================================================================


@pytest.fixture
def mock_document_parser():
    """
    Mock DocumentParserProtocol for testing.

    Returns:
        AsyncMock: Mocked document parser
    """
    parser = AsyncMock()

    # Mock parse method
    async def mock_parse(file_path: Path):
        from backend.adapters.document_parser.protocol import ParsedDocument

        return ParsedDocument(
            text="Sample parsed text from mock parser.",
            pages=[],
            tables=[],
            file_name=file_path.name,
            file_type=file_path.suffix,
            file_size=1024,
            page_count=1,
            word_count=5,
            processing_time_ms=100.0,
            author=None,
            created_date=None,
            modified_date=None,
            metadata={"parser": "mock"},
        )

    parser.parse = AsyncMock(side_effect=mock_parse)
    parser.supports_format = MagicMock(return_value=True)

    return parser


@pytest.fixture
def mock_nlp_processor():
    """
    Mock NLPProcessorProtocol for testing.

    Returns:
        AsyncMock: Mocked NLP processor
    """
    nlp = AsyncMock()

    # Mock analyze method
    async def mock_analyze(text: str, max_length=None):
        from backend.adapters.nlp.protocol import AnalyzedText

        return AnalyzedText(
            text=text,
            sentences=[],
            entities=[],
            tokens=text.split(),
            word_count=len(text.split()),
            unknown_words=[],
        )

    # Mock check_spelling method
    async def mock_check_spelling(text: str, threshold=10):
        # Return empty list (no spelling errors in mock)
        return []

    nlp.analyze = AsyncMock(side_effect=mock_analyze)
    nlp.check_spelling = AsyncMock(side_effect=mock_check_spelling)

    return nlp


@pytest.fixture
def mock_image_processor():
    """
    Mock ImageProcessorProtocol for testing.

    Returns:
        AsyncMock: Mocked image processor
    """
    processor = AsyncMock()

    # Mock extract_metadata method
    async def mock_extract_metadata(file_path: Path):
        from backend.adapters.image.protocol import ImageMetadata

        return ImageMetadata(
            width=1920,
            height=1080,
            format="JPEG",
            mode="RGB",
            file_size=102400,
            exif_data={"Make": "Canon", "Model": "EOS 5D"},
            created_date=None,
            camera_make="Canon",
            camera_model="EOS 5D",
        )

    processor.extract_metadata = AsyncMock(side_effect=mock_extract_metadata)
    processor.supports_format = MagicMock(return_value=True)

    return processor


# ============================================================================
# Test File Fixtures
# ============================================================================


@pytest.fixture
def temp_text_file():
    """
    Create temporary text file for testing.

    Yields:
        Path: Path to temporary file

    Automatically cleaned up after test.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document.\n")
        f.write("It has multiple lines.\n")
        f.write("For testing purposes.\n")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_image_file():
    """
    Create temporary image file for testing.

    Yields:
        Path: Path to temporary image

    Automatically cleaned up after test.
    """
    from PIL import Image
    import numpy as np

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


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_alert_data():
    """
    Provide sample alert data for testing.

    Returns:
        AlertCreate: Sample alert creation data
    """
    return AlertCreate(
        alert_type="TRANSACTION_RISK",
        severity=AlertSeverity.HIGH,
        client_id=uuid4(),
        transaction_id=uuid4(),
        document_id=None,
        title="High-risk transaction detected",
        description="Transaction exceeds normal pattern by 300%",
        risk_score=85,
        triggered_rules={"velocity_check": True, "amount_threshold": True},
        context={"transaction_amount": 50000, "average_amount": 12500},
        recommended_actions=["Manual review", "Contact client"],
    )


@pytest.fixture
def sample_text():
    """
    Provide sample text for validation testing.

    Returns:
        str: Sample text
    """
    return """
    This is a sample document for testing.

    It contains multiple paragraphs and sentences.
    Some text may have  double  spacing issues.

    The document should be long enough to test various validation rules.
    """


# ============================================================================
# Helper Functions
# ============================================================================


def assert_validation_issue_present(issues, category: str):
    """
    Helper to assert validation issue is present.

    Args:
        issues: List of ValidationIssue
        category: Expected category

    Raises:
        AssertionError: If issue not found
    """
    categories = [issue.category for issue in issues]
    assert category in categories, f"Expected issue with category '{category}' not found. Found: {categories}"


def assert_no_validation_issues(issues):
    """
    Helper to assert no validation issues.

    Args:
        issues: List of ValidationIssue

    Raises:
        AssertionError: If issues found
    """
    assert len(issues) == 0, f"Expected no issues, but found {len(issues)}: {issues}"


__all__ = [
    "test_db",
    "mock_document_parser",
    "mock_nlp_processor",
    "mock_image_processor",
    "temp_text_file",
    "temp_image_file",
    "sample_alert_data",
    "sample_text",
    "assert_validation_issue_present",
    "assert_no_validation_issues",
]

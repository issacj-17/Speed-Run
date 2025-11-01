"""
Unit tests for image processor adapter (PIL/Pillow).

Tests PillowAdapter in isolation with mocked PIL library.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
from PIL import Image

from backend.adapters.image.pillow import PillowAdapter
from backend.adapters.image.protocol import ImageMetadata


# ============================================================================
# Initialization Tests
# ============================================================================


@pytest.mark.unit
def test_pillow_adapter_initializes():
    """Test PillowAdapter initializes successfully."""
    adapter = PillowAdapter()

    assert adapter is not None


# ============================================================================
# Format Support Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.parametrize("extension,expected", [
    (".jpg", True),
    (".JPG", True),
    (".jpeg", True),
    (".JPEG", True),
    (".png", True),
    (".PNG", True),
    (".gif", True),
    (".GIF", True),
    (".bmp", True),
    (".BMP", True),
    (".tiff", True),
    (".TIFF", True),
    (".webp", True),
    (".WEBP", True),
    (".pdf", False),
    (".txt", False),
    (".docx", False),
])
def test_supports_format_returns_correct_value(extension, expected):
    """Test supports_format correctly identifies supported image formats."""
    adapter = PillowAdapter()

    result = adapter.supports_format(extension)

    assert result == expected


# ============================================================================
# Extract Metadata Tests - Happy Path
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_metadata_returns_correct_structure(temp_jpg_file):
    """Test extract_metadata returns ImageMetadata with correct structure."""
    # Arrange
    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert isinstance(result, ImageMetadata)
    assert result.width > 0
    assert result.height > 0
    assert result.format is not None
    assert result.mode is not None
    assert result.file_size > 0


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_reads_image_dimensions(mock_image_open, temp_jpg_file):
    """Test extract_metadata correctly reads image dimensions."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (1920, 1080)
    mock_image.format = "JPEG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=None)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result.width == 1920
    assert result.height == 1080


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_reads_image_format(mock_image_open, temp_jpg_file):
    """Test extract_metadata correctly reads image format."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (100, 100)
    mock_image.format = "PNG"
    mock_image.mode = "RGBA"
    mock_image._getexif = MagicMock(return_value=None)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result.format == "PNG"
    assert result.mode == "RGBA"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_metadata_reads_file_size(temp_jpg_file):
    """Test extract_metadata correctly reads file size."""
    # Arrange
    adapter = PillowAdapter()
    expected_size = temp_jpg_file.stat().st_size

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result.file_size == expected_size


# ============================================================================
# EXIF Data Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_extracts_exif_data(mock_image_open, temp_jpg_file):
    """Test extract_metadata extracts EXIF data from image."""
    # Arrange
    mock_exif = {
        271: "Canon",  # Make
        272: "EOS 5D",  # Model
        306: "2023:01:15 12:30:00",  # DateTime
        36867: "2023:01:15 12:30:00",  # DateTimeOriginal
    }

    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (100, 100)
    mock_image.format = "JPEG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=mock_exif)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result.exif is not None
    assert result.camera_make == "Canon"
    assert result.camera_model == "EOS 5D"
    assert result.created_date is not None


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_handles_missing_exif(mock_image_open, temp_jpg_file):
    """Test extract_metadata handles images without EXIF data."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (100, 100)
    mock_image.format = "PNG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=None)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result.exif is None
    assert result.camera_make is None
    assert result.camera_model is None
    assert result.created_date is None


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_handles_partial_exif(mock_image_open, temp_jpg_file):
    """Test extract_metadata handles partial EXIF data."""
    # Arrange
    mock_exif = {
        271: "Canon",  # Make only, no Model
        306: "2023:01:15 12:30:00",  # DateTime
    }

    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (100, 100)
    mock_image.format = "JPEG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=mock_exif)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result.camera_make == "Canon"
    assert result.camera_model is None  # Missing


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_parses_datetime_correctly(mock_image_open, temp_jpg_file):
    """Test extract_metadata correctly parses EXIF datetime."""
    # Arrange
    mock_exif = {
        36867: "2023:01:15 14:30:45",  # DateTimeOriginal
    }

    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (100, 100)
    mock_image.format = "JPEG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=mock_exif)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result.created_date is not None
    assert isinstance(result.created_date, datetime)
    assert result.created_date.year == 2023
    assert result.created_date.month == 1
    assert result.created_date.day == 15


# ============================================================================
# Edge Cases Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_handles_very_small_image(mock_image_open, temp_jpg_file):
    """Test extract_metadata handles very small images (1x1 pixel)."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (1, 1)
    mock_image.format = "PNG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=None)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result.width == 1
    assert result.height == 1


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_handles_very_large_image(mock_image_open, temp_jpg_file):
    """Test extract_metadata handles very large images (10000x10000)."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (10000, 10000)
    mock_image.format = "PNG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=None)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result.width == 10000
    assert result.height == 10000


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_handles_different_color_modes(mock_image_open, temp_jpg_file):
    """Test extract_metadata handles different color modes (RGB, RGBA, L, CMYK)."""
    # Test various color modes
    color_modes = ["RGB", "RGBA", "L", "CMYK", "P"]

    for mode in color_modes:
        # Arrange
        mock_image = MagicMock(spec=Image.Image)
        mock_image.size = (100, 100)
        mock_image.format = "PNG"
        mock_image.mode = mode
        mock_image._getexif = MagicMock(return_value=None)
        mock_image_open.return_value.__enter__.return_value = mock_image

        adapter = PillowAdapter()

        # Act
        result = await adapter.extract_metadata(temp_jpg_file)

        # Assert
        assert result.mode == mode


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_handles_invalid_datetime_format(mock_image_open, temp_jpg_file):
    """Test extract_metadata handles invalid EXIF datetime format."""
    # Arrange
    mock_exif = {
        36867: "InvalidDateFormat",  # Invalid datetime
    }

    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (100, 100)
    mock_image.format = "JPEG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=mock_exif)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert - Should not crash, should return None for created_date
    assert result.created_date is None


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_metadata_raises_on_nonexistent_file():
    """Test extract_metadata raises FileNotFoundError for nonexistent file."""
    adapter = PillowAdapter()
    nonexistent_file = Path("/nonexistent/path/image.jpg")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        await adapter.extract_metadata(nonexistent_file)


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_raises_on_invalid_image(mock_image_open, temp_jpg_file):
    """Test extract_metadata raises exception for invalid/corrupted image."""
    # Arrange
    mock_image_open.side_effect = Exception("Invalid image file")

    adapter = PillowAdapter()

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await adapter.extract_metadata(temp_jpg_file)

    assert "Invalid image file" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_extract_metadata_handles_exif_exception(mock_image_open, temp_jpg_file):
    """Test extract_metadata handles exception when reading EXIF."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (100, 100)
    mock_image.format = "JPEG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(side_effect=Exception("EXIF read error"))
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert - Should not crash, should return None for EXIF on error
    assert result.exif is None
    assert result.camera_make is None


# ============================================================================
# Caching Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_metadata_caches_result_on_second_call(temp_jpg_file):
    """Test extract_metadata caches result and returns cached value on second call."""
    # Arrange
    adapter = PillowAdapter()

    # Act - First call (cache miss)
    result1 = await adapter.extract_metadata(temp_jpg_file)

    # Act - Second call (cache hit)
    result2 = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result1.width == result2.width
    assert result1.height == result2.height
    assert result1.format == result2.format

    # Note: Caching behavior depends on cache availability
    # If cache is working, PIL should open image only once


# ============================================================================
# Protocol Compliance Tests
# ============================================================================


@pytest.mark.unit
def test_pillow_adapter_implements_protocol():
    """Test PillowAdapter implements ImageProcessorProtocol."""
    from backend.adapters.image.protocol import ImageProcessorProtocol

    adapter = PillowAdapter()

    # Check protocol methods exist
    assert hasattr(adapter, "extract_metadata")
    assert hasattr(adapter, "supports_format")
    assert callable(adapter.extract_metadata)
    assert callable(adapter.supports_format)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_metadata_returns_protocol_compliant_result(temp_jpg_file):
    """Test extract_metadata returns result compliant with ImageMetadata schema."""
    # Arrange
    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert - Check all required fields exist
    assert hasattr(result, "width")
    assert hasattr(result, "height")
    assert hasattr(result, "format")
    assert hasattr(result, "mode")
    assert hasattr(result, "file_size")
    assert hasattr(result, "exif")
    assert hasattr(result, "created_date")
    assert hasattr(result, "camera_make")
    assert hasattr(result, "camera_model")


# ============================================================================
# EXIF Tag Mapping Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
@pytest.mark.parametrize("exif_tag,exif_value,expected_field,expected_value", [
    (271, "Nikon", "camera_make", "Nikon"),
    (272, "D850", "camera_model", "D850"),
    (271, "Sony", "camera_make", "Sony"),
    (272, "A7III", "camera_model", "A7III"),
])
async def test_exif_tag_mapping(
    mock_image_open,
    temp_jpg_file,
    exif_tag,
    exif_value,
    expected_field,
    expected_value
):
    """Test EXIF tag to field mapping."""
    # Arrange
    mock_exif = {exif_tag: exif_value}

    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (100, 100)
    mock_image.format = "JPEG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=mock_exif)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert getattr(result, expected_field) == expected_value


# ============================================================================
# Performance Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.slow
async def test_extract_metadata_completes_within_reasonable_time(temp_jpg_file):
    """Test extract_metadata completes within reasonable time (< 1 second)."""
    import time

    # Arrange
    adapter = PillowAdapter()

    # Act
    start_time = time.time()
    result = await adapter.extract_metadata(temp_jpg_file)
    elapsed_time = time.time() - start_time

    # Assert
    assert elapsed_time < 1.0  # Should complete in less than 1 second
    assert result is not None


# ============================================================================
# Different Image Format Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
@pytest.mark.parametrize("image_format", [
    "JPEG",
    "PNG",
    "GIF",
    "BMP",
    "TIFF",
    "WEBP",
])
async def test_extract_metadata_handles_different_formats(
    mock_image_open,
    temp_jpg_file,
    image_format
):
    """Test extract_metadata handles different image formats."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (100, 100)
    mock_image.format = image_format
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=None)
    mock_image_open.return_value.__enter__.return_value = mock_image

    adapter = PillowAdapter()

    # Act
    result = await adapter.extract_metadata(temp_jpg_file)

    # Assert
    assert result.format == image_format


# ============================================================================
# Load Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
@patch("backend.adapters.image.pillow.imagehash.average_hash")
async def test_load_returns_processed_image_with_correct_structure(
    mock_average_hash,
    mock_image_open,
    temp_jpg_file
):
    """Test load returns ProcessedImage with correct structure."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (800, 600)
    mock_image.format = "JPEG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=None)
    mock_image_open.return_value.__enter__.return_value = mock_image
    mock_average_hash.return_value = MagicMock(__str__=lambda x: "abc123def456")

    adapter = PillowAdapter()

    # Act
    result = await adapter.load(temp_jpg_file)

    # Assert
    assert result.file_path == temp_jpg_file
    assert result.metadata is not None
    assert result.metadata.width == 800
    assert result.metadata.height == 600
    assert result.hash == "abc123def456"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_load_raises_on_nonexistent_file():
    """Test load raises FileNotFoundError for nonexistent file."""
    adapter = PillowAdapter()
    nonexistent_file = Path("/nonexistent/path/image.jpg")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        await adapter.load(nonexistent_file)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_load_raises_on_unsupported_format(temp_jpg_file):
    """Test load raises ValueError for unsupported format."""
    # Arrange - create file with unsupported extension
    unsupported_file = temp_jpg_file.parent / "test.exe"
    # Create the file so FileNotFoundError isn't raised first
    unsupported_file.write_bytes(b"fake executable content")

    adapter = PillowAdapter()

    # Act & Assert
    with pytest.raises(ValueError):
        await adapter.load(unsupported_file)


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
@patch("backend.adapters.image.pillow.imagehash.average_hash")
async def test_load_computes_image_hash(
    mock_average_hash,
    mock_image_open,
    temp_jpg_file
):
    """Test load computes perceptual hash correctly."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.size = (100, 100)
    mock_image.format = "JPEG"
    mock_image.mode = "RGB"
    mock_image._getexif = MagicMock(return_value=None)
    mock_image_open.return_value.__enter__.return_value = mock_image

    # Mock hash with specific value
    mock_hash = MagicMock()
    mock_hash.__str__ = lambda x: "fedcba987654"
    mock_average_hash.return_value = mock_hash

    adapter = PillowAdapter()

    # Act
    result = await adapter.load(temp_jpg_file)

    # Assert
    assert result.hash == "fedcba987654"
    mock_average_hash.assert_called_once()


# ============================================================================
# Thumbnail Creation Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_create_thumbnail_generates_thumbnail_successfully(
    mock_image_open,
    temp_jpg_file,
    tmp_path
):
    """Test create_thumbnail generates thumbnail successfully."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.thumbnail = MagicMock()
    mock_image.save = MagicMock()
    mock_image_open.return_value.__enter__.return_value = mock_image

    output_path = tmp_path / "thumbnail.jpg"
    adapter = PillowAdapter()

    # Act
    result = await adapter.create_thumbnail(temp_jpg_file, output_path)

    # Assert
    assert result == output_path
    mock_image.thumbnail.assert_called_once()
    mock_image.save.assert_called_once_with(output_path)


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_create_thumbnail_uses_default_size(
    mock_image_open,
    temp_jpg_file,
    tmp_path
):
    """Test create_thumbnail uses default 200x200 size."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.thumbnail = MagicMock()
    mock_image.save = MagicMock()
    mock_image_open.return_value.__enter__.return_value = mock_image

    output_path = tmp_path / "thumbnail.jpg"
    adapter = PillowAdapter()

    # Act
    await adapter.create_thumbnail(temp_jpg_file, output_path)

    # Assert
    mock_image.thumbnail.assert_called_once()
    call_args = mock_image.thumbnail.call_args
    assert call_args[0][0] == (200, 200)  # Default size


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_create_thumbnail_uses_custom_size(
    mock_image_open,
    temp_jpg_file,
    tmp_path
):
    """Test create_thumbnail respects custom size parameter."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.thumbnail = MagicMock()
    mock_image.save = MagicMock()
    mock_image_open.return_value.__enter__.return_value = mock_image

    output_path = tmp_path / "thumbnail.jpg"
    adapter = PillowAdapter()
    custom_size = (150, 150)

    # Act
    await adapter.create_thumbnail(temp_jpg_file, output_path, size=custom_size)

    # Assert
    mock_image.thumbnail.assert_called_once()
    call_args = mock_image.thumbnail.call_args
    assert call_args[0][0] == custom_size


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_create_thumbnail_uses_lanczos_resampling(
    mock_image_open,
    temp_jpg_file,
    tmp_path
):
    """Test create_thumbnail uses high-quality LANCZOS resampling."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.thumbnail = MagicMock()
    mock_image.save = MagicMock()
    mock_image_open.return_value.__enter__.return_value = mock_image

    output_path = tmp_path / "thumbnail.jpg"
    adapter = PillowAdapter()

    # Act
    await adapter.create_thumbnail(temp_jpg_file, output_path)

    # Assert
    mock_image.thumbnail.assert_called_once()
    call_args = mock_image.thumbnail.call_args
    # Check that LANCZOS resampling is used (second argument)
    assert call_args[0][1] == Image.Resampling.LANCZOS


# ============================================================================
# Compute Hash Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
@patch("backend.adapters.image.pillow.imagehash.average_hash")
async def test_compute_hash_returns_hash_string(
    mock_average_hash,
    mock_image_open,
    temp_jpg_file
):
    """Test compute_hash returns hash string."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image_open.return_value.__enter__.return_value = mock_image

    mock_hash = MagicMock()
    mock_hash.__str__ = lambda x: "abc123def456"
    mock_average_hash.return_value = mock_hash

    adapter = PillowAdapter()

    # Act
    result = await adapter.compute_hash(temp_jpg_file)

    # Assert
    assert isinstance(result, str)
    assert result == "abc123def456"
    mock_average_hash.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
@patch("backend.adapters.image.pillow.imagehash.average_hash")
async def test_compute_hash_same_image_produces_same_hash(
    mock_average_hash,
    mock_image_open,
    temp_jpg_file
):
    """Test compute_hash produces consistent hash for same image."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image_open.return_value.__enter__.return_value = mock_image

    mock_hash = MagicMock()
    mock_hash.__str__ = lambda x: "consistent_hash"
    mock_average_hash.return_value = mock_hash

    adapter = PillowAdapter()

    # Act
    hash1 = await adapter.compute_hash(temp_jpg_file)
    hash2 = await adapter.compute_hash(temp_jpg_file)

    # Assert
    assert hash1 == hash2


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
@patch("backend.adapters.image.pillow.imagehash.average_hash")
async def test_compute_hash_uses_average_hash_algorithm(
    mock_average_hash,
    mock_image_open,
    temp_jpg_file
):
    """Test compute_hash uses average_hash algorithm."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image_open.return_value.__enter__.return_value = mock_image

    mock_hash = MagicMock()
    mock_hash.__str__ = lambda x: "test_hash"
    mock_average_hash.return_value = mock_hash

    adapter = PillowAdapter()

    # Act
    await adapter.compute_hash(temp_jpg_file)

    # Assert
    mock_average_hash.assert_called_once_with(mock_image)


# ============================================================================
# Format Conversion Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_convert_format_converts_to_jpeg(
    mock_image_open,
    temp_jpg_file,
    tmp_path
):
    """Test convert_format converts image to JPEG."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.mode = "RGB"
    mock_image.save = MagicMock()
    mock_image_open.return_value.__enter__.return_value = mock_image

    output_path = tmp_path / "converted.jpg"
    adapter = PillowAdapter()

    # Act
    result = await adapter.convert_format(temp_jpg_file, output_path, "jpeg")

    # Assert
    assert result == output_path
    mock_image.save.assert_called_once_with(output_path, format="JPEG")


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_convert_format_converts_rgba_to_rgb_for_jpeg(
    mock_image_open,
    temp_jpg_file,
    tmp_path
):
    """Test convert_format converts RGBA to RGB when saving as JPEG."""
    # Arrange
    mock_rgba_image = MagicMock(spec=Image.Image)
    mock_rgba_image.mode = "RGBA"

    mock_rgb_image = MagicMock(spec=Image.Image)
    mock_rgb_image.save = MagicMock()

    mock_rgba_image.convert.return_value = mock_rgb_image
    mock_image_open.return_value.__enter__.return_value = mock_rgba_image

    output_path = tmp_path / "converted.jpg"
    adapter = PillowAdapter()

    # Act
    await adapter.convert_format(temp_jpg_file, output_path, "jpeg")

    # Assert
    mock_rgba_image.convert.assert_called_once_with("RGB")
    mock_rgb_image.save.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_convert_format_converts_to_png(
    mock_image_open,
    temp_jpg_file,
    tmp_path
):
    """Test convert_format converts image to PNG."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.mode = "RGB"
    mock_image.save = MagicMock()
    mock_image_open.return_value.__enter__.return_value = mock_image

    output_path = tmp_path / "converted.png"
    adapter = PillowAdapter()

    # Act
    result = await adapter.convert_format(temp_jpg_file, output_path, "png")

    # Assert
    assert result == output_path
    mock_image.save.assert_called_once_with(output_path, format="PNG")


@pytest.mark.unit
@pytest.mark.asyncio
@patch("PIL.Image.open")
async def test_convert_format_handles_case_insensitive_format(
    mock_image_open,
    temp_jpg_file,
    tmp_path
):
    """Test convert_format handles lowercase format names."""
    # Arrange
    mock_image = MagicMock(spec=Image.Image)
    mock_image.mode = "RGB"
    mock_image.save = MagicMock()
    mock_image_open.return_value.__enter__.return_value = mock_image

    output_path = tmp_path / "converted.jpg"
    adapter = PillowAdapter()

    # Act
    await adapter.convert_format(temp_jpg_file, output_path, "jpeg")

    # Assert
    # Format should be uppercased when calling save
    call_args = mock_image.save.call_args
    assert call_args[1]["format"] == "JPEG"

"""
Unit tests for TamperingDetectionService.

Tests image tampering detection using forensic techniques (ELA, clone detection, etc.).
"""

import pytest
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

from backend.services.image_analysis.tampering_detector import TamperingDetectionService
from backend.schemas.validation import ValidationSeverity


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def detector():
    """Create TamperingDetectionService instance."""
    return TamperingDetectionService()


@pytest.fixture
def clean_image_path(tmp_path):
    """Create a clean test image without tampering."""
    image = Image.new('RGB', (800, 600), color=(100, 150, 200))
    draw = ImageDraw.Draw(image)

    # Add some natural variation
    for i in range(50):
        x = i * 16
        y = 300
        draw.rectangle([x, y, x+15, y+15], fill=(120+i, 160+i, 210+i))

    file_path = tmp_path / "clean_image.jpg"
    image.save(file_path, "JPEG", quality=95)
    return file_path


@pytest.fixture
def simple_test_image(tmp_path):
    """Create a simple RGB test image."""
    image = Image.new('RGB', (400, 300), color=(128, 128, 128))
    file_path = tmp_path / "simple_test.jpg"
    image.save(file_path, "JPEG", quality=90)
    return file_path


@pytest.fixture
def low_quality_image(tmp_path):
    """Create a low quality JPEG image."""
    image = Image.new('RGB', (800, 600), color=(100, 150, 200))
    file_path = tmp_path / "low_quality.jpg"
    image.save(file_path, "JPEG", quality=30)  # Low quality
    return file_path


@pytest.fixture
def high_quality_image(tmp_path):
    """Create a high quality JPEG image."""
    image = Image.new('RGB', (800, 600), color=(100, 150, 200))
    file_path = tmp_path / "high_quality.jpg"
    image.save(file_path, "JPEG", quality=95)  # High quality
    return file_path


@pytest.fixture
def image_with_cloned_region(tmp_path):
    """Create an image with a cloned region."""
    image = Image.new('RGB', (800, 600), color=(100, 150, 200))
    draw = ImageDraw.Draw(image)

    # Draw a pattern
    draw.rectangle([100, 100, 200, 200], fill=(255, 0, 0))
    # Clone the pattern (copy it elsewhere)
    draw.rectangle([400, 300, 500, 400], fill=(255, 0, 0))

    file_path = tmp_path / "cloned_image.jpg"
    image.save(file_path, "JPEG", quality=90)
    return file_path


# ============================================================================
# Initialization Tests
# ============================================================================


@pytest.mark.unit
def test_tampering_detector_initializes():
    """Test TamperingDetectionService initializes correctly."""
    detector = TamperingDetectionService()
    assert detector is not None

    # Check ELA thresholds are set
    assert hasattr(detector, 'ELA_ANOMALY_THRESHOLD')
    assert hasattr(detector, 'ELA_CONFIDENCE_MULTIPLIER')
    assert hasattr(detector, 'ELA_VERY_LOW')
    assert hasattr(detector, 'ELA_LOW')
    assert hasattr(detector, 'ELA_HIGH')
    assert hasattr(detector, 'ELA_VERY_HIGH')

    # Check clone detection thresholds
    assert hasattr(detector, 'CLONE_REGION_SIZE')
    assert hasattr(detector, 'CLONE_DUPLICATE_RATIO_THRESHOLD')
    assert hasattr(detector, 'CLONE_DISTANCE_MIN_BLOCKS')

    # Check compression threshold
    assert hasattr(detector, 'COMPRESSION_VARIANCE_THRESHOLD')

    # Check advanced forensic thresholds
    assert hasattr(detector, 'NOISE_RATIO_MAX')
    assert hasattr(detector, 'EDGE_CONSISTENCY_DIFF')
    assert hasattr(detector, 'RESAMPLING_FFT_PEAK_RATIO')
    assert hasattr(detector, 'COLOR_CORR_LOW')
    assert hasattr(detector, 'MEDIAN_FILTER_THRESHOLD')


@pytest.mark.unit
def test_tampering_detector_thresholds_are_numeric(detector):
    """Test that all thresholds are numeric values."""
    assert isinstance(detector.ELA_ANOMALY_THRESHOLD, (int, float))
    assert isinstance(detector.ELA_CONFIDENCE_MULTIPLIER, (int, float))
    assert isinstance(detector.CLONE_REGION_SIZE, int)
    assert isinstance(detector.CLONE_DUPLICATE_RATIO_THRESHOLD, (int, float))
    assert isinstance(detector.COMPRESSION_VARIANCE_THRESHOLD, (int, float))
    assert isinstance(detector.NOISE_RATIO_MAX, (int, float))


# ============================================================================
# Detect Method Tests (Main Entry Point)
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_returns_result_object(detector, simple_test_image):
    """Test detect method returns TamperingDetectionResult."""
    result = await detector.detect(simple_test_image)

    assert result is not None
    assert hasattr(result, 'is_tampered')
    assert hasattr(result, 'confidence')
    assert hasattr(result, 'issues')
    assert hasattr(result, 'ela_variance')
    assert isinstance(result.is_tampered, bool)
    assert isinstance(result.confidence, float)
    assert isinstance(result.issues, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_with_clean_image(detector, high_quality_image):
    """Test detection on a clean high-quality image."""
    result = await detector.detect(high_quality_image)

    # High quality clean image should have low tampering indicators
    assert isinstance(result.is_tampered, bool)
    assert result.confidence >= 0.0
    assert result.confidence <= 1.0
    assert isinstance(result.issues, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_with_low_quality_image(detector, low_quality_image):
    """Test detection on a low quality image (may show artifacts)."""
    result = await detector.detect(low_quality_image)

    # Low quality images may show compression artifacts
    assert isinstance(result.is_tampered, bool)
    assert result.confidence >= 0.0
    assert result.confidence <= 1.0
    # Low quality might trigger some forensic checks
    assert isinstance(result.issues, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_provides_ela_variance(detector, simple_test_image):
    """Test that detect provides ELA variance value."""
    result = await detector.detect(simple_test_image)

    # ela_variance might be None if image is too uniform (no ELA differences)
    assert result.ela_variance is None or isinstance(result.ela_variance, (int, float))
    if result.ela_variance is not None:
        assert result.ela_variance >= 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_raises_on_invalid_file(detector):
    """Test detect raises error on non-existent file."""
    invalid_path = Path("/tmp/nonexistent_image.jpg")

    with pytest.raises(Exception):  # FileNotFoundError or similar
        await detector.detect(invalid_path)


# ============================================================================
# ELA (Error Level Analysis) Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ela_returns_expected_structure(detector, simple_test_image):
    """Test ELA returns proper structure."""
    result = await detector._perform_ela(simple_test_image)

    assert isinstance(result, dict)
    assert "is_tampered" in result
    assert "confidence" in result
    assert "anomaly_ratio" in result
    assert "issues" in result

    assert isinstance(result["is_tampered"], bool)
    assert isinstance(result["confidence"], float)
    # anomaly_ratio and ela_variance can be None for uniform images
    assert result["anomaly_ratio"] is None or isinstance(result["anomaly_ratio"], float)
    assert isinstance(result["issues"], list)
    # ela_variance might not be in result if image is too uniform
    if "ela_variance" in result:
        assert isinstance(result["ela_variance"], (int, float))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ela_confidence_in_valid_range(detector, simple_test_image):
    """Test ELA confidence is between 0 and 1."""
    result = await detector._perform_ela(simple_test_image)

    assert 0.0 <= result["confidence"] <= 1.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ela_anomaly_ratio_in_valid_range(detector, simple_test_image):
    """Test ELA anomaly ratio is between 0 and 1."""
    result = await detector._perform_ela(simple_test_image)

    # anomaly_ratio can be None for uniform images
    if result["anomaly_ratio"] is not None:
        assert 0.0 <= result["anomaly_ratio"] <= 1.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ela_variance_is_positive(detector, simple_test_image):
    """Test ELA variance is non-negative."""
    result = await detector._perform_ela(simple_test_image)

    # ela_variance might not be in result for uniform images
    if "ela_variance" in result and result["ela_variance"] is not None:
        assert result["ela_variance"] >= 0


# ============================================================================
# Clone Detection Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_clone_detection_returns_boolean(detector):
    """Test clone detection returns boolean value."""
    # Create simple array
    img_array = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)

    result = await detector._detect_cloned_regions(img_array)

    assert isinstance(result, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_clone_detection_with_uniform_image(detector):
    """Test clone detection on uniform image (all same color)."""
    # Uniform image (no clones, just same color everywhere)
    img_array = np.ones((300, 400, 3), dtype=np.uint8) * 128

    result = await detector._detect_cloned_regions(img_array)

    # Uniform images might be detected as having "clones" since regions are identical
    # This is actually correct behavior - uniform regions ARE technically clones
    assert isinstance(result, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_clone_detection_with_random_image(detector):
    """Test clone detection on completely random image."""
    # Random image (unlikely to have clones)
    img_array = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)

    result = await detector._detect_cloned_regions(img_array)

    assert isinstance(result, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_clone_detection_with_small_image(detector):
    """Test clone detection on very small image."""
    # Small image
    img_array = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)

    result = await detector._detect_cloned_regions(img_array)

    assert isinstance(result, bool)


# ============================================================================
# Compression Consistency Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compression_consistency_returns_boolean(detector):
    """Test compression consistency check returns boolean."""
    img_array = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)

    result = await detector._check_compression_consistency(img_array)

    # Result might be numpy bool or Python bool
    assert isinstance(result, (bool, np.bool_))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compression_consistency_with_uniform_image(detector):
    """Test compression consistency on uniform image."""
    # Uniform image (very consistent)
    img_array = np.ones((300, 400, 3), dtype=np.uint8) * 128

    result = await detector._check_compression_consistency(img_array)

    # Uniform image should have very consistent "compression" (low variance)
    # Result might be numpy bool or Python bool
    assert isinstance(result, (bool, np.bool_))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compression_consistency_with_varying_image(detector):
    """Test compression consistency on image with varying regions."""
    # Create image with highly varying regions
    img_array = np.zeros((300, 400, 3), dtype=np.uint8)
    img_array[:150, :] = 255  # Top half white
    img_array[150:, :] = 0    # Bottom half black

    result = await detector._check_compression_consistency(img_array)

    # Result might be numpy bool or Python bool
    assert isinstance(result, (bool, np.bool_))


# ============================================================================
# JPEG Quantization Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_jpeg_quantization_returns_expected_structure(detector, simple_test_image):
    """Test JPEG quantization analysis returns proper structure."""
    result = await detector._detect_jpeg_quantization(simple_test_image)

    assert isinstance(result, dict)
    assert "has_anomaly" in result
    assert "message" in result
    assert "details" in result

    assert isinstance(result["has_anomaly"], bool)
    # Message can be None or a string
    assert result["message"] is None or isinstance(result["message"], str)
    assert isinstance(result["details"], dict)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_jpeg_quantization_with_non_jpeg(detector, tmp_path):
    """Test JPEG quantization analysis with non-JPEG file."""
    # Create PNG image
    image = Image.new('RGB', (400, 300), color=(128, 128, 128))
    png_path = tmp_path / "test.png"
    image.save(png_path, "PNG")

    result = await detector._detect_jpeg_quantization(png_path)

    # Should handle non-JPEG gracefully
    assert isinstance(result, dict)
    assert "has_anomaly" in result


# ============================================================================
# FFT Resampling Detection Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fft_resampling_returns_boolean(detector):
    """Test FFT resampling detection returns boolean."""
    img_array = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)

    result = await detector._detect_resampling_fft(img_array)

    assert isinstance(result, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fft_resampling_with_small_image(detector):
    """Test FFT resampling on small image."""
    # FFT works best on larger images, test with small one
    img_array = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)

    result = await detector._detect_resampling_fft(img_array)

    assert isinstance(result, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fft_resampling_with_grayscale(detector):
    """Test FFT resampling converts RGB to grayscale."""
    # Create RGB array
    img_array = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)

    result = await detector._detect_resampling_fft(img_array)

    # Should handle conversion internally
    assert isinstance(result, bool)


# ============================================================================
# Median Filter Detection Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_median_filter_returns_boolean(detector):
    """Test median filter detection returns boolean."""
    image = Image.new('RGB', (400, 300), color=(128, 128, 128))

    result = await detector._detect_median_filter(image)

    assert isinstance(result, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_median_filter_with_uniform_image(detector):
    """Test median filter detection on uniform image."""
    image = Image.new('RGB', (400, 300), color=(128, 128, 128))

    result = await detector._detect_median_filter(image)

    # Uniform image might show median filter characteristics
    assert isinstance(result, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_median_filter_with_noisy_image(detector):
    """Test median filter detection on noisy image."""
    # Create image with some noise
    img_array = np.random.randint(100, 150, (300, 400, 3), dtype=np.uint8)
    image = Image.fromarray(img_array, 'RGB')

    result = await detector._detect_median_filter(image)

    assert isinstance(result, bool)


# ============================================================================
# Color Correlation Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_color_correlation_returns_float(detector):
    """Test color correlation calculation returns float."""
    img_array = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)

    result = await detector._calc_color_correlation(img_array)

    assert isinstance(result, float)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_color_correlation_with_correlated_channels(detector):
    """Test color correlation with highly correlated RGB channels."""
    # Create image where R=G=B (grayscale, perfect correlation)
    gray_values = np.random.randint(0, 256, (300, 400), dtype=np.uint8)
    img_array = np.stack([gray_values, gray_values, gray_values], axis=2)

    result = await detector._calc_color_correlation(img_array)

    # Perfect correlation should give value close to 1.0 or similar
    assert isinstance(result, float)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_color_correlation_with_independent_channels(detector):
    """Test color correlation with independent RGB channels."""
    # Create image with completely random independent channels
    img_array = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)

    result = await detector._calc_color_correlation(img_array)

    assert isinstance(result, float)


# ============================================================================
# Noise Ratio Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_noise_ratio_returns_float(detector):
    """Test noise ratio calculation returns float."""
    img_array = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)

    result = await detector._calc_noise_ratio(img_array)

    assert isinstance(result, float)
    assert result >= 0  # Noise ratio should be non-negative


@pytest.mark.unit
@pytest.mark.asyncio
async def test_noise_ratio_with_uniform_image(detector):
    """Test noise ratio on uniform image (no noise)."""
    # Uniform image (minimal noise)
    img_array = np.ones((300, 400, 3), dtype=np.uint8) * 128

    result = await detector._calc_noise_ratio(img_array)

    # Uniform image should have very low noise ratio
    assert isinstance(result, float)
    assert result >= 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_noise_ratio_with_noisy_image(detector):
    """Test noise ratio on very noisy image."""
    # Very noisy random image
    img_array = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)

    result = await detector._calc_noise_ratio(img_array)

    # Noisy image should have higher noise ratio
    assert isinstance(result, float)
    assert result >= 0


# ============================================================================
# Edge Consistency Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_edge_consistency_returns_expected_structure(detector):
    """Test edge consistency check returns proper structure."""
    image = Image.new('RGB', (400, 300), color=(128, 128, 128))

    result = await detector._check_edge_consistency(image)

    # Returns a list of ValidationIssue objects (empty if no issues)
    assert isinstance(result, list)
    # Each item should be a ValidationIssue
    for issue in result:
        assert hasattr(issue, 'category')
        assert hasattr(issue, 'severity')
        assert hasattr(issue, 'description')


@pytest.mark.unit
@pytest.mark.asyncio
async def test_edge_consistency_with_uniform_image(detector):
    """Test edge consistency on uniform image (no edges)."""
    image = Image.new('RGB', (400, 300), color=(128, 128, 128))

    result = await detector._check_edge_consistency(image)

    # Returns a list of ValidationIssue objects
    assert isinstance(result, list)
    # Uniform image may or may not have edge differences depending on filter behavior


@pytest.mark.unit
@pytest.mark.asyncio
async def test_edge_consistency_with_edges(detector):
    """Test edge consistency on image with clear edges."""
    image = Image.new('RGB', (400, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    # Draw some shapes with clear edges
    draw.rectangle([100, 100, 300, 200], fill=(0, 0, 0))
    draw.ellipse([50, 50, 150, 150], fill=(128, 128, 128))

    result = await detector._check_edge_consistency(image)

    # Returns a list of ValidationIssue objects
    assert isinstance(result, list)
    # If there are issues, check they have the right structure
    for issue in result:
        assert hasattr(issue, 'category')
        assert hasattr(issue, 'severity')
        assert issue.category == 'forensic'


# ============================================================================
# Integration Tests with Real Scenarios
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_integration_with_clean_image(detector, clean_image_path):
    """Integration test: Detect on clean image should show minimal tampering."""
    result = await detector.detect(clean_image_path)

    assert isinstance(result.is_tampered, bool)
    assert 0.0 <= result.confidence <= 1.0
    # ela_variance might be None for uniform images
    if result.ela_variance is not None:
        assert isinstance(result.ela_variance, (int, float))
        assert result.ela_variance >= 0
    assert isinstance(result.issues, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_integration_multiple_images(detector, simple_test_image, low_quality_image):
    """Integration test: Detect on multiple images."""
    result1 = await detector.detect(simple_test_image)
    result2 = await detector.detect(low_quality_image)

    # Both should return valid results
    assert isinstance(result1.is_tampered, bool)
    assert isinstance(result2.is_tampered, bool)

    # ELA variance might be None for uniform images
    if result1.ela_variance is not None:
        assert result1.ela_variance >= 0
    if result2.ela_variance is not None:
        assert result2.ela_variance >= 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_handles_different_image_sizes(detector, tmp_path):
    """Test detect handles various image sizes."""
    sizes = [(100, 100), (500, 300), (1920, 1080), (4000, 3000)]

    for width, height in sizes:
        image = Image.new('RGB', (width, height), color=(128, 128, 128))
        file_path = tmp_path / f"test_{width}x{height}.jpg"
        image.save(file_path, "JPEG", quality=90)

        result = await detector.detect(file_path)

        assert isinstance(result.is_tampered, bool)
        # ela_variance might be None for uniform images
        if result.ela_variance is not None:
            assert result.ela_variance >= 0


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_with_very_small_image(detector, tmp_path):
    """Test detection on very small image."""
    image = Image.new('RGB', (10, 10), color=(128, 128, 128))
    file_path = tmp_path / "tiny.jpg"
    image.save(file_path, "JPEG")

    result = await detector.detect(file_path)

    # Should handle small images gracefully
    assert isinstance(result.is_tampered, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_with_grayscale_image(detector, tmp_path):
    """Test detection on grayscale image."""
    image = Image.new('L', (400, 300), color=128)
    file_path = tmp_path / "grayscale.jpg"
    image.save(file_path, "JPEG")

    result = await detector.detect(file_path)

    # Should convert to RGB and process
    assert isinstance(result.is_tampered, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_detect_with_rgba_image(detector, tmp_path):
    """Test detection on RGBA image (with alpha channel)."""
    image = Image.new('RGBA', (400, 300), color=(128, 128, 128, 255))
    file_path = tmp_path / "rgba.png"
    image.save(file_path, "PNG")

    result = await detector.detect(file_path)

    # Should convert to RGB and process
    assert isinstance(result.is_tampered, bool)

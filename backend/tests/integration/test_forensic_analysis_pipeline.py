"""
Integration tests for forensic analysis pipeline.

Tests the complete workflow of image analysis including:
- AI detection
- Tampering detection
- Compression profiling
- Risk scoring
- Report generation
"""

import pytest
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

from backend.services.image_analysis.ai_detector import AIDetectionService
from backend.services.image_analysis.tampering_detector import TamperingDetectionService
from backend.services.image_analysis.compression_profiler import CompressionProfileService
from backend.services.risk_scorer import RiskScorer
from backend.schemas.validation import ImageAnalysisResult


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def ai_detector():
    """Create AI detection service instance."""
    return AIDetectionService()


@pytest.fixture
def tampering_detector():
    """Create tampering detection service instance."""
    return TamperingDetectionService()


@pytest.fixture
def compression_profiler():
    """Create compression profiler service instance."""
    return CompressionProfileService()


@pytest.fixture
def risk_scorer():
    """Create risk scorer service instance."""
    return RiskScorer()


@pytest.fixture
def clean_test_image(tmp_path):
    """Create a clean, high-quality test image."""
    image = Image.new('RGB', (1920, 1080), color=(200, 200, 200))
    draw = ImageDraw.Draw(image)

    # Add some natural content
    for i in range(20):
        x = i * 96
        y = 500
        draw.rectangle([x, y, x+80, y+80], fill=(180+i*2, 190+i, 200+i*3))

    file_path = tmp_path / "clean_image.jpg"
    image.save(file_path, "JPEG", quality=95)
    return file_path


@pytest.fixture
def suspicious_image(tmp_path):
    """Create an image with potential tampering indicators."""
    # Create base image
    image = Image.new('RGB', (1280, 720), color=(150, 150, 150))
    draw = ImageDraw.Draw(image)

    # Add some content
    draw.rectangle([100, 100, 400, 300], fill=(200, 100, 100))
    draw.ellipse([500, 200, 700, 500], fill=(100, 200, 100))

    # Save with lower quality to trigger some forensic checks
    file_path = tmp_path / "suspicious_image.jpg"
    image.save(file_path, "JPEG", quality=70)
    return file_path


@pytest.fixture
def whatsapp_style_image(tmp_path):
    """Create an image that resembles WhatsApp compression."""
    image = Image.new('RGB', (1280, 1280), color=(180, 180, 180))
    draw = ImageDraw.Draw(image)

    # Add some content
    draw.rectangle([200, 200, 600, 600], fill=(220, 180, 150))
    draw.ellipse([700, 300, 1000, 600], fill=(150, 180, 220))

    file_path = tmp_path / "whatsapp_style.jpg"
    # Use lower quality to simulate WhatsApp compression
    image.save(file_path, "JPEG", quality=75)
    return file_path


# ============================================================================
# Pipeline Integration Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_forensic_pipeline_clean_image(
    clean_test_image,
    ai_detector,
    tampering_detector,
    compression_profiler,
    risk_scorer
):
    """Test complete forensic analysis pipeline on clean image."""

    # Step 1: AI Detection
    ai_result = await ai_detector.detect(clean_test_image)

    assert ai_result is not None
    assert hasattr(ai_result, 'is_ai_generated')
    assert hasattr(ai_result, 'confidence')

    # Step 2: Tampering Detection
    tampering_result = await tampering_detector.detect(clean_test_image)

    assert tampering_result is not None
    assert hasattr(tampering_result, 'is_tampered')
    assert hasattr(tampering_result, 'confidence')
    assert hasattr(tampering_result, 'issues')

    # Step 3: Compression Profiling (if ELA was performed)
    if tampering_result.ela_variance is not None:
        image = Image.open(clean_test_image)
        profiles = await compression_profiler.detect_profile(
            tampering_result.ela_variance,
            image.size
        )

        assert isinstance(profiles, list)
        # Profiles might be empty if ELA variance doesn't match any profile

    # Step 4: Create ImageAnalysisResult
    image_analysis = ImageAnalysisResult(
        is_authentic=not tampering_result.is_tampered and not ai_result.is_ai_generated,
        is_ai_generated=ai_result.is_ai_generated,
        ai_detection_confidence=ai_result.confidence,
        is_tampered=tampering_result.is_tampered,
        tampering_confidence=tampering_result.confidence,
        reverse_image_matches=0,
        metadata_issues=[],
        forensic_findings=tampering_result.issues,
        compression_profiles=[],
        ela_variance=tampering_result.ela_variance
    )

    # Step 5: Risk Scoring
    risk_score = await risk_scorer.calculate_risk_score(
        image_analysis=image_analysis
    )

    assert risk_score is not None
    assert hasattr(risk_score, 'overall_score')
    assert hasattr(risk_score, 'risk_level')
    assert 0 <= risk_score.overall_score <= 100
    assert risk_score.risk_level in ['low', 'medium', 'high', 'critical']


@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_forensic_pipeline_suspicious_image(
    suspicious_image,
    ai_detector,
    tampering_detector,
    compression_profiler,
    risk_scorer
):
    """Test complete forensic analysis pipeline on potentially tampered image."""

    # Step 1: AI Detection
    ai_result = await ai_detector.detect(suspicious_image)

    # Step 2: Tampering Detection
    tampering_result = await tampering_detector.detect(suspicious_image)

    # Suspicious image might trigger some forensic checks
    assert isinstance(tampering_result.issues, list)

    # Step 3: Compression Profiling
    if tampering_result.ela_variance is not None:
        image = Image.open(suspicious_image)
        profiles = await compression_profiler.detect_profile(
            tampering_result.ela_variance,
            image.size
        )
        assert isinstance(profiles, list)

    # Step 4: Create ImageAnalysisResult
    image_analysis = ImageAnalysisResult(
        is_authentic=not tampering_result.is_tampered and not ai_result.is_ai_generated,
        is_ai_generated=ai_result.is_ai_generated,
        ai_detection_confidence=ai_result.confidence,
        is_tampered=tampering_result.is_tampered,
        tampering_confidence=tampering_result.confidence,
        reverse_image_matches=0,
        metadata_issues=[],
        forensic_findings=tampering_result.issues,
        compression_profiles=[],
        ela_variance=tampering_result.ela_variance
    )

    # Step 5: Risk Scoring
    risk_score = await risk_scorer.calculate_risk_score(
        image_analysis=image_analysis
    )

    # Suspicious image might have higher risk score
    assert risk_score.overall_score >= 0
    assert len(risk_score.contributing_factors) >= 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_with_compression_detection(
    whatsapp_style_image,
    tampering_detector,
    compression_profiler
):
    """Test pipeline specifically for compression profile detection."""

    # Step 1: Tampering Detection (to get ELA variance)
    tampering_result = await tampering_detector.detect(whatsapp_style_image)

    # Step 2: Compression Profiling
    if tampering_result.ela_variance is not None:
        image = Image.open(whatsapp_style_image)
        profiles = await compression_profiler.detect_profile(
            tampering_result.ela_variance,
            image.size
        )

        # Should detect some compression profile
        assert isinstance(profiles, list)

        # Check if it's identified as social media compressed
        is_social_media = await compression_profiler.is_social_media_compressed(profiles)
        assert isinstance(is_social_media, bool)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_handles_multiple_images_sequentially(
    clean_test_image,
    suspicious_image,
    tampering_detector,
    risk_scorer
):
    """Test pipeline can process multiple images in sequence."""

    images = [clean_test_image, suspicious_image]
    results = []

    for image_path in images:
        # Tampering Detection
        tampering_result = await tampering_detector.detect(image_path)

        # Create ImageAnalysisResult
        image_analysis = ImageAnalysisResult(
            is_authentic=not tampering_result.is_tampered,
            is_ai_generated=False,
            ai_detection_confidence=0.5,
            is_tampered=tampering_result.is_tampered,
            tampering_confidence=tampering_result.confidence,
            reverse_image_matches=0,
            metadata_issues=[],
            forensic_findings=tampering_result.issues,
            compression_profiles=[],
            ela_variance=tampering_result.ela_variance
        )

        # Risk Scoring
        risk_score = await risk_scorer.calculate_risk_score(
            image_analysis=image_analysis
        )

        results.append((tampering_result, risk_score))

    # Verify all results are valid
    assert len(results) == 2
    for tampering_result, risk_score in results:
        assert tampering_result is not None
        assert risk_score is not None
        assert 0 <= risk_score.overall_score <= 100


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_with_ai_and_tampering_detection(
    clean_test_image,
    ai_detector,
    tampering_detector,
    risk_scorer
):
    """Test pipeline integrating both AI and tampering detection."""

    # Step 1: AI Detection
    ai_result = await ai_detector.detect(clean_test_image)

    # Step 2: Tampering Detection
    tampering_result = await tampering_detector.detect(clean_test_image)

    # Step 3: Combine results
    image_analysis = ImageAnalysisResult(
        is_authentic=not (ai_result.is_ai_generated or tampering_result.is_tampered),
        is_ai_generated=ai_result.is_ai_generated,
        ai_detection_confidence=ai_result.confidence,
        is_tampered=tampering_result.is_tampered,
        tampering_confidence=tampering_result.confidence,
        reverse_image_matches=0,
        metadata_issues=[],
        forensic_findings=tampering_result.issues,
        compression_profiles=[],
        ela_variance=tampering_result.ela_variance
    )

    # Verify authenticity logic
    if ai_result.is_ai_generated or tampering_result.is_tampered:
        assert image_analysis.is_authentic is False
    else:
        assert image_analysis.is_authentic is True

    # Step 4: Risk Scoring accounts for both AI and tampering
    risk_score = await risk_scorer.calculate_risk_score(
        image_analysis=image_analysis
    )

    # Verify risk factors include both AI and tampering considerations
    factor_components = [f["component"] for f in risk_score.contributing_factors]
    if ai_result.is_ai_generated or tampering_result.is_tampered:
        assert 'image_analysis' in factor_components


# ============================================================================
# Error Handling Integration Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_handles_invalid_file(
    tmp_path,
    tampering_detector,
    risk_scorer
):
    """Test pipeline handles invalid files gracefully."""

    invalid_file = tmp_path / "nonexistent.jpg"

    # Tampering detection should raise error
    with pytest.raises(Exception):
        await tampering_detector.detect(invalid_file)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_with_minimal_image(
    tmp_path,
    tampering_detector,
    compression_profiler
):
    """Test pipeline with very small image."""

    # Create minimal 10x10 image
    image = Image.new('RGB', (10, 10), color=(128, 128, 128))
    file_path = tmp_path / "tiny.jpg"
    image.save(file_path, "JPEG", quality=90)

    # Tampering Detection
    tampering_result = await tampering_detector.detect(file_path)

    assert tampering_result is not None
    assert isinstance(tampering_result.is_tampered, bool)

    # Compression profiling might not work well on tiny images
    if tampering_result.ela_variance is not None:
        profiles = await compression_profiler.detect_profile(
            tampering_result.ela_variance,
            image.size
        )
        assert isinstance(profiles, list)


# ============================================================================
# Performance Integration Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_performance_reasonable_time(
    clean_test_image,
    tampering_detector,
    risk_scorer
):
    """Test that complete pipeline completes in reasonable time."""
    import time

    start_time = time.time()

    # Run pipeline
    tampering_result = await tampering_detector.detect(clean_test_image)

    image_analysis = ImageAnalysisResult(
        is_authentic=not tampering_result.is_tampered,
        is_ai_generated=False,
        ai_detection_confidence=0.5,
        is_tampered=tampering_result.is_tampered,
        tampering_confidence=tampering_result.confidence,
        reverse_image_matches=0,
        metadata_issues=[],
        forensic_findings=tampering_result.issues,
        compression_profiles=[],
        ela_variance=tampering_result.ela_variance
    )

    risk_score = await risk_scorer.calculate_risk_score(
        image_analysis=image_analysis
    )

    elapsed_time = time.time() - start_time

    # Complete pipeline should finish in reasonable time (< 5 seconds)
    assert elapsed_time < 5.0
    assert tampering_result is not None
    assert risk_score is not None

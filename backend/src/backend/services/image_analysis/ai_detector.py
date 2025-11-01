"""
AI detection service.

Single Responsibility: Detect AI-generated images using heuristic analysis.
"""

import asyncio
from pathlib import Path
from typing import List, Optional

import numpy as np
from PIL import Image

from backend.adapters.image import ImageProcessorProtocol
from backend.schemas.image_analysis import AIDetectionResult
from backend.logging import get_logger

logger = get_logger(__name__)


class AIDetectionService:
    """
    Service for detecting AI-generated images.

    Responsibilities:
    - Analyze noise levels (AI images often have low noise)
    - Calculate color distribution entropy
    - Check edge consistency
    - Detect AI-specific artifacts (perfect symmetry, etc.)

    Note: In production, this should use a specialized ML model.
    Current implementation uses heuristic analysis.
    """

    # Detection thresholds
    LOW_NOISE_THRESHOLD = 5.0
    LOW_ENTROPY_THRESHOLD = 5.0
    HIGH_EDGE_CONSISTENCY_THRESHOLD = 0.8
    SYMMETRY_DIFFERENCE_THRESHOLD = 5.0

    # Confidence weights
    NOISE_WEIGHT = 0.3
    ENTROPY_WEIGHT = 0.2
    EDGE_WEIGHT = 0.2
    ARTIFACT_WEIGHT = 0.3

    def __init__(self, image_processor: Optional[ImageProcessorProtocol] = None):
        """
        Initialize AI detection service.

        Args:
            image_processor: Image processor for image loading (injected)
        """
        self.image_processor = image_processor
        logger.info("ai_detection_service_initialized", has_processor=image_processor is not None)

    async def detect(self, file_path: Path) -> AIDetectionResult:
        """
        Detect if image is AI-generated.

        Args:
            file_path: Path to the image file

        Returns:
            AIDetectionResult with detection analysis
        """
        logger.info("ai_detection_started", file_name=file_path.name)

        # Load image
        image = await asyncio.to_thread(Image.open, file_path)
        img_array = await asyncio.to_thread(lambda: np.array(image.convert("RGB")))

        detection_factors = []
        confidence_score = 0.0

        # Check 1: Noise analysis
        noise_level = await self._calculate_noise_level(img_array)
        if noise_level < self.LOW_NOISE_THRESHOLD:
            confidence_score += self.NOISE_WEIGHT
            detection_factors.append(f"Low noise level ({noise_level:.2f})")

        # Check 2: Color entropy
        color_entropy = await self._calculate_color_entropy(img_array)
        if color_entropy < self.LOW_ENTROPY_THRESHOLD:
            confidence_score += self.ENTROPY_WEIGHT
            detection_factors.append(f"Low color entropy ({color_entropy:.2f})")

        # Check 3: Edge consistency
        edge_score = await self._analyze_edges(img_array)
        if edge_score > self.HIGH_EDGE_CONSISTENCY_THRESHOLD:
            confidence_score += self.EDGE_WEIGHT
            detection_factors.append(f"High edge consistency ({edge_score:.2f})")

        # Check 4: AI artifacts
        has_ai_artifacts = await self._check_ai_artifacts(img_array)
        if has_ai_artifacts:
            confidence_score += self.ARTIFACT_WEIGHT
            detection_factors.append("Perfect symmetry detected")

        # Normalize confidence
        final_confidence = min(confidence_score, 1.0)

        # Determine if AI-generated (threshold: 0.5)
        is_ai_generated = final_confidence > 0.5

        result = AIDetectionResult(
            is_ai_generated=is_ai_generated,
            confidence=round(final_confidence, 3),
            noise_level=round(noise_level, 3),
            color_entropy=round(color_entropy, 3),
            edge_consistency_score=round(edge_score, 3),
            has_ai_artifacts=has_ai_artifacts,
            detection_factors=detection_factors,
        )

        logger.info(
            "ai_detection_completed",
            file_name=file_path.name,
            is_ai_generated=result.is_ai_generated,
            confidence=result.confidence,
            factor_count=len(detection_factors),
        )

        return result

    async def _calculate_noise_level(self, img_array: np.ndarray) -> float:
        """Calculate noise level using Laplacian variance."""

        def _compute():
            gray = np.mean(img_array, axis=2).astype(np.uint8)

            # Simple Laplacian kernel
            laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])

            try:
                from scipy.ndimage import convolve

                variance = np.var(convolve(gray, laplacian))
                return float(variance)
            except ImportError:
                # Fallback: manual convolution (slower)
                logger.warning("scipy_not_available", fallback="manual_convolution")
                return 10.0  # Assume normal noise level

        return await asyncio.to_thread(_compute)

    async def _calculate_color_entropy(self, img_array: np.ndarray) -> float:
        """Calculate color distribution entropy."""

        def _compute():
            pixels = img_array.reshape(-1, 3)

            entropy_sum = 0.0
            for channel in range(3):
                hist, _ = np.histogram(pixels[:, channel], bins=256, range=(0, 256))
                hist = hist / hist.sum()  # Normalize
                hist = hist[hist > 0]  # Remove zeros
                entropy = -np.sum(hist * np.log2(hist))
                entropy_sum += entropy

            return entropy_sum / 3  # Average across channels

        return await asyncio.to_thread(_compute)

    async def _analyze_edges(self, img_array: np.ndarray) -> float:
        """Analyze edge consistency (AI images often have very smooth edges)."""

        def _compute():
            gray = np.mean(img_array, axis=2).astype(np.uint8)

            # Simple gradient-based edge detection
            grad_x = np.diff(gray, axis=1)
            grad_y = np.diff(gray, axis=0)

            # Calculate edge strength
            edge_strength = np.mean(np.abs(grad_x)) + np.mean(np.abs(grad_y))

            # Normalize to 0-1 range (heuristic)
            normalized = min(edge_strength / 50.0, 1.0)

            return normalized

        return await asyncio.to_thread(_compute)

    async def _check_ai_artifacts(self, img_array: np.ndarray) -> bool:
        """Check for artifacts typical of AI-generated images (e.g., perfect symmetry)."""

        def _compute():
            height, width = img_array.shape[:2]

            # Check for perfect left-right symmetry (common in AI faces)
            left_half = img_array[:, : width // 2]
            right_half = np.fliplr(img_array[:, width // 2 :])

            # Ensure same dimensions
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]

            # Calculate similarity
            difference = np.mean(np.abs(left_half.astype(float) - right_half.astype(float)))

            # If nearly identical, might be AI-generated
            is_perfectly_symmetric = difference < self.SYMMETRY_DIFFERENCE_THRESHOLD

            return is_perfectly_symmetric

        return await asyncio.to_thread(_compute)


__all__ = ["AIDetectionService"]

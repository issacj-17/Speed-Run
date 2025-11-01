"""
Tampering detection service.

Single Responsibility: Detect image tampering using forensic techniques.
"""

import asyncio
import io
import hashlib
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageChops, ImageEnhance

from backend.schemas.image_analysis import TamperingDetectionResult
from backend.schemas.validation import ValidationIssue, ValidationSeverity
from backend.logging import get_logger

logger = get_logger(__name__)


class TamperingDetectionService:
    """
    Service for detecting image tampering.

    Responsibilities:
    - Error Level Analysis (ELA)
    - Detect cloned/copied regions
    - Check compression consistency
    - Identify manipulation indicators
    """

    # ELA thresholds
    ELA_ANOMALY_THRESHOLD = 0.15  # 15% anomalous pixels
    ELA_CONFIDENCE_MULTIPLIER = 3.0

    # Clone detection thresholds
    CLONE_REGION_SIZE = 32
    CLONE_DUPLICATE_RATIO_THRESHOLD = 0.05

    # Compression consistency threshold
    COMPRESSION_VARIANCE_THRESHOLD = 1000

    def __init__(self):
        """Initialize tampering detection service."""
        logger.info("tampering_detection_service_initialized")

    async def detect(self, file_path: Path) -> TamperingDetectionResult:
        """
        Detect image tampering using multiple forensic techniques.

        Args:
            file_path: Path to the image file

        Returns:
            TamperingDetectionResult with tampering analysis
        """
        logger.info("tampering_detection_started", file_name=file_path.name)

        issues: List[ValidationIssue] = []

        # 1. Error Level Analysis (ELA)
        ela_result = await self._perform_ela(file_path)
        is_tampered_ela = ela_result["is_tampered"]
        ela_confidence = ela_result["confidence"]
        ela_anomaly_ratio = ela_result["anomaly_ratio"]
        issues.extend(ela_result["issues"])

        # 2. Load image for other checks
        image = await asyncio.to_thread(Image.open, file_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        img_array = await asyncio.to_thread(lambda: np.array(image))

        # 3. Clone detection
        has_clones = await self._detect_cloned_regions(img_array)
        if has_clones:
            issues.append(
                ValidationIssue(
                    category="forensic",
                    severity=ValidationSeverity.HIGH,
                    description="Detected potentially cloned/copied regions in image",
                    details={"detection_method": "region_hashing"},
                )
            )

        # 4. Compression consistency
        compression_consistent = await self._check_compression_consistency(img_array)
        if not compression_consistent:
            issues.append(
                ValidationIssue(
                    category="forensic",
                    severity=ValidationSeverity.MEDIUM,
                    description="Inconsistent compression levels detected across image",
                    details={"detection_method": "variance_analysis"},
                )
            )

        # Overall tampering verdict
        is_tampered = is_tampered_ela or has_clones or not compression_consistent

        # Calculate overall confidence
        if is_tampered_ela:
            confidence = ela_confidence
        elif has_clones or not compression_consistent:
            confidence = 0.6  # Medium confidence for other indicators
        else:
            confidence = 0.0

        result = TamperingDetectionResult(
            is_tampered=is_tampered,
            confidence=round(confidence, 3),
            ela_performed=ela_result["ela_performed"],
            ela_anomaly_ratio=ela_anomaly_ratio,
            has_cloned_regions=has_clones,
            compression_consistent=compression_consistent,
            issues=issues,
        )

        logger.info(
            "tampering_detection_completed",
            file_name=file_path.name,
            is_tampered=result.is_tampered,
            confidence=result.confidence,
            issue_count=len(issues),
        )

        return result

    async def _perform_ela(self, file_path: Path) -> dict:
        """
        Perform Error Level Analysis (ELA).

        ELA identifies areas with different compression levels, indicating manipulation.
        """

        def _compute_ela():
            try:
                # Load original image
                original = Image.open(file_path)

                # Convert to RGB
                if original.mode != "RGB":
                    original = original.convert("RGB")

                # Save at 90% quality
                temp_buffer = io.BytesIO()
                original.save(temp_buffer, format="JPEG", quality=90)
                temp_buffer.seek(0)

                # Reload compressed image
                compressed = Image.open(temp_buffer)

                # Calculate difference (ELA)
                ela_image = ImageChops.difference(original, compressed)

                # Enhance to make differences more visible
                extrema = ela_image.getextrema()
                max_diff = max([ex[1] for ex in extrema])

                if max_diff == 0:
                    # No differences found
                    return {
                        "ela_performed": True,
                        "is_tampered": False,
                        "confidence": 0.0,
                        "anomaly_ratio": None,
                        "issues": [],
                    }

                scale = 255.0 / max_diff
                ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

                # Convert to numpy for analysis
                ela_array = np.array(ela_image)

                # Calculate statistics
                mean_error = np.mean(ela_array)
                std_error = np.std(ela_array)

                # Detect anomalous regions (high error levels)
                threshold = mean_error + 2 * std_error
                anomalous_pixels = np.sum(ela_array > threshold)
                total_pixels = ela_array.size
                anomaly_ratio = anomalous_pixels / total_pixels

                # Determine tampering likelihood
                is_tampered = anomaly_ratio > self.ELA_ANOMALY_THRESHOLD

                # Calculate confidence
                confidence = min(anomaly_ratio * self.ELA_CONFIDENCE_MULTIPLIER, 1.0)

                issues = []
                if is_tampered:
                    issues.append(
                        ValidationIssue(
                            category="forensic",
                            severity=ValidationSeverity.CRITICAL,
                            description="Image shows signs of tampering (ELA analysis)",
                            details={
                                "anomaly_ratio": round(anomaly_ratio, 4),
                                "mean_error": round(float(mean_error), 2),
                                "detection_method": "error_level_analysis",
                            },
                        )
                    )

                return {
                    "ela_performed": True,
                    "is_tampered": is_tampered,
                    "confidence": confidence,
                    "anomaly_ratio": round(anomaly_ratio, 4) if anomaly_ratio else None,
                    "issues": issues,
                }

            except Exception as e:
                logger.warning("ela_analysis_failed", error=str(e))
                return {
                    "ela_performed": False,
                    "is_tampered": False,
                    "confidence": 0.0,
                    "anomaly_ratio": None,
                    "issues": [
                        ValidationIssue(
                            category="forensic",
                            severity=ValidationSeverity.LOW,
                            description=f"Could not perform ELA analysis: {str(e)}",
                        )
                    ],
                }

        return await asyncio.to_thread(_compute_ela)

    async def _detect_cloned_regions(self, img_array: np.ndarray) -> bool:
        """Detect cloned/copied regions using region hashing."""

        def _compute():
            height, width = img_array.shape[:2]
            region_size = self.CLONE_REGION_SIZE

            hashes = []
            for y in range(0, height - region_size, region_size):
                for x in range(0, width - region_size, region_size):
                    region = img_array[y : y + region_size, x : x + region_size]
                    region_hash = hashlib.md5(region.tobytes()).hexdigest()
                    hashes.append(region_hash)

            # Check for duplicate hashes
            unique_hashes = len(set(hashes))
            total_hashes = len(hashes)

            if total_hashes == 0:
                return False

            # Calculate duplicate ratio
            duplicate_ratio = 1 - (unique_hashes / total_hashes)

            # If more than threshold duplicates, might have cloned regions
            return duplicate_ratio > self.CLONE_DUPLICATE_RATIO_THRESHOLD

        return await asyncio.to_thread(_compute)

    async def _check_compression_consistency(self, img_array: np.ndarray) -> bool:
        """Check if compression is consistent across the image."""

        def _compute():
            height, width = img_array.shape[:2]

            # Divide image into quadrants
            quadrants = [
                img_array[: height // 2, : width // 2],
                img_array[: height // 2, width // 2 :],
                img_array[height // 2 :, : width // 2],
                img_array[height // 2 :, width // 2 :],
            ]

            # Calculate variance for each quadrant
            variances = [np.var(q) for q in quadrants]

            # Check if variances are similar
            variance_std = np.std(variances)

            # If standard deviation of variances is high, compression is inconsistent
            return variance_std < self.COMPRESSION_VARIANCE_THRESHOLD

        return await asyncio.to_thread(_compute)


__all__ = ["TamperingDetectionService"]

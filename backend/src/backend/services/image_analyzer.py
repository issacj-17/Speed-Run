"""Image analysis service for authenticity verification and tampering detection."""

import io
import hashlib
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image, ImageChops, ImageEnhance
import numpy as np
from datetime import datetime
import json

from backend.schemas.validation import (
    ImageAnalysisResult,
    ValidationIssue,
    ValidationSeverity,
)


class ImageAnalyzer:
    """Service for analyzing image authenticity and detecting tampering."""

    def __init__(self):
        """Initialize the image analyzer."""
        pass

    async def analyze_image(
        self,
        image_path: Path,
        perform_reverse_search: bool = True,
    ) -> ImageAnalysisResult:
        """
        Perform comprehensive image analysis.

        Args:
            image_path: Path to the image file
            perform_reverse_search: Whether to perform reverse image search

        Returns:
            ImageAnalysisResult with analysis findings
        """
        metadata_issues: List[ValidationIssue] = []
        forensic_findings: List[ValidationIssue] = []

        # Load image
        try:
            image = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")

        # 1. EXIF Metadata Analysis
        metadata_issues.extend(await self._analyze_metadata(image, image_path))

        # 2. AI-Generated Detection
        is_ai_generated, ai_confidence = await self._detect_ai_generated(image)

        # 3. Tampering Detection using ELA (Error Level Analysis)
        is_tampered, tampering_confidence, ela_findings = await self._detect_tampering_ela(image_path)
        forensic_findings.extend(ela_findings)

        # 4. Additional forensic checks
        forensic_findings.extend(await self._forensic_analysis(image))

        # 5. Reverse image search (placeholder - requires API integration)
        reverse_image_matches = 0
        if perform_reverse_search:
            reverse_image_matches = await self._reverse_image_search(image_path)

        # Determine overall authenticity
        is_authentic = not (is_ai_generated or is_tampered or reverse_image_matches > 5)

        return ImageAnalysisResult(
            is_authentic=is_authentic,
            is_ai_generated=is_ai_generated,
            ai_detection_confidence=ai_confidence,
            is_tampered=is_tampered,
            tampering_confidence=tampering_confidence,
            reverse_image_matches=reverse_image_matches,
            metadata_issues=metadata_issues,
            forensic_findings=forensic_findings,
        )

    async def _analyze_metadata(self, image: Image.Image, image_path: Path) -> List[ValidationIssue]:
        """Analyze image EXIF metadata for inconsistencies."""
        issues: List[ValidationIssue] = []

        # Extract EXIF data
        exif_data = image.getexif()

        if not exif_data:
            issues.append(ValidationIssue(
                category="metadata",
                severity=ValidationSeverity.MEDIUM,
                description="Image has no EXIF metadata (may have been stripped)",
                details={"exif_present": False}
            ))
            return issues

        # Check for suspicious metadata patterns
        exif_dict = {k: v for k, v in exif_data.items()}

        # Check for editing software indicators
        software_tags = [0x0131, 0x0305]  # Software tag IDs
        for tag in software_tags:
            if tag in exif_dict:
                software = str(exif_dict[tag])
                if any(editor in software.lower() for editor in ['photoshop', 'gimp', 'paint', 'edit']):
                    issues.append(ValidationIssue(
                        category="metadata",
                        severity=ValidationSeverity.HIGH,
                        description=f"Image shows signs of editing (software: {software})",
                        details={"software": software}
                    ))

        # Check DateTime consistency
        datetime_tags = {
            0x0132: "DateTime",
            0x9003: "DateTimeOriginal",
            0x9004: "DateTimeDigitized"
        }

        dates = {}
        for tag_id, tag_name in datetime_tags.items():
            if tag_id in exif_dict:
                dates[tag_name] = str(exif_dict[tag_id])

        # Check for datetime inconsistencies
        if len(set(dates.values())) > 1 and len(dates) > 1:
            issues.append(ValidationIssue(
                category="metadata",
                severity=ValidationSeverity.MEDIUM,
                description="Inconsistent timestamps in EXIF data",
                details={"timestamps": dates}
            ))

        # Check for missing camera information
        camera_tags = [0x010F, 0x0110]  # Make and Model
        camera_info_present = any(tag in exif_dict for tag in camera_tags)

        if not camera_info_present:
            issues.append(ValidationIssue(
                category="metadata",
                severity=ValidationSeverity.LOW,
                description="Missing camera information in EXIF data",
            ))

        return issues

    async def _detect_ai_generated(self, image: Image.Image) -> Tuple[bool, float]:
        """
        Detect if image is AI-generated using heuristic analysis.

        In production, this would use a specialized ML model.
        """
        # Heuristic approach: AI-generated images often have:
        # 1. Perfect symmetry
        # 2. Unusual color distributions
        # 3. Repetitive patterns
        # 4. Lack of noise

        confidence_score = 0.0
        checks_performed = 0

        # Convert to numpy array
        img_array = np.array(image.convert('RGB'))

        # Check 1: Noise analysis
        # Real photos have natural noise, AI images often don't
        noise_level = self._calculate_noise_level(img_array)
        checks_performed += 1

        if noise_level < 5.0:  # Very low noise
            confidence_score += 0.3

        # Check 2: Color distribution analysis
        # AI images often have unusual color distributions
        color_entropy = self._calculate_color_entropy(img_array)
        checks_performed += 1

        if color_entropy < 5.0:  # Low entropy
            confidence_score += 0.2

        # Check 3: Edge consistency
        # AI images may have overly smooth or perfect edges
        edge_score = self._analyze_edges(img_array)
        checks_performed += 1

        if edge_score > 0.8:  # Very consistent edges
            confidence_score += 0.2

        # Check 4: Artifacts typical of AI generation
        has_ai_artifacts = self._check_ai_artifacts(img_array)
        checks_performed += 1

        if has_ai_artifacts:
            confidence_score += 0.3

        # Normalize confidence
        final_confidence = min(confidence_score, 1.0)

        # Threshold for detection
        is_ai_generated = final_confidence > 0.5

        return is_ai_generated, round(final_confidence, 3)

    async def _detect_tampering_ela(self, image_path: Path) -> Tuple[bool, float, List[ValidationIssue]]:
        """
        Detect tampering using Error Level Analysis (ELA).

        ELA identifies areas of an image with different compression levels,
        which can indicate manipulation.
        """
        findings: List[ValidationIssue] = []

        try:
            # Load original image
            original = Image.open(image_path)

            # Save at 90% quality
            temp_buffer = io.BytesIO()
            original.save(temp_buffer, format='JPEG', quality=90)
            temp_buffer.seek(0)

            # Reload the compressed image
            compressed = Image.open(temp_buffer)

            # Calculate difference (ELA)
            ela_image = ImageChops.difference(original.convert('RGB'), compressed.convert('RGB'))

            # Enhance to make differences more visible
            extrema = ela_image.getextrema()
            max_diff = max([ex[1] for ex in extrema])

            if max_diff == 0:
                # No differences found
                return False, 0.0, findings

            scale = 255.0 / max_diff
            ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

            # Convert to numpy for analysis
            ela_array = np.array(ela_image)

            # Calculate statistics
            mean_error = np.mean(ela_array)
            std_error = np.std(ela_array)
            max_error = np.max(ela_array)

            # Detect anomalous regions (high error levels)
            threshold = mean_error + 2 * std_error
            anomalous_pixels = np.sum(ela_array > threshold)
            total_pixels = ela_array.size
            anomaly_ratio = anomalous_pixels / total_pixels

            # Determine tampering likelihood
            is_tampered = anomaly_ratio > 0.15  # More than 15% anomalous pixels

            # Calculate confidence
            confidence = min(anomaly_ratio * 3, 1.0)  # Scale up ratio for confidence

            if is_tampered:
                findings.append(ValidationIssue(
                    category="forensic",
                    severity=ValidationSeverity.CRITICAL,
                    description="Image shows signs of tampering (ELA analysis)",
                    details={
                        "anomaly_ratio": round(anomaly_ratio, 4),
                        "mean_error": round(float(mean_error), 2),
                        "max_error": int(max_error)
                    }
                ))

            return is_tampered, round(confidence, 3), findings

        except Exception as e:
            findings.append(ValidationIssue(
                category="forensic",
                severity=ValidationSeverity.LOW,
                description=f"Could not perform ELA analysis: {str(e)}",
            ))
            return False, 0.0, findings

    async def _forensic_analysis(self, image: Image.Image) -> List[ValidationIssue]:
        """Perform additional forensic checks."""
        findings: List[ValidationIssue] = []

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        img_array = np.array(image)

        # Check 1: Clone detection (repeated regions)
        has_clones = self._detect_cloned_regions(img_array)
        if has_clones:
            findings.append(ValidationIssue(
                category="forensic",
                severity=ValidationSeverity.HIGH,
                description="Detected potentially cloned/copied regions in image",
            ))

        # Check 2: Consistency in JPEG compression
        # Different parts of the image should have similar compression artifacts
        compression_consistent = self._check_compression_consistency(img_array)
        if not compression_consistent:
            findings.append(ValidationIssue(
                category="forensic",
                severity=ValidationSeverity.MEDIUM,
                description="Inconsistent compression levels detected across image",
            ))

        # Check 3: Unusual aspect ratio or dimensions
        width, height = image.size
        aspect_ratio = width / height

        # Check for unusual dimensions (common in fake documents)
        if aspect_ratio > 5 or aspect_ratio < 0.2:
            findings.append(ValidationIssue(
                category="forensic",
                severity=ValidationSeverity.LOW,
                description=f"Unusual aspect ratio: {aspect_ratio:.2f}",
                details={"width": width, "height": height}
            ))

        return findings

    async def _reverse_image_search(self, image_path: Path) -> int:
        """
        Perform reverse image search to find matches online.

        This is a placeholder - in production, integrate with:
        - Google Reverse Image Search API
        - TinEye API
        - Bing Visual Search API
        """
        # Placeholder implementation
        # In production, call external APIs here

        # For now, return 0 (no matches found)
        # This would need API keys and HTTP requests to external services

        return 0

    def _calculate_noise_level(self, img_array: np.ndarray) -> float:
        """Calculate noise level in image."""
        # Use Laplacian variance as noise estimate
        gray = np.mean(img_array, axis=2).astype(np.uint8)

        # Simple Laplacian kernel
        laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])

        # Apply convolution (simplified)
        from scipy.ndimage import convolve
        try:
            variance = np.var(convolve(gray, laplacian))
            return float(variance)
        except ImportError:
            # Fallback if scipy not available
            return 10.0  # Assume normal noise level

    def _calculate_color_entropy(self, img_array: np.ndarray) -> float:
        """Calculate color distribution entropy."""
        # Flatten and calculate histogram
        pixels = img_array.reshape(-1, 3)

        # Calculate entropy for each channel
        entropy_sum = 0.0
        for channel in range(3):
            hist, _ = np.histogram(pixels[:, channel], bins=256, range=(0, 256))
            hist = hist / hist.sum()  # Normalize
            hist = hist[hist > 0]  # Remove zeros
            entropy = -np.sum(hist * np.log2(hist))
            entropy_sum += entropy

        return entropy_sum / 3  # Average across channels

    def _analyze_edges(self, img_array: np.ndarray) -> float:
        """Analyze edge consistency."""
        gray = np.mean(img_array, axis=2).astype(np.uint8)

        # Simple edge detection using gradient
        grad_x = np.diff(gray, axis=1)
        grad_y = np.diff(gray, axis=0)

        # Calculate edge strength
        edge_strength = np.mean(np.abs(grad_x)) + np.mean(np.abs(grad_y))

        # Normalize to 0-1 range (heuristic)
        normalized = min(edge_strength / 50.0, 1.0)

        return normalized

    def _check_ai_artifacts(self, img_array: np.ndarray) -> bool:
        """Check for artifacts typical of AI-generated images."""
        # Look for:
        # 1. Perfect symmetry (common in AI faces)
        # 2. Repetitive patterns
        # 3. Impossible geometry

        height, width = img_array.shape[:2]

        # Check for perfect left-right symmetry
        left_half = img_array[:, :width//2]
        right_half = np.fliplr(img_array[:, width//2:])

        # Ensure same dimensions
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]

        # Calculate similarity
        difference = np.mean(np.abs(left_half.astype(float) - right_half.astype(float)))

        # If nearly identical, might be AI-generated
        is_perfectly_symmetric = difference < 5.0

        return is_perfectly_symmetric

    def _detect_cloned_regions(self, img_array: np.ndarray) -> bool:
        """Detect cloned/copied regions in image."""
        # This is a simplified check
        # In production, use more sophisticated algorithms like SIFT matching

        # Calculate image hash for regions
        height, width = img_array.shape[:2]
        region_size = 32

        hashes = []
        for y in range(0, height - region_size, region_size):
            for x in range(0, width - region_size, region_size):
                region = img_array[y:y+region_size, x:x+region_size]
                region_hash = hashlib.md5(region.tobytes()).hexdigest()
                hashes.append(region_hash)

        # Check for duplicate hashes
        unique_hashes = len(set(hashes))
        total_hashes = len(hashes)

        # If more than 5% duplicates, might have cloned regions
        duplicate_ratio = 1 - (unique_hashes / total_hashes)

        return duplicate_ratio > 0.05

    def _check_compression_consistency(self, img_array: np.ndarray) -> bool:
        """Check if compression is consistent across image."""
        # Divide image into quadrants and check variance
        height, width = img_array.shape[:2]

        quadrants = [
            img_array[:height//2, :width//2],
            img_array[:height//2, width//2:],
            img_array[height//2:, :width//2],
            img_array[height//2:, width//2:],
        ]

        variances = [np.var(q) for q in quadrants]

        # Check if variances are similar
        variance_std = np.std(variances)

        # If standard deviation of variances is high, compression is inconsistent
        return variance_std < 1000  # Threshold is heuristic

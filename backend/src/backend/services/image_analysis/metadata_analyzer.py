"""
Metadata analysis service.

Single Responsibility: Analyze image EXIF metadata for authenticity verification.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any

from backend.adapters.image import ImageProcessorProtocol
from backend.schemas.image_analysis import MetadataAnalysisResult
from backend.schemas.validation import ValidationIssue, ValidationSeverity
from backend.logging import get_logger

logger = get_logger(__name__)


class MetadataAnalysisService:
    """
    Service for analyzing image metadata.

    Responsibilities:
    - Extract EXIF metadata
    - Detect editing software signatures
    - Validate timestamp consistency
    - Check for camera information presence
    """

    # EXIF tag IDs
    SOFTWARE_TAGS = [0x0131, 0x0305]  # Software tag IDs
    DATETIME_TAGS = {
        0x0132: "DateTime",
        0x9003: "DateTimeOriginal",
        0x9004: "DateTimeDigitized",
    }
    CAMERA_TAGS = [0x010F, 0x0110]  # Make and Model

    # Known editing software patterns
    EDITING_SOFTWARE = ["photoshop", "gimp", "paint", "edit", "lightroom", "affinity", "corel"]

    def __init__(self, image_processor: Optional[ImageProcessorProtocol] = None):
        """
        Initialize metadata analysis service.

        Args:
            image_processor: Image processor for metadata extraction (injected)
        """
        self.image_processor = image_processor
        logger.info("metadata_analysis_service_initialized", has_processor=image_processor is not None)

    async def analyze(self, file_path: Path) -> MetadataAnalysisResult:
        """
        Analyze image metadata for authenticity indicators.

        Args:
            file_path: Path to the image file

        Returns:
            MetadataAnalysisResult with metadata analysis
        """
        logger.info("metadata_analysis_started", file_name=file_path.name)

        issues: List[ValidationIssue] = []
        exif_data: Optional[Dict[str, Any]] = None

        # Extract metadata using image processor
        if self.image_processor:
            try:
                metadata = await self.image_processor.extract_metadata(file_path)
                exif_data = metadata.exif_data
                logger.debug("metadata_extracted", exif_present=exif_data is not None)
            except Exception as e:
                logger.warning("metadata_extraction_failed", error=str(e))
                exif_data = None

        # Check if EXIF exists
        has_exif = exif_data is not None and len(exif_data) > 0

        if not has_exif:
            issues.append(
                ValidationIssue(
                    category="metadata",
                    severity=ValidationSeverity.MEDIUM,
                    description="Image has no EXIF metadata (may have been stripped or generated)",
                    details={"exif_present": False},
                )
            )

            return MetadataAnalysisResult(
                has_exif=False,
                has_editing_software_signs=False,
                has_timestamp_inconsistencies=False,
                has_camera_info=False,
                exif_data=None,
                issues=issues,
            )

        # Check for editing software
        editing_result = await self._check_editing_software(exif_data)
        issues.extend(editing_result["issues"])

        # Check timestamp consistency
        timestamp_result = await self._check_timestamps(exif_data)
        issues.extend(timestamp_result["issues"])

        # Check camera information
        camera_result = await self._check_camera_info(exif_data)
        issues.extend(camera_result["issues"])

        result = MetadataAnalysisResult(
            has_exif=True,
            has_editing_software_signs=editing_result["has_editing_software"],
            has_timestamp_inconsistencies=timestamp_result["has_inconsistencies"],
            has_camera_info=camera_result["has_camera_info"],
            exif_data=exif_data,
            issues=issues,
        )

        logger.info(
            "metadata_analysis_completed",
            file_name=file_path.name,
            has_editing_signs=result.has_editing_software_signs,
            has_timestamp_issues=result.has_timestamp_inconsistencies,
            issue_count=len(issues),
        )

        return result

    async def _check_editing_software(self, exif_data: Dict[str, Any]) -> dict:
        """Check for editing software signatures in metadata."""
        has_editing_software = False
        issues = []
        detected_software = []

        for tag in self.SOFTWARE_TAGS:
            if tag in exif_data:
                software = str(exif_data[tag]).lower()

                # Check if any known editing software is mentioned
                for editor in self.EDITING_SOFTWARE:
                    if editor in software:
                        has_editing_software = True
                        detected_software.append(exif_data[tag])
                        break

        if has_editing_software:
            issues.append(
                ValidationIssue(
                    category="metadata",
                    severity=ValidationSeverity.HIGH,
                    description=f"Image shows signs of editing (software detected: {', '.join(detected_software)})",
                    details={"software": detected_software},
                )
            )

        return {"has_editing_software": has_editing_software, "issues": issues}

    async def _check_timestamps(self, exif_data: Dict[str, Any]) -> dict:
        """Check for timestamp inconsistencies in EXIF data."""
        has_inconsistencies = False
        issues = []

        dates = {}
        for tag_id, tag_name in self.DATETIME_TAGS.items():
            if tag_id in exif_data:
                dates[tag_name] = str(exif_data[tag_id])

        # Check for inconsistencies (different timestamps)
        if len(dates) > 1:
            unique_dates = len(set(dates.values()))
            if unique_dates > 1:
                has_inconsistencies = True
                issues.append(
                    ValidationIssue(
                        category="metadata",
                        severity=ValidationSeverity.MEDIUM,
                        description="Inconsistent timestamps in EXIF data (may indicate editing)",
                        details={"timestamps": dates},
                    )
                )

        return {"has_inconsistencies": has_inconsistencies, "issues": issues}

    async def _check_camera_info(self, exif_data: Dict[str, Any]) -> dict:
        """Check for presence of camera information."""
        camera_info_present = any(tag in exif_data for tag in self.CAMERA_TAGS)
        issues = []

        if not camera_info_present:
            issues.append(
                ValidationIssue(
                    category="metadata",
                    severity=ValidationSeverity.LOW,
                    description="Missing camera information in EXIF data (may be screenshot or synthetic)",
                    details={"camera_info_present": False},
                )
            )

        return {"has_camera_info": camera_info_present, "issues": issues}


__all__ = ["MetadataAnalysisService"]

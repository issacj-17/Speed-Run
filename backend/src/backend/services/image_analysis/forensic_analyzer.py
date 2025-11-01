"""
Forensic analysis orchestrator service.

Single Responsibility: Orchestrate all image analysis services and provide comprehensive verdict.
"""

import asyncio
from pathlib import Path
from typing import List, Optional

from backend.adapters.image import ImageProcessorProtocol
from backend.schemas.image_analysis import (
    ForensicAnalysisResult,
    MetadataAnalysisResult,
    AIDetectionResult,
    TamperingDetectionResult,
)
from backend.schemas.validation import ValidationIssue
from backend.cache.decorators import cache_by_file_hash, CacheConfig
from backend.logging import get_logger

from .metadata_analyzer import MetadataAnalysisService
from .ai_detector import AIDetectionService
from .tampering_detector import TamperingDetectionService

logger = get_logger(__name__)


class ForensicAnalysisService:
    """
    Service for orchestrating comprehensive forensic image analysis.

    Responsibilities:
    - Orchestrate metadata, AI detection, and tampering services
    - Perform reverse image search (integration point)
    - Provide overall authenticity verdict
    - Calculate comprehensive authenticity score
    """

    # Reverse image search threshold
    REVERSE_SEARCH_MATCH_THRESHOLD = 5

    # Authenticity score weights
    METADATA_WEIGHT = 0.2
    AI_WEIGHT = 0.3
    TAMPERING_WEIGHT = 0.4
    REVERSE_SEARCH_WEIGHT = 0.1

    def __init__(
        self,
        image_processor: Optional[ImageProcessorProtocol] = None,
        metadata_analyzer: Optional[MetadataAnalysisService] = None,
        ai_detector: Optional[AIDetectionService] = None,
        tampering_detector: Optional[TamperingDetectionService] = None,
    ):
        """
        Initialize forensic analysis service.

        Args:
            image_processor: Image processor for image operations (injected)
            metadata_analyzer: Metadata analysis service (injected, optional)
            ai_detector: AI detection service (injected, optional)
            tampering_detector: Tampering detection service (injected, optional)
        """
        self.image_processor = image_processor

        # Initialize sub-services (with DI)
        self.metadata_analyzer = metadata_analyzer or MetadataAnalysisService(image_processor)
        self.ai_detector = ai_detector or AIDetectionService(image_processor)
        self.tampering_detector = tampering_detector or TamperingDetectionService()

        logger.info("forensic_analysis_service_initialized", has_processor=image_processor is not None)

    @cache_by_file_hash(ttl=CacheConfig.FORENSIC_ANALYSIS_TTL, key_prefix="forensic_analyze")
    async def analyze(
        self,
        file_path: Path,
        perform_reverse_search: bool = True,
    ) -> ForensicAnalysisResult:
        """
        Perform comprehensive forensic analysis on image.

        Cached by file hash for 2 hours as forensic analysis is very expensive (ELA, AI detection, etc.).

        Args:
            file_path: Path to the image file
            perform_reverse_search: Whether to perform reverse image search

        Returns:
            ForensicAnalysisResult with comprehensive analysis
        """
        logger.info("forensic_analysis_started", file_name=file_path.name)

        # Run all analyses in parallel for performance
        metadata_task = self.metadata_analyzer.analyze(file_path)
        ai_detection_task = self.ai_detector.detect(file_path)
        tampering_task = self.tampering_detector.detect(file_path)

        # Wait for all analyses to complete
        metadata_result, ai_result, tampering_result = await asyncio.gather(
            metadata_task,
            ai_detection_task,
            tampering_task,
        )

        # Perform reverse image search if requested
        reverse_image_matches = 0
        if perform_reverse_search:
            reverse_image_matches = await self._reverse_image_search(file_path)

        # Collect all issues
        all_issues: List[ValidationIssue] = []
        all_issues.extend(metadata_result.issues)
        all_issues.extend(tampering_result.issues)

        # Calculate authenticity score
        authenticity_score = await self._calculate_authenticity_score(
            metadata_result,
            ai_result,
            tampering_result,
            reverse_image_matches,
        )

        # Determine overall authenticity
        is_authentic = await self._determine_authenticity(
            metadata_result,
            ai_result,
            tampering_result,
            reverse_image_matches,
        )

        result = ForensicAnalysisResult(
            is_authentic=is_authentic,
            reverse_image_matches=reverse_image_matches,
            metadata_analysis=metadata_result,
            ai_detection=ai_result,
            tampering_detection=tampering_result,
            all_issues=all_issues,
            authenticity_score=round(authenticity_score, 3),
        )

        logger.info(
            "forensic_analysis_completed",
            file_name=file_path.name,
            is_authentic=result.is_authentic,
            authenticity_score=result.authenticity_score,
            total_issues=len(all_issues),
        )

        return result

    async def _calculate_authenticity_score(
        self,
        metadata: MetadataAnalysisResult,
        ai_detection: AIDetectionResult,
        tampering: TamperingDetectionResult,
        reverse_matches: int,
    ) -> float:
        """
        Calculate overall authenticity score (0=not authentic, 1=authentic).

        Uses weighted factors from all analyses.
        """
        score = 1.0  # Start with perfect score

        # Metadata factors (reduce score for issues)
        metadata_score = 1.0
        if not metadata.has_exif:
            metadata_score -= 0.4
        if metadata.has_editing_software_signs:
            metadata_score -= 0.3
        if metadata.has_timestamp_inconsistencies:
            metadata_score -= 0.2
        if not metadata.has_camera_info:
            metadata_score -= 0.1
        metadata_score = max(0.0, metadata_score)

        # AI detection factors
        ai_score = 1.0 - ai_detection.confidence if ai_detection.is_ai_generated else 1.0

        # Tampering factors
        tampering_score = 1.0 - tampering.confidence if tampering.is_tampered else 1.0

        # Reverse search factors
        reverse_score = 1.0
        if reverse_matches > self.REVERSE_SEARCH_MATCH_THRESHOLD:
            # Many matches suggest it's not original
            reverse_score = max(0.0, 1.0 - (reverse_matches / 20.0))

        # Weighted average
        final_score = (
            metadata_score * self.METADATA_WEIGHT
            + ai_score * self.AI_WEIGHT
            + tampering_score * self.TAMPERING_WEIGHT
            + reverse_score * self.REVERSE_SEARCH_WEIGHT
        )

        return max(0.0, min(1.0, final_score))

    async def _determine_authenticity(
        self,
        metadata: MetadataAnalysisResult,
        ai_detection: AIDetectionResult,
        tampering: TamperingDetectionResult,
        reverse_matches: int,
    ) -> bool:
        """Determine overall authenticity verdict."""
        # Image is NOT authentic if:
        # 1. AI-generated with high confidence
        # 2. Tampered with high confidence
        # 3. Too many reverse image matches
        # 4. Critical metadata issues + other issues

        if ai_detection.is_ai_generated and ai_detection.confidence > 0.7:
            return False

        if tampering.is_tampered and tampering.confidence > 0.7:
            return False

        if reverse_matches > self.REVERSE_SEARCH_MATCH_THRESHOLD:
            return False

        # Check for combination of issues
        issue_count = len(metadata.issues) + len(tampering.issues)
        if issue_count > 3:
            return False

        # Otherwise, likely authentic
        return True

    async def _reverse_image_search(self, file_path: Path) -> int:
        """
        Perform reverse image search to find matches online.

        This is an integration point for external APIs:
        - Google Reverse Image Search API
        - TinEye API
        - Bing Visual Search API

        Returns:
            Number of matches found
        """
        # Placeholder implementation
        # In production, this would call external APIs

        # Example integration structure:
        # 1. Upload image or send image hash to API
        # 2. Receive list of matches with similarity scores
        # 3. Filter matches by similarity threshold
        # 4. Return count of high-confidence matches

        logger.debug("reverse_image_search", file_name=file_path.name, status="placeholder")

        # For now, return 0 (no matches)
        # TODO: Integrate with reverse image search APIs
        return 0

    async def analyze_with_checks(
        self,
        file_path: Path,
        check_metadata: bool = True,
        check_ai: bool = True,
        check_tampering: bool = True,
        perform_reverse_search: bool = True,
    ) -> ForensicAnalysisResult:
        """
        Perform selective forensic analysis based on flags.

        Useful for performance optimization when only specific checks are needed.

        Args:
            file_path: Path to the image file
            check_metadata: Whether to perform metadata analysis
            check_ai: Whether to perform AI detection
            check_tampering: Whether to perform tampering detection
            perform_reverse_search: Whether to perform reverse image search

        Returns:
            ForensicAnalysisResult with selected analyses
        """
        logger.info(
            "forensic_analysis_selective",
            file_name=file_path.name,
            checks={
                "metadata": check_metadata,
                "ai": check_ai,
                "tampering": check_tampering,
                "reverse": perform_reverse_search,
            },
        )

        # Run selected analyses in parallel
        tasks = []

        if check_metadata:
            tasks.append(self.metadata_analyzer.analyze(file_path))
        else:
            # Create empty result
            tasks.append(
                asyncio.create_task(
                    asyncio.coroutine(lambda: MetadataAnalysisResult(
                        has_exif=True,
                        has_editing_software_signs=False,
                        has_timestamp_inconsistencies=False,
                        has_camera_info=True,
                        issues=[],
                    ))()
                )
            )

        if check_ai:
            tasks.append(self.ai_detector.detect(file_path))
        else:
            tasks.append(
                asyncio.create_task(
                    asyncio.coroutine(lambda: AIDetectionResult(
                        is_ai_generated=False,
                        confidence=0.0,
                        noise_level=10.0,
                        color_entropy=7.0,
                        edge_consistency_score=0.5,
                        has_ai_artifacts=False,
                        detection_factors=[],
                    ))()
                )
            )

        if check_tampering:
            tasks.append(self.tampering_detector.detect(file_path))
        else:
            tasks.append(
                asyncio.create_task(
                    asyncio.coroutine(lambda: TamperingDetectionResult(
                        is_tampered=False,
                        confidence=0.0,
                        ela_performed=False,
                        has_cloned_regions=False,
                        compression_consistent=True,
                        issues=[],
                    ))()
                )
            )

        results = await asyncio.gather(*tasks)
        metadata_result, ai_result, tampering_result = results

        # Reverse search
        reverse_matches = 0
        if perform_reverse_search:
            reverse_matches = await self._reverse_image_search(file_path)

        # Calculate scores
        all_issues = []
        all_issues.extend(metadata_result.issues)
        all_issues.extend(tampering_result.issues)

        authenticity_score = await self._calculate_authenticity_score(
            metadata_result, ai_result, tampering_result, reverse_matches
        )

        is_authentic = await self._determine_authenticity(
            metadata_result, ai_result, tampering_result, reverse_matches
        )

        return ForensicAnalysisResult(
            is_authentic=is_authentic,
            reverse_image_matches=reverse_matches,
            metadata_analysis=metadata_result,
            ai_detection=ai_result,
            tampering_detection=tampering_result,
            all_issues=all_issues,
            authenticity_score=round(authenticity_score, 3),
        )


__all__ = ["ForensicAnalysisService"]

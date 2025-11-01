"""Main corroboration service that orchestrates all validation services."""

import time
import tempfile
from pathlib import Path
from typing import Optional

from backend.adapters.document_parser import DocumentParserProtocol
from backend.adapters.nlp import NLPProcessorProtocol
from backend.adapters.image import ImageProcessorProtocol
from backend.services.validation import (
    FormatValidationService,
    StructureValidationService,
    ContentValidationService,
)
from backend.services.image_analysis import (
    ForensicAnalysisService,
    MetadataAnalysisService,
    AIDetectionService,
    TamperingDetectionService,
)
from backend.services.risk_scorer import RiskScorer
from backend.services.report_generator import ReportGenerator
from backend.schemas.validation import (
    CorroborationReport,
    CorroborationRequest,
    FormatValidationResult,
    StructureValidationResult,
    ContentValidationResult,
    ImageAnalysisResult,
)
from backend.logging import get_logger

logger = get_logger(__name__)


class CorroborationService:
    """
    Main service for orchestrating document and image corroboration.

    Refactored to use dependency injection and focused services following SOLID principles.
    """

    def __init__(
        self,
        document_parser: Optional[DocumentParserProtocol] = None,
        nlp_processor: Optional[NLPProcessorProtocol] = None,
        image_processor: Optional[ImageProcessorProtocol] = None,
        risk_scorer: Optional[RiskScorer] = None,
        report_generator: Optional[ReportGenerator] = None,
    ):
        """
        Initialize the corroboration service with dependency injection.

        Args:
            document_parser: Document parser adapter (injected from container)
            nlp_processor: NLP processor adapter (injected from container)
            image_processor: Image processor adapter (injected from container)
            risk_scorer: Risk scoring service (injected, optional)
            report_generator: Report generation service (injected, optional)
        """
        # Get dependencies from container if not provided
        if not all([document_parser, nlp_processor, image_processor]):
            from container import get_container

            container = get_container()
            document_parser = document_parser or container.document_parser
            nlp_processor = nlp_processor or container.nlp_processor
            image_processor = image_processor or container.image_processor

        # Store adapters
        self.document_parser = document_parser
        self.nlp_processor = nlp_processor
        self.image_processor = image_processor

        # Initialize validation services with DI
        self.format_validator = FormatValidationService(nlp_processor=nlp_processor)
        self.structure_validator = StructureValidationService()
        self.content_validator = ContentValidationService()

        # Initialize image analysis services with DI
        self.metadata_analyzer = MetadataAnalysisService(image_processor=image_processor)
        self.ai_detector = AIDetectionService(image_processor=image_processor)
        self.tampering_detector = TamperingDetectionService()
        self.forensic_analyzer = ForensicAnalysisService(
            image_processor=image_processor,
            metadata_analyzer=self.metadata_analyzer,
            ai_detector=self.ai_detector,
            tampering_detector=self.tampering_detector,
        )

        # Initialize other services
        self.risk_scorer = risk_scorer or RiskScorer()
        self.report_generator = report_generator or ReportGenerator()

        logger.info("corroboration_service_initialized", dependency_injection=True)

    async def analyze_document(
        self,
        file_bytes: bytes,
        filename: str,
        request: CorroborationRequest,
    ) -> CorroborationReport:
        """
        Perform comprehensive document corroboration analysis.

        Args:
            file_bytes: Document/image file bytes
            filename: Original filename
            request: Corroboration request parameters

        Returns:
            CorroborationReport with comprehensive analysis
        """
        start_time = time.time()
        engines_used = []

        # Save to temporary file
        file_ext = Path(filename).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = Path(tmp_file.name)

        try:
            # Determine if this is an image or document
            is_image = file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
            is_document = file_ext in ['.pdf', '.docx', '.txt']

            format_validation: Optional[FormatValidationResult] = None
            structure_validation: Optional[StructureValidationResult] = None
            content_validation: Optional[ContentValidationResult] = None
            image_analysis: Optional[ImageAnalysisResult] = None

            # Extract text content (if applicable)
            text_content = ""
            if is_document:
                engines_used.append("document_parser")
                # Parse document using injected document parser
                logger.info("parsing_document", file_name=filename)
                parsed_doc = await self.document_parser.parse(tmp_path)
                text_content = parsed_doc.text
                logger.info("document_parsed", text_length=len(text_content))

            # 1. Image Analysis (for images or documents with images)
            if is_image and request.perform_image_analysis:
                engines_used.extend(["metadata_analyzer", "ai_detector", "tampering_detector"])
                logger.info("performing_forensic_analysis", file_name=filename)
                # Use new forensic analysis service (orchestrates all image analysis)
                forensic_result = await self.forensic_analyzer.analyze(
                    tmp_path,
                    perform_reverse_search=request.enable_reverse_image_search,
                )

                # Convert to old ImageAnalysisResult format for backward compatibility
                from backend.schemas.validation import ValidationIssue

                all_issues = forensic_result.all_issues
                image_analysis = ImageAnalysisResult(
                    is_authentic=forensic_result.is_authentic,
                    is_ai_generated=forensic_result.ai_detection.is_ai_generated,
                    ai_detection_confidence=forensic_result.ai_detection.confidence,
                    is_tampered=forensic_result.tampering_detection.is_tampered,
                    tampering_confidence=forensic_result.tampering_detection.confidence,
                    reverse_image_matches=forensic_result.reverse_image_matches,
                    metadata_issues=forensic_result.metadata_analysis.issues,
                    forensic_findings=forensic_result.tampering_detection.issues,
                )
                logger.info(
                    "forensic_analysis_completed",
                    is_authentic=image_analysis.is_authentic,
                    is_ai_generated=image_analysis.is_ai_generated,
                )

            # 2. Format Validation (for documents)
            if is_document and request.perform_format_validation and text_content:
                engines_used.append("format_validator")
                logger.info("validating_format", file_name=filename)
                format_validation = await self.format_validator.validate(
                    text_content,
                    tmp_path,
                )
                logger.info("format_validation_completed", issue_count=len(format_validation.issues))

            # 3. Structure Validation (for documents)
            if is_document and request.perform_structure_validation and text_content:
                engines_used.append("structure_validator")
                logger.info("validating_structure", file_name=filename)
                structure_validation = await self.structure_validator.validate(
                    text_content,
                    tmp_path,
                    expected_document_type=request.expected_document_type,
                )
                logger.info(
                    "structure_validation_completed",
                    is_complete=structure_validation.is_complete,
                    template_match_score=structure_validation.template_match_score,
                )

            # 4. Content Validation (for documents)
            if is_document and request.perform_content_validation and text_content:
                engines_used.append("content_validator")
                logger.info("validating_content", file_name=filename)
                content_validation = await self.content_validator.validate(text_content)
                logger.info(
                    "content_validation_completed",
                    quality_score=content_validation.quality_score,
                    has_sensitive_data=content_validation.has_sensitive_data,
                )

            # 5. Calculate Risk Score
            engines_used.append("risk_scorer")
            risk_score = await self.risk_scorer.calculate_risk_score(
                format_validation=format_validation,
                structure_validation=structure_validation,
                content_validation=content_validation,
                image_analysis=image_analysis,
            )

            # 6. Generate Report
            processing_time = time.time() - start_time

            report = await self.report_generator.generate_report(
                file_name=filename,
                file_type=file_ext,
                format_validation=format_validation,
                structure_validation=structure_validation,
                content_validation=content_validation,
                image_analysis=image_analysis,
                risk_score=risk_score,
                processing_time=processing_time,
                engines_used=engines_used,
            )

            return report

        finally:
            # Clean up temporary file
            if tmp_path.exists():
                tmp_path.unlink()

    async def analyze_image_only(
        self,
        file_bytes: bytes,
        filename: str,
        enable_reverse_search: bool = True,
    ) -> ImageAnalysisResult:
        """
        Perform image-only analysis using new forensic analysis services.

        Args:
            file_bytes: Image file bytes
            filename: Original filename
            enable_reverse_search: Whether to perform reverse image search

        Returns:
            ImageAnalysisResult with image analysis findings
        """
        logger.info("analyze_image_only_started", file_name=filename)

        file_ext = Path(filename).suffix.lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = Path(tmp_file.name)

        try:
            # Use new forensic analysis service
            forensic_result = await self.forensic_analyzer.analyze(
                tmp_path,
                perform_reverse_search=enable_reverse_search,
            )

            # Convert to ImageAnalysisResult for backward compatibility
            result = ImageAnalysisResult(
                is_authentic=forensic_result.is_authentic,
                is_ai_generated=forensic_result.ai_detection.is_ai_generated,
                ai_detection_confidence=forensic_result.ai_detection.confidence,
                is_tampered=forensic_result.tampering_detection.is_tampered,
                tampering_confidence=forensic_result.tampering_detection.confidence,
                reverse_image_matches=forensic_result.reverse_image_matches,
                metadata_issues=forensic_result.metadata_analysis.issues,
                forensic_findings=forensic_result.tampering_detection.issues,
            )

            logger.info(
                "analyze_image_only_completed",
                file_name=filename,
                is_authentic=result.is_authentic,
                authenticity_score=forensic_result.authenticity_score,
            )

            return result

        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    async def get_report(self, document_id: str) -> Optional[CorroborationReport]:
        """
        Retrieve a previously generated report.

        Args:
            document_id: Unique document identifier

        Returns:
            CorroborationReport if found, None otherwise
        """
        return await self.report_generator.get_report(document_id)

    async def list_reports(
        self,
        limit: int = 100,
        risk_level: Optional[str] = None,
        requires_manual_review: Optional[bool] = None,
    ):
        """
        List reports from audit logs.

        Args:
            limit: Maximum number of reports to return
            risk_level: Filter by risk level
            requires_manual_review: Filter by manual review requirement

        Returns:
            List of report summaries
        """
        from backend.schemas.validation import ValidationSeverity

        risk_level_enum = None
        if risk_level:
            risk_level_enum = ValidationSeverity(risk_level.lower())

        return await self.report_generator.list_reports(
            limit=limit,
            risk_level=risk_level_enum,
            requires_manual_review=requires_manual_review,
        )

    async def export_report_markdown(self, document_id: str) -> Optional[str]:
        """
        Export a report as markdown.

        Args:
            document_id: Unique document identifier

        Returns:
            Markdown formatted report if found, None otherwise
        """
        report = await self.get_report(document_id)
        if not report:
            return None

        return await self.report_generator.export_report_markdown(report)

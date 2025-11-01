"""Main corroboration service that orchestrates all validation services."""

import time
import tempfile
from pathlib import Path
from typing import Optional

from backend.services.document_validator import DocumentValidator
from backend.services.image_analyzer import ImageAnalyzer
from backend.services.risk_scorer import RiskScorer
from backend.services.report_generator import ReportGenerator
from backend.services.document_service import DocumentService
from backend.schemas.validation import (
    CorroborationReport,
    CorroborationRequest,
    FormatValidationResult,
    StructureValidationResult,
    ContentValidationResult,
    ImageAnalysisResult,
)


class CorroborationService:
    """Main service for orchestrating document and image corroboration."""

    def __init__(self):
        """Initialize the corroboration service."""
        self.document_validator = DocumentValidator()
        self.image_analyzer = ImageAnalyzer()
        self.risk_scorer = RiskScorer()
        self.report_generator = ReportGenerator()
        self.document_service = DocumentService()

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
                engines_used.append("docling")
                # Parse document to extract text
                parse_result = await self.document_service.parse_document(tmp_path)
                text_content = parse_result.text

            # 1. Image Analysis (for images or documents with images)
            if is_image and request.perform_image_analysis:
                engines_used.append("image_analyzer")
                image_analysis = await self.image_analyzer.analyze_image(
                    tmp_path,
                    perform_reverse_search=request.enable_reverse_image_search,
                )

            # 2. Format Validation (for documents)
            if is_document and request.perform_format_validation and text_content:
                engines_used.append("format_validator")
                format_validation = await self.document_validator.validate_format(
                    text_content,
                    tmp_path,
                )

            # 3. Structure Validation (for documents)
            if is_document and request.perform_structure_validation and text_content:
                engines_used.append("structure_validator")
                structure_validation = await self.document_validator.validate_structure(
                    text_content,
                    tmp_path,
                    expected_document_type=request.expected_document_type,
                )

            # 4. Content Validation (for documents)
            if is_document and request.perform_content_validation and text_content:
                engines_used.append("content_validator")
                content_validation = await self.document_validator.validate_content(
                    text_content,
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
        Perform image-only analysis.

        Args:
            file_bytes: Image file bytes
            filename: Original filename
            enable_reverse_search: Whether to perform reverse image search

        Returns:
            ImageAnalysisResult with image analysis findings
        """
        file_ext = Path(filename).suffix.lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = Path(tmp_file.name)

        try:
            result = await self.image_analyzer.analyze_image(
                tmp_path,
                perform_reverse_search=enable_reverse_search,
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

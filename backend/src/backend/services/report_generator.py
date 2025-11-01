"""Report generation and audit trail service."""

import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.schemas.validation import (
    CorroborationReport,
    FormatValidationResult,
    StructureValidationResult,
    ContentValidationResult,
    ImageAnalysisResult,
    RiskScore,
    ValidationSeverity,
)


class ReportGenerator:
    """Service for generating comprehensive corroboration reports and audit trails."""

    def __init__(self, audit_log_path: Optional[Path] = None):
        """
        Initialize the report generator.

        Args:
            audit_log_path: Path to store audit logs (defaults to /tmp/corroboration_audit)
        """
        self.audit_log_path = audit_log_path or Path("/tmp/corroboration_audit")
        self.audit_log_path.mkdir(parents=True, exist_ok=True)

    async def generate_report(
        self,
        file_name: str,
        file_type: str,
        format_validation: Optional[FormatValidationResult] = None,
        structure_validation: Optional[StructureValidationResult] = None,
        content_validation: Optional[ContentValidationResult] = None,
        image_analysis: Optional[ImageAnalysisResult] = None,
        risk_score: RiskScore = None,
        processing_time: float = 0.0,
        engines_used: List[str] = None,
    ) -> CorroborationReport:
        """
        Generate comprehensive corroboration report.

        Args:
            file_name: Original file name
            file_type: File type/extension
            format_validation: Format validation results
            structure_validation: Structure validation results
            content_validation: Content validation results
            image_analysis: Image analysis results
            risk_score: Risk assessment
            processing_time: Total processing time
            engines_used: List of analysis engines used

        Returns:
            CorroborationReport with all findings
        """
        document_id = str(uuid.uuid4())
        analysis_timestamp = datetime.now()

        # Count total issues
        total_issues = 0
        critical_issues = 0

        if format_validation:
            total_issues += len(format_validation.issues)
            critical_issues += sum(
                1 for issue in format_validation.issues
                if issue.severity == ValidationSeverity.CRITICAL
            )

        if structure_validation:
            total_issues += len(structure_validation.issues)
            critical_issues += sum(
                1 for issue in structure_validation.issues
                if issue.severity == ValidationSeverity.CRITICAL
            )

        if content_validation:
            total_issues += len(content_validation.issues)
            critical_issues += sum(
                1 for issue in content_validation.issues
                if issue.severity == ValidationSeverity.CRITICAL
            )

        if image_analysis:
            total_issues += len(image_analysis.metadata_issues) + len(image_analysis.forensic_findings)
            critical_issues += sum(
                1 for issue in (image_analysis.metadata_issues + image_analysis.forensic_findings)
                if issue.severity == ValidationSeverity.CRITICAL
            )

        # Determine if manual review is required
        requires_manual_review = (
            risk_score.risk_level in [ValidationSeverity.HIGH, ValidationSeverity.CRITICAL]
            or critical_issues > 0
        )

        report = CorroborationReport(
            document_id=document_id,
            file_name=file_name,
            file_type=file_type,
            analysis_timestamp=analysis_timestamp,
            format_validation=format_validation,
            structure_validation=structure_validation,
            content_validation=content_validation,
            image_analysis=image_analysis,
            risk_score=risk_score,
            processing_time=processing_time,
            engines_used=engines_used or [],
            total_issues_found=total_issues,
            critical_issues_count=critical_issues,
            requires_manual_review=requires_manual_review,
        )

        # Log to audit trail
        await self._log_audit_trail(report)

        return report

    async def _log_audit_trail(self, report: CorroborationReport):
        """
        Log report to audit trail.

        Args:
            report: Corroboration report to log
        """
        try:
            # Create audit log entry
            audit_entry = {
                "document_id": report.document_id,
                "file_name": report.file_name,
                "file_type": report.file_type,
                "timestamp": report.analysis_timestamp.isoformat(),
                "risk_score": report.risk_score.overall_score,
                "risk_level": report.risk_score.risk_level.value,
                "total_issues": report.total_issues_found,
                "critical_issues": report.critical_issues_count,
                "requires_manual_review": report.requires_manual_review,
                "processing_time": report.processing_time,
                "engines_used": report.engines_used,
            }

            # Save to audit log file (append mode)
            audit_log_file = self.audit_log_path / f"audit_log_{datetime.now().strftime('%Y%m%d')}.jsonl"

            with open(audit_log_file, "a") as f:
                f.write(json.dumps(audit_entry) + "\n")

            # Also save full report
            report_file = self.audit_log_path / f"report_{report.document_id}.json"
            with open(report_file, "w") as f:
                f.write(report.model_dump_json(indent=2))

        except Exception as e:
            # Don't fail report generation if audit logging fails
            print(f"Warning: Failed to log audit trail: {str(e)}")

    async def get_report(self, document_id: str) -> Optional[CorroborationReport]:
        """
        Retrieve a report from audit logs.

        Args:
            document_id: Unique document identifier

        Returns:
            CorroborationReport if found, None otherwise
        """
        try:
            report_file = self.audit_log_path / f"report_{document_id}.json"

            if not report_file.exists():
                return None

            with open(report_file, "r") as f:
                report_data = json.load(f)

            return CorroborationReport(**report_data)

        except Exception as e:
            print(f"Error retrieving report: {str(e)}")
            return None

    async def list_reports(
        self,
        limit: int = 100,
        risk_level: Optional[ValidationSeverity] = None,
        requires_manual_review: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        List reports from audit logs.

        Args:
            limit: Maximum number of reports to return
            risk_level: Filter by risk level
            requires_manual_review: Filter by manual review requirement

        Returns:
            List of report summaries
        """
        try:
            # Read audit log for today
            audit_log_file = self.audit_log_path / f"audit_log_{datetime.now().strftime('%Y%m%d')}.jsonl"

            if not audit_log_file.exists():
                return []

            reports = []
            with open(audit_log_file, "r") as f:
                for line in f:
                    entry = json.loads(line)

                    # Apply filters
                    if risk_level and entry.get("risk_level") != risk_level.value:
                        continue

                    if requires_manual_review is not None and entry.get("requires_manual_review") != requires_manual_review:
                        continue

                    reports.append(entry)

                    if len(reports) >= limit:
                        break

            # Sort by timestamp (newest first)
            reports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            return reports

        except Exception as e:
            print(f"Error listing reports: {str(e)}")
            return []

    async def export_report_markdown(self, report: CorroborationReport) -> str:
        """
        Export report as markdown.

        Args:
            report: Corroboration report

        Returns:
            Markdown formatted report
        """
        md = []

        md.append(f"# Document Corroboration Report")
        md.append(f"")
        md.append(f"**Document ID:** `{report.document_id}`")
        md.append(f"**File Name:** {report.file_name}")
        md.append(f"**File Type:** {report.file_type}")
        md.append(f"**Analysis Date:** {report.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        md.append(f"")

        # Risk Assessment
        md.append(f"## Risk Assessment")
        md.append(f"")
        md.append(f"- **Overall Risk Score:** {report.risk_score.overall_score:.2f}/100")
        md.append(f"- **Risk Level:** {report.risk_score.risk_level.value.upper()}")
        md.append(f"- **Confidence:** {report.risk_score.confidence:.2%}")
        md.append(f"- **Requires Manual Review:** {'Yes ⚠️' if report.requires_manual_review else 'No ✓'}")
        md.append(f"")

        # Recommendations
        if report.risk_score.recommendations:
            md.append(f"### Recommendations")
            md.append(f"")
            for rec in report.risk_score.recommendations:
                md.append(f"- {rec}")
            md.append(f"")

        # Issues Summary
        md.append(f"## Issues Summary")
        md.append(f"")
        md.append(f"- **Total Issues Found:** {report.total_issues_found}")
        md.append(f"- **Critical Issues:** {report.critical_issues_count}")
        md.append(f"")

        # Validation Results
        if report.format_validation:
            md.append(f"### Format Validation")
            md.append(f"")
            md.append(f"- Double Spacing: {'Yes ⚠️' if report.format_validation.has_double_spacing else 'No'}")
            md.append(f"- Font Inconsistencies: {'Yes ⚠️' if report.format_validation.has_font_inconsistencies else 'No'}")
            md.append(f"- Indentation Issues: {'Yes ⚠️' if report.format_validation.has_indentation_issues else 'No'}")
            md.append(f"- Spelling Errors: {report.format_validation.spelling_error_count}")
            md.append(f"")

        if report.structure_validation:
            md.append(f"### Structure Validation")
            md.append(f"")
            md.append(f"- Document Complete: {'Yes ✓' if report.structure_validation.is_complete else 'No ⚠️'}")
            md.append(f"- Template Match Score: {report.structure_validation.template_match_score:.2%}")
            md.append(f"- Missing Sections: {len(report.structure_validation.missing_sections)}")
            if report.structure_validation.missing_sections:
                for section in report.structure_validation.missing_sections:
                    md.append(f"  - {section}")
            md.append(f"")

        if report.content_validation:
            md.append(f"### Content Validation")
            md.append(f"")
            md.append(f"- Quality Score: {report.content_validation.quality_score:.2%}")
            md.append(f"- Readability Score: {report.content_validation.readability_score:.1f}")
            md.append(f"- Word Count: {report.content_validation.word_count}")
            md.append(f"- Contains PII: {'Yes ⚠️' if report.content_validation.has_sensitive_data else 'No'}")
            md.append(f"")

        if report.image_analysis:
            md.append(f"### Image Analysis")
            md.append(f"")
            md.append(f"- Authentic: {'Yes ✓' if report.image_analysis.is_authentic else 'No ⚠️'}")
            md.append(f"- AI-Generated: {'Yes ⚠️' if report.image_analysis.is_ai_generated else 'No'} (Confidence: {report.image_analysis.ai_detection_confidence:.2%})")
            md.append(f"- Tampered: {'Yes ⚠️' if report.image_analysis.is_tampered else 'No'} (Confidence: {report.image_analysis.tampering_confidence:.2%})")
            md.append(f"- Reverse Image Matches: {report.image_analysis.reverse_image_matches}")
            md.append(f"")

        # Processing Information
        md.append(f"## Processing Information")
        md.append(f"")
        md.append(f"- **Processing Time:** {report.processing_time:.2f}s")
        md.append(f"- **Engines Used:** {', '.join(report.engines_used)}")
        md.append(f"")

        md.append(f"---")
        md.append(f"*Report generated by Document Corroboration System*")

        return "\n".join(md)

"""Risk scoring engine for document corroboration."""

from typing import List, Dict, Any, Optional
from backend.schemas.validation import (
    RiskScore,
    ValidationSeverity,
    FormatValidationResult,
    StructureValidationResult,
    ContentValidationResult,
    ImageAnalysisResult,
)


class RiskScorer:
    """Service for calculating risk scores based on validation results."""

    # Configurable weights for different validation components
    WEIGHTS = {
        "format_validation": 0.15,
        "structure_validation": 0.25,
        "content_validation": 0.20,
        "image_analysis": 0.40,
    }

    # Severity score mappings
    SEVERITY_SCORES = {
        ValidationSeverity.LOW: 10,
        ValidationSeverity.MEDIUM: 30,
        ValidationSeverity.HIGH: 60,
        ValidationSeverity.CRITICAL: 100,
    }

    # Risk level thresholds
    RISK_THRESHOLDS = {
        "low": 25,
        "medium": 50,
        "high": 75,
        # critical: > 75
    }

    def __init__(self):
        """Initialize the risk scorer."""
        pass

    async def calculate_risk_score(
        self,
        format_validation: Optional[FormatValidationResult] = None,
        structure_validation: Optional[StructureValidationResult] = None,
        content_validation: Optional[ContentValidationResult] = None,
        image_analysis: Optional[ImageAnalysisResult] = None,
    ) -> RiskScore:
        """
        Calculate comprehensive risk score from validation results.

        Args:
            format_validation: Format validation results
            structure_validation: Structure validation results
            content_validation: Content validation results
            image_analysis: Image analysis results

        Returns:
            RiskScore with overall assessment
        """
        contributing_factors: List[Dict[str, Any]] = []
        total_score = 0.0
        confidence_factors: List[float] = []

        # 1. Format Validation Score
        if format_validation:
            format_score, format_confidence, format_factors = self._score_format_validation(
                format_validation
            )
            total_score += format_score * self.WEIGHTS["format_validation"]
            confidence_factors.append(format_confidence)
            contributing_factors.extend(format_factors)

        # 2. Structure Validation Score
        if structure_validation:
            structure_score, structure_confidence, structure_factors = self._score_structure_validation(
                structure_validation
            )
            total_score += structure_score * self.WEIGHTS["structure_validation"]
            confidence_factors.append(structure_confidence)
            contributing_factors.extend(structure_factors)

        # 3. Content Validation Score
        if content_validation:
            content_score, content_confidence, content_factors = self._score_content_validation(
                content_validation
            )
            total_score += content_score * self.WEIGHTS["content_validation"]
            confidence_factors.append(content_confidence)
            contributing_factors.extend(content_factors)

        # 4. Image Analysis Score
        if image_analysis:
            image_score, image_confidence, image_factors = self._score_image_analysis(
                image_analysis
            )
            total_score += image_score * self.WEIGHTS["image_analysis"]
            confidence_factors.append(image_confidence)
            contributing_factors.extend(image_factors)

        # Calculate overall confidence
        overall_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

        # Determine risk level
        risk_level = self._categorize_risk_level(total_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            total_score,
            format_validation,
            structure_validation,
            content_validation,
            image_analysis,
        )

        return RiskScore(
            overall_score=round(total_score, 2),
            risk_level=risk_level,
            confidence=round(overall_confidence, 3),
            contributing_factors=contributing_factors,
            recommendations=recommendations,
        )

    def _score_format_validation(
        self, result: FormatValidationResult
    ) -> tuple[float, float, List[Dict[str, Any]]]:
        """Score format validation results."""
        score = 0.0
        factors: List[Dict[str, Any]] = []

        # Severity-based scoring
        for issue in result.issues:
            issue_score = self.SEVERITY_SCORES[issue.severity]
            score += issue_score * 0.1  # Scale down individual issues

            factors.append({
                "component": "format_validation",
                "factor": issue.description,
                "severity": issue.severity.value,
                "impact": issue_score * 0.1,
            })

        # Specific checks
        if result.has_spelling_errors and result.spelling_error_count > 10:
            score += 20
            factors.append({
                "component": "format_validation",
                "factor": f"High number of spelling errors ({result.spelling_error_count})",
                "severity": "medium",
                "impact": 20,
            })

        if result.has_indentation_issues:
            score += 10
            factors.append({
                "component": "format_validation",
                "factor": "Inconsistent indentation detected",
                "severity": "low",
                "impact": 10,
            })

        # Cap score at 100
        score = min(score, 100)

        # Confidence based on number of checks performed
        confidence = 0.9 if len(result.issues) > 0 else 0.7

        return score, confidence, factors

    def _score_structure_validation(
        self, result: StructureValidationResult
    ) -> tuple[float, float, List[Dict[str, Any]]]:
        """Score structure validation results."""
        score = 0.0
        factors: List[Dict[str, Any]] = []

        # Template match score (inverse relationship)
        template_penalty = (1.0 - result.template_match_score) * 50
        score += template_penalty

        if result.template_match_score < 0.7:
            factors.append({
                "component": "structure_validation",
                "factor": f"Low template match score ({result.template_match_score:.2f})",
                "severity": "high",
                "impact": template_penalty,
            })

        # Missing sections
        if result.missing_sections:
            missing_penalty = len(result.missing_sections) * 15
            score += missing_penalty

            factors.append({
                "component": "structure_validation",
                "factor": f"Missing {len(result.missing_sections)} expected sections",
                "severity": "high",
                "impact": missing_penalty,
                "details": {"missing_sections": result.missing_sections},
            })

        # Incomplete document
        if not result.is_complete:
            score += 40
            factors.append({
                "component": "structure_validation",
                "factor": "Document appears incomplete",
                "severity": "critical",
                "impact": 40,
            })

        # Issues
        for issue in result.issues:
            issue_score = self.SEVERITY_SCORES[issue.severity]
            score += issue_score * 0.15

            factors.append({
                "component": "structure_validation",
                "factor": issue.description,
                "severity": issue.severity.value,
                "impact": issue_score * 0.15,
            })

        score = min(score, 100)
        confidence = 0.85

        return score, confidence, factors

    def _score_content_validation(
        self, result: ContentValidationResult
    ) -> tuple[float, float, List[Dict[str, Any]]]:
        """Score content validation results."""
        score = 0.0
        factors: List[Dict[str, Any]] = []

        # Quality score (inverse)
        quality_penalty = (1.0 - result.quality_score) * 30
        score += quality_penalty

        if result.quality_score < 0.5:
            factors.append({
                "component": "content_validation",
                "factor": f"Low content quality score ({result.quality_score:.2f})",
                "severity": "medium",
                "impact": quality_penalty,
            })

        # Sensitive data
        if result.has_sensitive_data:
            score += 25
            factors.append({
                "component": "content_validation",
                "factor": "Contains sensitive/PII data",
                "severity": "high",
                "impact": 25,
            })

        # Readability
        if result.readability_score < 30:
            score += 15
            factors.append({
                "component": "content_validation",
                "factor": f"Very low readability ({result.readability_score:.1f})",
                "severity": "low",
                "impact": 15,
            })

        # Word count (too short or suspiciously long)
        if result.word_count < 50:
            score += 20
            factors.append({
                "component": "content_validation",
                "factor": f"Suspiciously short document ({result.word_count} words)",
                "severity": "medium",
                "impact": 20,
            })

        # Issues
        for issue in result.issues:
            issue_score = self.SEVERITY_SCORES[issue.severity]
            score += issue_score * 0.12

            factors.append({
                "component": "content_validation",
                "factor": issue.description,
                "severity": issue.severity.value,
                "impact": issue_score * 0.12,
            })

        score = min(score, 100)
        confidence = 0.8

        return score, confidence, factors

    def _score_image_analysis(
        self, result: ImageAnalysisResult
    ) -> tuple[float, float, List[Dict[str, Any]]]:
        """Score image analysis results."""
        score = 0.0
        factors: List[Dict[str, Any]] = []

        # AI-generated detection
        if result.is_ai_generated:
            ai_penalty = result.ai_detection_confidence * 80
            score += ai_penalty

            factors.append({
                "component": "image_analysis",
                "factor": "Image appears to be AI-generated",
                "severity": "critical",
                "impact": ai_penalty,
                "details": {"confidence": result.ai_detection_confidence},
            })

        # Tampering detection
        if result.is_tampered:
            tamper_penalty = result.tampering_confidence * 90
            score += tamper_penalty

            factors.append({
                "component": "image_analysis",
                "factor": "Image shows signs of tampering",
                "severity": "critical",
                "impact": tamper_penalty,
                "details": {"confidence": result.tampering_confidence},
            })

        # Reverse image matches
        if result.reverse_image_matches > 5:
            match_penalty = min(result.reverse_image_matches * 5, 50)
            score += match_penalty

            factors.append({
                "component": "image_analysis",
                "factor": f"Found {result.reverse_image_matches} matches in reverse image search",
                "severity": "high",
                "impact": match_penalty,
            })

        # Metadata issues
        for issue in result.metadata_issues:
            issue_score = self.SEVERITY_SCORES[issue.severity]
            score += issue_score * 0.2

            factors.append({
                "component": "image_analysis",
                "factor": issue.description,
                "severity": issue.severity.value,
                "impact": issue_score * 0.2,
                "category": "metadata",
            })

        # Forensic findings
        for finding in result.forensic_findings:
            finding_score = self.SEVERITY_SCORES[finding.severity]
            score += finding_score * 0.25

            factors.append({
                "component": "image_analysis",
                "factor": finding.description,
                "severity": finding.severity.value,
                "impact": finding_score * 0.25,
                "category": "forensic",
            })

        # Not authentic
        if not result.is_authentic:
            score += 30
            factors.append({
                "component": "image_analysis",
                "factor": "Image authenticity could not be verified",
                "severity": "high",
                "impact": 30,
            })

        score = min(score, 100)

        # Confidence based on available data
        confidence = 0.9 if (result.ai_detection_confidence > 0 or result.tampering_confidence > 0) else 0.7

        return score, confidence, factors

    def _categorize_risk_level(self, score: float) -> ValidationSeverity:
        """Categorize risk level based on score."""
        if score < self.RISK_THRESHOLDS["low"]:
            return ValidationSeverity.LOW
        elif score < self.RISK_THRESHOLDS["medium"]:
            return ValidationSeverity.MEDIUM
        elif score < self.RISK_THRESHOLDS["high"]:
            return ValidationSeverity.HIGH
        else:
            return ValidationSeverity.CRITICAL

    def _generate_recommendations(
        self,
        score: float,
        format_validation: Optional[FormatValidationResult],
        structure_validation: Optional[StructureValidationResult],
        content_validation: Optional[ContentValidationResult],
        image_analysis: Optional[ImageAnalysisResult],
    ) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations: List[str] = []

        # Overall recommendations
        if score > 75:
            recommendations.append("REJECT: Document has critical issues and high fraud risk")
            recommendations.append("Immediate manual review required by compliance officer")
        elif score > 50:
            recommendations.append("HOLD: Document requires thorough manual review")
            recommendations.append("Request additional supporting documents")
        elif score > 25:
            recommendations.append("REVIEW: Document has minor issues")
            recommendations.append("Consider requesting clarification on flagged items")
        else:
            recommendations.append("ACCEPT: Document appears legitimate")
            recommendations.append("Proceed with standard processing")

        # Specific recommendations based on findings
        if image_analysis:
            if image_analysis.is_ai_generated:
                recommendations.append("Request original document or high-resolution scan")
                recommendations.append("Verify document through alternative channels")

            if image_analysis.is_tampered:
                recommendations.append("Flag for fraud investigation")
                recommendations.append("Compare with original document from issuing authority")

            if image_analysis.reverse_image_matches > 5:
                recommendations.append("Image may be stock photo or stolen from another source")
                recommendations.append("Request additional proof of authenticity")

        if structure_validation:
            if not structure_validation.is_complete:
                recommendations.append("Request complete document with all required sections")

            if structure_validation.missing_sections:
                recommendations.append(
                    f"Request missing sections: {', '.join(structure_validation.missing_sections[:3])}"
                )

        if content_validation:
            if content_validation.has_sensitive_data:
                recommendations.append("Review PII handling and compliance requirements")

        if format_validation:
            if format_validation.spelling_error_count > 20:
                recommendations.append("High number of errors suggests unprofessional or fake document")

        return recommendations[:10]  # Limit to 10 recommendations

# API Contract Analysis - Frontend vs Backend

## Critical Mismatches Found

### 1. Document Analysis Endpoint (`POST /api/v1/corroboration/analyze`)

#### Backend Schema (`CorroborationReport`)
```python
class CorroborationReport(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    analysis_timestamp: datetime

    # Validation results (nested objects)
    format_validation: Optional[FormatValidationResult] = None
    structure_validation: Optional[StructureValidationResult] = None
    content_validation: Optional[ContentValidationResult] = None
    image_analysis: Optional[ImageAnalysisResult] = None

    # Risk assessment (nested object)
    risk_score: RiskScore  # ❌ OBJECT, not number!

    # Processing metadata
    processing_time: float
    engines_used: List[str]

    # Summary
    total_issues_found: int
    critical_issues_count: int
    requires_manual_review: bool
```

#### Frontend TypeScript Interface (WRONG)
```typescript
export interface CorroborationResponse {
  document_id: string
  analysis_complete: boolean  // ❌ NOT IN BACKEND
  risk_score: number          // ❌ WRONG - backend returns RiskScore object
  risk_level: string          // ❌ WRONG - inside RiskScore object
  findings: {                 // ❌ WRONG - backend uses separate properties
    format_validation: any
    structure_validation: any
    image_analysis: any
  }
  alert_id?: string          // ❌ NOT IN BACKEND
}
```

### 2. Risk Score Structure Mismatch

#### Backend `RiskScore` Object
```python
class RiskScore(BaseModel):
    overall_score: float       # 0-100
    risk_level: ValidationSeverity  # "low" | "medium" | "high" | "critical"
    confidence: float          # 0-1
    contributing_factors: List[Dict[str, Any]]
    recommendations: List[str]
```

#### Frontend Expectation
```typescript
risk_score: number  // ❌ Expects flat number, gets object
risk_level: string  // ❌ Expects at root level, actually in risk_score object
```

### 3. Validation Results Structure

#### Backend Structure
```python
# Separate top-level properties
format_validation: Optional[FormatValidationResult]
structure_validation: Optional[StructureValidationResult]
content_validation: Optional[ContentValidationResult]
image_analysis: Optional[ImageAnalysisResult]
```

#### Frontend Expectation (WRONG)
```typescript
findings: {  // ❌ No "findings" wrapper in backend
  format_validation: any
  structure_validation: any
  image_analysis: any
}
```

### 4. Missing Fields in Frontend

Backend fields NOT in frontend interface:
- `file_name: str`
- `file_type: str`
- `analysis_timestamp: datetime`
- `content_validation: Optional[ContentValidationResult]`
- `processing_time: float`
- `engines_used: List[str]`
- `total_issues_found: int`
- `critical_issues_count: int`
- `requires_manual_review: bool`

### 5. Extra Fields in Frontend

Frontend fields NOT in backend:
- `analysis_complete: boolean`
- `alert_id?: string`

## Impact

### Current State
❌ **DocumentUploadAnalysis component will fail** because:
1. It accesses `response.risk_score` as a number (it's an object)
2. It accesses `response.risk_level` at root (it's inside `risk_score` object)
3. It accesses `response.findings` (doesn't exist - should use separate properties)

### Example of Current Broken Code
```typescript
// frontend/components/compliance/DocumentUploadAnalysis.tsx:123-130
const transformBackendResponse = (response: CorroborationResponse, file: File): AnalysisResult => {
  return {
    riskScore: response.risk_score,        // ❌ Gets object, expects number
    riskLevel: response.risk_level as ..., // ❌ undefined, is in risk_score.risk_level
    issuesDetected: extractIssues(response.findings),  // ❌ undefined
    passedChecks: extractPassedChecks(response.findings), // ❌ undefined
    // ...
  };
};
```

## Required Fixes

### 1. Update Frontend Types (`frontend/lib/api.ts`)

**Before:**
```typescript
export interface CorroborationResponse {
  document_id: string
  analysis_complete: boolean
  risk_score: number
  risk_level: string
  findings: { ... }
  alert_id?: string
}
```

**After:**
```typescript
export interface RiskScore {
  overall_score: number
  risk_level: "low" | "medium" | "high" | "critical"
  confidence: number
  contributing_factors: Array<{ factor: string; weight: number; score: number }>
  recommendations: string[]
}

export interface ValidationIssue {
  category: string
  severity: "low" | "medium" | "high" | "critical"
  description: string
  location?: string
  details?: Record<string, any>
}

export interface FormatValidationResult {
  has_double_spacing: boolean
  has_font_inconsistencies: boolean
  has_indentation_issues: boolean
  has_spelling_errors: boolean
  spelling_error_count: number
  issues: ValidationIssue[]
  has_formatting_issues: boolean
  double_spacing_count: number
  trailing_whitespace_count: number
  spelling_errors: string[]
}

export interface StructureValidationResult {
  is_complete: boolean
  missing_sections: string[]
  has_correct_headers: boolean
  template_match_score: number
  issues: ValidationIssue[]
}

export interface ContentValidationResult {
  has_sensitive_data: boolean
  quality_score: number
  readability_score: number
  word_count: number
  issues: ValidationIssue[]
}

export interface ImageAnalysisResult {
  is_authentic: boolean
  is_ai_generated: boolean
  ai_detection_confidence: number
  is_tampered: boolean
  tampering_confidence: number
  reverse_image_matches: number
  metadata_issues: ValidationIssue[]
  forensic_findings: ValidationIssue[]
}

export interface CorroborationResponse {
  document_id: string
  file_name: string
  file_type: string
  analysis_timestamp: string

  // Validation results (separate properties, not "findings")
  format_validation?: FormatValidationResult
  structure_validation?: StructureValidationResult
  content_validation?: ContentValidationResult
  image_analysis?: ImageAnalysisResult

  // Risk assessment (nested object)
  risk_score: RiskScore  // ✅ Now an object

  // Processing metadata
  processing_time: number
  engines_used: string[]

  // Summary
  total_issues_found: number
  critical_issues_count: number
  requires_manual_review: boolean
}
```

### 2. Update `transformBackendResponse` Function

**Before:**
```typescript
const transformBackendResponse = (response: CorroborationResponse, file: File): AnalysisResult => {
  return {
    riskScore: response.risk_score,  // ❌ Wrong
    riskLevel: response.risk_level as ...,  // ❌ Wrong
    issuesDetected: extractIssues(response.findings),  // ❌ Wrong
    passedChecks: extractPassedChecks(response.findings),  // ❌ Wrong
    // ...
  };
};
```

**After:**
```typescript
const transformBackendResponse = (response: CorroborationResponse, file: File): AnalysisResult => {
  return {
    riskScore: response.risk_score.overall_score,  // ✅ Correct
    riskLevel: response.risk_score.risk_level,     // ✅ Correct
    issuesDetected: extractIssues(response),       // ✅ Pass full response
    passedChecks: extractPassedChecks(response),   // ✅ Pass full response
    recommendation: response.risk_score.recommendations[0] || generateRecommendation(response.risk_score.risk_level),
    fileType: file.type.includes("pdf") ? "pdf" : "image",
    tampering: response.image_analysis?.is_tampered || false,
  };
};
```

### 3. Update `extractIssues` Function

**Before:**
```typescript
const extractIssues = (findings: any): string[] => {
  const issues: string[] = [];
  if (findings?.format_validation?.issues) {
    issues.push(...findings.format_validation.issues);  // ❌ Wrong
  }
  // ...
};
```

**After:**
```typescript
const extractIssues = (response: CorroborationResponse): string[] => {
  const issues: string[] = [];

  // Format validation issues
  if (response.format_validation?.issues) {
    issues.push(...response.format_validation.issues.map(i => i.description));
  }

  // Structure validation issues
  if (response.structure_validation?.issues) {
    issues.push(...response.structure_validation.issues.map(i => i.description));
  }

  // Content validation issues
  if (response.content_validation?.issues) {
    issues.push(...response.content_validation.issues.map(i => i.description));
  }

  // Image analysis issues
  if (response.image_analysis?.metadata_issues) {
    issues.push(...response.image_analysis.metadata_issues.map(i => i.description));
  }
  if (response.image_analysis?.forensic_findings) {
    issues.push(...response.image_analysis.forensic_findings.map(i => i.description));
  }

  return issues.length > 0 ? issues : ["No issues detected"];
};
```

### 4. Update `extractPassedChecks` Function

**Before:**
```typescript
const extractPassedChecks = (findings: any): string[] => {
  const checks: string[] = [];
  if (findings?.format_validation?.passed) {
    checks.push(...findings.format_validation.passed);  // ❌ "passed" doesn't exist
  }
  // ...
};
```

**After:**
```typescript
const extractPassedChecks = (response: CorroborationResponse): string[] => {
  const checks: string[] = [];

  // Format validation passed
  if (response.format_validation) {
    if (!response.format_validation.has_double_spacing) {
      checks.push("No double spacing issues");
    }
    if (!response.format_validation.has_font_inconsistencies) {
      checks.push("Font consistency verified");
    }
    if (!response.format_validation.has_spelling_errors) {
      checks.push("No spelling errors");
    }
  }

  // Structure validation passed
  if (response.structure_validation) {
    if (response.structure_validation.is_complete) {
      checks.push("Document structure is complete");
    }
    if (response.structure_validation.has_correct_headers) {
      checks.push("Headers are correctly formatted");
    }
  }

  // Image analysis passed
  if (response.image_analysis) {
    if (response.image_analysis.is_authentic) {
      checks.push("Image authenticity verified");
    }
    if (!response.image_analysis.is_ai_generated) {
      checks.push("No AI-generated content detected");
    }
    if (!response.image_analysis.is_tampered) {
      checks.push("No tampering detected");
    }
  }

  return checks.length > 0 ? checks : ["All checks passed"];
};
```

## Testing Verification

After fixes, verify:
1. ✅ Document upload to `/api/v1/corroboration/analyze` works
2. ✅ Risk score displays correctly (0-100 number)
3. ✅ Risk level displays correctly (low/medium/high/critical)
4. ✅ Issues are extracted from validation results
5. ✅ Passed checks are inferred from validation results
6. ✅ No TypeScript errors in frontend build
7. ✅ Console logs show correct response structure

## Summary

**Root Cause**: Frontend was designed with incorrect assumptions about backend response structure.

**Fix Priority**: **CRITICAL** - Must be fixed before frontend can work with backend.

**Files to Update**:
1. `frontend/lib/api.ts` - Update all type definitions
2. `frontend/components/compliance/DocumentUploadAnalysis.tsx` - Update response handling

**Estimated Time**: 30-45 minutes

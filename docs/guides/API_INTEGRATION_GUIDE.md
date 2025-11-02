# API Integration Guide
## Frontend-Backend Integration for Speed-Run Platform

**Version:** 1.0
**Date:** November 1, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Current Integration Status](#current-integration-status)
3. [Backend API Endpoints](#backend-api-endpoints)
4. [Frontend API Client](#frontend-api-client)
5. [Integration Implementation](#integration-implementation)
6. [Error Handling](#error-handling)
7. [Testing Integration](#testing-integration)

---

## 1. Overview

### 1.1 Architecture Overview

```
Frontend (Next.js)              Backend (FastAPI)
Port: 3000                      Port: 8000
├── API Client (lib/api.ts)     ├── Main App (main.py)
│   └── HTTP requests ─────────→│   ├── OCR Router
│                                │   ├── Document Router
│                                │   └── Corroboration Router
│                                │
└── Components                   └── Services
    ├── Dashboard                    ├── OCRService
    ├── Investigation                ├── DocumentService
    └── Document Viewer              └── CorroborationService
```

### 1.2 Communication Protocol

- **Protocol:** HTTP/REST
- **Data Format:** JSON
- **Authentication:** None (Phase 1), JWT (Phase 2)
- **CORS:** Enabled for `localhost:3000` and `localhost:5173`

---

## 2. Current Integration Status

### 2.1 Implemented Backend Endpoints ✅

| Endpoint | Method | Status | Purpose |
|----------|--------|--------|---------|
| `/` | GET | ✅ | Root endpoint |
| `/health` | GET | ✅ | Health check |
| `/api/v1/ocr/extract` | POST | ✅ | OCR text extraction |
| `/api/v1/ocr/health` | GET | ✅ | OCR health |
| `/api/v1/documents/parse` | POST | ✅ | Document parsing |
| `/api/v1/documents/extract-tables` | POST | ✅ | Table extraction |
| `/api/v1/documents/health` | GET | ✅ | Parser health |
| `/api/v1/corroboration/analyze` | POST | ✅ | Full fraud analysis |
| `/api/v1/corroboration/analyze-image` | POST | ✅ | Image analysis |
| `/api/v1/corroboration/validate-format` | POST | ✅ | Format validation |
| `/api/v1/corroboration/validate-structure` | POST | ✅ | Structure validation |
| `/api/v1/corroboration/report/{id}` | GET | ✅ | Get report |
| `/api/v1/corroboration/report/{id}/markdown` | GET | ✅ | Get report (MD) |
| `/api/v1/corroboration/reports` | GET | ✅ | List reports |
| `/api/v1/corroboration/health` | GET | ✅ | Corroboration health |

### 2.2 Frontend Expected Endpoints (Mock Data) 🟡

| Endpoint | Method | Status | Purpose |
|----------|--------|--------|---------|
| `/api/alerts/summary` | GET | 🟡 Mock | Dashboard summary |
| `/api/alerts/active` | GET | 🟡 Mock | Active alerts |
| `/api/transactions/volume` | GET | 🟡 Mock | Transaction volume |
| `/api/alerts/{id}` | GET | 🟡 Mock | Alert details |
| `/api/alerts/{id}/remediate` | POST | 🟡 Mock | Remediate alert |
| `/api/audit-trail/{id}` | GET | 🟡 Mock | Audit trail |

### 2.3 Integration Gap Analysis

**Gap:** Frontend expects AML-specific alert management endpoints that don't exist in backend yet.

**Recommendation:** Create bridge endpoints in backend that:
1. Map document corroboration results to alert format
2. Store alerts in memory or database
3. Provide alert management capabilities

---

## 3. Backend API Endpoints

### 3.1 Document Corroboration API

#### POST /api/v1/corroboration/analyze

**Purpose:** Comprehensive document fraud detection

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/corroboration/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.pdf" \
  -F "perform_format_validation=true" \
  -F "perform_structure_validation=true" \
  -F "perform_content_validation=true" \
  -F "perform_image_analysis=false" \
  -F "expected_document_type=invoice"
```

**Response (200):**
```json
{
  "document_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "file_name": "invoice.pdf",
  "file_type": ".pdf",
  "analysis_timestamp": "2025-11-01T12:34:56.789Z",
  "format_validation": {
    "has_double_spacing": false,
    "has_font_inconsistencies": false,
    "has_indentation_issues": false,
    "has_spelling_errors": true,
    "spelling_error_count": 3,
    "issues": [
      {
        "category": "content",
        "severity": "medium",
        "description": "Detected 3 potential spelling errors",
        "location": null,
        "details": {"sample_errors": ["acount", "recipt", "ammount"]}
      }
    ]
  },
  "structure_validation": {
    "is_complete": true,
    "missing_sections": [],
    "has_correct_headers": true,
    "template_match_score": 0.95,
    "issues": []
  },
  "content_validation": {
    "has_sensitive_data": false,
    "quality_score": 0.87,
    "readability_score": 62.5,
    "word_count": 342,
    "issues": []
  },
  "image_analysis": null,
  "risk_score": {
    "overall_score": 22.5,
    "risk_level": "low",
    "confidence": 0.85,
    "contributing_factors": [
      {
        "component": "format_validation",
        "factor": "Detected 3 potential spelling errors",
        "severity": "medium",
        "impact": 20
      }
    ],
    "recommendations": [
      "ACCEPT: Document appears legitimate",
      "Proceed with standard processing",
      "Consider requesting clarification on flagged items"
    ]
  },
  "processing_time": 2.341,
  "engines_used": ["docling", "format_validator", "structure_validator", "content_validator", "risk_scorer"],
  "total_issues_found": 1,
  "critical_issues_count": 0,
  "requires_manual_review": false
}
```

**Error Responses:**
```json
// 400 Bad Request
{
  "detail": "Unsupported file type. Allowed: ['.pdf', '.png', '.jpg', ...]"
}

// 500 Internal Server Error
{
  "detail": "Analysis failed: <error message>"
}
```

#### POST /api/v1/corroboration/analyze-image

**Purpose:** Image-only fraud detection

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/corroboration/analyze-image" \
  -F "file=@photo.jpg" \
  -F "enable_reverse_search=false"
```

**Response (200):**
```json
{
  "is_authentic": true,
  "is_ai_generated": false,
  "ai_detection_confidence": 0.234,
  "is_tampered": false,
  "tampering_confidence": 0.12,
  "reverse_image_matches": 0,
  "metadata_issues": [
    {
      "category": "metadata",
      "severity": "low",
      "description": "Missing camera information in EXIF data"
    }
  ],
  "forensic_findings": []
}
```

#### GET /api/v1/corroboration/reports

**Purpose:** List and filter corroboration reports

**Request:**
```bash
curl "http://localhost:8000/api/v1/corroboration/reports?limit=10&risk_level=high&requires_manual_review=true"
```

**Response (200):**
```json
[
  {
    "document_id": "uuid1",
    "file_name": "suspicious_doc.pdf",
    "timestamp": "2025-11-01T10:30:00Z",
    "risk_score": 78.5,
    "risk_level": "high",
    "total_issues": 12,
    "critical_issues": 3,
    "requires_manual_review": true
  }
]
```

---

## 4. Frontend API Client

### 4.1 Current Implementation (lib/api.ts)

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // Current methods (using mock data)
  async getDashboardSummary(): Promise<DashboardSummary> {
    return this.request<DashboardSummary>("/api/alerts/summary");
  }

  async getActiveAlerts(): Promise<Alert[]> {
    return this.request<Alert[]>("/api/alerts/active");
  }

  // ... other methods
}

export const apiClient = new ApiClient(API_URL);
```

### 4.2 Recommended Enhancements

#### Add Document Corroboration Methods

```typescript
class ApiClient {
  // ... existing methods

  /**
   * Upload and analyze a document for fraud
   */
  async analyzeDocument(
    file: File,
    options?: {
      performFormatValidation?: boolean;
      performStructureValidation?: boolean;
      performContentValidation?: boolean;
      performImageAnalysis?: boolean;
      expectedDocumentType?: string;
    }
  ): Promise<CorroborationReport> {
    const formData = new FormData();
    formData.append("file", file);

    if (options?.performFormatValidation !== undefined) {
      formData.append("perform_format_validation", String(options.performFormatValidation));
    }
    if (options?.performStructureValidation !== undefined) {
      formData.append("perform_structure_validation", String(options.performStructureValidation));
    }
    if (options?.performContentValidation !== undefined) {
      formData.append("perform_content_validation", String(options.performContentValidation));
    }
    if (options?.performImageAnalysis !== undefined) {
      formData.append("perform_image_analysis", String(options.performImageAnalysis));
    }
    if (options?.expectedDocumentType) {
      formData.append("expected_document_type", options.expectedDocumentType);
    }

    const response = await fetch(`${this.baseUrl}/api/v1/corroboration/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Analysis failed");
    }

    return response.json();
  }

  /**
   * Analyze image for fraud
   */
  async analyzeImage(
    file: File,
    enableReverseSearch: boolean = false
  ): Promise<ImageAnalysisResult> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("enable_reverse_search", String(enableReverseSearch));

    const response = await fetch(`${this.baseUrl}/api/v1/corroboration/analyze-image`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Image analysis failed");
    }

    return response.json();
  }

  /**
   * Get corroboration report by ID
   */
  async getCorroborationReport(documentId: string): Promise<CorroborationReport> {
    return this.request<CorroborationReport>(
      `/api/v1/corroboration/report/${documentId}`
    );
  }

  /**
   * List corroboration reports
   */
  async listCorroborationReports(filters?: {
    limit?: number;
    riskLevel?: "low" | "medium" | "high" | "critical";
    requiresManualReview?: boolean;
  }): Promise<CorroborationReportSummary[]> {
    const params = new URLSearchParams();
    if (filters?.limit) params.append("limit", String(filters.limit));
    if (filters?.riskLevel) params.append("risk_level", filters.riskLevel);
    if (filters?.requiresManualReview !== undefined) {
      params.append("requires_manual_review", String(filters.requiresManualReview));
    }

    return this.request<CorroborationReportSummary[]>(
      `/api/v1/corroboration/reports?${params.toString()}`
    );
  }
}
```

#### Add TypeScript Types

```typescript
// types/corroboration.ts

export interface CorroborationReport {
  document_id: string;
  file_name: string;
  file_type: string;
  analysis_timestamp: string;
  format_validation: FormatValidationResult | null;
  structure_validation: StructureValidationResult | null;
  content_validation: ContentValidationResult | null;
  image_analysis: ImageAnalysisResult | null;
  risk_score: RiskScore;
  processing_time: number;
  engines_used: string[];
  total_issues_found: number;
  critical_issues_count: number;
  requires_manual_review: boolean;
}

export interface RiskScore {
  overall_score: number;  // 0-100
  risk_level: "low" | "medium" | "high" | "critical";
  confidence: number;  // 0-1
  contributing_factors: ContributingFactor[];
  recommendations: string[];
}

export interface ValidationIssue {
  category: string;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  location?: string;
  details?: Record<string, any>;
}

export interface FormatValidationResult {
  has_double_spacing: boolean;
  has_font_inconsistencies: boolean;
  has_indentation_issues: boolean;
  has_spelling_errors: boolean;
  spelling_error_count: number;
  issues: ValidationIssue[];
}

export interface StructureValidationResult {
  is_complete: boolean;
  missing_sections: string[];
  has_correct_headers: boolean;
  template_match_score: number;  // 0-1
  issues: ValidationIssue[];
}

export interface ContentValidationResult {
  has_sensitive_data: boolean;
  quality_score: number;  // 0-1
  readability_score: number;  // 0-100
  word_count: number;
  issues: ValidationIssue[];
}

export interface ImageAnalysisResult {
  is_authentic: boolean;
  is_ai_generated: boolean;
  ai_detection_confidence: number;  // 0-1
  is_tampered: boolean;
  tampering_confidence: number;  // 0-1
  reverse_image_matches: number;
  metadata_issues: ValidationIssue[];
  forensic_findings: ValidationIssue[];
}
```

---

## 5. Integration Implementation

### 5.1 Document Upload Component

```typescript
// components/DocumentUpload.tsx

"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);

  const analyzeMutation = useMutation({
    mutationFn: (file: File) => apiClient.analyzeDocument(file, {
      performFormatValidation: true,
      performStructureValidation: true,
      performContentValidation: true,
      performImageAnalysis: false,
      expectedDocumentType: "invoice",
    }),
    onSuccess: (data) => {
      setResult(data);
    },
    onError: (error) => {
      console.error("Analysis failed:", error);
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      analyzeMutation.mutate(file);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Document for Analysis</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,.docx"
            onChange={handleFileChange}
            className="block w-full"
          />

          <Button
            type="submit"
            disabled={!file || analyzeMutation.isPending}
          >
            {analyzeMutation.isPending ? "Analyzing..." : "Analyze Document"}
          </Button>
        </form>

        {result && (
          <div className="mt-4 space-y-4">
            <div>
              <h3 className="font-bold">Risk Score: {result.risk_score.overall_score}</h3>
              <p>Risk Level: {result.risk_score.risk_level.toUpperCase()}</p>
              <p>Requires Manual Review: {result.requires_manual_review ? "Yes" : "No"}</p>
            </div>

            {result.risk_score.recommendations.map((rec: string, idx: number) => (
              <p key={idx} className="text-sm">{rec}</p>
            ))}

            <div>
              <h4 className="font-semibold">Issues Found: {result.total_issues_found}</h4>
              <p>Critical Issues: {result.critical_issues_count}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

### 5.2 Reports List Component

```typescript
// components/CorroborationReportsList.tsx

"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export function CorroborationReportsList() {
  const { data: reports, isLoading } = useQuery({
    queryKey: ["corroboration-reports"],
    queryFn: () => apiClient.listCorroborationReports({ limit: 50 }),
  });

  if (isLoading) return <div>Loading reports...</div>;

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Document ID</TableHead>
          <TableHead>File Name</TableHead>
          <TableHead>Timestamp</TableHead>
          <TableHead>Risk Score</TableHead>
          <TableHead>Risk Level</TableHead>
          <TableHead>Manual Review</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {reports?.map((report) => (
          <TableRow key={report.document_id}>
            <TableCell className="font-mono text-xs">
              {report.document_id.slice(0, 8)}...
            </TableCell>
            <TableCell>{report.file_name}</TableCell>
            <TableCell>{new Date(report.timestamp).toLocaleString()}</TableCell>
            <TableCell>{report.risk_score.toFixed(1)}</TableCell>
            <TableCell>
              <Badge
                variant={
                  report.risk_level === "critical" ? "destructive" :
                  report.risk_level === "high" ? "destructive" :
                  report.risk_level === "medium" ? "default" :
                  "secondary"
                }
              >
                {report.risk_level.toUpperCase()}
              </Badge>
            </TableCell>
            <TableCell>
              {report.requires_manual_review ? "Yes" : "No"}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
```

---

## 6. Error Handling

### 6.1 Backend Error Responses

**Standard Error Format:**
```json
{
  "detail": "Error message description"
}
```

**Common Error Codes:**
- `400 Bad Request` - Invalid input, unsupported file type, file too large
- `404 Not Found` - Report not found
- `500 Internal Server Error` - Processing failure

### 6.2 Frontend Error Handling

```typescript
// lib/api.ts

class ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new ApiError(error.detail, response.status);
      }

      return response.json();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError("Network error occurred", 0);
    }
  }
}

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}
```

**Usage in Components:**
```typescript
const mutation = useMutation({
  mutationFn: apiClient.analyzeDocument,
  onError: (error) => {
    if (error instanceof ApiError) {
      if (error.statusCode === 400) {
        toast.error("Invalid file. Please check file type and size.");
      } else if (error.statusCode === 500) {
        toast.error("Analysis failed. Please try again.");
      }
    }
  },
});
```

---

## 7. Testing Integration

### 7.1 Backend API Testing

```bash
# Test health check
curl http://localhost:8000/health

# Test OCR
curl -X POST "http://localhost:8000/api/v1/ocr/extract" \
  -F "file=@test_image.png"

# Test document corroboration
curl -X POST "http://localhost:8000/api/v1/corroboration/analyze" \
  -F "file=@test_invoice.pdf" \
  -F "expected_document_type=invoice"

# Test list reports
curl "http://localhost:8000/api/v1/corroboration/reports?limit=10"
```

### 7.2 Frontend Integration Testing

```typescript
// __tests__/api-client.test.ts

import { apiClient } from "@/lib/api";

describe("API Client", () => {
  it("should analyze document", async () => {
    const file = new File(["test content"], "test.pdf", { type: "application/pdf" });

    const result = await apiClient.analyzeDocument(file);

    expect(result).toHaveProperty("document_id");
    expect(result).toHaveProperty("risk_score");
    expect(result.risk_score).toHaveProperty("overall_score");
  });

  it("should handle error responses", async () => {
    const invalidFile = new File(["test"], "test.exe", { type: "application/exe" });

    await expect(apiClient.analyzeDocument(invalidFile)).rejects.toThrow();
  });
});
```

### 7.3 End-to-End Testing

```typescript
// e2e/document-upload.spec.ts

import { test, expect } from "@playwright/test";

test("document upload and analysis flow", async ({ page }) => {
  await page.goto("http://localhost:3000/upload");

  // Upload file
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles("./test-files/invoice.pdf");

  // Submit
  await page.click('button:has-text("Analyze Document")');

  // Wait for results
  await page.waitForSelector('text=Risk Score', { timeout: 10000 });

  // Verify results displayed
  const riskScore = await page.textContent('[data-testid="risk-score"]');
  expect(riskScore).toBeTruthy();
});
```

---

## 8. Configuration

### 8.1 Environment Variables

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (.env):**
```bash
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
MAX_FILE_SIZE=10485760  # 10MB
AUDIT_LOG_PATH=/tmp/corroboration_audit
```

### 8.2 CORS Configuration

**Backend (main.py):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 9. Next Steps

### 9.1 Immediate Actions

1. **Add corroboration methods to frontend API client**
2. **Create TypeScript types for corroboration responses**
3. **Implement document upload component**
4. **Add reports list component**
5. **Test end-to-end integration**

### 9.2 Phase 2 Enhancements

1. **Implement AML alert management endpoints in backend**
2. **Add WebSocket support for real-time updates**
3. **Implement authentication (JWT)**
4. **Add file upload progress tracking**
5. **Implement batch processing**

---

**Document Status:** ✅ Complete
**Last Updated:** 2025-11-01

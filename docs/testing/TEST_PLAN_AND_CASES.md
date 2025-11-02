# Test Plan and Test Cases
## Speed-Run: Document Corroboration Platform

**Version:** 1.0
**Date:** November 1, 2025
**Test Phase:** MVP (Phase 1)

---

## Table of Contents

1. [Test Strategy](#test-strategy)
2. [Test Environments](#test-environments)
3. [Unit Test Cases](#unit-test-cases)
4. [Integration Test Cases](#integration-test-cases)
5. [API Test Cases](#api-test-cases)
6. [End-to-End Test Cases](#end-to-end-test-cases)
7. [Performance Test Cases](#performance-test-cases)
8. [Security Test Cases](#security-test-cases)
9. [Sample Test Data](#sample-test-data)
10. [Test Execution Guide](#test-execution-guide)

---

## 1. Test Strategy

### 1.1 Testing Pyramid

```
                    ▲
                   / \
                  /   \
                 / E2E \                 10% - End-to-End Tests
                /───────\
               /         \
              / Integration \           30% - Integration Tests
             /─────────────\
            /               \
           /   Unit  Tests   \         60% - Unit Tests
          /───────────────────\
```

### 1.2 Test Levels

| Level | Coverage | Tools | Responsibility |
|-------|----------|-------|----------------|
| Unit Tests | 80%+ | pytest, jest | Developers |
| Integration Tests | Key workflows | pytest, React Testing Library | Developers |
| API Tests | All endpoints | pytest, curl, Postman | QA/Developers |
| E2E Tests | Critical paths | Playwright | QA |
| Performance Tests | Load scenarios | Locust, k6 | QA/DevOps |
| Security Tests | OWASP Top 10 | OWASP ZAP, Bandit | Security Team |

### 1.3 Test Scope

**In Scope:**
- ✅ Backend API endpoints
- ✅ Document processing services
- ✅ Validation logic
- ✅ Risk scoring algorithm
- ✅ Report generation
- ✅ Frontend components
- ✅ API integration
- ✅ Error handling

**Out of Scope (Phase 2):**
- ❌ Authentication/Authorization
- ❌ Database operations (no DB in MVP)
- ❌ External API integrations (optional)
- ❌ Real-time WebSocket updates
- ❌ Mobile applications

---

## 2. Test Environments

### 2.1 Local Development
```
Frontend: http://localhost:3000
Backend: http://localhost:8000
Audit Logs: /tmp/corroboration_audit
```

### 2.2 Test Data Location
```
test-files/
├── documents/
│   ├── valid/
│   │   ├── invoice_clean.pdf
│   │   ├── contract_complete.pdf
│   │   └── report_proper.docx
│   ├── invalid/
│   │   ├── invoice_spelling_errors.pdf
│   │   ├── contract_incomplete.pdf
│   │   └── document_tampered.pdf
│   └── edge_cases/
│       ├── empty.pdf
│       ├── large_5mb.pdf
│       └── corrupt.pdf
└── images/
    ├── valid/
    │   ├── passport_real.jpg
    │   └── id_card_authentic.png
    ├── suspicious/
    │   ├── ai_generated_face.jpg
    │   ├── tampered_photo.png
    │   └── no_exif.jpg
    └── edge_cases/
        ├── tiny_10x10.png
        └── huge_10mb.jpg
```

---

## 3. Unit Test Cases

### 3.1 Backend Unit Tests

#### Test Suite: DocumentValidator

**Test File:** `tests/test_document_validator.py`

```python
import pytest
from pathlib import Path
from backend.services.document_validator import DocumentValidator
from backend.schemas.validation import ValidationSeverity

@pytest.fixture
def validator():
    return DocumentValidator()

class TestFormatValidation:
    """Test format validation functionality"""

    async def test_detect_double_spacing(self, validator):
        """TC-UV-001: Should detect double spacing"""
        text = "This  document  has  double  spaces."
        result = await validator.validate_format(text, Path("dummy.txt"))

        assert result.has_double_spacing is True
        assert len(result.issues) > 0
        assert any("spacing" in issue.description.lower() for issue in result.issues)

    async def test_detect_spelling_errors(self, validator):
        """TC-UV-002: Should detect spelling errors"""
        text = "This documnt has splling erors."
        result = await validator.validate_format(text, Path("dummy.txt"))

        assert result.has_spelling_errors is True
        assert result.spelling_error_count > 0

    async def test_clean_document_passes(self, validator):
        """TC-UV-003: Clean document should pass validation"""
        text = "This is a properly formatted document with correct spelling."
        result = await validator.validate_format(text, Path("dummy.txt"))

        assert result.has_double_spacing is False
        assert result.spelling_error_count == 0

class TestStructureValidation:
    """Test structure validation functionality"""

    async def test_detect_missing_sections(self, validator):
        """TC-UV-004: Should detect missing sections"""
        text = "Introduction only, no conclusion."
        result = await validator.validate_structure(
            text,
            Path("dummy.txt"),
            expected_document_type="report"
        )

        assert not result.is_complete
        assert len(result.missing_sections) > 0

    async def test_template_matching(self, validator):
        """TC-UV-005: Should match invoice template"""
        text = "Invoice Date Amount Description Total"
        result = await validator.validate_structure(
            text,
            Path("dummy.txt"),
            expected_document_type="invoice"
        )

        assert result.template_match_score > 0.5

class TestContentValidation:
    """Test content validation functionality"""

    async def test_detect_pii(self, validator):
        """TC-UV-006: Should detect PII in content"""
        text = "My SSN is 123-45-6789 and credit card 4111-1111-1111-1111"
        result = await validator.validate_content(text)

        assert result.has_sensitive_data is True
        assert any("PII" in issue.description or "sensitive" in issue.description
                   for issue in result.issues)

    async def test_readability_score(self, validator):
        """TC-UV-007: Should calculate readability score"""
        text = "The quick brown fox jumps over the lazy dog. " * 20
        result = await validator.validate_content(text)

        assert 0 <= result.readability_score <= 100
        assert result.word_count > 0
```

#### Test Suite: ImageAnalyzer

**Test File:** `tests/test_image_analyzer.py`

```python
import pytest
from pathlib import Path
from PIL import Image
import numpy as np
from backend.services.image_analyzer import ImageAnalyzer

@pytest.fixture
def analyzer():
    return ImageAnalyzer()

@pytest.fixture
def test_image_path(tmp_path):
    """Create a test image"""
    img = Image.new('RGB', (100, 100), color='red')
    path = tmp_path / "test.png"
    img.save(path)
    return path

class TestImageAnalysis:
    """Test image analysis functionality"""

    async def test_analyze_valid_image(self, analyzer, test_image_path):
        """TC-UV-008: Should analyze valid image"""
        result = await analyzer.analyze_image(test_image_path, perform_reverse_search=False)

        assert result is not None
        assert hasattr(result, 'is_authentic')
        assert hasattr(result, 'is_ai_generated')
        assert 0 <= result.ai_detection_confidence <= 1

    async def test_exif_metadata_extraction(self, analyzer, test_image_path):
        """TC-UV-009: Should extract EXIF metadata"""
        result = await analyzer.analyze_image(test_image_path)

        # Image created without EXIF should be flagged
        assert len(result.metadata_issues) > 0

    async def test_tampering_detection(self, analyzer, test_image_path):
        """TC-UV-010: Should detect tampering via ELA"""
        result = await analyzer.analyze_image(test_image_path)

        assert hasattr(result, 'is_tampered')
        assert hasattr(result, 'tampering_confidence')
        assert 0 <= result.tampering_confidence <= 1
```

#### Test Suite: RiskScorer

**Test File:** `tests/test_risk_scorer.py`

```python
import pytest
from backend.services.risk_scorer import RiskScorer
from backend.schemas.validation import *

@pytest.fixture
def scorer():
    return RiskScorer()

class TestRiskScoring:
    """Test risk scoring functionality"""

    async def test_calculate_low_risk(self, scorer):
        """TC-UV-011: Clean document should have low risk"""
        format_val = FormatValidationResult(
            has_double_spacing=False,
            has_font_inconsistencies=False,
            has_indentation_issues=False,
            has_spelling_errors=False,
            spelling_error_count=0,
            issues=[]
        )

        structure_val = StructureValidationResult(
            is_complete=True,
            missing_sections=[],
            has_correct_headers=True,
            template_match_score=0.95,
            issues=[]
        )

        content_val = ContentValidationResult(
            has_sensitive_data=False,
            quality_score=0.9,
            readability_score=70.0,
            word_count=300,
            issues=[]
        )

        risk = await scorer.calculate_risk_score(
            format_validation=format_val,
            structure_validation=structure_val,
            content_validation=content_val,
            image_analysis=None
        )

        assert risk.overall_score < 25
        assert risk.risk_level == ValidationSeverity.LOW

    async def test_calculate_critical_risk(self, scorer):
        """TC-UV-012: Tampered image should have critical risk"""
        image_analysis = ImageAnalysisResult(
            is_authentic=False,
            is_ai_generated=True,
            ai_detection_confidence=0.95,
            is_tampered=True,
            tampering_confidence=0.9,
            reverse_image_matches=10,
            metadata_issues=[],
            forensic_findings=[]
        )

        risk = await scorer.calculate_risk_score(
            format_validation=None,
            structure_validation=None,
            content_validation=None,
            image_analysis=image_analysis
        )

        assert risk.overall_score > 75
        assert risk.risk_level == ValidationSeverity.CRITICAL
        assert len(risk.recommendations) > 0
```

---

## 4. Integration Test Cases

### 4.1 Service Integration Tests

**Test File:** `tests/integration/test_corroboration_service.py`

```python
import pytest
from pathlib import Path
from backend.services.corroboration_service import CorroborationService
from backend.schemas.validation import CorroborationRequest

@pytest.fixture
def corroboration_service():
    return CorroborationService()

@pytest.fixture
def sample_pdf_bytes():
    """Read sample PDF file"""
    path = Path("test-files/documents/valid/invoice_clean.pdf")
    with open(path, "rb") as f:
        return f.read()

class TestCorroborationWorkflow:
    """Test end-to-end corroboration workflow"""

    async def test_analyze_pdf_document(self, corroboration_service, sample_pdf_bytes):
        """TC-IT-001: Should analyze PDF document end-to-end"""
        request = CorroborationRequest(
            perform_format_validation=True,
            perform_structure_validation=True,
            perform_content_validation=True,
            perform_image_analysis=False,
            expected_document_type="invoice"
        )

        report = await corroboration_service.analyze_document(
            file_bytes=sample_pdf_bytes,
            filename="invoice.pdf",
            request=request
        )

        assert report.document_id is not None
        assert report.file_name == "invoice.pdf"
        assert report.risk_score is not None
        assert report.format_validation is not None
        assert report.structure_validation is not None
        assert report.content_validation is not None
        assert report.processing_time > 0

    async def test_report_generation_and_retrieval(self, corroboration_service, sample_pdf_bytes):
        """TC-IT-002: Should generate and retrieve report"""
        request = CorroborationRequest()

        # Generate report
        report = await corroboration_service.analyze_document(
            sample_pdf_bytes,
            "test.pdf",
            request
        )

        document_id = report.document_id

        # Retrieve report
        retrieved = await corroboration_service.get_report(document_id)

        assert retrieved is not None
        assert retrieved.document_id == document_id
        assert retrieved.file_name == report.file_name
```

---

## 5. API Test Cases

### 5.1 REST API Tests

**Test File:** `tests/api/test_corroboration_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from pathlib import Path

@pytest.fixture
def client():
    return TestClient(app)

class TestCorroborationAPI:
    """Test Corroboration API endpoints"""

    def test_health_endpoint(self, client):
        """TC-API-001: Health check should return 200"""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_analyze_endpoint_with_pdf(self, client):
        """TC-API-002: Should analyze PDF document"""
        with open("test-files/documents/valid/invoice_clean.pdf", "rb") as f:
            response = client.post(
                "/api/v1/corroboration/analyze",
                files={"file": ("invoice.pdf", f, "application/pdf")},
                data={
                    "perform_format_validation": "true",
                    "perform_structure_validation": "true",
                    "expected_document_type": "invoice"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert "risk_score" in data
        assert "overall_score" in data["risk_score"]

    def test_analyze_endpoint_invalid_file_type(self, client):
        """TC-API-003: Should reject invalid file type"""
        with open("test-files/invalid/test.exe", "rb") as f:
            response = client.post(
                "/api/v1/corroboration/analyze",
                files={"file": ("test.exe", f, "application/exe")}
            )

        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

    def test_analyze_endpoint_file_too_large(self, client):
        """TC-API-004: Should reject file exceeding size limit"""
        # Create 11MB file (exceeds 10MB limit)
        large_content = b"x" * (11 * 1024 * 1024)

        response = client.post(
            "/api/v1/corroboration/analyze",
            files={"file": ("large.pdf", large_content, "application/pdf")}
        )

        assert response.status_code == 400
        assert "exceeds maximum" in response.json()["detail"]

    def test_list_reports_endpoint(self, client):
        """TC-API-005: Should list reports"""
        response = client.get("/api/v1/corroboration/reports?limit=10")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_reports_with_filters(self, client):
        """TC-API-006: Should filter reports by risk level"""
        response = client.get(
            "/api/v1/corroboration/reports?risk_level=high&limit=10"
        )

        assert response.status_code == 200
        reports = response.json()
        for report in reports:
            assert report["risk_level"] == "high"

    def test_get_report_by_id(self, client):
        """TC-API-007: Should retrieve report by ID"""
        # First create a report
        with open("test-files/documents/valid/invoice_clean.pdf", "rb") as f:
            create_response = client.post(
                "/api/v1/corroboration/analyze",
                files={"file": ("invoice.pdf", f, "application/pdf")}
            )

        document_id = create_response.json()["document_id"]

        # Retrieve the report
        response = client.get(f"/api/v1/corroboration/report/{document_id}")

        assert response.status_code == 200
        assert response.json()["document_id"] == document_id

    def test_get_report_markdown(self, client):
        """TC-API-008: Should export report as markdown"""
        # First create a report
        with open("test-files/documents/valid/invoice_clean.pdf", "rb") as f:
            create_response = client.post(
                "/api/v1/corroboration/analyze",
                files={"file": ("invoice.pdf", f, "application/pdf")}
            )

        document_id = create_response.json()["document_id"]

        # Get markdown
        response = client.get(f"/api/v1/corroboration/report/{document_id}/markdown")

        assert response.status_code == 200
        assert "# Document Corroboration Report" in response.text

    def test_analyze_image_endpoint(self, client):
        """TC-API-009: Should analyze image"""
        with open("test-files/images/valid/passport_real.jpg", "rb") as f:
            response = client.post(
                "/api/v1/corroboration/analyze-image",
                files={"file": ("passport.jpg", f, "image/jpeg")},
                data={"enable_reverse_search": "false"}
            )

        assert response.status_code == 200
        data = response.json()
        assert "is_authentic" in data
        assert "is_ai_generated" in data
        assert "is_tampered" in data
```

### 5.2 Curl Test Commands

```bash
#!/bin/bash
# API Test Script

BASE_URL="http://localhost:8000"
TEST_FILES="test-files"

echo "=== API Test Suite ==="

# TC-API-001: Health Check
echo "\n[TC-API-001] Testing health endpoint..."
curl -s $BASE_URL/health | jq .

# TC-API-002: Analyze PDF Document
echo "\n[TC-API-002] Analyzing PDF document..."
curl -X POST "$BASE_URL/api/v1/corroboration/analyze" \
  -F "file=@$TEST_FILES/documents/valid/invoice_clean.pdf" \
  -F "expected_document_type=invoice" \
  | jq '.risk_score'

# TC-API-003: Invalid File Type
echo "\n[TC-API-003] Testing invalid file type..."
curl -X POST "$BASE_URL/api/v1/corroboration/analyze" \
  -F "file=@$TEST_FILES/invalid/test.exe" \
  | jq .

# TC-API-005: List Reports
echo "\n[TC-API-005] Listing reports..."
curl -s "$BASE_URL/api/v1/corroboration/reports?limit=5" | jq 'length'

# TC-API-009: Analyze Image
echo "\n[TC-API-009] Analyzing image..."
curl -X POST "$BASE_URL/api/v1/corroboration/analyze-image" \
  -F "file=@$TEST_FILES/images/valid/passport_real.jpg" \
  | jq '.is_authentic, .is_ai_generated'

echo "\n=== Tests Complete ==="
```

---

## 6. End-to-End Test Cases

### 6.1 Playwright E2E Tests

**Test File:** `e2e/document-workflow.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Document Upload and Analysis Workflow', () => {
  test('TC-E2E-001: Complete document analysis workflow', async ({ page }) => {
    // Navigate to upload page
    await page.goto('http://localhost:3000/upload');

    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./test-files/documents/valid/invoice_clean.pdf');

    // Submit analysis
    await page.click('button:has-text("Analyze Document")');

    // Wait for processing
    await page.waitForSelector('[data-testid="risk-score"]', { timeout: 10000 });

    // Verify results displayed
    const riskScore = await page.textContent('[data-testid="risk-score"]');
    expect(parseFloat(riskScore!)).toBeGreaterThanOrEqual(0);
    expect(parseFloat(riskScore!)).toBeLessThanOrEqual(100);

    // Verify risk level shown
    await expect(page.locator('[data-testid="risk-level"]')).toBeVisible();

    // Verify recommendations shown
    await expect(page.locator('[data-testid="recommendations"]')).toBeVisible();
  });

  test('TC-E2E-002: View reports list', async ({ page }) => {
    await page.goto('http://localhost:3000/reports');

    // Wait for reports to load
    await page.waitForSelector('table tbody tr', { timeout: 5000 });

    // Verify table has rows
    const rows = await page.locator('table tbody tr').count();
    expect(rows).toBeGreaterThan(0);

    // Click on first report
    await page.click('table tbody tr:first-child');

    // Verify report detail page loads
    await expect(page.locator('h1:has-text("Report Details")')).toBeVisible();
  });

  test('TC-E2E-003: Error handling for invalid file', async ({ page }) => {
    await page.goto('http://localhost:3000/upload');

    // Try to upload invalid file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./test-files/invalid/test.exe');

    await page.click('button:has-text("Analyze Document")');

    // Verify error message shown
    await expect(page.locator('text=Unsupported file type')).toBeVisible({ timeout: 5000 });
  });
});
```

---

## 7. Performance Test Cases

### 7.1 Load Testing with Locust

**Test File:** `tests/performance/locustfile.py`

```python
from locust import HttpUser, task, between

class DocumentAnalysisUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def analyze_document(self):
        """TC-PERF-001: Load test document analysis"""
        with open("test-files/documents/valid/invoice_clean.pdf", "rb") as f:
            files = {"file": ("invoice.pdf", f, "application/pdf")}
            self.client.post(
                "/api/v1/corroboration/analyze",
                files=files,
                data={"expected_document_type": "invoice"}
            )

    @task(2)
    def list_reports(self):
        """TC-PERF-002: Load test report listing"""
        self.client.get("/api/v1/corroboration/reports?limit=10")

    @task(1)
    def health_check(self):
        """TC-PERF-003: Health check endpoint"""
        self.client.get("/health")
```

**Run Performance Test:**
```bash
# Test with 10 concurrent users
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2
```

**Performance Acceptance Criteria:**
- P50 response time: < 500ms
- P95 response time: < 2000ms
- P99 response time: < 5000ms
- Error rate: < 1%
- Throughput: > 100 requests/second

---

## 8. Security Test Cases

### 8.1 Security Tests

```python
# tests/security/test_security.py

class TestSecurity:
    """Security test cases"""

    def test_sql_injection_prevention(self, client):
        """TC-SEC-001: Should prevent SQL injection"""
        malicious_input = "'; DROP TABLE reports; --"

        response = client.get(
            f"/api/v1/corroboration/report/{malicious_input}"
        )

        assert response.status_code in [400, 404]
        # System should not crash

    def test_xss_prevention(self, client):
        """TC-SEC-002: Should prevent XSS attacks"""
        with open("test-files/malicious/xss_payload.pdf", "rb") as f:
            response = client.post(
                "/api/v1/corroboration/analyze",
                files={"file": ("<script>alert('xss')</script>.pdf", f)}
            )

        # Should sanitize filename
        if response.status_code == 200:
            data = response.json()
            assert "<script>" not in data["file_name"]

    def test_file_upload_size_limit(self, client):
        """TC-SEC-003: Should enforce file size limits"""
        # Exceeds 10MB limit
        large_content = b"x" * (11 * 1024 * 1024)

        response = client.post(
            "/api/v1/corroboration/analyze",
            files={"file": ("large.pdf", large_content)}
        )

        assert response.status_code == 400

    def test_malicious_file_handling(self, client):
        """TC-SEC-004: Should reject malicious files"""
        with open("test-files/malicious/virus.txt", "rb") as f:
            response = client.post(
                "/api/v1/corroboration/analyze",
                files={"file": ("virus.txt", f)}
            )

        # Should reject or handle safely
        assert response.status_code in [400, 500]
```

---

## 9. Sample Test Data

### 9.1 Create Test Files Script

```python
# scripts/create_test_files.py

"""
Generate sample test files for testing
"""

from pathlib import Path
from PIL import Image
import random

def create_test_directories():
    """Create test directory structure"""
    base = Path("test-files")

    dirs = [
        "documents/valid",
        "documents/invalid",
        "documents/edge_cases",
        "images/valid",
        "images/suspicious",
        "images/edge_cases",
    ]

    for dir_path in dirs:
        (base / dir_path).mkdir(parents=True, exist_ok=True)

def create_sample_images():
    """Create sample test images"""
    base = Path("test-files/images")

    # Valid image
    img = Image.new('RGB', (800, 600), color='blue')
    img.save(base / "valid/sample_clean.jpg", quality=95)

    # Tiny image (edge case)
    tiny = Image.new('RGB', (10, 10), color='red')
    tiny.save(base / "edge_cases/tiny_10x10.png")

    # Large image
    large = Image.new('RGB', (4000, 3000), color='green')
    large.save(base / "edge_cases/large_image.jpg", quality=95)

def create_sample_documents():
    """Create sample text documents"""
    base = Path("test-files/documents")

    # Valid document
    valid_text = """
    INVOICE

    Invoice Number: INV-2024-001
    Date: November 1, 2024
    Amount: $1,250.00

    Description:
    Consulting services for October 2024

    Total: $1,250.00

    Thank you for your business.
    """
    (base / "valid/invoice_text.txt").write_text(valid_text)

    # Invalid document with spelling errors
    invalid_text = """
    INVOCE

    Invoce Numbr: INV-2024-002
    Dat: November 1, 2024
    Ammount: $1,250.00

    Descriptin:
    Consultin servces for Octobr 2024

    Totl: $1,250.00

    Thnk you for your busines.
    """
    (base / "invalid/invoice_spelling_errors.txt").write_text(invalid_text)

    # Empty document (edge case)
    (base / "edge_cases/empty.txt").write_text("")

if __name__ == "__main__":
    create_test_directories()
    create_sample_images()
    create_sample_documents()
    print("✅ Test files created successfully!")
```

### 9.2 Sample Test Data

#### Valid Invoice (invoice_clean.txt)
```
INVOICE

Invoice Number: INV-2024-12345
Date: November 1, 2024
Customer: Acme Corporation
Address: 123 Business St, New York, NY 10001

Description                  Quantity    Unit Price    Amount
-----------------------------------------------------------
Consulting Services             40          $150      $6,000
Software License                 1        $1,200      $1,200
Support Package                  1          $500        $500
-----------------------------------------------------------
Subtotal:                                             $7,700
Tax (8%):                                               $616
Total:                                                $8,316

Payment Terms: Net 30
Due Date: December 1, 2024

Thank you for your business!
```

#### Invalid Invoice with Errors (invoice_errors.txt)
```
INVOCE

Invoce  Number:  INV-2024-12345
Dat: Novembr 1, 2024
Custmer: Acme Corpration
Adress: 123 Busness St, New York, NY 10001

Descriptin                  Quantity    Unit Pric    Amount
-----------------------------------------------------------
Consultin Servces             40          $150      $6,000
Softare Licens                 1        $1,200      $1,200
Suport Packge                  1          $500        $500
-----------------------------------------------------------
Subtotl:                                             $7,700
Tx (8%):                                               $616
Totl:                                                $8,316

Payement Trms: Net 30
Du Date: Decembr 1, 2024

Thnk you for your busines!
```

---

## 10. Test Execution Guide

### 10.1 Running Backend Tests

```bash
# Install test dependencies
cd backend
pip install pytest pytest-asyncio pytest-cov

# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=backend --cov-report=html

# Run integration tests
pytest tests/integration/ -v

# Run API tests
pytest tests/api/ -v

# Run specific test
pytest tests/unit/test_document_validator.py::TestFormatValidation::test_detect_double_spacing

# Run tests matching pattern
pytest -k "validate" -v
```

### 10.2 Running Frontend Tests

```bash
# Install test dependencies
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Run tests in watch mode
npm test -- --watch
```

### 10.3 Running API Tests with Curl

```bash
# Make script executable
chmod +x scripts/api_tests.sh

# Run all API tests
./scripts/api_tests.sh

# Run single test
curl -X POST "http://localhost:8000/api/v1/corroboration/analyze" \
  -F "file=@test-files/documents/valid/invoice_clean.pdf"
```

### 10.4 Running Performance Tests

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Open browser to http://localhost:8089
# Configure: 100 users, spawn rate 10/sec
```

### 10.5 CI/CD Integration

**GitHub Actions Workflow (.github/workflows/test.yml):**
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
          python -m spacy download en_core_web_sm
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage
```

---

## 11. Test Metrics and Reporting

### 11.1 Success Criteria

| Metric | Target | Current |
|--------|--------|---------|
| Unit Test Coverage | 80%+ | 🟡 TBD |
| Integration Test Coverage | 60%+ | 🟡 TBD |
| API Test Coverage | 100% endpoints | 🟡 TBD |
| E2E Critical Paths | 100% | 🟡 TBD |
| Performance (P95) | < 2s | 🟡 TBD |
| Security Tests | 0 critical vulnerabilities | 🟡 TBD |

### 11.2 Test Report Template

```
Test Execution Report
Date: [Date]
Environment: [Dev/Staging/Prod]
Build: [Version]

Summary:
- Total Tests: [N]
- Passed: [N] (X%)
- Failed: [N] (X%)
- Skipped: [N] (X%)

Details:
- Unit Tests: [N/N]
- Integration Tests: [N/N]
- API Tests: [N/N]
- E2E Tests: [N/N]
- Performance Tests: [Pass/Fail]
- Security Tests: [Pass/Fail]

Failed Tests:
1. [Test ID] - [Test Name] - [Reason]

Blockers:
1. [Issue] - [Description]

Notes:
[Additional observations]
```

---

## 12. Defect Management

### 12.1 Bug Report Template

```markdown
**Bug ID:** BUG-001
**Severity:** Critical/High/Medium/Low
**Priority:** P0/P1/P2/P3
**Status:** Open/In Progress/Resolved/Closed

**Summary:**
[Brief description]

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

**Environment:**
- OS: [Operating System]
- Browser: [If applicable]
- API Version: [Version]

**Logs/Screenshots:**
[Attach relevant logs or screenshots]

**Test Case:** TC-XXX-XXX
```

---

**Document Status:** ✅ Complete
**Last Updated:** 2025-11-01
**Next Review:** Before each release

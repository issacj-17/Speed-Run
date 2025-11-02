# Technical Architecture Document
## Speed-Run: AI-Powered AML Document Corroboration Platform

**Version:** 1.0
**Date:** November 1, 2025
**Classification:** Internal Technical Documentation

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [UML Diagrams](#uml-diagrams)
4. [Component Specifications](#component-specifications)
5. [Data Models](#data-models)
6. [API Specifications](#api-specifications)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)

---

## 1. System Overview

### 1.1 Architecture Philosophy

Speed-Run follows a **microservices-inspired monolithic architecture** with clear separation of concerns:

- **Frontend:** Next.js 14 (React) - Server-side rendering, static generation
- **Backend:** FastAPI (Python) - Async API server with modular services
- **Communication:** RESTful API over HTTP/HTTPS
- **Data Flow:** Request → Validation → Processing → Risk Scoring → Response
- **Storage:** File-based audit logs (JSONL), no database in MVP

### 1.2 Technology Stack

#### Frontend Stack
```
Next.js 14.2.5 (App Router)
├── React 18.3.1
├── TypeScript 5.5.4
├── TanStack Query 5.51.1 (data fetching)
├── Recharts 2.12.7 (visualization)
├── Tailwind CSS 3.4.7 (styling)
└── Lucide React 0.408.0 (icons)
```

#### Backend Stack
```
FastAPI 0.115.0
├── Uvicorn 0.32.0 (ASGI server)
├── Pydantic 2.9.2 (validation)
├── Docling 2.9.1 (OCR/parsing)
├── spaCy 3.7.2 (NLP)
├── NumPy 1.26.4 (numerics)
├── SciPy 1.11.4 (scientific)
└── Pillow 10.4.0 (images)
```

### 1.3 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│                                                                   │
│  ┌─────────────────┐      ┌──────────────────┐                 │
│  │   Web Browser   │      │  Compliance      │                 │
│  │   (Desktop)     │      │  Officer Portal  │                 │
│  └────────┬────────┘      └────────┬─────────┘                 │
│           │                         │                            │
└───────────┼─────────────────────────┼────────────────────────────┘
            │                         │
            └─────────────┬───────────┘
                          │ HTTPS/REST
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             Next.js 14 Frontend Application               │  │
│  │                                                            │  │
│  │  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐ │  │
│  │  │  Dashboard   │  │ Investigation │  │   Reports    │ │  │
│  │  │     Page     │  │   Workflow    │  │    Page      │ │  │
│  │  └──────────────┘  └───────────────┘  └──────────────┘ │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │            API Client (lib/api.ts)                  │ │  │
│  │  │    - HTTP requests                                  │ │  │
│  │  │    - Data transformation                            │ │  │
│  │  │    - Error handling                                 │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend Application                  │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │                API Routers                          │ │  │
│  │  │  ┌──────────┐ ┌─────────────┐ ┌───────────────┐  │ │  │
│  │  │  │   OCR    │ │  Documents  │ │Corroboration  │  │ │  │
│  │  │  │  Router  │ │   Router    │ │    Router     │  │ │  │
│  │  │  └──────────┘ └─────────────┘ └───────────────┘  │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │              Middleware Layer                        │ │  │
│  │  │  - CORS handling                                     │ │  │
│  │  │  - Request validation                                │ │  │
│  │  │  - Error handling                                    │ │  │
│  │  │  - Logging                                           │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                               │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Corroboration Orchestration Service               │  │
│  │         (corroboration_service.py)                        │  │
│  └─────────────────┬────────────────────────────────────────┘  │
│                    │                                             │
│        ┌───────────┼───────────┬─────────────┬─────────────┐   │
│        │           │           │             │             │   │
│        ▼           ▼           ▼             ▼             ▼   │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐ │
│  │Document │ │  Image  │ │   Risk   │ │ Report  │ │  OCR   │ │
│  │Validator│ │Analyzer │ │  Scorer  │ │Generator│ │Service │ │
│  └─────────┘ └─────────┘ └──────────┘ └─────────┘ └────────┘ │
│                                                                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER                              │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Docling    │  │    spaCy     │  │   NumPy/SciPy/PIL    │ │
│  │  (OCR/Parse) │  │  (NLP/Text)  │  │  (Image Analysis)    │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          External APIs (Optional, Phase 2)                │  │
│  │  - Google Cloud Vision                                    │  │
│  │  - TinEye                                                 │  │
│  │  - Hive AI                                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                               │
│                                                                   │
│  ┌──────────────────────┐  ┌──────────────────────────────┐    │
│  │   Audit Logs         │  │    Temporary File Storage     │    │
│  │   (JSONL files)      │  │    (/tmp/uploads)             │    │
│  │   /tmp/corroboration │  │                                │    │
│  │   _audit/            │  │                                │    │
│  └──────────────────────┘  └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Diagrams

### 2.1 High-Level System Context Diagram

```
                    ┌─────────────────────────┐
                    │   Compliance Officer    │
                    │   (Primary User)        │
                    └───────────┬─────────────┘
                                │
                                │ Uses
                                ▼
┌───────────────────────────────────────────────────────────┐
│                                                             │
│                Speed-Run AML Platform                      │
│                                                             │
│  ┌─────────────────────┐      ┌──────────────────────┐   │
│  │                     │      │                       │   │
│  │  Frontend (Next.js) ├──────►  Backend (FastAPI)   │   │
│  │                     │ REST │                       │   │
│  └─────────────────────┘      └──────────────────────┘   │
│                                                             │
└───────────┬───────────────────────────┬───────────────────┘
            │                           │
            │ Integrates                │ Stores
            ▼                           ▼
┌────────────────────────┐    ┌─────────────────────┐
│  External Services     │    │   File System       │
│  - Docling (OCR)       │    │   - Audit Logs      │
│  - spaCy (NLP)         │    │   - Temp Files      │
│  - NumPy/SciPy (Math)  │    │   - Reports         │
│  - PIL (Images)        │    └─────────────────────┘
│  - [Optional APIs]     │
└────────────────────────┘
```

### 2.2 Component Interaction Diagram

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     │ 1. Upload Document
     ▼
┌────────────────────┐
│   FastAPI Router   │
│  (corroboration)   │
└────┬───────────────┘
     │
     │ 2. Validate & Route
     ▼
┌──────────────────────────────┐
│  Corroboration Service       │
│  (Orchestrator)               │
└────┬─────────────────────────┘
     │
     │ 3. Parallel Processing
     ├──────────┬──────────┬──────────┬─────────┐
     │          │          │          │         │
     ▼          ▼          ▼          ▼         ▼
┌─────────┐ ┌────────┐ ┌────────┐ ┌───────┐ ┌────────┐
│Document │ │ Image  │ │  Risk  │ │Report │ │  OCR   │
│Validator│ │Analyzer│ │ Scorer │ │ Gen   │ │Service │
└────┬────┘ └────┬───┘ └────┬───┘ └───┬───┘ └────┬───┘
     │           │          │         │          │
     │           │          │         │          │
     └───────────┴──────────┴─────────┴──────────┘
                      │
                      │ 4. Aggregate Results
                      ▼
            ┌───────────────────┐
            │ Corroboration     │
            │ Report            │
            └─────────┬─────────┘
                      │
                      │ 5. Return Response
                      ▼
                  ┌────────┐
                  │ Client │
                  └────────┘
```

### 2.3 Data Flow Diagram

```
                        START
                          │
                          ▼
            ┌──────────────────────────┐
            │  1. Document Upload      │
            │  - File validation       │
            │  - Size check            │
            │  - Type verification     │
            └────────────┬─────────────┘
                         │
                         ▼
            ┌──────────────────────────┐
            │  2. Document Parsing     │
            │  - OCR (if image)        │
            │  - PDF/DOCX extraction   │
            │  - Metadata extraction   │
            └────────────┬─────────────┘
                         │
                         ▼
            ┌──────────────────────────┐
            │  3. Parallel Validation  │
            └────────────┬─────────────┘
                         │
       ┌─────────────────┼─────────────────┬──────────────┐
       │                 │                 │              │
       ▼                 ▼                 ▼              ▼
┌────────────┐   ┌────────────┐   ┌──────────┐   ┌────────────┐
│  Format    │   │ Structure  │   │ Content  │   │   Image    │
│ Validation │   │ Validation │   │Validation│   │  Analysis  │
│            │   │            │   │          │   │            │
│ - Spelling │   │ - Template │   │ - PII    │   │ - AI Gen   │
│ - Spacing  │   │ - Sections │   │ - Quality│   │ - Tamper   │
│ - Fonts    │   │ - Headers  │   │ - Read.  │   │ - EXIF     │
└────┬───────┘   └────┬───────┘   └────┬─────┘   └────┬───────┘
     │                │                │              │
     └────────────────┴────────────────┴──────────────┘
                         │
                         ▼
            ┌──────────────────────────┐
            │  4. Risk Scoring         │
            │  - Weight components     │
            │  - Calculate score       │
            │  - Categorize risk       │
            │  - Generate recomm.      │
            └────────────┬─────────────┘
                         │
                         ▼
            ┌──────────────────────────┐
            │  5. Report Generation    │
            │  - Compile findings      │
            │  - Format report         │
            │  - Log to audit trail    │
            │  - Store report          │
            └────────────┬─────────────┘
                         │
                         ▼
            ┌──────────────────────────┐
            │  6. Response             │
            │  - JSON/Markdown report  │
            │  - Risk score            │
            │  - Recommendations       │
            └──────────────────────────┘
                         │
                         ▼
                        END
```

---

## 3. UML Diagrams

### 3.1 Use Case Diagram

```
                    Speed-Run AML Platform Use Cases

                ┌────────────────────────────────────┐
                │        System Boundary             │
                │                                     │
    ┌────┐      │                                     │      ┌─────────┐
    │    │      │  ┌───────────────────────────┐    │      │External │
    │ CO │◄─────┼──┤ Upload Document           │    │      │  API    │
    │    │      │  └───────────────────────────┘    │      │Services │
    └────┘      │           │                        │      └────┬────┘
      │         │           │ includes               │           │
      │         │           ▼                        │           │
      │         │  ┌───────────────────────────┐    │           │
      │         │  │ Validate Document         │    │           │
      │         │  │ - Format                  │    │           │
      │         │  │ - Structure               │    │           │
      │         │  │ - Content                 │    │           │
      │         │  └───────────────────────────┘    │           │
      │         │           │                        │           │
      │         │           │ includes               │           │
      │         │           ▼                        │           │
      │         │  ┌───────────────────────────┐    │           │
      ├─────────┼──┤ Analyze Image             │    │           │
      │         │  │ - AI Detection            │────┼───────────┤
      │         │  │ - Tampering               │    │  extends  │
      │         │  │ - EXIF                    │    │           │
      │         │  └───────────────────────────┘    │           │
      │         │           │                        │           │
      │         │           │ includes               │           │
      │         │           ▼                        │           │
      │         │  ┌───────────────────────────┐    │           │
      ├─────────┼──┤ Calculate Risk Score      │    │           │
      │         │  └───────────────────────────┘    │           │
      │         │           │                        │           │
      │         │           │ includes               │           │
      │         │           ▼                        │           │
      │         │  ┌───────────────────────────┐    │           │
      ├─────────┼──┤ Generate Report           │    │           │
      │         │  └───────────────────────────┘    │           │
      │         │           │                        │           │
      │         │           │ includes               │           │
      │         │           ▼                        │           │
      │         │  ┌───────────────────────────┐    │           │
      ├─────────┼──┤ View Audit Trail          │    │           │
      │         │  └───────────────────────────┘    │           │
      │         │                                     │           │
      │         │  ┌───────────────────────────┐    │           │
      └─────────┼──┤ Export Report             │    │           │
                │  │ - JSON                    │    │           │
                │  │ - Markdown                │    │           │
                │  └───────────────────────────┘    │           │
                │                                     │           │
                │  ┌───────────────────────────┐    │           │
    ┌────┐      │  │ List & Filter Reports     │    │           │
    │    │      │  └───────────────────────────┘    │           │
    │ SA │◄─────┤                                     │           │
    │    │      │  ┌───────────────────────────┐    │           │
    └────┘      │  │ Monitor System Health     │    │           │
                │  └───────────────────────────┘    │           │
                │                                     │           │
                └────────────────────────────────────┘           │
                                                                  │
Legend:                                                           │
CO = Compliance Officer (Primary Actor)                          │
SA = System Administrator (Secondary Actor)                      │
──────────────────────────────────────────────────────────────────┘
```

### 3.2 Class Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Backend Class Structure                       │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────────────┐
│    FastAPIApplication     │
│───────────────────────────│
│ + app: FastAPI            │
│ + routers: List[APIRouter]│
│───────────────────────────│
│ + include_router()        │
│ + add_middleware()        │
│ + startup()               │
│ + shutdown()              │
└──────────┬────────────────┘
           │ uses
           ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Routers                             │
├─────────────────┬─────────────────┬─────────────────────────┤
│ OCRRouter       │ DocumentRouter  │ CorroborationRouter     │
│─────────────────│─────────────────│─────────────────────────│
│ + extract()     │ + parse()       │ + analyze()             │
│ + health()      │ + extract_tables│ + analyze_image()       │
│                 │ + health()      │ + validate_format()     │
│                 │                 │ + validate_structure()  │
│                 │                 │ + get_report()          │
│                 │                 │ + list_reports()        │
│                 │                 │ + health()              │
└─────────────────┴─────────────────┴────────┬────────────────┘
                                              │ uses
                                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Service Layer                                 │
├────────────────────────────────────────────────────────────────┬─┤
│              CorroborationService                              │ │
│────────────────────────────────────────────────────────────────│ │
│ - document_validator: DocumentValidator                        │ │
│ - image_analyzer: ImageAnalyzer                                │ │
│ - risk_scorer: RiskScorer                                      │ │
│ - report_generator: ReportGenerator                            │ │
│ - document_service: DocumentService                            │ │
│────────────────────────────────────────────────────────────────│ │
│ + analyze_document(bytes, filename, request): CorroborationReport│
│ + analyze_image_only(bytes, filename): ImageAnalysisResult    │ │
│ + get_report(document_id): CorroborationReport                │ │
│ + list_reports(limit, filters): List[Report]                  │ │
└────────────────────────────────────────────────────────────────┘ │
           │                                                         │
           ├─────────────┬──────────────┬──────────────┬────────────┤
           ▼             ▼              ▼              ▼            ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐
│DocumentValidator│ │ImageAnalyzer │ │RiskScorer│ │Report   │ │OCR     │
│─────────────────│ │──────────────│ │──────────│ │Generator│ │Service │
│+ validate_format│ │+ analyze     │ │+ calc    │ │+ generate│ │+ process│
│+ validate_struct│ │  _image()    │ │  _risk() │ │  _report│ │  _image│
│+ validate_content│ │+ detect_ai() │ │+ score   │ │+ export │ │        │
└─────────────────┘ │+ detect      │ │  _*()    │ │  _markdown│       │
                    │  _tampering()│ │          │ │+ log_audit│       │
                    │+ analyze     │ │          │ └─────────┘ └────────┘
                    │  _metadata() │ │          │
                    └──────────────┘ └──────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        Data Models (Pydantic)                        │
├────────────────────────┬──────────────────────┬──────────────────────┤
│ CorroborationRequest   │ ValidationIssue      │ CorroborationReport  │
│────────────────────────│──────────────────────│──────────────────────│
│ + perform_format_val   │ + category: str      │ + document_id: str   │
│ + perform_struct_val   │ + severity: enum     │ + file_name: str     │
│ + perform_content_val  │ + description: str   │ + risk_score: Risk   │
│ + perform_image_anal   │ + location: str      │ + format_validation  │
│ + expected_doc_type    │ + details: dict      │ + structure_validation│
│ + enable_reverse_search│                      │ + content_validation │
│ + risk_threshold       │                      │ + image_analysis     │
└────────────────────────┴──────────────────────┴──────────────────────┘

├────────────────────────┬──────────────────────┬──────────────────────┤
│ FormatValidationResult │StructureValidationRes│ ContentValidationRes │
│────────────────────────│──────────────────────│──────────────────────│
│ + has_double_spacing   │ + is_complete        │ + has_sensitive_data │
│ + has_font_inconsist   │ + missing_sections   │ + quality_score      │
│ + has_indent_issues    │ + has_correct_headers│ + readability_score  │
│ + spelling_error_count │ + template_match_score│ + word_count        │
│ + issues: List[Issue]  │ + issues: List[Issue]│ + issues: List[Issue]│
└────────────────────────┴──────────────────────┴──────────────────────┘

├────────────────────────┬──────────────────────┬──────────────────────┤
│ ImageAnalysisResult    │ RiskScore            │ ValidationSeverity   │
│────────────────────────│──────────────────────│──────────────────────│
│ + is_authentic         │ + overall_score: float│ Enum:               │
│ + is_ai_generated      │ + risk_level: enum   │ - LOW                │
│ + ai_detection_conf    │ + confidence: float  │ - MEDIUM             │
│ + is_tampered          │ + contributing_factors│ - HIGH              │
│ + tampering_conf       │ + recommendations    │ - CRITICAL           │
│ + reverse_image_matches│                      │                      │
│ + metadata_issues      │                      │                      │
│ + forensic_findings    │                      │                      │
└────────────────────────┴──────────────────────┴──────────────────────┘
```

### 3.3 Sequence Diagram - Document Analysis Flow

```
Client          Router          Corroboration    Document     Image        Risk        Report
  │               │              Service         Validator    Analyzer     Scorer      Generator
  │               │                │                │            │           │            │
  │─POST /analyze─►               │                │            │           │            │
  │               │                │                │            │           │            │
  │               │─validate req──►│                │            │           │            │
  │               │                │                │            │           │            │
  │               │                │─save temp file─►           │           │            │
  │               │                │                │            │           │            │
  │               │                │─parse document─►           │           │            │
  │               │                │◄───text────────┤           │           │            │
  │               │                │                │            │           │            │
  │               │                │─validate format───────────►│           │            │
  │               │                │◄──result────────           │           │            │
  │               │                │                │            │           │            │
  │               │                │─validate structure─────────►           │            │
  │               │                │◄──result────────────────────           │            │
  │               │                │                │            │           │            │
  │               │                │─validate content────────────►          │            │
  │               │                │◄──result────────────────────           │            │
  │               │                │                │            │           │            │
  │               │                │─analyze image (if applicable)──────────►           │
  │               │                │◄──result────────────────────────────────           │
  │               │                │                │            │           │            │
  │               │                │─calculate risk score──────────────────────────────►│
  │               │                │◄──risk score───────────────────────────────────────┤
  │               │                │                │            │           │            │
  │               │                │─generate report────────────────────────────────────►
  │               │                │◄──full report──────────────────────────────────────┤
  │               │                │                │            │           │            │
  │               │                │─cleanup temp file──────────►│           │            │
  │               │                │                │            │           │            │
  │               │◄────report─────┤                │            │           │            │
  │◄────200 OK────┤                │                │            │           │            │
  │   JSON Report │                │                │            │           │            │
  │               │                │                │            │           │            │

Total Processing Time: ~2-5 seconds (depending on document size)

Note: Steps 4-7 (validations) can be parallelized for better performance
```

### 3.4 Sequence Diagram - Frontend API Integration

```
User        Browser         Next.js App      API Client       FastAPI          Services
 │             │                │                │                 │                │
 │─click───────►                │                │                 │                │
 │ Upload      │                │                │                 │                │
 │             │                │                │                 │                │
 │             │◄───form────────┤                │                 │                │
 │             │                │                │                 │                │
 │─select file─►                │                │                 │                │
 │             │                │                │                 │                │
 │             │─submit form────►                │                 │                │
 │             │                │                │                 │                │
 │             │                │─POST /api/v1/──────────────────►│                │
 │             │                │  corroboration/│                 │                │
 │             │                │  analyze       │                 │                │
 │             │                │                │                 │                │
 │             │                │                │─validate────────►                │
 │             │                │                │                 │                │
 │             │                │                │─process─────────►                │
 │             │                │                │                 │                │
 │             │                │                │                 │─analyze────────►
 │             │                │                │                 │◄──results──────┤
 │             │                │                │                 │                │
 │             │                │◄───200 OK──────┤                 │                │
 │             │                │    Report JSON │                 │                │
 │             │                │                │                 │                │
 │             │                │─transform data─►                 │                │
 │             │                │                │                 │                │
 │             │◄──update UI────┤                │                 │                │
 │             │                │                │                 │                │
 │◄─display────┤                │                │                 │                │
 │  results    │                │                │                 │                │
 │             │                │                │                 │                │
```

---

## 4. Component Specifications

### 4.1 Backend Services

#### 4.1.1 CorroborationService
**Purpose:** Main orchestration service that coordinates all validation and analysis

**Responsibilities:**
- Receive and validate input files
- Coordinate parallel validation services
- Aggregate results
- Generate comprehensive reports

**Dependencies:**
- DocumentValidator
- ImageAnalyzer
- RiskScorer
- ReportGenerator
- DocumentService

**Key Methods:**
```python
async def analyze_document(
    file_bytes: bytes,
    filename: str,
    request: CorroborationRequest
) -> CorroborationReport
```

#### 4.1.2 DocumentValidator
**Purpose:** Validate document format, structure, and content

**Responsibilities:**
- Spell checking (spaCy)
- Format validation (spacing, fonts, indentation)
- Structure validation (sections, headers, completeness)
- Content quality assessment
- PII detection

**Key Methods:**
```python
async def validate_format(text: str, file_path: Path) -> FormatValidationResult
async def validate_structure(text: str, expected_type: str) -> StructureValidationResult
async def validate_content(text: str) -> ContentValidationResult
```

#### 4.1.3 ImageAnalyzer
**Purpose:** Detect image fraud, AI generation, and tampering

**Responsibilities:**
- AI-generated image detection (heuristic)
- Tampering detection (Error Level Analysis)
- EXIF metadata extraction
- Forensic analysis
- Reverse image search integration (optional)

**Key Methods:**
```python
async def analyze_image(image_path: Path) -> ImageAnalysisResult
async def _detect_ai_generated(image: Image) -> Tuple[bool, float]
async def _detect_tampering_ela(image_path: Path) -> Tuple[bool, float, List]
```

#### 4.1.4 RiskScorer
**Purpose:** Calculate risk scores and generate recommendations

**Responsibilities:**
- Weighted scoring of validation results
- Risk level categorization
- Contributing factors analysis
- Recommendation generation

**Scoring Weights:**
- Format Validation: 15%
- Structure Validation: 25%
- Content Validation: 20%
- Image Analysis: 40%

**Key Methods:**
```python
async def calculate_risk_score(
    format_val: FormatValidationResult,
    structure_val: StructureValidationResult,
    content_val: ContentValidationResult,
    image_anal: ImageAnalysisResult
) -> RiskScore
```

#### 4.1.5 ReportGenerator
**Purpose:** Generate reports and maintain audit trails

**Responsibilities:**
- Compile comprehensive reports
- Export to JSON and Markdown
- Log to audit trail (JSONL)
- Report retrieval and filtering
- Report storage

**Key Methods:**
```python
async def generate_report(...) -> CorroborationReport
async def export_report_markdown(report: CorroborationReport) -> str
async def log_audit_trail(report: CorroborationReport) -> None
async def get_report(document_id: str) -> CorroborationReport
async def list_reports(filters: dict) -> List[Report]
```

### 4.2 Frontend Components

#### 4.2.1 Dashboard Page
**Purpose:** Main monitoring interface for compliance officers

**Components:**
- AlertBanner - Critical alerts
- KPICard - Key metrics display
- AlertTriageTable - Alert queue
- PieChart - Alert distribution
- LineChart - Transaction trends

**Data Flow:**
```typescript
useQuery() → apiClient.getDashboardSummary() → State → UI Update
```

#### 4.2.2 API Client (lib/api.ts)
**Purpose:** Centralized HTTP client for backend communication

**Methods:**
```typescript
async getDashboardSummary(): Promise<DashboardSummary>
async getActiveAlerts(): Promise<Alert[]>
async getAlertDetails(alertId: string): Promise<AlertDetails>
async remediateAlert(alertId: string): Promise<{success: boolean}>
async getAuditTrail(alertId: string): Promise<AuditLogEntry[]>
```

**Configuration:**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
```

---

## 5. Data Models

### 5.1 Backend Data Models (Pydantic)

#### CorroborationReport
```python
class CorroborationReport(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    analysis_timestamp: datetime
    format_validation: Optional[FormatValidationResult]
    structure_validation: Optional[StructureValidationResult]
    content_validation: Optional[ContentValidationResult]
    image_analysis: Optional[ImageAnalysisResult]
    risk_score: RiskScore
    processing_time: float
    engines_used: List[str]
    total_issues_found: int
    critical_issues_count: int
    requires_manual_review: bool
```

#### RiskScore
```python
class RiskScore(BaseModel):
    overall_score: float  # 0-100
    risk_level: ValidationSeverity  # LOW/MEDIUM/HIGH/CRITICAL
    confidence: float  # 0-1
    contributing_factors: List[Dict[str, Any]]
    recommendations: List[str]
```

#### ValidationIssue
```python
class ValidationIssue(BaseModel):
    category: str  # "formatting", "content", "structure", etc.
    severity: ValidationSeverity
    description: str
    location: Optional[str]
    details: Optional[Dict[str, Any]]
```

### 5.2 Frontend Data Models (TypeScript)

#### Alert
```typescript
interface Alert {
  alert_id: string
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
  client: string
  type: string
  amount: number
  currency: string
  risk_score: number
  status: "pending" | "investigating" | "resolved"
  timestamp: string
}
```

#### AlertDetails
```typescript
interface AlertDetails extends Alert {
  agent_findings: AgentFinding[]
  document_issues: DocumentIssue[]
  transaction_history: TransactionHistory[]
  document_url?: string
}
```

---

## 6. API Specifications

### 6.1 Backend API Endpoints

#### POST /api/v1/corroboration/analyze
**Description:** Comprehensive document fraud analysis

**Request:**
```
Content-Type: multipart/form-data

file: <binary>
perform_format_validation: boolean (default: true)
perform_structure_validation: boolean (default: true)
perform_content_validation: boolean (default: true)
perform_image_analysis: boolean (default: true)
expected_document_type: string (optional)
enable_reverse_image_search: boolean (default: false)
```

**Response (200):**
```json
{
  "document_id": "uuid",
  "file_name": "invoice.pdf",
  "file_type": ".pdf",
  "analysis_timestamp": "2025-11-01T12:00:00Z",
  "risk_score": {
    "overall_score": 65.5,
    "risk_level": "high",
    "confidence": 0.87,
    "contributing_factors": [...],
    "recommendations": [...]
  },
  "format_validation": {...},
  "structure_validation": {...},
  "content_validation": {...},
  "image_analysis": null,
  "processing_time": 2.34,
  "total_issues_found": 8,
  "critical_issues_count": 2,
  "requires_manual_review": true
}
```

#### GET /api/v1/corroboration/reports
**Description:** List corroboration reports

**Query Parameters:**
- `limit` (int, default: 100)
- `risk_level` (string: "low"|"medium"|"high"|"critical")
- `requires_manual_review` (boolean)

**Response (200):**
```json
[
  {
    "document_id": "uuid1",
    "file_name": "doc1.pdf",
    "timestamp": "2025-11-01T12:00:00Z",
    "risk_score": 75.0,
    "risk_level": "high"
  },
  ...
]
```

### 6.2 Frontend Expected API (To Be Implemented)

#### GET /api/alerts/summary
**Response:**
```json
{
  "total_active_alerts": 42,
  "critical_alerts": 8,
  "pending_cases": 15,
  "avg_resolution_time": 4.5,
  "alerts_by_risk": {
    "critical": 8,
    "high": 12,
    "medium": 15,
    "low": 7
  }
}
```

#### GET /api/alerts/active
**Response:**
```json
[
  {
    "alert_id": "ALT-2024-001",
    "priority": "CRITICAL",
    "client": "Zhao Industries",
    "type": "Large Transaction",
    "amount": 2500000,
    "currency": "USD",
    "risk_score": 89,
    "status": "pending",
    "timestamp": "2024-07-15T09:30:00Z"
  },
  ...
]
```

---

## 7. Security Architecture

### 7.1 Security Layers

```
┌─────────────────────────────────────────────────────┐
│              Transport Layer Security                │
│  - HTTPS/TLS 1.3                                    │
│  - Certificate validation                            │
└─────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│           Application Security (Phase 2)            │
│  - JWT authentication                                │
│  - Role-based access control (RBAC)                 │
│  - API rate limiting                                 │
└─────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│              Data Security                          │
│  - Input validation (Pydantic)                      │
│  - File type validation                             │
│  - Size limits                                      │
│  - SQL injection prevention                         │
│  - XSS prevention                                   │
└─────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│              Audit & Compliance                     │
│  - Complete audit trail (JSONL)                     │
│  - Immutable logging                                │
│  - GDPR/PII compliance                              │
│  - Timestamp verification                           │
└─────────────────────────────────────────────────────┘
```

### 7.2 Data Protection

**PII Handling:**
- Detection of SSN, credit cards, emails
- Flagging in content validation
- No storage of PII in logs
- Redaction in reports (Phase 2)

**File Security:**
- Temporary storage only (/tmp)
- Automatic cleanup after processing
- No permanent file storage in MVP
- Virus scanning (Phase 2)

---

## 8. Deployment Architecture

### 8.1 Local Development

```
┌─────────────────────────────────────────────┐
│          Developer Machine                   │
│                                              │
│  ┌────────────────┐    ┌─────────────────┐ │
│  │  Frontend      │    │  Backend        │ │
│  │  localhost:3000│    │  localhost:8000 │ │
│  │  (Next.js dev) │    │  (Uvicorn)      │ │
│  └────────────────┘    └─────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  File System                            │ │
│  │  /tmp/uploads                           │ │
│  │  /tmp/corroboration_audit               │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 8.2 Production Architecture (Proposed)

```
                    Internet
                       │
                       ▼
            ┌──────────────────────┐
            │   Load Balancer      │
            │   (AWS ALB/Nginx)    │
            └──────┬───────┬───────┘
                   │       │
        ┌──────────┘       └──────────┐
        │                              │
        ▼                              ▼
┌──────────────┐              ┌──────────────┐
│  Frontend    │              │  Backend     │
│  (Next.js)   │              │  (FastAPI)   │
│  Vercel/     │◄────REST─────┤  EC2/ECS     │
│  AWS Amplify │              │  Auto-scaling│
└──────────────┘              └──────┬───────┘
                                     │
                         ┌───────────┴──────────────┐
                         │                          │
                         ▼                          ▼
                  ┌─────────────┐          ┌──────────────┐
                  │  S3 Bucket  │          │  CloudWatch  │
                  │  (Audit     │          │  (Logs &     │
                  │   Logs)     │          │   Metrics)   │
                  └─────────────┘          └──────────────┘
```

---

## Appendix A: Technology Decisions

### A.1 Why FastAPI?
- **Async Support:** Native async/await for I/O-bound operations
- **Performance:** Comparable to Node.js and Go
- **Automatic Docs:** OpenAPI/Swagger generation
- **Type Safety:** Pydantic integration
- **Developer Experience:** Fast development, easy testing

### A.2 Why Next.js?
- **Server-Side Rendering:** SEO and performance
- **App Router:** Modern routing with React Server Components
- **Developer Experience:** Hot reload, TypeScript support
- **Performance:** Automatic code splitting, image optimization
- **Deployment:** Easy Vercel deployment

### A.3 Why Docling?
- **Accuracy:** >95% OCR accuracy
- **Multi-format:** PDF, DOCX, images
- **Table Extraction:** Built-in table structure recognition
- **Metadata:** Rich metadata extraction
- **Active Development:** Regular updates and improvements

---

## Appendix B: Future Enhancements

1. **Database Integration:** PostgreSQL for persistent storage
2. **Message Queue:** Celery/RabbitMQ for async processing
3. **Caching Layer:** Redis for performance
4. **ML Models:** Custom trained fraud detection models
5. **Mobile App:** React Native application
6. **Real-time Notifications:** WebSocket integration
7. **Advanced Analytics:** Data warehouse integration
8. **Multi-language Support:** i18n implementation

---

**Document Version:** 1.0
**Last Updated:** 2025-11-01
**Status:** ✅ Complete

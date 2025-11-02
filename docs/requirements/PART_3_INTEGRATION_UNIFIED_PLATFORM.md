# Part 3: Integration & Unified Platform
## Enriched Challenge Requirements & Technical Specifications

> **Integration Goal:** Create a unified AML platform that seamlessly connects real-time transaction monitoring (Part 1) with document corroboration (Part 2), providing a single source of truth for compliance teams with no mocked data.

---

## Table of Contents
1. [Overview & Integration Vision](#overview--integration-vision)
2. [Architecture Design](#architecture-design)
3. [Database Schema & Data Flow](#database-schema--data-flow)
4. [API Integration Layer](#api-integration-layer)
5. [Frontend-Backend Connection](#frontend-backend-connection)
6. [Cross-Referencing Mechanism](#cross-referencing-mechanism)
7. [Unified Dashboard Requirements](#unified-dashboard-requirements)
8. [Deployment Architecture](#deployment-architecture)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Overview & Integration Vision

### Current State Analysis

**What Exists:**
- ✅ **Backend (Part 2):** Fully functional document corroboration APIs
- ✅ **Frontend UI:** Beautiful dashboards for Compliance and RM teams
- ❌ **Connection:** Frontend uses mock data, not connected to backend
- ❌ **Part 1 Backend:** Transaction monitoring not implemented
- ❌ **Database:** No persistent storage (file-based only)

**Integration Challenge:**
```
Frontend Expectations          Backend Reality
────────────────────          ───────────────
/api/alerts/summary           /api/v1/corroboration/analyze
/api/alerts/active            /api/v1/corroboration/reports
/api/alerts/{id}              /api/v1/corroboration/report/{id}
/api/alerts/{id}/remediate    (not implemented)
/api/audit-trail/{id}         (audit trail exists for documents only)
```

### Integration Vision

**Goal:** Build a unified platform where:
1. **Backend is source of truth** - No mocked data in frontend
2. **Database-backed** - PostgreSQL for persistent storage
3. **Real-time sync** - Frontend displays live backend data
4. **Cross-referenced** - Link transactions ↔ documents ↔ alerts
5. **Working prototype** - End-to-end functionality for demo

### Success Criteria
- ✅ Frontend fetches 100% real data from backend (0% mocked)
- ✅ All CRUD operations persist to database
- ✅ Document analysis triggers alerts in unified system
- ✅ Transaction alerts (when Part 1 complete) integrate seamlessly
- ✅ Single audit trail across all components
- ✅ <2 second page load time with real data
- ✅ Real-time updates via WebSocket or polling

---

## Architecture Design

### System Integration Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 14)                            │
│                     Port: 3000                                        │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │  Compliance      │  │  Relationship    │  │  Legal Team      │ │
│  │  Dashboard       │  │  Manager         │  │  Dashboard       │ │
│  │                  │  │  Dashboard       │  │                  │ │
│  │  - KYC Reviews   │  │  - Client List   │  │  - Audit Trail   │ │
│  │  - Document      │  │  - Risk Ratings  │  │  - Reports       │ │
│  │    Upload        │  │  - Document      │  │  - Regulatory    │ │
│  │  - Kanban Board  │  │    Upload        │  │    Compliance    │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                │                                     │
│                    ┌───────────┴───────────┐                        │
│                    │   API Client Layer    │                        │
│                    │   (lib/api.ts)        │                        │
│                    │   - TanStack Query    │                        │
│                    │   - Real API calls    │                        │
│                    │   - Error handling    │                        │
│                    └───────────┬───────────┘                        │
└────────────────────────────────┼─────────────────────────────────────┘
                                 │ HTTP/REST + WebSocket
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 Backend (FastAPI)                                    │
│                 Port: 8000                                           │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              API Gateway / BFF Layer                          │  │
│  │  - Route mapping (alerts API → corroboration API)            │  │
│  │  - Response transformation                                    │  │
│  │  - Authentication & authorization                             │  │
│  │  - Rate limiting                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                │                                     │
│       ┌────────────────────────┼────────────────────────┐           │
│       ▼                        ▼                        ▼           │
│  ┌─────────┐           ┌──────────────┐        ┌──────────────┐   │
│  │ Part 1  │           │   Part 2     │        │   Unified    │   │
│  │ Transaction         │ Document     │        │   Alert      │   │
│  │ Monitoring          │ Corroboration│        │   System     │   │
│  │                     │              │        │              │   │
│  │ - Regulatory        │ - OCR        │        │ - Alert      │   │
│  │   Ingestion         │ - Validation │        │   Management │   │
│  │ - Transaction       │ - Image      │        │ - Routing    │   │
│  │   Analysis          │   Analysis   │        │ - Escalation │   │
│  │ - Risk Scoring      │ - Risk Score │        │ - Workflow   │   │
│  │                     │              │        │              │   │
│  │ Status: 🔄 TODO     │ Status: ✅   │        │ Status: 🔄   │   │
│  └─────────┘           └──────────────┘        └──────────────┘   │
│       │                        │                        │           │
│       └────────────────────────┼────────────────────────┘           │
│                                ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Shared Services Layer                            │  │
│  │  - Audit Trail Service (unified logging)                     │  │
│  │  - Notification Service (email, SMS, in-app)                 │  │
│  │  - Report Generation Service                                 │  │
│  │  - Document Storage Service                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                │                                     │
└────────────────────────────────┼─────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Database Layer (PostgreSQL)                       │
│                                                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │ Clients    │  │ Transactions│  │ Documents  │  │ Alerts     │   │
│  ├────────────┤  ├────────────┤  ├────────────┤  ├────────────┤   │
│  │ - ID       │  │ - ID       │  │ - ID       │  │ - ID       │   │
│  │ - Name     │  │ - Client FK│  │ - Client FK│  │ - Type     │   │
│  │ - Risk     │  │ - Amount   │  │ - Content  │  │ - Severity │   │
│  │ - KYC      │  │ - Risk     │  │ - Risk     │  │ - Status   │   │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘   │
│                                                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │ Validations│  │ Images     │  │ Audit Logs │  │ Reports    │   │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘   │
│                                                                       │
│  Status: 🔄 TO BE IMPLEMENTED                                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

**Document Upload Flow:**
```
1. User uploads document in Frontend
   ↓
2. Frontend sends POST /api/v1/documents/upload
   ↓
3. Backend saves file to storage
   ↓
4. Backend triggers corroboration analysis
   ↓
5. Analysis results saved to database
   ↓
6. Alert created if risk score >= threshold
   ↓
7. Alert routed to appropriate users
   ↓
8. Frontend receives response + alert notification
   ↓
9. Dashboard updates in real-time
```

**Transaction Analysis Flow (Part 1 - Future):**
```
1. Transaction ingested from CSV/Kafka
   ↓
2. Backend analyzes against rules
   ↓
3. Risk score calculated
   ↓
4. Alert created if threshold exceeded
   ↓
5. Frontend notified via WebSocket
   ↓
6. Alert appears in dashboard
```

**Cross-Reference Flow:**
```
1. Transaction alert created
   ↓
2. System checks if client has documents
   ↓
3. If document analysis exists, link them
   ↓
4. Combined risk view shown in dashboard
   ↓
5. Compliance officer sees both transaction + document risk
```

---

## Database Schema & Data Flow

### PostgreSQL Database Design

#### Core Tables

**1. Clients Table**
```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_name VARCHAR(255) NOT NULL,
    client_type VARCHAR(50) NOT NULL, -- INDIVIDUAL, CORPORATE, TRUST
    risk_rating VARCHAR(20) NOT NULL, -- LOW, MEDIUM, HIGH
    kyc_status VARCHAR(50) NOT NULL, -- CURRENT, EXPIRING_SOON, EXPIRED
    kyc_last_updated TIMESTAMP WITH TIME ZONE,
    onboarding_date DATE NOT NULL,
    relationship_manager_id UUID,
    jurisdiction VARCHAR(3), -- ISO 3166 country code
    industry VARCHAR(100),
    pep_status BOOLEAN DEFAULT FALSE,
    sanctions_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_clients_rm ON clients(relationship_manager_id);
CREATE INDEX idx_clients_risk ON clients(risk_rating);
CREATE INDEX idx_clients_kyc ON clients(kyc_status);
```

**2. Documents Table**
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL, -- KYC, PROOF_OF_ADDRESS, SOURCE_OF_WEALTH, CONTRACT
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    page_count INTEGER,
    word_count INTEGER,
    uploaded_by UUID, -- User ID
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB, -- Document metadata (author, dates, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_client ON documents(client_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_processed ON documents(processed);
```

**3. Document Validations Table**
```sql
CREATE TABLE document_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    format_validation JSONB NOT NULL, -- FormatValidationResult
    structure_validation JSONB NOT NULL, -- StructureValidationResult
    content_validation JSONB NOT NULL, -- ContentValidationResult
    format_score INTEGER NOT NULL, -- 0-100
    structure_score INTEGER NOT NULL,
    content_score INTEGER NOT NULL,
    validated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_validations_document ON document_validations(document_id);
```

**4. Images Table**
```sql
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    image_type VARCHAR(50), -- PHOTO, SCAN, DIAGRAM
    ai_generated_result JSONB, -- AI detection result
    tampering_result JSONB, -- Tampering detection result
    authenticity_result JSONB, -- Reverse search result
    exif_data JSONB, -- EXIF metadata
    risk_score INTEGER NOT NULL, -- 0-100
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_images_document ON images(document_id);
CREATE INDEX idx_images_risk ON images(risk_score);
```

**5. Risk Scores Table**
```sql
CREATE TABLE risk_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL, -- DOCUMENT, TRANSACTION, CLIENT
    entity_id UUID NOT NULL,
    total_score INTEGER NOT NULL, -- 0-100
    risk_level VARCHAR(20) NOT NULL, -- LOW, MEDIUM, HIGH, CRITICAL
    component_scores JSONB NOT NULL, -- Breakdown by component
    contributing_factors JSONB NOT NULL, -- List of risk factors
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_risk_scores_entity ON risk_scores(entity_type, entity_id);
CREATE INDEX idx_risk_scores_level ON risk_scores(risk_level);
```

**6. Alerts Table**
```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_type VARCHAR(100) NOT NULL, -- TRANSACTION_RISK, DOCUMENT_RISK, PATTERN_DETECTED, etc.
    severity VARCHAR(20) NOT NULL, -- LOW, MEDIUM, HIGH, CRITICAL
    status VARCHAR(50) NOT NULL DEFAULT 'NEW', -- NEW, ACKNOWLEDGED, IN_REVIEW, ESCALATED, RESOLVED, FALSE_POSITIVE
    client_id UUID NOT NULL REFERENCES clients(id),
    transaction_id UUID REFERENCES transactions(id),
    document_id UUID REFERENCES documents(id),
    risk_score INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    triggered_rules JSONB, -- List of rules that triggered alert
    context JSONB, -- Additional context
    recommended_actions JSONB, -- Suggested actions
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID,
    resolution_type VARCHAR(50),
    resolution_notes TEXT
);

CREATE INDEX idx_alerts_client ON alerts(client_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_document ON alerts(document_id);
CREATE INDEX idx_alerts_transaction ON alerts(transaction_id);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);
```

**7. Alert Recipients Table**
```sql
CREATE TABLE alert_recipients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    user_role VARCHAR(50) NOT NULL, -- RM, COMPLIANCE, LEGAL
    notified_at TIMESTAMP WITH TIME ZONE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    viewed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_recipients_alert ON alert_recipients(alert_id);
CREATE INDEX idx_recipients_user ON alert_recipients(user_id);
```

**8. Transactions Table (Part 1 - Future)**
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_external_id VARCHAR(255) UNIQUE NOT NULL,
    client_id UUID NOT NULL REFERENCES clients(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    amount DECIMAL(20, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- WIRE, CASH, TRADE, FX
    source_account VARCHAR(255),
    destination_account VARCHAR(255),
    counterparty_name VARCHAR(255),
    counterparty_jurisdiction VARCHAR(3),
    swift_code VARCHAR(50),
    purpose TEXT,
    screening_flags JSONB, -- PEP, SANCTIONS, etc.
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, PROCESSING, COMPLETED, BLOCKED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_transactions_client ON transactions(client_id);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX idx_transactions_amount ON transactions(amount);
```

**9. Audit Logs Table**
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) DEFAULT 'INFO', -- INFO, WARNING, ERROR
    user_id UUID,
    user_role VARCHAR(50),
    session_id VARCHAR(255),
    ip_address INET,
    entity_type VARCHAR(50),
    entity_id UUID,
    action VARCHAR(100),
    before_state JSONB,
    after_state JSONB,
    metadata JSONB
);

CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
```

**10. Reports Table**
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type VARCHAR(100) NOT NULL, -- DOCUMENT_CORROBORATION, TRANSACTION_ANALYSIS, ALERT_SUMMARY
    document_id UUID REFERENCES documents(id),
    alert_id UUID REFERENCES alerts(id),
    client_id UUID REFERENCES clients(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    generated_by UUID,
    content JSONB NOT NULL, -- Full report content
    pdf_path TEXT, -- Path to PDF export
    markdown_path TEXT -- Path to markdown export
);

CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_document ON reports(document_id);
CREATE INDEX idx_reports_alert ON reports(alert_id);
```

### Database Relationships

```
clients (1) ──┬── (N) documents
              ├── (N) transactions
              └── (N) alerts

documents (1) ──┬── (1) document_validations
                ├── (N) images
                ├── (N) alerts
                └── (N) reports

transactions (1) ── (N) alerts

alerts (1) ──┬── (N) alert_recipients
             └── (N) reports

risk_scores (1) ── (1) documents or transactions

audit_logs (independent, references everything)
```

---

## API Integration Layer

### Current State: API Mismatch

**Frontend Expects (from lib/api.ts):**
```typescript
// Dashboard Summary
GET /api/alerts/summary
Response: {
  pending_reviews: number,
  critical_cases: number,
  red_flags: number,
  avg_lead_time: number
}

// Active Alerts
GET /api/alerts/active
Response: Alert[]

// Alert Details
GET /api/alerts/{id}
Response: AlertDetail

// Remediation
POST /api/alerts/{id}/remediate
Body: { action: string, notes: string }
```

**Backend Provides:**
```python
# Document Corroboration
POST /api/v1/corroboration/analyze
GET /api/v1/corroboration/reports
GET /api/v1/corroboration/report/{id}
```

### Solution: API Adapter/Bridge Layer

**Approach 1: Backend Adapter (Recommended)**
Create new FastAPI router that maps frontend expectations to backend reality.

```python
# backend/src/backend/routers/alerts.py (NEW FILE)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import alert_service

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

@router.get("/summary")
async def get_alert_summary(db: Session = Depends(get_db)):
    """
    Get dashboard summary statistics.
    Maps to frontend expectation: /api/alerts/summary
    """
    return await alert_service.get_summary(db)

@router.get("/active")
async def get_active_alerts(
    status: str = "NEW,IN_REVIEW",
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of active alerts.
    Maps to frontend expectation: /api/alerts/active
    """
    alerts = await alert_service.get_alerts(
        db,
        status=status.split(","),
        limit=limit
    )
    return {"alerts": alerts}

@router.get("/{alert_id}")
async def get_alert_details(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed alert information.
    Maps to frontend expectation: /api/alerts/{id}
    """
    alert = await alert_service.get_alert_by_id(db, alert_id)
    return alert

@router.post("/{alert_id}/remediate")
async def remediate_alert(
    alert_id: str,
    action: str,
    notes: str,
    db: Session = Depends(get_db)
):
    """
    Execute remediation action on alert.
    Maps to frontend expectation: POST /api/alerts/{id}/remediate
    """
    result = await alert_service.remediate(db, alert_id, action, notes)
    return result

@router.get("/audit-trail/{alert_id}")
async def get_audit_trail(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """
    Get audit trail for alert.
    Maps to frontend expectation: GET /api/audit-trail/{alertId}
    """
    logs = await alert_service.get_audit_trail(db, alert_id)
    return {"audit_trail": logs}
```

**Approach 2: Frontend Adapter (Alternative)**
Update frontend API client to match backend endpoints.

```typescript
// frontend/lib/api.ts (UPDATED)
import { QueryClient } from '@tanstack/react-query';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Adapter functions
export async function getDashboardSummary() {
  // Map corroboration reports to dashboard summary
  const reports = await fetch(`${API_BASE}/corroboration/reports?limit=1000`);
  const data = await reports.json();

  // Calculate statistics from reports
  return {
    pending_reviews: data.filter(r => r.risk_level === 'MEDIUM' || r.risk_level === 'HIGH').length,
    critical_cases: data.filter(r => r.risk_level === 'CRITICAL').length,
    red_flags: data.reduce((sum, r) => sum + r.findings_summary.high_issues, 0),
    avg_lead_time: calculateAverageLeadTime(data)
  };
}

export async function getActiveAlerts() {
  // Fetch all high-risk reports and convert to alerts
  const reports = await fetch(`${API_BASE}/corroboration/reports?risk_level=HIGH,CRITICAL`);
  const data = await reports.json();

  // Transform reports to alert format
  return data.map(report => ({
    id: report.report_id,
    type: 'DOCUMENT_RISK',
    severity: report.risk_score.risk_level,
    client: report.document_info.client_name,
    description: `Document analysis flagged ${report.findings_summary.high_issues} high-risk issues`,
    created_at: report.analyzed_at,
    status: 'NEW'
  }));
}
```

**Recommended Approach: Hybrid**
1. Create backend bridge API (cleaner, scalable)
2. Update frontend to use new endpoints
3. Maintain backward compatibility during transition

### Alert Service Implementation

```python
# backend/src/backend/services/alert_service.py (NEW FILE)
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Alert, AlertRecipient, Client, Document
from typing import List, Dict

class AlertService:
    async def get_summary(self, db: Session) -> Dict:
        """Get dashboard summary statistics."""
        # Count alerts by status
        new_alerts = db.query(Alert).filter(Alert.status == 'NEW').count()
        in_review = db.query(Alert).filter(Alert.status == 'IN_REVIEW').count()
        critical = db.query(Alert).filter(Alert.severity == 'CRITICAL').count()

        # Calculate average lead time
        resolved = db.query(Alert).filter(Alert.status == 'RESOLVED').all()
        lead_times = [(a.resolved_at - a.created_at).total_seconds() / 3600 for a in resolved if a.resolved_at]
        avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0

        # Count red flags
        red_flags = db.query(Alert).filter(
            Alert.severity.in_(['HIGH', 'CRITICAL']),
            Alert.status.in_(['NEW', 'IN_REVIEW'])
        ).count()

        return {
            "pending_reviews": new_alerts + in_review,
            "critical_cases": critical,
            "red_flags": red_flags,
            "avg_lead_time": round(avg_lead_time, 1)
        }

    async def get_alerts(
        self,
        db: Session,
        status: List[str] = None,
        severity: List[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get list of alerts with filters."""
        query = db.query(Alert).join(Client)

        if status:
            query = query.filter(Alert.status.in_(status))
        if severity:
            query = query.filter(Alert.severity.in_(severity))

        query = query.order_by(Alert.created_at.desc()).limit(limit)
        alerts = query.all()

        return [self._format_alert(alert) for alert in alerts]

    async def get_alert_by_id(self, db: Session, alert_id: str) -> Dict:
        """Get detailed alert information."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return self._format_alert_detail(alert)

    async def remediate(
        self,
        db: Session,
        alert_id: str,
        action: str,
        notes: str,
        user_id: str = None
    ) -> Dict:
        """Execute remediation action."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        # Update alert status based on action
        if action == "APPROVE":
            alert.status = "RESOLVED"
            alert.resolution_type = "APPROVED"
        elif action == "REJECT":
            alert.status = "RESOLVED"
            alert.resolution_type = "BLOCKED"
        elif action == "ESCALATE":
            alert.status = "ESCALATED"
        elif action == "FALSE_POSITIVE":
            alert.status = "RESOLVED"
            alert.resolution_type = "FALSE_POSITIVE"

        alert.resolution_notes = notes
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = user_id

        db.commit()

        # Log to audit trail
        await self._log_audit(db, "ALERT_REMEDIATED", alert_id, user_id, action, notes)

        return {"success": True, "alert_id": alert_id, "new_status": alert.status}

    def _format_alert(self, alert: Alert) -> Dict:
        """Format alert for API response."""
        return {
            "id": str(alert.id),
            "type": alert.alert_type,
            "severity": alert.severity,
            "status": alert.status,
            "title": alert.title,
            "client": alert.client.client_name,
            "risk_score": alert.risk_score,
            "created_at": alert.created_at.isoformat(),
            "due_date": alert.due_date.isoformat() if alert.due_date else None
        }
```

---

## Frontend-Backend Connection

### Current Frontend API Client

**Location:** `frontend/lib/api.ts`

**Current Implementation (Mock Data):**
```typescript
// Using Supabase placeholder + mock fallback
import { supabase } from './supabase';

export async function getDashboardSummary() {
  // Try Supabase first, fall back to mock
  const { data, error } = await supabase
    .from('alert_summary')
    .select('*')
    .single();

  if (error) {
    // Return mock data
    return {
      pending_reviews: 24,
      critical_cases: 3,
      red_flags: 8,
      avg_lead_time: 2.5
    };
  }

  return data;
}
```

### Updated Implementation (Real Backend)

```typescript
// frontend/lib/api.ts (UPDATED - NO MOCKED DATA)
import { QueryClient } from '@tanstack/react-query';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Helper: Make authenticated API request
async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      // TODO: Add authentication token
      // 'Authorization': `Bearer ${getToken()}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'API request failed');
  }

  return response.json();
}

// Dashboard API
export async function getDashboardSummary() {
  return fetchAPI('/alerts/summary');
}

export async function getActiveAlerts() {
  return fetchAPI('/alerts/active');
}

export async function getAlertDetails(alertId: string) {
  return fetchAPI(`/alerts/${alertId}`);
}

// Document API
export async function uploadDocument(file: File, clientId: string) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('client_id', clientId);

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Document upload failed');
  }

  return response.json();
}

export async function analyzeDocument(documentId: string) {
  return fetchAPI(`/corroboration/analyze/${documentId}`, {
    method: 'POST',
  });
}

// Alert Actions
export async function remediateAlert(alertId: string, action: string, notes: string) {
  return fetchAPI(`/alerts/${alertId}/remediate`, {
    method: 'POST',
    body: JSON.stringify({ action, notes }),
  });
}

export async function getAuditTrail(alertId: string) {
  return fetchAPI(`/audit-trail/${alertId}`);
}

// React Query Hooks
export function useDashboardSummary() {
  return useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: getDashboardSummary,
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

export function useActiveAlerts() {
  return useQuery({
    queryKey: ['alerts', 'active'],
    queryFn: getActiveAlerts,
    refetchInterval: 10000, // Refresh every 10 seconds
  });
}

export function useAlertDetails(alertId: string) {
  return useQuery({
    queryKey: ['alerts', alertId],
    queryFn: () => getAlertDetails(alertId),
    enabled: !!alertId,
  });
}
```

### Frontend Component Updates

**Example: Compliance Dashboard**

**Before (Mock Data):**
```typescript
// frontend/app/compliance/page.tsx (OLD)
export default function ComplianceDashboard() {
  const [stats, setStats] = useState({
    pending_reviews: 24,
    critical_cases: 3,
    red_flags: 8,
    avg_lead_time: 2.5
  });

  // Mock data - no API call
}
```

**After (Real API):**
```typescript
// frontend/app/compliance/page.tsx (UPDATED)
import { useDashboardSummary, useActiveAlerts } from '@/lib/api';

export default function ComplianceDashboard() {
  const { data: summary, isLoading: summaryLoading } = useDashboardSummary();
  const { data: alerts, isLoading: alertsLoading } = useActiveAlerts();

  if (summaryLoading || alertsLoading) {
    return <LoadingState />;
  }

  return (
    <div>
      <KPICard
        title="Pending Reviews"
        value={summary.pending_reviews}
        trend="+5%"
      />
      <KPICard
        title="Critical Cases"
        value={summary.critical_cases}
        trend="-2%"
      />
      {/* ... rest of dashboard */}
      <AlertTriageTable alerts={alerts} />
    </div>
  );
}
```

### Environment Configuration

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/speedrun_aml
CORS_ORIGINS=http://localhost:3000
JWT_SECRET_KEY=your-secret-key-here
```

---

## Cross-Referencing Mechanism

### Linking Transactions ↔ Documents ↔ Alerts

**Use Case 1: Document Analysis Triggers Alert**
```python
# Workflow
1. User uploads document for Client A
2. Backend analyzes document → Risk score = 75 (HIGH)
3. System automatically creates alert:
   - Alert type: DOCUMENT_RISK
   - Linked to: document_id
   - Linked to: client_id
   - Recipients: RM (Client A) + Compliance team
4. Alert appears in dashboards
5. Users can click alert → see document analysis → see client profile
```

**Implementation:**
```python
# backend/src/backend/services/corroboration_service.py (UPDATED)
async def analyze_document(self, document_id: str, db: Session):
    """Analyze document and create alert if needed."""
    # Perform analysis
    result = await self.full_analysis(document_id)

    # Check if alert needed
    if result.risk_score.total_score >= 51:  # HIGH or CRITICAL
        alert = Alert(
            alert_type="DOCUMENT_RISK",
            severity=result.risk_score.risk_level,
            client_id=document.client_id,
            document_id=document_id,
            risk_score=result.risk_score.total_score,
            title=f"High-risk document detected for {client.client_name}",
            description=f"Document analysis flagged {result.findings_summary.high_issues} high-risk issues",
            triggered_rules=[],  # Can add specific validation rules
            context={
                "document_type": document.document_type,
                "filename": document.filename,
                "findings": result.findings_summary
            },
            recommended_actions=result.recommendations
        )
        db.add(alert)
        db.commit()

        # Route alert to recipients
        await alert_service.route_alert(db, alert.id)

    return result
```

**Use Case 2: Transaction Analysis Links to Documents**
```python
# Workflow (Part 1 - Future)
1. Transaction flagged for Client A (amount > threshold)
2. System checks: Does Client A have recent document analysis?
3. If yes, cross-reference:
   - Transaction risk: 60 (HIGH)
   - Document risk: 75 (HIGH)
   - Combined view: Client A has multiple risk signals
4. Single alert created with both contexts
5. Compliance officer sees complete picture
```

**Implementation:**
```python
async def analyze_transaction(self, transaction_id: str, db: Session):
    """Analyze transaction and cross-reference with documents."""
    # Perform transaction analysis
    tx_result = await self.transaction_analysis(transaction_id)

    # Get client's recent document analysis
    recent_docs = db.query(Document).filter(
        Document.client_id == transaction.client_id,
        Document.processed == True
    ).order_by(Document.processed_at.desc()).limit(5).all()

    # Check for correlated risks
    doc_risks = [d.risk_score for d in recent_docs if hasattr(d, 'risk_score')]
    has_doc_risk = any(score >= 51 for score in doc_risks)

    if tx_result.risk_score >= 51 and has_doc_risk:
        # Create correlated alert
        alert = Alert(
            alert_type="CORRELATED_RISK",
            severity="CRITICAL",
            client_id=transaction.client_id,
            transaction_id=transaction_id,
            document_id=recent_docs[0].id if recent_docs else None,
            risk_score=max(tx_result.risk_score, max(doc_risks)),
            title=f"Multiple risk signals for {client.client_name}",
            description="Both transaction and document analysis indicate high risk",
            context={
                "transaction_risk": tx_result.risk_score,
                "document_risk": max(doc_risks) if doc_risks else 0,
                "risk_factors": tx_result.risk_factors + doc_result.risk_factors
            }
        )
        db.add(alert)
        db.commit()
```

### Cross-Reference API Endpoints

```python
# Get all entities linked to a client
GET /api/v1/clients/{client_id}/risk-overview
Response: {
  "client": {...},
  "documents": [
    {"document_id": "...", "risk_score": 75, "analyzed_at": "..."}
  ],
  "transactions": [
    {"transaction_id": "...", "risk_score": 60, "timestamp": "..."}
  ],
  "alerts": [
    {"alert_id": "...", "type": "DOCUMENT_RISK", "severity": "HIGH"}
  ],
  "combined_risk_score": 80,
  "risk_level": "HIGH"
}

# Get all alerts for a document
GET /api/v1/documents/{document_id}/alerts
Response: {
  "document_id": "...",
  "alerts": [...]
}

# Get all documents related to an alert
GET /api/v1/alerts/{alert_id}/related-documents
Response: {
  "alert_id": "...",
  "primary_document": {...},
  "related_documents": [...]
}
```

---

## Unified Dashboard Requirements

### Role-Based Views

**1. Compliance Officer Dashboard**

**Features:**
- KPI cards (pending reviews, critical cases, red flags, lead time)
- Alert triage table with filters
- Document upload and analysis
- KYC review Kanban board
- Risk analytics charts

**Data Sources:**
```typescript
// Real-time data from backend
- /api/v1/alerts/summary → KPI cards
- /api/v1/alerts/active → Alert triage table
- /api/v1/documents/recent → Recent uploads
- /api/v1/analytics/trends → Charts
```

**2. Relationship Manager Dashboard**

**Features:**
- Client portfolio overview
- Client risk ratings
- Document upload for clients
- Alert notifications for their clients
- Client search and filtering

**Data Sources:**
```typescript
- /api/v1/clients?rm_id={user_id} → Client list
- /api/v1/alerts/my-alerts → Alerts for RM's clients
- /api/v1/clients/{id}/risk-overview → Client risk details
```

**3. Legal Team Dashboard**

**Features:**
- Critical alerts only
- Audit trail viewer
- Regulatory reports
- Escalation queue
- Legal action tracking

**Data Sources:**
```typescript
- /api/v1/alerts?severity=CRITICAL → Critical alerts
- /api/v1/audit/logs → Audit trail
- /api/v1/reports/regulatory → Compliance reports
```

### Real-Time Updates

**Option 1: WebSocket (Recommended for Real-Time)**
```python
# Backend: WebSocket endpoint
from fastapi import WebSocket

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Send new alerts to connected clients
        new_alerts = await get_new_alerts()
        await websocket.send_json({"type": "NEW_ALERT", "data": new_alerts})
        await asyncio.sleep(5)
```

```typescript
// Frontend: WebSocket client
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws/alerts');

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'NEW_ALERT') {
      // Update UI with new alert
      queryClient.invalidateQueries(['alerts']);
      toast.success('New alert received!');
    }
  };

  return () => ws.close();
}, []);
```

**Option 2: Polling (Simple, Works for Prototype)**
```typescript
// Frontend: Auto-refresh using React Query
useQuery({
  queryKey: ['alerts', 'active'],
  queryFn: getActiveAlerts,
  refetchInterval: 10000, // Poll every 10 seconds
});
```

---

## Deployment Architecture

### Development Environment

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: speedrun_aml
      POSTGRES_USER: speedrun
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://speedrun:devpassword@postgres:5432/speedrun_aml
      REDIS_URL: redis://redis:6379
      CORS_ORIGINS: http://localhost:3000
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    command: npm run dev
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  postgres_data:
```

**Start Development Environment:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Production Architecture (Future)

```
┌─────────────────────────────────────────────┐
│            Load Balancer / CDN              │
│            (Cloudflare / AWS ALB)           │
└───────────────────┬─────────────────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│  Frontend       │   │  Backend API    │
│  (Vercel/AWS)   │   │  (ECS/K8s)      │
│  - Next.js      │   │  - FastAPI      │
│  - Static CDN   │   │  - Auto-scaling │
└─────────────────┘   └────────┬────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
           ┌─────────────────┐   ┌─────────────────┐
           │  PostgreSQL     │   │  Redis Cache    │
           │  (RDS/Cloud SQL)│   │  (ElastiCache)  │
           └─────────────────┘   └─────────────────┘
                    │
                    ▼
           ┌─────────────────┐
           │  S3/Cloud       │
           │  Storage        │
           │  (Documents)    │
           └─────────────────┘
```

---

## Implementation Roadmap

### Phase 1: Database Setup (Week 1)
**Goal:** Set up PostgreSQL with complete schema

**Tasks:**
- [ ] Install PostgreSQL
- [ ] Create database schema (all tables)
- [ ] Set up SQLAlchemy models
- [ ] Create database migrations (Alembic)
- [ ] Seed test data

**Deliverables:**
- Working database with all tables
- Migration scripts
- Test data for 10 clients, 50 documents, 30 alerts

### Phase 2: Alert Management API (Week 1-2)
**Goal:** Create bridge API for frontend

**Tasks:**
- [ ] Create `alerts.py` router
- [ ] Implement `alert_service.py`
- [ ] Add alert creation from document analysis
- [ ] Implement alert routing logic
- [ ] Add audit logging

**Deliverables:**
- 8+ alert management endpoints
- Unit tests for alert service
- Integration with document corroboration

### Phase 3: Frontend Integration (Week 2)
**Goal:** Connect frontend to real backend

**Tasks:**
- [ ] Update `lib/api.ts` with real endpoints
- [ ] Remove all mock data
- [ ] Add error handling
- [ ] Add loading states
- [ ] Test all API calls

**Deliverables:**
- Frontend fetching 100% real data
- No mocked responses
- Proper error handling

### Phase 4: Document Upload Flow (Week 3)
**Goal:** Complete end-to-end document workflow

**Tasks:**
- [ ] Implement file upload endpoint
- [ ] Save documents to database
- [ ] Trigger analysis on upload
- [ ] Create alerts automatically
- [ ] Update frontend to show results

**Deliverables:**
- Upload document → Analysis → Alert → Dashboard
- Complete audit trail
- Real-time updates in UI

### Phase 5: Cross-Referencing (Week 3-4)
**Goal:** Link documents, transactions, alerts

**Tasks:**
- [ ] Implement client risk overview API
- [ ] Add document-alert linking
- [ ] Create transaction-document correlation (when Part 1 ready)
- [ ] Build unified client view

**Deliverables:**
- Single client view with all risks
- Cross-referenced alerts
- Comprehensive risk scoring

### Phase 6: Testing & Optimization (Week 4)
**Goal:** Ensure stability and performance

**Tasks:**
- [ ] Integration testing (frontend ↔ backend)
- [ ] Performance testing (load times, API response times)
- [ ] Security testing (OWASP Top 10)
- [ ] User acceptance testing

**Deliverables:**
- Test coverage reports
- Performance benchmarks met
- Security vulnerabilities addressed

---

## Success Metrics

### Integration Success Criteria

**Technical Metrics:**
- ✅ 0% mocked data in frontend (100% real backend)
- ✅ <2 second page load time
- ✅ <200ms API response time (P95)
- ✅ 100% of features working end-to-end
- ✅ Database persisting all data
- ✅ Real-time updates functional

**Functional Metrics:**
- ✅ Upload document → See analysis results workflow works
- ✅ Document analysis creates alerts automatically
- ✅ Alerts appear in both Compliance and RM dashboards
- ✅ Alert remediation updates database and UI
- ✅ Audit trail captures all activities
- ✅ Reports can be generated and exported

**User Experience Metrics:**
- ✅ No errors or crashes during normal use
- ✅ Loading states for all async operations
- ✅ Error messages are clear and actionable
- ✅ UI updates reflect backend changes immediately
- ✅ Navigation is intuitive and responsive

---

**Document Version:** 1.0.0
**Last Updated:** 2025-01-15
**Status:** Final
**Owner:** Speed-Run Development Team

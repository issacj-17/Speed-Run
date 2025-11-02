# Frontend Architecture Analysis - Speed-Run AML Platform

**Created**: November 2, 2025
**Framework**: Next.js 14 (App Router), React 18, TypeScript
**Status**: UI Complete, Backend Integration Pending

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Component Hierarchy](#component-hierarchy)
3. [Data Flow Architecture](#data-flow-architecture)
4. [State Management](#state-management)
5. [API Integration Status](#api-integration-status)
6. [Key Components Deep Dive](#key-components-deep-dive)
7. [Implementation Roadmap](#implementation-roadmap)

---

## Project Structure

```
frontend/
├── app/                            # Next.js 14 App Router
│   ├── layout.tsx                  # Root layout (ErrorBoundary + Providers)
│   ├── page.tsx                    # Home - Role selector
│   ├── providers.tsx               # React Query setup
│   ├── globals.css                 # Global styles
│   ├── compliance/
│   │   └── page.tsx                # Compliance dashboard (Kanban + Upload)
│   ├── rm/
│   │   └── page.tsx                # RM dashboard (Clients + Upload)
│   └── investigation/
│       └── [alertId]/
│           └── page.tsx            # Investigation cockpit
│
├── components/
│   ├── ui/                         # Shadcn UI (10 components)
│   ├── charts/                     # Chart wrappers (2 components)
│   ├── compliance/                 # Compliance UI (11 components)
│   │   ├── DocumentUploadAnalysis.tsx  ⭐ KEY COMPONENT
│   │   ├── KanbanBoardDnD.tsx     # Drag-drop Kanban
│   │   └── ...                     # 9 other components
│   ├── investigation/              # Investigation UI (5 components)
│   └── dashboard/                  # Dashboard UI (4 components)
│
├── lib/
│   ├── api.ts                      # Backend API client ✅
│   ├── mock-data.ts                # Mock data (to be removed)
│   ├── supabase.ts                 # Supabase client (to be removed)
│   └── utils.ts                    # Utility functions
│
└── types/
    └── index.ts                    # Shared TypeScript types
```

**Total Components**: 33 .tsx files
**Pages**: 4 routes (home, compliance, rm, investigation)
**API Functions**: 12 implemented, ready to use

---

## Component Hierarchy

### Visual Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION TREE                            │
└─────────────────────────────────────────────────────────────────┘

RootLayout (app/layout.tsx)
├── ErrorBoundary (global error handling)
└── Providers (React Query + QueryClient)
    └── {children} (routed page content)

┌─────────────────────────────────────────────────────────────────┐
│                         PAGES                                    │
└─────────────────────────────────────────────────────────────────┘

1. HOME (/)
   └── Role selector buttons → /compliance or /rm

2. COMPLIANCE DASHBOARD (/compliance)
   ├── Header with back button
   ├── 4x KPI Cards (Pending Reviews, Critical Cases, Red Flags, Avg Time)
   ├── DocumentUploadAnalysis ⭐
   │   ├── Upload zone (drag/drop)
   │   ├── File list with progress
   │   └── Analysis results (risk, issues, checks, recommendation)
   ├── Business Metrics (2 cards)
   └── KanbanBoardDnD
       ├── Filter bar (All/Critical/High/Medium)
       ├── 4 Columns (New/Review/Flagged/Resolved)
       │   └── SortableCard[] (draggable)
       │       ├── Client info
       │       ├── Risk score badge
       │       ├── Red flags counter
       │       ├── Time in queue
       │       ├── Assigned officer
       │       └── Action menu (Start/Flag/Resolve/Open)
       └── Drag overlay

3. RM DASHBOARD (/rm)
   ├── Header
   ├── 3x Quick Stats (Clients, Reviews, Alerts)
   ├── Document Upload Section
   └── Client Table (searchable)
       └── Rows: Name, Risk, KYC Status, Docs, Alerts, Actions

4. INVESTIGATION (/investigation/[alertId])
   ├── Header
   ├── Two-column layout
   │   ├── LEFT: TransactionDetails (alert info, client, transaction)
   │   └── RIGHT: DocumentViewer (preview + issues)
   ├── AgentFindings (3 AI agents)
   │   └── Cards: Agent name, priority, finding, regulation
   ├── HistoricalContext (transaction chart)
   └── Action buttons
       ├── QuickApproval (4 types, with reason modal)
       ├── Escalate
       ├── View Audit Trail
       └── Reject
```

---

## Data Flow Architecture

### Current State: Mock Data

```
┌───────────────────────────────────────────────────────────────┐
│               CURRENT DATA FLOW (MOCK)                        │
└───────────────────────────────────────────────────────────────┘

Component → import mock data from lib/mock-data.ts → Display

Examples:
- Compliance dashboard → mockKanbanCards[] → Kanban board
- RM dashboard → mockClients[] → Client table
- Investigation → mockAlertDetails → Alert details
- DocumentUploadAnalysis → generateMockAnalysis() → Fake results
```

### Target State: Backend API Integration

```
┌───────────────────────────────────────────────────────────────┐
│            TARGET DATA FLOW (BACKEND API)                     │
└───────────────────────────────────────────────────────────────┘

User Action
    ↓
Component Event Handler
    ↓
Call API function from lib/api.ts
    ↓
HTTP Request → FastAPI Backend (localhost:8000/api/v1)
    ↓
Backend Processing:
  - Database queries
  - AI/ML inference (Docling, spaCy, PIL)
  - Risk scoring
  - Fraud detection
    ↓
JSON Response
    ↓
Transform to UI format
    ↓
Update Component State
    ↓
React Re-render
    ↓
Display Results to User
```

### Document Upload Flow (CRITICAL PATH)

```
┌──────────────────────────────────────────────────────────────┐
│     DocumentUploadAnalysis - Data Flow                       │
└──────────────────────────────────────────────────────────────┘

User drops/selects file
    ↓
handleFiles(files: File[])
    ├─ Validate file type (PDF, JPG, PNG)
    ├─ Validate size (≤ 10MB)
    └─ Create UploadedFile objects
    ↓
setState: status = "uploading"
    ↓
Call: analyzeDocument(file, clientId?)
    ↓
POST /api/v1/corroboration/analyze
    ├─ FormData with file
    └─ Optional: client_id parameter
    ↓
Backend processes (3-10 seconds):
    ├─ Docling: Parse document, extract text/tables
    ├─ Format validation: Check structure, consistency
    ├─ Structure validation: Verify document integrity
    ├─ Image analysis: Detect tampering, AI-generated content
    └─ Risk scoring: Calculate overall risk (0-100)
    ↓
Backend returns CorroborationResponse:
{
  document_id: string
  analysis_complete: boolean
  risk_score: number
  risk_level: "low" | "medium" | "high" | "critical"
  findings: {
    format_validation: { valid, issues[], passed[] }
    structure_validation: { valid, issues[], passed[] }
    image_analysis: { tampering_detected, issues[], passed[] }
  }
  alert_id?: string  // If high risk → auto-create alert
}
    ↓
transformBackendResponse()
    ├─ Extract issues from findings
    ├─ Extract passed checks
    ├─ Generate UI-friendly recommendation
    └─ Map to AnalysisResult interface
    ↓
setState: status = "complete", analysis = result
    ↓
React re-renders:
    ├─ Risk score badge (color-coded)
    ├─ Issues detected (red list)
    ├─ Passed checks (green list)
    ├─ Recommendation box (color-coded)
    └─ Action buttons
```

---

## State Management

### Global State

**Provider**: React Query (@tanstack/react-query)
**Location**: `app/providers.tsx`
**Configuration**:
```typescript
new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60000,  // 1 minute
      refetchOnWindowFocus: false,
    },
  },
})
```

**Status**: Configured but not yet used (ready for integration)

### Local Component State

#### DocumentUploadAnalysis (Most Complex)

```typescript
const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
const [isDragging, setIsDragging] = useState(false)
const [showResults, setShowResults] = useState(false)

interface UploadedFile {
  id: string
  file: File
  status: "uploading" | "analyzing" | "complete" | "error"
  progress: number
  analysis?: AnalysisResult
}
```

**State Transitions**:
```
null → "uploading" → "analyzing" → "complete"
                               ↘  "error"
```

**Events**:
- `onFileSelect`: null → uploading
- `onUploadComplete`: uploading → analyzing
- `onAnalysisSuccess`: analyzing → complete
- `onAnalysisError`: analyzing → error
- `onRetry`: error → uploading
- `onRemove`: any → removed

#### KanbanBoardDnD

```typescript
const [cards, setCards] = useState(initialCards)
const [activeId, setActiveId] = useState<string | null>(null)
const [selectedFilter, setSelectedFilter] = useState<string>("all")
const [showResolveModal, setShowResolveModal] = useState(false)
const [resolveCardId, setResolveCardId] = useState<string | null>(null)
const [resolveReason, setResolveReason] = useState("")
const [showActionMenu, setShowActionMenu] = useState<string | null>(null)
```

#### QuickApproval (Investigation Page)

```typescript
const [showReasonModal, setShowReasonModal] = useState(false)
const [selectedAction, setSelectedAction] = useState<string>("")
const [reason, setReason] = useState("")
```

#### RM Dashboard

```typescript
const [searchQuery, setSearchQuery] = useState("")
// Used for filtering client table
```

---

## API Integration Status

### Backend API Client (lib/api.ts)

**Base URL**: `http://localhost:8000/api/v1` (configurable via env)

#### Available Functions

| Function | Method | Endpoint | Status | Used By |
|----------|--------|----------|--------|---------|
| `getDashboardSummary()` | GET | `/alerts/summary` | ✅ Ready | Compliance Dashboard |
| `getActiveAlerts()` | GET | `/alerts/?status=active` | ✅ Ready | Compliance/RM Dashboard |
| `getAlertDetails(id)` | GET | `/alerts/{id}` | ✅ Ready | Investigation Page |
| `updateAlertStatus(id, status)` | PUT | `/alerts/{id}/status` | ✅ Ready | Investigation Page |
| `remediateAlert(id)` | PUT | `/alerts/{id}/status` | ✅ Ready | Investigation Page |
| `getAuditTrail(id)` | GET | `/alerts/{id}/audit-trail` | ✅ Ready | Investigation Page |
| `analyzeDocument(file, clientId?)` | POST | `/corroboration/analyze` | ✅ Ready | DocumentUploadAnalysis |
| `performOCR(file)` | POST | `/ocr/extract` | ✅ Ready | (Future) |
| `parseDocument(file)` | POST | `/documents/parse` | ✅ Ready | (Future) |
| `checkBackendHealth()` | GET | `/health` | ✅ Ready | (Monitoring) |
| `getTransactionVolume()` | - | (Mock data) | ⚠️ TODO Backend | Dashboard |

#### Utility Functions

```typescript
// JSON API calls
fetchFromBackend(endpoint: string, options?: RequestInit)

// File uploads (FormData)
uploadFile(endpoint: string, file: File, additionalData?: Record<string, any>)
```

### Integration Status by Component

| Component | Current | Target | Priority |
|-----------|---------|--------|----------|
| **DocumentUploadAnalysis** | Mock analysis | `analyzeDocument()` | 🔴 **HIGH** |
| Compliance Dashboard | Mock cards | `getDashboardSummary()`, `getActiveAlerts()` | 🟡 MEDIUM |
| Investigation Page | Mock details | `getAlertDetails()`, `updateAlertStatus()` | 🟡 MEDIUM |
| RM Dashboard | Mock clients | (Backend endpoint needed) | 🟢 LOW |

---

## Key Components Deep Dive

### 1. DocumentUploadAnalysis ⭐ CRITICAL COMPONENT

**File**: `components/compliance/DocumentUploadAnalysis.tsx`
**Purpose**: Upload documents, detect fraud, display risk analysis
**Priority**: HIGH - Core functionality

#### Current Implementation (Mock)

**Features**:
- Drag-and-drop file upload
- Multiple file support
- File type validation (PDF, JPG, PNG, JPEG)
- File size validation (10MB max)
- Simulated progress bar
- Mock fraud detection
- Risk scoring display (0-100)
- Issues list (red)
- Passed checks list (green)
- Recommendations

**Mock Analysis Logic**:
```typescript
generateMockAnalysis(file, fileType) {
  // Semi-intelligent mock:
  // - Base risk: random 20-60
  // - Add 30 if filename contains: "copy", "scan", "temp"
  // - Tampering detected if risk > 70

  riskLevel:
    ≥86 → "critical"
    ≥71 → "high"
    ≥41 → "medium"
    else → "low"
}
```

**UI Components**:
1. **Upload Zone** (Card with drag/drop)
2. **File List** (shows each uploaded file)
3. **Progress Bar** (during upload)
4. **Analysis Results**:
   - File icon (PDF/Image)
   - File name & size
   - Remove button (X)
   - Risk score badge (color-coded)
   - Issues detected (red boxes)
   - Passed checks (green boxes)
   - Recommendation (color-coded box)

**Color Coding**:
```typescript
Risk Score Badge:
  critical (≥86) → bg-red-600
  high (≥71)     → bg-orange-600
  medium (≥41)   → bg-yellow-600
  low            → bg-green-600

Recommendation Box:
  critical/high → red (bg-red-50 border-red-200)
  medium        → yellow (bg-yellow-50 border-yellow-200)
  low           → green (bg-green-50 border-green-200)
```

#### Backend Integration Requirements

**Required Changes**:

1. **Import API function**:
```typescript
import { analyzeDocument, CorroborationResponse } from "@/lib/api"
```

2. **Replace `simulateAnalysis()` with real API call**:
```typescript
const realAnalysis = async (fileId: string) => {
  try {
    const upload = uploadedFiles.find(f => f.id === fileId)
    if (!upload) return

    // Set analyzing status
    setUploadedFiles(prev =>
      prev.map(f => f.id === fileId ?
        {...f, status: "analyzing"} : f
      )
    )

    // Call backend
    const response: CorroborationResponse =
      await analyzeDocument(upload.file)

    // Transform response
    const analysis = transformBackendResponse(response)

    // Update state
    setUploadedFiles(prev =>
      prev.map(f => f.id === fileId ?
        {...f, status: "complete", analysis} : f
      )
    )
  } catch (error) {
    console.error("Analysis failed:", error)
    setUploadedFiles(prev =>
      prev.map(f => f.id === fileId ?
        {...f, status: "error"} : f
      )
    )
  }
}
```

3. **Add response transformer**:
```typescript
const transformBackendResponse = (
  response: CorroborationResponse
): AnalysisResult => {
  return {
    riskScore: response.risk_score,
    riskLevel: response.risk_level as "low" | "medium" | "high" | "critical",
    issuesDetected: extractIssues(response.findings),
    passedChecks: extractPassedChecks(response.findings),
    recommendation: generateRecommendation(response.risk_level),
    fileType: response.findings.format_validation?.file_type || "pdf",
    tampering: response.risk_score > 70
  }
}

const extractIssues = (findings: any): string[] => {
  const issues: string[] = []

  if (findings.format_validation?.issues) {
    issues.push(...findings.format_validation.issues)
  }

  if (findings.structure_validation?.issues) {
    issues.push(...findings.structure_validation.issues)
  }

  if (findings.image_analysis?.issues) {
    issues.push(...findings.image_analysis.issues)
  }

  return issues.length > 0 ? issues : ["No issues detected"]
}

const extractPassedChecks = (findings: any): string[] => {
  const checks: string[] = []

  if (findings.format_validation?.passed) {
    checks.push(...findings.format_validation.passed)
  }

  if (findings.structure_validation?.passed) {
    checks.push(...findings.structure_validation.passed)
  }

  if (findings.image_analysis?.passed) {
    checks.push(...findings.image_analysis.passed)
  }

  return checks.length > 0 ? checks : ["All checks passed"]
}

const generateRecommendation = (riskLevel: string): string => {
  switch (riskLevel) {
    case "critical":
      return "ESCALATE - Critical fraud indicators detected. Requires immediate senior review and potential account freeze."
    case "high":
      return "ESCALATE - High risk of fraud detected. Requires senior compliance officer review before approval."
    case "medium":
      return "REVIEW - Moderate risk indicators present. Additional verification recommended before proceeding."
    case "low":
      return "APPROVE - Document appears authentic with no significant risk indicators. Proceed with standard review process."
    default:
      return "REVIEW - Unable to determine risk level. Manual review recommended."
  }
}
```

4. **Add error handling UI**:
```typescript
// In render section:
{upload.status === "error" && (
  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
    <p className="text-sm text-red-600">
      ❌ Analysis failed. Please try again.
    </p>
    <Button
      size="sm"
      variant="outline"
      className="mt-2"
      onClick={() => realAnalysis(upload.id)}
    >
      Retry
    </Button>
  </div>
)}
```

5. **Update analyzing indicator**:
```typescript
{upload.status === "analyzing" && (
  <div className="flex items-center gap-2 text-sm text-blue-600">
    <div className="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
    <span>Analyzing document with AI detection engines...</span>
  </div>
)}
```

#### Expected Backend Response

```typescript
interface CorroborationResponse {
  document_id: string           // e.g., "doc_123abc"
  analysis_complete: boolean    // true when processing done
  risk_score: number           // 0-100
  risk_level: string           // "low" | "medium" | "high" | "critical"
  findings: {
    format_validation: {
      valid: boolean
      file_type: string
      issues: string[]
      passed: string[]
    }
    structure_validation: {
      valid: boolean
      issues: string[]
      passed: string[]
    }
    image_analysis: {
      tampering_detected: boolean
      ai_generated: boolean
      issues: string[]
      passed: string[]
    }
  }
  alert_id?: string             // If risk high enough → auto-create alert
}
```

### 2. KanbanBoardDnD

**File**: `components/compliance/KanbanBoardDnD.tsx`
**Purpose**: Visual task management for KYC reviews
**Library**: `@dnd-kit/core`, `@dnd-kit/sortable`

**Features**:
- 4 columns: New, Review, Flagged, Resolved
- Drag-and-drop cards between columns
- Filter bar (All, Critical, High, Medium risk)
- Card actions: Start Review, Flag, Resolve, Open Full Review
- Resolve modal with reason input
- Real-time drag overlay
- Auto-sort by priority within columns

**State**: Complex drag/drop state management
**Backend Integration**: Should sync card positions with backend on drop

### 3. Investigation Page (Alert Cockpit)

**File**: `app/investigation/[alertId]/page.tsx`
**Purpose**: Full investigation interface for alerts

**Components**:
1. **TransactionDetails** - Alert + transaction info
2. **DocumentViewer** - Document preview with issue markers
3. **AgentFindings** - AI agent analysis (3 agents)
4. **HistoricalContext** - Transaction history chart
5. **QuickApproval** - Approval workflow with reason modal

**Backend Integration Needed**:
- `getAlertDetails(alertId)` - Load alert data
- `updateAlertStatus(alertId, status)` - Update when approved/rejected
- `getAuditTrail(alertId)` - Show audit log

---

## Implementation Roadmap

### Phase 1: Core Functionality (HIGH PRIORITY)

**Goal**: Get document fraud detection working end-to-end

**Tasks**:
1. ✅ Create frontend `.env.local` with backend URL
2. ✅ Replace Supabase with backend API client (`lib/api.ts`)
3. 🔄 Integrate DocumentUploadAnalysis with backend
   - Replace mock analysis with `analyzeDocument()` API
   - Add response transformer
   - Add error handling UI
   - Add retry functionality
   - Test with real PDFs and images
4. Update frontend README.md with:
   - Environment variable setup
   - Backend integration instructions
   - Development workflow

**Estimated Time**: 1-2 hours
**Impact**: CRITICAL - Enables core fraud detection feature

### Phase 2: Dashboard Integration (MEDIUM PRIORITY)

**Goal**: Show real-time alert data on dashboards

**Tasks**:
1. Compliance Dashboard (`app/compliance/page.tsx`):
   - Replace `mockKanbanCards` with `getActiveAlerts()`
   - Add React Query hook: `useQuery(['alerts'], getActiveAlerts)`
   - Add loading skeleton (use LoadingState component)
   - Add error boundary
   - Update KPI cards with `getDashboardSummary()`
2. RM Dashboard (`app/rm/page.tsx`):
   - Backend needs `/api/v1/clients` endpoint (not implemented)
   - Temporary: Use `getActiveAlerts()` to show alert count
3. Add auto-refresh every 30 seconds for dashboards

**Estimated Time**: 2-3 hours
**Impact**: HIGH - Real-time compliance monitoring

### Phase 3: Investigation Workflow (MEDIUM PRIORITY)

**Goal**: Enable full alert investigation and resolution

**Tasks**:
1. Investigation Page (`app/investigation/[alertId]/page.tsx`):
   - Replace `mockAlertDetails` with `getAlertDetails(alertId)`
   - Add React Query: `useQuery(['alert', alertId], () => getAlertDetails(alertId))`
   - Wire up approval buttons to `updateAlertStatus()`
   - Add audit trail view with `getAuditTrail()`
   - Add optimistic updates for better UX
2. Add success/error toasts for user actions
3. Add loading states during API calls

**Estimated Time**: 2-3 hours
**Impact**: HIGH - Complete case management workflow

### Phase 4: Polish & Optimization (LOW PRIORITY)

**Tasks**:
1. Add React Query mutations for all write operations
2. Implement optimistic updates throughout
3. Add proper error boundaries per route
4. Add WebSocket support for real-time updates (optional)
5. Add toast notifications for all actions
6. Remove all mock data files
7. Remove Supabase dependency completely
8. Add comprehensive loading skeletons
9. Add offline mode handling
10. Optimize bundle size

**Estimated Time**: 4-5 hours
**Impact**: MEDIUM - Better UX and performance

---

## Technical Stack

### Core

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **Component Library**: Shadcn UI

### Key Libraries

- **State Management**: React Query (@tanstack/react-query)
- **Drag & Drop**: @dnd-kit/core, @dnd-kit/sortable
- **Charts**: Recharts
- **Icons**: Lucide React
- **Forms**: (not yet implemented - TODO)
- **Validation**: (not yet implemented - TODO)

### Build Tools

- **Package Manager**: npm
- **Bundler**: Next.js (webpack under the hood)
- **TypeScript**: tsc
- **CSS**: PostCSS + Tailwind

---

## Environment Configuration

### Required Variables

```bash
# .env.local (frontend root)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_USE_BACKEND_API=true
NEXT_PUBLIC_DEBUG=false
```

### Backend Requirements

The frontend expects the backend to be running at `http://localhost:8000` with the following endpoints available:

**Required for Phase 1**:
- `POST /api/v1/corroboration/analyze`

**Required for Phase 2**:
- `GET /api/v1/alerts/summary`
- `GET /api/v1/alerts/?status=active`

**Required for Phase 3**:
- `GET /api/v1/alerts/{id}`
- `PUT /api/v1/alerts/{id}/status`
- `GET /api/v1/alerts/{id}/audit-trail`

---

## Current Status Summary

### ✅ Complete

- UI/UX design and implementation
- Component architecture
- Page routing
- Mock data for prototyping
- Drag-and-drop Kanban
- Document upload interface
- Risk visualization
- Backend API client (`lib/api.ts`)
- Environment configuration (`.env.local`)

### 🔄 In Progress

- Backend API integration
- DocumentUploadAnalysis real fraud detection
- Error handling
- Loading states

### ⏳ TODO

- Remove Supabase dependency
- Remove mock data files
- Add React Query hooks throughout
- Implement form validation
- Add toast notifications
- WebSocket for real-time updates (optional)
- Comprehensive error boundaries
- Loading skeletons
- Offline mode

---

## Performance Considerations

### Bundle Size
- Current: Not optimized
- TODO: Code splitting per route
- TODO: Dynamic imports for heavy components
- TODO: Image optimization with next/image

### API Calls
- Current: No caching, no error retry
- TODO: React Query caching (staleTime: 60s)
- TODO: Automatic retry on failure
- TODO: Optimistic updates
- TODO: Request deduplication

### Rendering
- Current: Client-side rendering for all pages
- TODO: Server-side rendering for dashboard data
- TODO: Streaming for long-running analysis
- TODO: Suspense boundaries for better loading UX

---

## Testing Strategy (Future)

### Unit Tests
- Component rendering
- User interactions
- State management
- Utility functions

### Integration Tests
- API client functions
- Form submissions
- File uploads
- Drag-and-drop

### E2E Tests
- Complete user workflows
- Document upload → analysis → approval
- Alert investigation → resolution
- Dashboard interactions

---

## Maintenance Notes

### When Adding New API Endpoints

1. Add function to `lib/api.ts`
2. Add TypeScript interface for response
3. Update this document with new endpoint
4. Wire up in component
5. Add loading/error states
6. Add tests (future)

### When Adding New Components

1. Follow existing pattern (ui/, compliance/, etc.)
2. Use TypeScript for all props
3. Add error boundary if needed
4. Document in this file if complex
5. Use Tailwind for styling
6. Make responsive (mobile-first)

### Code Style

- Use functional components
- Prefer hooks over classes
- Use TypeScript interfaces over types
- Keep components small (<300 lines)
- Extract reusable logic to custom hooks
- Use const for all variables
- Destructure props
- Add JSDoc comments for complex functions

---

**Last Updated**: November 2, 2025
**Maintained By**: Speed-Run Development Team
**Next Review**: After Phase 1 completion

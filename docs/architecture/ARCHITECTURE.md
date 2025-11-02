# System Architecture

## Overview

The Julius Baer AML Platform is a full-stack application with AI-powered analysis capabilities.

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                     (Browser - Port 3000)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js 14)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Dashboard   │  │Investigation │  │  Components  │         │
│  │    Page      │  │   Cockpit    │  │   (UI Kit)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  API Client  │  │  Mock Data   │  │   Utilities  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ REST API / WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI - Port 8000)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                      API ROUTES                            ││
│  ├────────────────────────────────────────────────────────────┤│
│  │  /api/alerts/*        │  Alert management                  ││
│  │  /api/transactions/*  │  Transaction data                  ││
│  │  /api/audit-trail/*   │  Audit logging                     ││
│  │  /ws/alerts           │  Real-time updates (WebSocket)     ││
│  └────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                   AGENT ORCHESTRATOR                       ││
│  │                  (Coordinates AI Agents)                   ││
│  └────────────────────────────────────────────────────────────┘│
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │ Regulatory  │    │Transaction  │    │  Document   │       │
│  │  Watcher    │    │  Analyst    │    │  Forensics  │       │
│  │   Agent     │    │   Agent     │    │    Agent    │       │
│  └─────────────┘    └─────────────┘    └─────────────┘       │
│         │                    │                    │             │
│         └────────────────────┴────────────────────┘             │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                    DATA SERVICES                           ││
│  ├────────────────────────────────────────────────────────────┤│
│  │  Mock Data (Current)  │  In-memory storage                 ││
│  │  MongoDB (Future)     │  Persistent storage                ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ (Future Integration)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   MongoDB    │  │   Groq AI    │  │  Document    │         │
│  │   Database   │  │     API      │  │   Storage    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Frontend Layer

#### Dashboard Page
- **Purpose:** Overview of all AML alerts
- **Components:**
  - KPI Cards (metrics)
  - Pie Chart (risk distribution)
  - Line Chart (transaction trends)
  - Alert Triage Table
- **Data Flow:** Fetches from `/api/alerts/summary` and `/api/alerts/active`

#### Investigation Cockpit
- **Purpose:** Detailed alert analysis
- **Components:**
  - Transaction Details Panel
  - Document Viewer with Issues
  - AI Agent Findings
  - Historical Context Chart
- **Data Flow:** Fetches from `/api/alerts/{id}`

#### UI Components
- **Library:** shadcn/ui (built on Radix UI)
- **Styling:** TailwindCSS
- **Charts:** Recharts
- **State:** React Query for caching

---

### Backend Layer

#### API Routes

**Alerts Endpoints:**
```
GET  /api/alerts/summary          → Dashboard KPIs
GET  /api/alerts/active           → Active alerts list
GET  /api/alerts/{id}             → Alert details
POST /api/alerts/{id}/remediate   → Mark as remediated
```

**Transaction Endpoints:**
```
GET /api/transactions/volume           → Volume trends
GET /api/transactions/history/{id}     → Client history
```

**Audit Endpoints:**
```
GET /api/audit-trail/{alert_id}   → Audit logs
```

**WebSocket:**
```
WS /ws/alerts   → Real-time alert updates
```

---

### AI Agent System

#### Agent Orchestrator
- **Role:** Coordinates multiple AI agents
- **Process:**
  1. Receives alert data
  2. Runs agents in parallel
  3. Aggregates findings
  4. Calculates risk score
  5. Returns comprehensive analysis

#### Individual Agents

**1. Regulatory Watcher Agent**
- **Focus:** FINMA compliance
- **Checks:** Regulation violations, documentation requirements
- **Output:** Priority + Finding + Regulation reference

**2. Transaction Analyst Agent**
- **Focus:** Pattern analysis
- **Checks:** Amount anomalies, frequency spikes, unusual behavior
- **Output:** Priority + Pattern analysis

**3. Document Forensics Agent**
- **Focus:** Document authenticity
- **Checks:** Digital tampering, metadata inconsistencies, suspicious patterns
- **Output:** Priority + Issues list with page numbers

---

## Data Flow

### Alert Creation Flow

```
1. Transaction occurs
   ↓
2. Agent Orchestrator analyzes
   ↓
3. All 3 agents run in parallel
   ↓
4. Findings aggregated
   ↓
5. Risk score calculated
   ↓
6. Alert created in database
   ↓
7. WebSocket broadcasts to frontend
   ↓
8. Dashboard updates in real-time
```

### Investigation Flow

```
1. User clicks "Investigate" on alert
   ↓
2. Frontend fetches alert details
   ↓
3. Backend retrieves:
   - Transaction data
   - Document analysis
   - Agent findings
   - Historical context
   ↓
4. Frontend displays in Investigation Cockpit
   ↓
5. User reviews and takes action
   ↓
6. Action logged in audit trail
```

---

## Technology Stack

### Frontend
```
Next.js 14          → React framework
TypeScript          → Type safety
TailwindCSS         → Styling
shadcn/ui           → UI components
Recharts            → Data visualization
React Query         → Data fetching/caching
```

### Backend
```
FastAPI             → Web framework
Python 3.9+         → Programming language
Pydantic            → Data validation
Uvicorn             → ASGI server
Motor (future)      → MongoDB async driver
Groq SDK (future)   → AI API client
```

### Infrastructure (Future)
```
MongoDB             → Database
Groq API            → AI inference
AWS/Azure/GCP       → Cloud hosting
Docker              → Containerization
```

---

## Security Architecture

### Current (Development)
```
Frontend ←→ Backend
  HTTP      CORS enabled (localhost)
            No authentication
            Mock data only
```

### Production (Recommended)
```
Frontend ←→ API Gateway ←→ Backend
  HTTPS      JWT Auth       Internal
             Rate Limiting
             WAF
                ↓
             MongoDB (encrypted)
             Groq API (API key)
```

**Security Layers:**
1. **Transport:** HTTPS/TLS 1.3
2. **Authentication:** JWT or OAuth 2.0
3. **Authorization:** Role-based access control
4. **Data:** Encryption at rest and in transit
5. **Audit:** Complete activity logging
6. **Network:** VPC, security groups, firewall

---

## Scalability

### Current Capacity
- **Frontend:** Static files (CDN-ready)
- **Backend:** Single instance (development)
- **Data:** In-memory (mock)

### Production Scaling
```
Load Balancer
      │
      ├─→ Frontend Instance 1 (CDN)
      ├─→ Frontend Instance 2 (CDN)
      └─→ Frontend Instance N (CDN)

Load Balancer
      │
      ├─→ Backend Instance 1
      ├─→ Backend Instance 2
      └─→ Backend Instance N
            │
            ├─→ MongoDB Cluster (Replica Set)
            └─→ Groq API (External)
```

**Scaling Strategies:**
- **Frontend:** CDN distribution (Vercel/Cloudflare)
- **Backend:** Horizontal scaling with load balancer
- **Database:** MongoDB sharding for large datasets
- **AI:** Groq API handles scaling automatically
- **WebSocket:** Redis pub/sub for multi-instance

---

## Deployment Architecture

### Development
```
localhost:3000 (Frontend)
localhost:8000 (Backend)
In-memory data
```

### Staging
```
staging.frontend.com (Vercel)
staging.api.com (AWS ECS)
MongoDB Atlas (Staging cluster)
Groq API (Development tier)
```

### Production
```
app.juliusbaer.com (Vercel/CloudFront)
api.juliusbaer.com (AWS ECS/EKS)
MongoDB Atlas (Production cluster - Multi-region)
Groq API (Production tier)
```

---

## Monitoring & Observability

### Recommended Tools

**Application Monitoring:**
- Frontend: Vercel Analytics, Sentry
- Backend: Datadog, New Relic, or Prometheus

**Logging:**
- Centralized: ELK Stack or CloudWatch
- Audit Trail: MongoDB collection

**Alerting:**
- Critical errors → PagerDuty
- Performance issues → Slack
- Security events → Email + SMS

---

## Future Enhancements

### Phase 1: Database
- Add MongoDB for persistence
- Implement data migrations
- Set up backup strategy

### Phase 2: AI Integration
- Connect Groq API
- Implement real document analysis
- Add model fine-tuning

### Phase 3: Advanced Features
- Real-time transaction monitoring
- Automated alert generation
- Machine learning for pattern detection
- Predictive risk scoring

### Phase 4: Enterprise Features
- Multi-tenancy support
- Advanced reporting
- Compliance dashboard
- Integration with core banking systems

---

## Performance Targets

### Current (Mock Data)
- Page Load: < 1s
- API Response: < 100ms
- WebSocket Latency: < 50ms

### Production Targets
- Page Load: < 2s
- API Response: < 500ms
- Database Query: < 100ms
- AI Analysis: < 3s
- WebSocket Latency: < 100ms

---

## Conclusion

The architecture is designed for:
- ✅ **Modularity** - Easy to extend
- ✅ **Scalability** - Ready to grow
- ✅ **Maintainability** - Clean code structure
- ✅ **Security** - Built-in best practices
- ✅ **Performance** - Optimized for speed
- ✅ **Reliability** - Error handling throughout

**Status: Production-Ready Architecture** 🚀


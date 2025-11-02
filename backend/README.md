# Speed-Run Backend
## AML Compliance Platform - Backend Services

**Status:** Phase 1 Database Infrastructure Complete ✅
**Tech Stack:** FastAPI, PostgreSQL, Redis, SQLAlchemy, Docling
**Current Progress:** 6% (Database layer complete, Redis & Logging pending)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (via Docker)
- Redis 7+ (via Docker)

### 1. Start Infrastructure

```bash
cd /Users/issacj/Desktop/hackathons/Singhacks/Speed-Run/backend

# Start PostgreSQL + Redis
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

**Services Started:**
- **PostgreSQL:** localhost:5432 (user: speedrun, password: speedrun, db: speedrun_aml)
- **Redis:** localhost:6379
- **pgAdmin (optional):** localhost:5050 (admin@speedrun.com / admin)

### 2. Install Python Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt

# Install additional dependencies for Phase 1
pip install alembic redis[hiredis] structlog python-json-logger
```

### 3. Run Backend Server

```bash
# Using uv
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or using python
python -m backend.main
```

**API Available At:**
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📁 Project Structure

```
backend/
├── database/                    # ✅ Database layer (NEW - Phase 1)
│   ├── models.py               # 10 SQLAlchemy ORM models (650 lines)
│   ├── connection.py           # Async connection pooling (150 lines)
│   ├── session.py              # Session management (110 lines)
│   ├── schema.sql              # Raw SQL schema (345 lines)
│   └── __init__.py
│
├── cache/                       # ⏸️ Redis cache layer (TODO - Phase 1)
│   ├── redis_client.py
│   ├── cache_decorator.py
│   └── cache_keys.py
│
├── logging/                     # ⏸️ Structured logging (TODO - Phase 1)
│   ├── config.py
│   ├── audit_logger.py
│   └── formatters.py
│
├── src/backend/
│   ├── adapters/                # ⏸️ 3rd party service adapters (TODO - Phase 2)
│   │   ├── document_parser/    # Docling adapter
│   │   ├── nlp/                # spaCy adapter
│   │   └── image/              # PIL adapter
│   │
│   ├── routers/                 # API endpoints
│   │   ├── ocr.py              # ✅ OCR endpoints
│   │   ├── document_parser.py  # ✅ Document parsing endpoints
│   │   ├── corroboration.py    # ✅ Document corroboration
│   │   └── alerts.py           # ⏸️ Alert management (TODO - Phase 5)
│   │
│   ├── services/                # Business logic
│   │   ├── ocr_service.py              # ✅ OCR (106 lines)
│   │   ├── document_service.py         # ✅ Document parsing (170 lines)
│   │   ├── document_validator.py       # ✅ Validation (301 lines)
│   │   ├── image_analyzer.py           # ✅ Image forensics (462 lines)
│   │   ├── risk_scorer.py              # ✅ Risk scoring (453 lines)
│   │   ├── report_generator.py         # ✅ Reporting (331 lines)
│   │   └── corroboration_service.py    # ✅ Orchestrator (230 lines)
│   │
│   ├── schemas/                 # Pydantic models
│   │   ├── ocr.py
│   │   ├── document.py
│   │   └── validation.py
│   │
│   ├── config.py                # ✅ Configuration (UPDATED with DB & Redis)
│   └── main.py                  # FastAPI app
│
├── docker-compose.yml           # ✅ Infrastructure setup (NEW)
├── requirements.txt
└── README.md                    # This file
```

**Legend:** ✅ Complete | ⏸️ Pending | 🔄 In Progress

---

## 🗄️ Database Models (10 Tables - Complete ✅)

### Core Entities

1. **clients** - Client profiles and KYC information
   - Risk rating, KYC status, PEP/sanctions flags
   - Relationship manager assignment

2. **documents** - Document metadata and storage
   - File references, processing status
   - OCR/parsing results, client relationship

3. **document_validations** - Validation results
   - Format validation (spacing, fonts, spelling)
   - Structure validation (templates, sections)
   - Content validation (PII, quality)

4. **images** - Image forensic analysis
   - AI-generated detection, tampering detection
   - EXIF metadata, forensic analysis
   - Risk scoring per image

5. **risk_scores** - Risk calculations
   - Weighted component scoring
   - Risk level classification (LOW/MEDIUM/HIGH/CRITICAL)
   - Contributing factors and recommendations

### Compliance & Workflow

6. **alerts** - Compliance alerts
   - Alert type, severity, lifecycle status
   - SLA management, resolution tracking
   - Links to clients, documents, transactions

7. **alert_recipients** - Alert routing
   - User assignment, role-based routing
   - Notification and acknowledgment tracking

8. **transactions** - AML Monitoring (Part 1 placeholder)
   - Transaction details, screening flags
   - Counterparty info, SWIFT data

9. **audit_logs** - Immutable compliance log
   - All system activities, user actions
   - State changes, IP tracking, event correlation

10. **reports** - Generated reports
    - Report metadata, content (JSONB)
    - Export paths (PDF, Markdown, JSON)

**Features:**
- 20+ indexes for performance
- Connection pooling (20 connections, 10 overflow)
- JSONB columns for flexibility
- Timestamp tracking, audit trails

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://speedrun:speedrun@localhost:5432/speedrun_aml
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_ECHO=False  # Set to True for SQL query logging

# Redis Cache
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
CACHE_ENABLED=True
CACHE_DEFAULT_TTL=3600  # 1 hour

# Cache TTLs (seconds)
CACHE_TTL_DOCUMENT_PARSING=86400    # 24 hours
CACHE_TTL_OCR=172800                # 48 hours
CACHE_TTL_IMAGE_ANALYSIS=86400      # 24 hours
CACHE_TTL_VALIDATION=43200          # 12 hours

# Application
APP_NAME=Speed-Run AML Platform
VERSION=1.0.0
MAX_FILE_SIZE=10485760  # 10MB

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
LOG_FILE=  # Optional: Set to file path for persistent logging (e.g., /var/log/speedrun.log)

# Testing
TESTING=False  # Set to True when running tests to use test database

# External APIs (optional - for image reverse search)
GOOGLE_VISION_API_KEY=your-key-here
TINEYE_API_KEY=your-key-here
TINEYE_API_SECRET=your-secret-here
```

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f postgres
docker-compose logs -f redis

# Restart specific service
docker-compose restart postgres

# Rebuild containers
docker-compose up -d --build

# Remove volumes (clean slate - deletes data!)
docker-compose down -v

# Start with admin tools (pgAdmin, Redis Commander)
docker-compose --profile tools up -d
```

---

## 💾 Database Management

### Access PostgreSQL

```bash
# Method 1: Via Docker
docker exec -it speedrun-postgres psql -U speedrun -d speedrun_aml

# Method 2: Local psql
psql -U speedrun -d speedrun_aml -h localhost

# Common commands inside psql:
\dt                         # List all tables
\d clients                  # Describe clients table
\d+ documents               # Detailed table description
SELECT * FROM clients LIMIT 5;
\q                          # Quit
```

### Use pgAdmin (GUI)

```bash
# Start pgAdmin
docker-compose --profile tools up -d pgadmin

# Access in browser
open http://localhost:5050

# Login credentials
# Email: admin@speedrun.com
# Password: admin

# Add server in pgAdmin:
# Host: host.docker.internal (Mac) or postgres (Linux)
# Port: 5432
# Username: speedrun
# Password: speedrun
# Database: speedrun_aml
```

### Database Migrations with Alembic

```bash
# 1. Initialize Alembic (only once)
alembic init alembic

# 2. Edit alembic.ini - set:
# sqlalchemy.url = postgresql+asyncpg://speedrun:speedrun@localhost:5432/speedrun_aml

# 3. Edit alembic/env.py - import models:
# from database.models import Base
# target_metadata = Base.metadata

# 4. Create initial migration
alembic revision --autogenerate -m "Initial schema"

# 5. Apply migrations
alembic upgrade head

# 6. Check current version
alembic current

# 7. Rollback one version
alembic downgrade -1

# 8. Show migration history
alembic history
```

---

## 📡 API Endpoints

### Current Endpoints (✅ Working)

#### OCR
```http
POST   /api/v1/ocr/extract              # Extract text from image
GET    /api/v1/ocr/health               # Health check
```

#### Document Parsing
```http
POST   /api/v1/documents/parse          # Parse document (PDF, DOCX)
POST   /api/v1/documents/extract-tables # Extract tables from document
GET    /api/v1/documents/health         # Health check
```

#### Document Corroboration (Part 2 - Complete)
```http
POST   /api/v1/corroboration/analyze              # Full document analysis
POST   /api/v1/corroboration/analyze-image        # Image-only analysis
POST   /api/v1/corroboration/validate-format     # Quick format check
POST   /api/v1/corroboration/validate-structure  # Quick structure check
GET    /api/v1/corroboration/report/{id}         # Get report by ID
GET    /api/v1/corroboration/report/{id}/markdown # Export report as Markdown
GET    /api/v1/corroboration/reports             # List all reports
GET    /api/v1/corroboration/health              # Health check
```

### New Endpoints (⏸️ TODO - Phase 5)

#### Alert Management (Part 3 Integration)
```http
GET    /api/v1/alerts/summary           # Dashboard statistics
GET    /api/v1/alerts/active            # List active alerts
GET    /api/v1/alerts/{id}              # Alert details
POST   /api/v1/alerts/{id}/remediate    # Take remediation action
GET    /api/v1/alerts/{id}/audit-trail  # Get audit log for alert
POST   /api/v1/documents/upload         # Upload document with client_id
GET    /api/v1/clients/{id}/risk-overview # Complete client risk view
```

---

## 🧪 Development

### Run Tests

```bash
# Install pytest
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_document_service.py

# Run specific test
pytest tests/test_document_service.py::test_parse_pdf
```

### Code Quality

```bash
# Format code (Ruff)
ruff format .

# Lint code
ruff check .

# Fix auto-fixable issues
ruff check . --fix

# Type checking (MyPy)
mypy backend
```

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# 1. Check if PostgreSQL is running
docker-compose ps postgres
# Should show: Up

# 2. Check PostgreSQL logs
docker-compose logs postgres | tail -50

# 3. Test connection
docker exec -it speedrun-postgres psql -U speedrun -d speedrun_aml -c "SELECT 1"
# Should return: 1

# 4. Check port availability
lsof -i :5432
# Should show docker-proxy

# 5. Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### Redis Connection Issues

```bash
# 1. Check if Redis is running
docker-compose ps redis
# Should show: Up

# 2. Test Redis connection
docker exec -it speedrun-redis redis-cli ping
# Should return: PONG

# 3. Check Redis data
docker exec -it speedrun-redis redis-cli
> KEYS *
> INFO
> EXIT
```

### Port Already in Use

```bash
# Find and kill process using port
lsof -i :5432   # PostgreSQL
lsof -i :6379   # Redis
lsof -i :8000   # FastAPI

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Container Issues

```bash
# Remove all containers and start fresh
docker-compose down
docker-compose rm -f
docker volume prune
docker-compose up -d --build
```

---

## 📚 Documentation

### Main Documents

| Document | Purpose | Status |
|----------|---------|--------|
| `README.md` | Quick start & reference (this file) | ✅ |
| `REFACTORING_SUMMARY.md` | What's complete & next steps | ✅ |
| `REFACTORING_IMPLEMENTATION_GUIDE.md` | Detailed code examples for continuing | ✅ |
| `REFACTORING_PROGRESS.md` | Living memory tracker | 🔄 Updated |
| `database/schema.sql` | Raw SQL schema | ✅ |

### Requirement Documents

| Document | Purpose | Status |
|----------|---------|--------|
| `PART_1_REAL_TIME_AML_MONITORING.md` | Part 1 detailed specs | ✅ |
| `PART_2_DOCUMENT_IMAGE_CORROBORATION.md` | Part 2 detailed specs | ✅ |
| `PART_3_INTEGRATION_UNIFIED_PLATFORM.md` | Integration architecture | ✅ |
| `COMPLETION_STATUS_TRACKER.md` | Current implementation status | ✅ |

---

## ⏭️ Next Steps

### Phase 1 Remaining (67% pending)

**Task 1.2: Redis Cache Layer** (4-6 hours)
- [ ] Create `cache/redis_client.py`
- [ ] Create `cache/cache_decorator.py`
- [ ] Create `cache/cache_keys.py`
- [ ] Apply @cached decorator to expensive operations

**Task 1.3: Logging & Audit Trail** (4-6 hours)
- [ ] Create `logging/config.py` with structlog
- [ ] Create `logging/audit_logger.py` for compliance
- [ ] Create `middleware/logging_middleware.py` for requests
- [ ] Update main.py to use logging

**See:** `REFACTORING_IMPLEMENTATION_GUIDE.md` for complete code examples

### Phase 2: Adapter Pattern (Week 2)
- [ ] Create adapters for Docling, spaCy, PIL
- [ ] Implement dependency injection container
- [ ] Refactor services to use adapters

### Phase 3-6: Service Refactoring, Performance, APIs, Testing

**See:** `REFACTORING_SUMMARY.md` for complete roadmap

---

## 🤝 Contributing

### Before Making Changes

1. Read `REFACTORING_SUMMARY.md` for context
2. Update `REFACTORING_PROGRESS.md` with your plans
3. Follow SOLID principles
4. Write tests for new code
5. Update documentation

### Code Style

- Follow PEP 8
- Use type hints everywhere
- Write comprehensive docstrings
- Add comments for complex logic
- Keep functions small and focused

---

## 📊 Current Status

**Phase 1: Infrastructure Setup**
- ✅ Database layer complete (33%)
- ⏸️ Redis cache pending (33%)
- ⏸️ Logging system pending (33%)

**Overall Progress:** 6% (Phase 1: 33% complete)

**Next Task:** Implement Redis cache layer

**Timeline:** 6 weeks to complete all refactoring phases

---

**Created:** 2025-01-15
**Last Updated:** 2025-01-15
**Status:** Phase 1 Database Complete, Redis & Logging Pending
**Maintainer:** Speed-Run Team

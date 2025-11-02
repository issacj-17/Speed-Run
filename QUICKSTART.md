# Speed-Run - Quickstart Guide

**Get up and running in 5 minutes!**

---

## For Judges & Evaluators 👨‍⚖️

### Fastest Way to See the Demo

```bash
# 1. Clone repository
git clone <repository-url>
cd Speed-Run

# 2. Start with Docker (one command!)
docker-compose up -d

# 3. Wait 60 seconds, then open browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

**That's it!** The application is now running with sample data.

### What to Explore

1. **Compliance Dashboard** (http://localhost:3000/compliance)
   - See active alerts with risk scores
   - Drag-and-drop Kanban board
   - Real-time KPIs

2. **API Documentation** (http://localhost:8000/docs)
   - Interactive Swagger UI
   - Try the `/api/v1/documents/analyze` endpoint
   - Upload the sample document from `/sample_data/`

3. **Test Document Upload**
   - Upload: `Swiss_Home_Purchase_Agreement_Scanned_Noise_forparticipants.pdf`
   - Watch AI-powered fraud detection in action
   - See risk score calculation (should be HIGH RISK ~78/100)

---

## For Users 👤

### System Requirements

- Docker Desktop OR
- Python 3.11+ and Node.js 18+

### Installation

#### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd Speed-Run

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs if needed
docker-compose logs -f backend
```

**Access the app**:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

#### Option 2: Local Development

```bash
# Clone repository
git clone <repository-url>
cd Speed-Run

# Backend setup
cd backend
cp .env.example .env
# Edit .env if needed

# Install dependencies (using uv - fast!)
uv sync
# OR with pip:
# pip install -r requirements.txt

# Start backend server
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal - Frontend setup
cd ../frontend
cp .env.example .env.local
# Edit .env.local if needed

# Install dependencies
npm install

# Start frontend server
npm run dev
```

**Access the app**:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

### First Steps

1. **Navigate to Role Selector**
   - Open http://localhost:3000
   - Choose "Compliance Officer" or "Relationship Manager"

2. **Upload a Document**
   - Go to Compliance Dashboard
   - Click "Upload Document" or use Investigation page
   - Select a PDF, DOCX, or image file
   - Wait 5-10 seconds for analysis

3. **Review Results**
   - See risk score (0-100)
   - View fraud detection results
   - Check validation issues
   - Read recommendations

4. **Manage Alerts**
   - View alerts in Kanban board
   - Drag cards to update status
   - Click alerts for detailed investigation

---

## For New Developers 👨‍💻

### Development Setup

#### 1. Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version

# Check Node version (need 18+)
node --version

# Check Docker
docker --version

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. Clone and Setup

```bash
# Clone
git clone <repository-url>
cd Speed-Run

# Backend
cd backend
cp .env.example .env

# Install dependencies
uv sync

# Run tests to verify setup
uv run pytest
# Should see: 369 tests passed

# Frontend
cd ../frontend
cp .env.example .env.local

# Install dependencies
npm install

# Run tests to verify setup
npm test
# Should see: 17 tests passed
```

#### 3. Environment Configuration

**Backend** (`backend/.env`):
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/speedrun
REDIS_URL=redis://localhost:6379/0

# Features
ENABLE_AI_DETECTION=true
ENABLE_TAMPERING_DETECTION=true
ENABLE_REVERSE_IMAGE_SEARCH=false

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

**Frontend** (`frontend/.env.local`):
```bash
# API Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_USE_BACKEND_API=true

# Features
NEXT_PUBLIC_ENABLE_DOCUMENT_UPLOAD=true
NEXT_PUBLIC_ENABLE_AI_DETECTION=true

# Debug
NEXT_PUBLIC_DEBUG=false
```

#### 4. Start Development Servers

```bash
# Terminal 1 - Backend
cd backend
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Watch Tests (optional)
cd backend
uv run pytest-watch
```

#### 5. Verify Setup

```bash
# Test backend
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Test frontend
curl http://localhost:3000
# Should return HTML

# Run all tests
cd backend && uv run pytest && cd ../frontend && npm test
```

#### 6. Your First Contribution

See detailed guide in [CONTRIBUTING.md](./CONTRIBUTING.md)

Quick checklist:
- [ ] Create feature branch
- [ ] Write tests first (TDD)
- [ ] Implement feature
- [ ] Ensure tests pass
- [ ] Update documentation
- [ ] Create pull request

---

## Common Tasks

### Running Tests

```bash
# Backend - All tests
cd backend
uv run pytest

# Backend - Specific test file
uv run pytest tests/unit/services/test_document_service.py

# Backend - With coverage
uv run pytest --cov=backend --cov-report=html

# Frontend - All tests
cd frontend
npm test

# Frontend - Watch mode
npm run test

# Frontend - Coverage
npm run test:coverage
```

### Database Operations

```bash
# Start database with Docker
docker-compose up -d postgres

# Connect to database
docker exec -it speedrun-postgres psql -U speedrun

# Run migrations (if implemented)
cd backend
uv run alembic upgrade head

# Reset database
docker-compose down -v
docker-compose up -d
```

### Viewing Logs

```bash
# Backend logs (Docker)
docker-compose logs -f backend

# Frontend logs (Docker)
docker-compose logs -f frontend

# All services logs
docker-compose logs -f

# Local development logs
# Backend: Check console output
# Frontend: Check browser console
```

### Code Quality Checks

```bash
# Backend - Format code
cd backend
uv run ruff format .

# Backend - Lint code
uv run ruff check .

# Frontend - Format code
cd frontend
npm run format

# Frontend - Lint code
npm run lint
```

---

## Troubleshooting

### Issue: Backend won't start

**Symptom**: `Address already in use` error

**Solution**:
```bash
# Find process on port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Restart backend
cd backend
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue: Frontend won't start

**Symptom**: `Port 3000 is already in use`

**Solution**:
```bash
# Find and kill process
kill -9 $(lsof -ti:3000)

# Restart frontend
cd frontend
npm run dev
```

### Issue: Database connection error

**Symptom**: `Could not connect to database`

**Solution**:
```bash
# Verify database is running
docker-compose ps

# Restart database
docker-compose restart postgres

# Check database logs
docker-compose logs postgres

# Verify connection string in .env
cat backend/.env | grep DATABASE_URL
```

### Issue: Tests failing

**Symptom**: `ImportError` or `ModuleNotFoundError`

**Solution**:
```bash
# Backend - Reinstall dependencies
cd backend
rm -rf .venv
uv sync

# Frontend - Reinstall dependencies
cd frontend
rm -rf node_modules
npm install

# Clear caches
# Backend:
uv cache clean

# Frontend:
npm cache clean --force
```

### Issue: CORS errors in browser

**Symptom**: API calls blocked by CORS policy

**Solution**:
```bash
# Check backend CORS configuration
# File: backend/src/backend/config.py

# Verify ALLOWED_ORIGINS includes frontend URL
# Should include: http://localhost:3000

# Restart backend after changes
```

### Issue: Docker services not starting

**Symptom**: `docker-compose up` fails

**Solution**:
```bash
# Check Docker is running
docker ps

# Remove old containers
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Start services
docker-compose up -d

# Check logs for errors
docker-compose logs
```

---

## Quick Reference

### Important URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend App | http://localhost:3000 | Main application |
| Backend API | http://localhost:8000 | REST API |
| API Documentation | http://localhost:8000/docs | Swagger UI |
| API Alternative Docs | http://localhost:8000/redoc | ReDoc UI |
| Database | localhost:5432 | PostgreSQL |
| Redis | localhost:6379 | Redis cache |

### Key Commands

```bash
# Start everything (Docker)
docker-compose up -d

# Stop everything (Docker)
docker-compose down

# View logs
docker-compose logs -f [service]

# Run backend tests
cd backend && uv run pytest

# Run frontend tests
cd frontend && npm test

# Format code
cd backend && uv run ruff format .
cd frontend && npm run format

# Build for production
docker-compose -f docker-compose.prod.yml build
```

### File Structure Quick Reference

```
Speed-Run/
├── backend/              # Backend API (FastAPI)
│   ├── src/backend/     # Main source code
│   ├── tests/           # Test suite (369 tests)
│   └── docs/            # Backend documentation
├── frontend/            # Frontend app (Next.js)
│   ├── app/            # Pages (App Router)
│   ├── components/     # React components
│   ├── lib/            # Utilities & hooks
│   └── __tests__/      # Test suite (17 tests)
├── docs/               # Project documentation
│   ├── requirements/   # Requirements & challenge docs
│   ├── architecture/   # Architecture documentation
│   ├── progress/       # Implementation progress
│   ├── testing/        # Testing documentation
│   ├── frontend/       # Frontend-specific docs
│   ├── guides/         # User guides
│   └── sessions/       # Session summaries
├── sample_data/        # Test documents
├── docker-compose.yml  # Docker configuration
├── README.md          # Main README
├── QUICKSTART.md      # This file
├── CONTRIBUTING.md    # Contribution guidelines
└── PRESENTATION_OUTLINE.md  # Pitch deck guide
```

---

## What to Do Next

### For Judges
✅ Watch the [demo video](./demo_video/)
✅ Try uploading a document
✅ Review the [architecture documentation](./docs/architecture/)
✅ Check the [test results](./docs/testing/)

### For Users
✅ Complete the [user tutorial](./docs/guides/)
✅ Explore all dashboard features
✅ Try different document types
✅ Review generated reports

### For Developers
✅ Read [CONTRIBUTING.md](./CONTRIBUTING.md)
✅ Set up your development environment
✅ Run the test suites
✅ Pick a [good first issue](https://github.com/.../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
✅ Join the dev Slack channel

---

## Getting Help

### Resources
- **Documentation**: Browse `/docs` directory
- **API Reference**: http://localhost:8000/docs
- **Contributing Guide**: [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Demo Guide**: [DEMO_SETUP_AND_EXECUTION.md](./DEMO_SETUP_AND_EXECUTION.md)

### Support Channels
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions, share ideas
- **Slack**: #speed-run (if available)
- **Email**: support@speed-run.com (if available)

---

## Success Checklist

### Initial Setup
- [ ] Repository cloned
- [ ] Docker running (or Python/Node installed)
- [ ] Services started successfully
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend accessible at http://localhost:8000

### Verification
- [ ] Backend health check passes
- [ ] Frontend loads without errors
- [ ] Can navigate between dashboards
- [ ] Can upload a test document
- [ ] Document analysis completes successfully
- [ ] Risk score displayed correctly

### Development Ready
- [ ] Backend tests pass (369/369)
- [ ] Frontend tests pass (17/17)
- [ ] Environment variables configured
- [ ] Database connected
- [ ] Hot reload working

---

**🎉 Congratulations!** You're all set up and ready to use Speed-Run!

For detailed information about features and architecture, see the full [README.md](./README.md) and [documentation](/docs/).

---

**Document Version**: 1.0
**Last Updated**: November 2, 2025
**Estimated Setup Time**: 5-15 minutes

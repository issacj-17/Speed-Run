# Quick Start Guide
## Speed-Run: Get Up and Running in 10 Minutes

**Last Updated:** November 1, 2025

---

## 🚀 Prerequisites

- **Python 3.11+** (Backend)
- **Node.js 18+** (Frontend)
- **uv** or **pip** (Python package manager)
- **npm** (Node package manager)

---

## ⚡ Quick Setup (10 Minutes)

### Step 1: Clone and Navigate (1 min)

```bash
cd /path/to/Singhacks/Speed-Run
```

### Step 2: Backend Setup (4 mins)

```bash
# Navigate to backend
cd backend

# Install dependencies (using uv - recommended)
uv sync

# OR using pip
pip install -r requirements.txt

# Download spaCy model (required for NLP)
python -m spacy download en_core_web_sm
```

### Step 3: Start Backend (1 min)

```bash
# Using uv
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# OR using Python directly
python -m backend.main

# Backend will be available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Step 4: Frontend Setup (3 mins)

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Step 5: Start Frontend (1 min)

```bash
# Start development server
npm run dev

# Frontend will be available at: http://localhost:3000
```

---

## ✅ Verify Installation

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

### Test Frontend

1. Open browser: http://localhost:3000
2. You should see the dashboard
3. Upload a test document

---

## 🧪 Quick API Test

### Test Document Analysis

```bash
# Create a test file
echo "Invoice\nDate: 2024-11-01\nAmount: $1000\nTotal: $1000" > test_invoice.txt

# Analyze it
curl -X POST "http://localhost:8000/api/v1/corroboration/analyze" \
  -F "file=@test_invoice.txt" \
  -F "expected_document_type=invoice"
```

**Expected Response:**
```json
{
  "document_id": "...",
  "risk_score": {
    "overall_score": 25.5,
    "risk_level": "low"
  },
  "requires_manual_review": false
}
```

---

## 📚 Documentation Quick Links

| Document | Purpose | Location |
|----------|---------|----------|
| **Full Documentation Index** | Complete overview | `DOCUMENTATION_INDEX.md` |
| **Product Requirements** | Features & requirements | `PRODUCT_REQUIREMENTS_DOCUMENT.md` |
| **Technical Architecture** | System design & diagrams | `TECHNICAL_ARCHITECTURE_DOCUMENT.md` |
| **API Integration** | Frontend-backend integration | `API_INTEGRATION_GUIDE.md` |
| **Test Cases** | Testing guide | `TEST_PLAN_AND_CASES.md` |
| **Backend Setup** | Detailed backend setup | `backend/SETUP_GUIDE.md` |
| **Implementation Docs** | Development progress | `backend/IMPLEMENTATION_PROGRESS.md` |

---

## 🔧 Common Issues & Solutions

### Issue: spaCy model not found

```bash
# Solution: Download the model
python -m spacy download en_core_web_sm
```

### Issue: Port already in use

```bash
# Backend (8000)
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Frontend (3000)
lsof -ti:3000 | xargs kill -9
```

### Issue: CORS errors

**Solution:** Check backend `config.py`:
```python
ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
```

### Issue: File upload fails

**Check:**
1. File size < 10MB
2. File type is supported (.pdf, .docx, .png, .jpg, etc.)
3. Backend is running

---

## 🎯 Next Steps

### 1. Explore the API

Visit: http://localhost:8000/docs

Interactive Swagger UI with:
- All endpoints documented
- Try-it-out functionality
- Request/response schemas

### 2. Test Document Corroboration

```bash
# Format validation
curl -X POST "http://localhost:8000/api/v1/corroboration/validate-format" \
  -F "file=@your_document.pdf"

# Full analysis
curl -X POST "http://localhost:8000/api/v1/corroboration/analyze" \
  -F "file=@your_document.pdf" \
  -F "expected_document_type=invoice"

# List reports
curl "http://localhost:8000/api/v1/corroboration/reports?limit=10"
```

### 3. Review Documentation

1. **PRD** - Understand features and requirements
2. **Architecture** - Learn system design
3. **Integration Guide** - Implement frontend integration
4. **Test Plan** - Set up testing

---

## 📖 Key Concepts

### Document Corroboration

The system analyzes documents for fraud through:

1. **Format Validation** (15% weight)
   - Spelling errors
   - Spacing issues
   - Font inconsistencies

2. **Structure Validation** (25% weight)
   - Missing sections
   - Template matching
   - Document completeness

3. **Content Validation** (20% weight)
   - PII detection
   - Quality scoring
   - Readability

4. **Image Analysis** (40% weight)
   - AI-generated detection
   - Tampering detection (ELA)
   - EXIF metadata analysis

### Risk Scoring

- **0-25:** LOW - Accept document
- **25-50:** MEDIUM - Review minor issues
- **50-75:** HIGH - Manual review required
- **75-100:** CRITICAL - Reject, likely fraud

---

## 🧰 Development Tools

### Backend

```bash
# Run tests
pytest tests/ -v

# Check coverage
pytest --cov=backend --cov-report=html

# Format code
ruff format .

# Lint code
ruff check .
```

### Frontend

```bash
# Run tests
npm test

# Build for production
npm run build

# Start production server
npm start
```

---

## 📊 API Endpoint Summary

### Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/api/v1/corroboration/analyze` | Full document analysis |
| POST | `/api/v1/corroboration/analyze-image` | Image analysis only |
| GET | `/api/v1/corroboration/reports` | List reports |
| GET | `/api/v1/corroboration/report/{id}` | Get specific report |

### All Endpoints

See: `TECHNICAL_ARCHITECTURE_DOCUMENT.md` - Section 6 (API Specifications)

---

## 💡 Tips & Best Practices

### Performance

- Backend processes documents in ~2-5 seconds
- Use async/await patterns in frontend
- Enable caching for repeated requests

### Testing

- Always test with sample documents first
- Check audit logs: `/tmp/corroboration_audit/`
- Monitor processing times

### Integration

- Frontend connects via `lib/api.ts`
- Update `NEXT_PUBLIC_API_URL` for production
- Handle errors gracefully

---

## 🆘 Getting Help

### Documentation

1. Check `DOCUMENTATION_INDEX.md` for all documents
2. Review `TECHNICAL_ARCHITECTURE_DOCUMENT.md` for system design
3. See `TEST_PLAN_AND_CASES.md` for testing

### Troubleshooting

1. Check backend logs
2. Verify environment variables
3. Ensure all dependencies installed
4. Review audit logs for errors

### Support

- Issues: Create GitHub issue
- Questions: Review documentation
- Bugs: Include logs and steps to reproduce

---

## ✨ Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Health check passes
- [ ] Test document analysis works
- [ ] Swagger docs accessible
- [ ] Frontend loads dashboard
- [ ] Can upload and analyze documents
- [ ] Reports are generated
- [ ] Audit logs being created

---

## 🎉 You're Ready!

Your Speed-Run platform is now running. Here's what you can do:

1. **Upload Documents:** Test the corroboration system
2. **Review Reports:** Check the audit trail
3. **Explore API:** Use Swagger docs
4. **Read Documentation:** Understand the system
5. **Run Tests:** Validate functionality
6. **Develop Features:** Extend the platform

---

**Need More Details?**

→ See `DOCUMENTATION_INDEX.md` for complete documentation catalog

**Happy Coding!** 🚀

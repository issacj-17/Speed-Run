# Setup Guide - FastAPI Document Corroboration Backend

## Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
cd backend
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Download spaCy Model (Required for NLP)

```bash
python -m spacy download en_core_web_sm
```

### 3. Create .env File (Optional)

Create a `.env` file in the `backend/` directory:

```bash
# Application Settings
APP_NAME="OCR & Document Corroboration API"
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Corroboration Settings
AUDIT_LOG_PATH="/tmp/corroboration_audit"
ENABLE_REVERSE_IMAGE_SEARCH=false
ENABLE_ADVANCED_FORENSICS=true

# Risk Thresholds
RISK_THRESHOLD_LOW=25.0
RISK_THRESHOLD_MEDIUM=50.0
RISK_THRESHOLD_HIGH=75.0

# External API Keys (Optional - see IMPLEMENTATION_PROGRESS.md for details)
# GOOGLE_VISION_API_KEY=your_key_here
# TINEYE_API_KEY=your_key_here
# BING_VISUAL_SEARCH_KEY=your_key_here
# HIVE_AI_API_TOKEN=your_token_here
```

### 4. Run the Application

```bash
# Using uv
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or directly with Python
python -m backend.main

# Or with uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the API

- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

---

## Testing the Corroboration System

### Test 1: Full Document Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/corroboration/analyze" \
  -F "file=@sample_invoice.pdf" \
  -F "expected_document_type=invoice" \
  -F "perform_format_validation=true" \
  -F "perform_structure_validation=true" \
  -F "perform_content_validation=true" \
  -F "perform_image_analysis=false"
```

### Test 2: Image Fraud Detection

```bash
curl -X POST "http://localhost:8000/api/v1/corroboration/analyze-image" \
  -F "file=@photo.jpg" \
  -F "enable_reverse_search=false"
```

### Test 3: Retrieve Report

```bash
# Get JSON report
curl "http://localhost:8000/api/v1/corroboration/report/{document_id}"

# Get markdown report
curl "http://localhost:8000/api/v1/corroboration/report/{document_id}/markdown"
```

### Test 4: List Reports

```bash
# List all reports
curl "http://localhost:8000/api/v1/corroboration/reports"

# Filter by risk level
curl "http://localhost:8000/api/v1/corroboration/reports?risk_level=high"

# Filter by manual review requirement
curl "http://localhost:8000/api/v1/corroboration/reports?requires_manual_review=true"
```

---

## Understanding Risk Scores

### Risk Levels

- **LOW (0-25)**: Document appears legitimate, proceed with standard processing
- **MEDIUM (25-50)**: Document has minor issues, consider requesting clarification
- **HIGH (50-75)**: Document requires thorough manual review
- **CRITICAL (75-100)**: Document has critical issues, likely fraud, reject immediately

### Risk Score Components

Risk scores are calculated from weighted components:
- **Format Validation (15%)**: Spelling, spacing, font consistency
- **Structure Validation (25%)**: Completeness, missing sections, template matching
- **Content Validation (20%)**: Quality, PII, readability
- **Image Analysis (40%)**: AI detection, tampering, authenticity

---

## Optional: External API Integration

See `IMPLEMENTATION_PROGRESS.md` for detailed instructions on:

1. **Reverse Image Search APIs**
   - Google Cloud Vision (Free tier: 1000/month)
   - TinEye API
   - Bing Visual Search (Free tier: 1000/month)

2. **AI-Generated Detection**
   - Hive AI
   - Hugging Face models (free, self-hosted)

3. **Image Forensics**
   - Sightengine (free tier available)
   - AWS Rekognition

---

## Troubleshooting

### Issue: spaCy model not found

```bash
# Solution: Download the model
python -m spacy download en_core_web_sm
```

### Issue: scipy import error

```bash
# Solution: Ensure scipy is installed
pip install scipy==1.11.4
```

### Issue: PIL/Pillow errors

```bash
# Solution: Reinstall Pillow
pip uninstall Pillow
pip install Pillow==10.4.0
```

### Issue: Docling installation fails

```bash
# Solution: Update pip and retry
pip install --upgrade pip
pip install docling==2.9.1
```

---

## Development Tips

### Running Tests (Coming Soon)

```bash
pytest tests/
```

### Code Formatting

```bash
# Format code
ruff format .

# Check linting
ruff check .
```

### Viewing Logs

Audit logs are stored in `/tmp/corroboration_audit/`:

```bash
# View today's audit log
cat /tmp/corroboration_audit/audit_log_$(date +%Y%m%d).jsonl

# View a specific report
cat /tmp/corroboration_audit/report_{document_id}.json
```

---

## Production Deployment

### Environment Variables

Set these environment variables in production:

```bash
export APP_NAME="Production Document Corroboration API"
export MAX_FILE_SIZE=52428800  # 50MB for production
export AUDIT_LOG_PATH="/var/log/corroboration"
export ENABLE_REVERSE_IMAGE_SEARCH=true
export GOOGLE_VISION_API_KEY="your_production_key"
```

### Docker Deployment (Coming Soon)

```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Considerations

1. **Rate Limiting**: Add rate limiting middleware
2. **Authentication**: Implement JWT or API key authentication
3. **File Size Limits**: Enforce strict file size limits
4. **Virus Scanning**: Add virus scanning for uploaded files
5. **Audit Logs**: Ensure audit logs are backed up regularly

---

## Support

For issues and questions:
- Check `IMPLEMENTATION_PROGRESS.md` for implementation details
- Check `README.md` for API documentation
- Review the OpenAPI docs at `/docs` when the server is running

#!/bin/bash

echo "=========================================="
echo "  Speed-Run AML Platform - Backend API"
echo "  Julius Baer Hackathon Submission"
echo "=========================================="
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit 1

# Check for sample data
echo "Checking for sample data..."
if [ ! -f "../sample_data/Swiss_Home_Purchase_Agreement_Scanned_Noise_forparticipants.pdf" ]; then
    echo "⚠️  WARNING: Sample PDF not found in sample_data/"
    echo "   Please add: Swiss_Home_Purchase_Agreement_Scanned_Noise_forparticipants.pdf"
fi

if [ ! -f "../sample_data/transactions_mock_1000_for_participants.csv" ]; then
    echo "⚠️  WARNING: Sample CSV not found in sample_data/"
    echo "   Please add: transactions_mock_1000_for_participants.csv"
fi
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: 'uv' package manager not found"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Or use pip: pip install -r requirements.txt"
    echo ""
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env created - please review and update if needed"
    else
        echo "⚠️  .env.example not found - using defaults"
    fi
    echo ""
fi

# Install dependencies if needed
if [ ! -f ".venv/bin/python" ] && [ ! -d "venv" ]; then
    echo "Installing dependencies with uv..."
    uv sync
    echo "✅ Dependencies installed"
    echo ""
fi

# Run tests to verify setup
echo "Running quick health check..."
if uv run pytest tests/unit/services/test_document_service.py -v --tb=no 2>/dev/null | head -10; then
    echo "✅ Tests passed"
else
    echo "⚠️  Some tests failed - check backend/docs/testing/ for help"
fi
echo ""

# Start the server
echo "🚀 Starting backend API server..."
echo ""
echo "📍 Endpoints:"
echo "   • API:          http://localhost:8000"
echo "   • API Docs:     http://localhost:8000/docs"
echo "   • ReDoc:        http://localhost:8000/redoc"
echo "   • Health Check: http://localhost:8000/health"
echo ""
echo "📚 Documentation:"
echo "   • Setup Guide:  backend/SETUP_GUIDE.md"
echo "   • API Guide:    docs/guides/API_INTEGRATION_GUIDE.md"
echo "   • Quick Start:  QUICKSTART.md"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Start server with proper path
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

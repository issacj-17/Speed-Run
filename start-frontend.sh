#!/bin/bash

echo "============================================"
echo "  Speed-Run AML Platform - Frontend App"
echo "  Julius Baer Hackathon Submission"
echo "============================================"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit 1

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js not found"
    echo "   Install from: https://nodejs.org/ (v18+ required)"
    exit 1
fi

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "⚠️  WARNING: Node.js v18+ required (you have v$NODE_VERSION)"
    echo "   Install from: https://nodejs.org/"
fi
echo ""

# Check for .env.local file
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        echo "✅ .env.local created"
    else
        # Create default .env.local
        cat > .env.local << 'EOF'
# Backend API Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_USE_BACKEND_API=true

# Feature Flags
NEXT_PUBLIC_ENABLE_DOCUMENT_UPLOAD=true
NEXT_PUBLIC_ENABLE_AI_DETECTION=true

# UI Configuration
NEXT_PUBLIC_APP_NAME=Speed-Run AML Platform
NEXT_PUBLIC_ITEMS_PER_PAGE=20
NEXT_PUBLIC_AUTO_REFRESH_INTERVAL=30000

# Debug
NEXT_PUBLIC_DEBUG=false
EOF
        echo "✅ .env.local created with defaults"
    fi
    echo ""
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies with npm..."
    npm install
    echo "✅ Dependencies installed"
    echo ""
fi

# Run quick test
echo "Running quick health check..."
if npm test -- --run --reporter=verbose 2>/dev/null | tail -5; then
    echo "✅ Tests passed"
else
    echo "⚠️  Some tests failed - check frontend/__tests__/ for details"
fi
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  WARNING: Backend not detected at http://localhost:8000"
    echo "   Start backend first with: ./start-backend.sh"
    echo "   Or use Docker: docker-compose up -d"
    echo "   Frontend will use mock data until backend is available"
    echo ""
fi

# Start the server
echo "🚀 Starting frontend development server..."
echo ""
echo "📍 Endpoints:"
echo "   • Frontend:     http://localhost:3000"
echo "   • Compliance:   http://localhost:3000/compliance"
echo "   • RM Dashboard: http://localhost:3000/rm"
echo ""
echo "📚 Documentation:"
echo "   • Quick Start:  QUICKSTART.md"
echo "   • Demo Guide:   DEMO_SETUP_AND_EXECUTION.md"
echo "   • User Guide:   docs/guides/"
echo ""
echo "💡 Tips:"
echo "   • Dashboards work with or without backend (hybrid mode)"
echo "   • Upload documents at /compliance for analysis"
echo "   • Use Kanban board to manage alerts"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================"
echo ""

# Start server
npm run dev

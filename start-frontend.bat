@echo off
echo ============================================
echo   Speed-Run AML Platform - Frontend App
echo   Julius Baer Hackathon Submission
echo ============================================
echo.

cd /d "%~dp0frontend"

REM Check for Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found
    echo    Install from: https://nodejs.org/ (v18+ required)
    pause
    exit /b 1
)

REM Check Node version
for /f "tokens=1 delims=v." %%i in ('node -v') do set NODE_MAJOR=%%i
if %NODE_MAJOR% LSS 18 (
    echo WARNING: Node.js v18+ required
    echo    Install from: https://nodejs.org/
)
echo.

REM Check for .env.local file
if not exist ".env.local" (
    echo Creating .env.local file from template...
    if exist ".env.example" (
        copy .env.example .env.local >nul
        echo .env.local created
    ) else (
        REM Create default .env.local
        (
            echo # Backend API Configuration
            echo NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
            echo NEXT_PUBLIC_API_VERSION=v1
            echo NEXT_PUBLIC_USE_BACKEND_API=true
            echo.
            echo # Feature Flags
            echo NEXT_PUBLIC_ENABLE_DOCUMENT_UPLOAD=true
            echo NEXT_PUBLIC_ENABLE_AI_DETECTION=true
            echo.
            echo # UI Configuration
            echo NEXT_PUBLIC_APP_NAME=Speed-Run AML Platform
            echo NEXT_PUBLIC_ITEMS_PER_PAGE=20
            echo NEXT_PUBLIC_AUTO_REFRESH_INTERVAL=30000
            echo.
            echo # Debug
            echo NEXT_PUBLIC_DEBUG=false
        ) > .env.local
        echo .env.local created with defaults
    )
    echo.
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing dependencies with npm...
    call npm install
    echo Dependencies installed
    echo.
)

REM Run quick test
echo Running quick health check...
call npm test -- --run --reporter=verbose 2>nul | findstr /C:"passing"
if errorlevel 1 (
    echo WARNING: Some tests failed - check frontend\__tests__\ for details
) else (
    echo Tests passed
)
echo.

REM Check if backend is running
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: Backend not detected at http://localhost:8000
    echo    Start backend first with: start-backend.bat
    echo    Or use Docker: docker-compose up -d
    echo    Frontend will use mock data until backend is available
    echo.
)

REM Start the server
echo Starting frontend development server...
echo.
echo Endpoints:
echo    * Frontend:     http://localhost:3000
echo    * Compliance:   http://localhost:3000/compliance
echo    * RM Dashboard: http://localhost:3000/rm
echo.
echo Documentation:
echo    * Quick Start:  QUICKSTART.md
echo    * Demo Guide:   DEMO_SETUP_AND_EXECUTION.md
echo    * User Guide:   docs\guides\
echo.
echo Tips:
echo    * Dashboards work with or without backend (hybrid mode)
echo    * Upload documents at /compliance for analysis
echo    * Use Kanban board to manage alerts
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

call npm run dev

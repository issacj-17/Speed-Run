@echo off
echo ==========================================
echo   Speed-Run AML Platform - Backend API
echo   Julius Baer Hackathon Submission
echo ==========================================
echo.

cd /d "%~dp0backend"

REM Check for sample data
echo Checking for sample data...
if not exist "..\sample_data\Swiss_Home_Purchase_Agreement_Scanned_Noise_forparticipants.pdf" (
    echo WARNING: Sample PDF not found in sample_data/
    echo    Please add: Swiss_Home_Purchase_Agreement_Scanned_Noise_forparticipants.pdf
)
if not exist "..\sample_data\transactions_mock_1000_for_participants.csv" (
    echo WARNING: Sample CSV not found in sample_data/
    echo    Please add: transactions_mock_1000_for_participants.csv
)
echo.

REM Check if uv is installed
where uv >nul 2>&1
if errorlevel 1 (
    echo ERROR: 'uv' package manager not found
    echo    Install from: https://docs.astral.sh/uv/
    echo    Or use pip: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    echo Creating .env file from template...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo .env created - please review and update if needed
    ) else (
        echo WARNING: .env.example not found - using defaults
    )
    echo.
)

REM Install dependencies if needed
if not exist ".venv\Scripts\python.exe" (
    if not exist "venv" (
        echo Installing dependencies with uv...
        uv sync
        echo Dependencies installed
        echo.
    )
)

REM Run quick health check
echo Running quick health check...
uv run pytest tests\unit\services\test_document_service.py -v --tb=no 2>nul | findstr /C:"passed"
if errorlevel 1 (
    echo WARNING: Some tests failed - check backend\docs\testing\ for help
) else (
    echo Tests passed
)
echo.

REM Start the server
echo Starting backend API server...
echo.
echo Endpoints:
echo    * API:          http://localhost:8000
echo    * API Docs:     http://localhost:8000/docs
echo    * ReDoc:        http://localhost:8000/redoc
echo    * Health Check: http://localhost:8000/health
echo.
echo Documentation:
echo    * Setup Guide:  backend\SETUP_GUIDE.md
echo    * API Guide:    docs\guides\API_INTEGRATION_GUIDE.md
echo    * Quick Start:  QUICKSTART.md
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

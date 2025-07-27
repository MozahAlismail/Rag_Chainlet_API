@echo off
echo ========================================
echo    RAG Chainlit - Manual Startup
echo ========================================
echo.
echo This starts only the Chainlit interface.
echo Make sure FastAPI server is running first!
echo.

echo Activating Conda Environment...
call conda activate NLPenv
if errorlevel 1 (
    echo ❌ Failed to activate NLPenv environment
    pause
    exit /b 1
)

echo.
echo Testing FastAPI connection...
curl -f http://localhost:8000/ >nul 2>&1
if errorlevel 1 (
    echo ❌ FastAPI server is not running!
    echo.
    echo Please start FastAPI server first using: start_api.bat
    echo Or manually run: uvicorn api:app --host 127.0.0.1 --port 8000
    pause
    exit /b 1
) else (
    echo ✅ FastAPI server is running!
)

echo.
echo ========================================
echo Starting Chainlit Interface...
echo ========================================
echo Chainlit will be available at: http://localhost:8001
echo ========================================
echo.

chainlit run chainlet.py --port 8001 --host 127.0.0.1

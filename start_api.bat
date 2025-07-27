@echo off
echo ========================================
echo    RAG API - Manual Startup Guide
echo ========================================
echo.
echo This will help you start the servers step by step for easier debugging.
echo.

echo Step 1: Activate Conda Environment
echo Command: conda activate NLPenv
echo.
call conda activate NLPenv
if errorlevel 1 (
    echo ❌ Failed to activate NLPenv environment
    echo Please make sure the environment exists
    pause
    exit /b 1
)
echo ✅ Environment activated successfully!
echo.

echo Step 2: Install Dependencies
echo Command: pip install -r requirements.txt
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully!
echo.

echo Step 3: Starting FastAPI Server
echo Command: uvicorn api:app --host 127.0.0.1 --port 8000 --reload
echo.
echo ========================================
echo IMPORTANT: 
echo - FastAPI will start at: http://127.0.0.1:8000
echo - Keep this window open
echo - Open another terminal to start Chainlit
echo ========================================
echo.
echo Starting server in 3 seconds...
timeout /t 3 /nobreak >nul

uvicorn api:app --host 127.0.0.1 --port 8000 --reload

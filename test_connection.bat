@echo off
echo Testing RAG API Connection...

REM Test if FastAPI server is running
echo.
echo 1. Testing FastAPI server connection...
curl -X GET http://localhost:8000/ 2>nul
if errorlevel 1 (
    echo ❌ FastAPI server is NOT running or not accessible
    echo.
    echo Please start FastAPI server first:
    echo conda activate NLPenv
    echo uvicorn api:app --host 0.0.0.0 --port 8000
) else (
    echo ✅ FastAPI server is running!
)

echo.
echo 2. Testing chat endpoint...
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"question\": \"test\"}" 2>nul
if errorlevel 1 (
    echo ❌ Chat endpoint is not responding
) else (
    echo ✅ Chat endpoint is working!
)

echo.
echo 3. Checking what's running on port 8000...
netstat -an | findstr :8000

pause

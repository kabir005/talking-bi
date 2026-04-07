@echo off
REM Talking BI - Windows Startup Script
REM Starts both FastAPI and Celery worker

echo ================================================================================
echo    TALKING BI - Starting All Services
echo ================================================================================
echo.

REM Check if Redis is running
echo Checking Redis...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Redis is not running!
    echo           Celery worker will not start.
    echo           To start Redis: redis-server
    echo.
    echo Starting FastAPI only...
    python main.py
    exit /b
)

echo [OK] Redis is running
echo.

REM Start Celery worker in background
echo Starting Celery worker...
start /B python -m celery -A tasks.celery_app worker --loglevel=info --concurrency=2 --pool=solo

REM Wait a bit for Celery to start
timeout /t 3 /nobreak >nul

REM Start FastAPI server (foreground)
echo Starting FastAPI server...
echo.
echo ================================================================================
echo    Services Running:
echo    - FastAPI:  http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - Celery:   Background worker (2 concurrent tasks)
echo ================================================================================
echo.
echo Press Ctrl+C to stop all services
echo.

python main.py

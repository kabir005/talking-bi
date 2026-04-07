#!/bin/bash
# Talking BI - Linux/Mac Startup Script
# Starts both FastAPI and Celery worker

echo "================================================================================"
echo "   TALKING BI - Starting All Services"
echo "================================================================================"
echo ""

# Check if Redis is running
echo "Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "[WARNING] Redis is not running!"
    echo "          Celery worker will not start."
    echo "          To start Redis: redis-server"
    echo ""
    echo "Starting FastAPI only..."
    python main.py
    exit 0
fi

echo "[OK] Redis is running"
echo ""

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A tasks.celery_app worker --loglevel=info --concurrency=2 --pool=prefork &
CELERY_PID=$!

# Wait a bit for Celery to start
sleep 3

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $CELERY_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Start FastAPI server (foreground)
echo "Starting FastAPI server..."
echo ""
echo "================================================================================"
echo "   Services Running:"
echo "   - FastAPI:  http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Celery:   Background worker (PID: $CELERY_PID)"
echo "================================================================================"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

python main.py

# Cleanup on exit
cleanup

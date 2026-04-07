# ✅ Celery Integration Complete

## What Was Added

### 🎯 Automatic Celery Startup

You can now start both FastAPI and Celery with a single command!

### 📁 New Files Created

1. **`backend/start.bat`** - Windows startup script
2. **`backend/start.sh`** - Linux/Mac startup script  
3. **`backend/start_server.py`** - Python-based unified startup
4. **`backend/run_with_celery.py`** - Alternative threaded approach
5. **`backend/CELERY_INTEGRATION.md`** - Complete documentation

### 🚀 How to Use

#### Windows:
```bash
cd talking-bi/backend
start.bat
```

#### Linux/Mac:
```bash
cd talking-bi/backend
chmod +x start.sh
./start.sh
```

#### Python (Cross-platform):
```bash
cd talking-bi/backend
python start_server.py
```

### ✨ What Happens

1. **Checks Redis** - Verifies Redis is running
2. **Starts Celery Worker** - Launches in background (2 concurrent tasks)
3. **Starts FastAPI** - Launches API server on port 8000
4. **Monitors Processes** - Auto-restarts if they crash
5. **Graceful Shutdown** - Ctrl+C stops everything cleanly

### 📊 Output Example

```
================================================================================
   TALKING BI - Starting All Services
================================================================================

[OK] Redis is running
Starting Celery worker...
✓ Celery worker started (PID: 12345)
Starting FastAPI server...
✓ FastAPI server started (PID: 12346)

================================================================================
✅ TALKING BI - All Services Running
================================================================================
🌐 API Server:    http://localhost:8000
📚 API Docs:      http://localhost:8000/docs
💡 Health Check:  http://localhost:8000/health
🔴 Celery Worker: Running (2 concurrent tasks)
================================================================================

Press Ctrl+C to stop all services
```

### 🔧 Configuration

#### If Redis is NOT Running:

The scripts will detect this and:
- Show a warning
- Start FastAPI only (without Celery)
- Pipeline runs synchronously

#### To Install Redis:

**Windows:**
```bash
# Download from: https://github.com/microsoftarchive/redis/releases
# Or use Chocolatey:
choco install redis-64
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

### 🎛️ Alternative: Run Without Celery

If you don't need background tasks:

```bash
cd talking-bi/backend
python main.py
```

This runs FastAPI only (no Celery).

### 📝 Features

#### Startup Scripts Include:

- ✅ Redis availability check
- ✅ Automatic Celery worker startup
- ✅ Process monitoring
- ✅ Graceful shutdown handling
- ✅ Error messages with solutions
- ✅ Cross-platform support

#### Celery Configuration:

- **Concurrency:** 2 workers (adjustable)
- **Pool:** `solo` on Windows, `prefork` on Linux/Mac
- **Timeout:** 10 minutes per task
- **Retries:** 3 attempts with exponential backoff
- **Queue:** Redis on `localhost:6379`

### 🔍 Monitoring

#### Check if Everything is Running:

```bash
# Check Redis
redis-cli ping

# Check Celery workers
celery -A tasks.celery_app inspect active

# Check API
curl http://localhost:8000/health
```

#### View Logs:

- **FastAPI:** Console output
- **Celery:** Console output (or separate terminal)
- **Redis:** `redis-cli MONITOR`

### 🐛 Troubleshooting

#### Redis Not Running:

```
[WARNING] Redis is not running!
```

**Solution:** Start Redis first:
- Windows: `redis-server`
- Linux: `sudo systemctl start redis`
- Mac: `brew services start redis`

#### Port Already in Use:

```
Error: Address already in use
```

**Solution:** Kill existing process:
- Windows: `taskkill /F /IM python.exe`
- Linux/Mac: `pkill -f "uvicorn main:app"`

#### Celery Worker Fails:

```
Error: No module named 'tasks'
```

**Solution:** Run from correct directory:
```bash
cd talking-bi/backend
start.bat  # or ./start.sh
```

### 📚 Documentation

Full documentation available in:
- `backend/CELERY_INTEGRATION.md` - Complete guide
- `backend/tasks/celery_app.py` - Celery configuration
- `backend/tasks/pipeline_task.py` - Background task implementation

### 🎯 Benefits

#### With Celery (Recommended):
- ✅ Non-blocking uploads
- ✅ No timeout issues
- ✅ Progress tracking
- ✅ Task retries
- ✅ Better scalability

#### Without Celery (Simple):
- ✅ Easier setup
- ✅ No Redis dependency
- ✅ Good for development
- ⚠️ Blocking operations
- ⚠️ Timeout risk on large files

### 🚀 Production Deployment

For production, use:

1. **Supervisor** (Linux) - Process management
2. **Systemd** (Linux) - Service management
3. **Docker Compose** - Containerized deployment
4. **PM2** (Node.js) - Alternative process manager

See `CELERY_INTEGRATION.md` for detailed production setup.

### ✅ Summary

You can now run Talking BI with:

```bash
# Simple one-command startup
cd talking-bi/backend
start.bat  # Windows
./start.sh # Linux/Mac
```

This starts:
- ✅ FastAPI server (port 8000)
- ✅ Celery worker (2 concurrent tasks)
- ✅ Background pipeline processing
- ✅ Graceful shutdown on Ctrl+C

Everything is integrated and ready to use!

---

**Status:** ✅ COMPLETE  
**Date:** March 25, 2026  
**Version:** 1.0.0

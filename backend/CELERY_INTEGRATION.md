# Celery Integration Guide

## Overview

Talking BI now supports background task processing using Celery + Redis. This allows long-running data pipelines to run asynchronously without blocking the API.

## Prerequisites

### 1. Install Redis

**Windows:**
```bash
# Download from: https://github.com/microsoftarchive/redis/releases
# Or use Chocolatey:
choco install redis-64

# Start Redis:
redis-server
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

### 2. Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

## Running with Celery

### Option 1: Simple Startup Script (Recommended)

**Windows:**
```bash
cd talking-bi/backend
start.bat
```

**Linux/Mac:**
```bash
cd talking-bi/backend
chmod +x start.sh
./start.sh
```

This will:
- Check if Redis is running
- Start Celery worker in background
- Start FastAPI server in foreground
- Handle graceful shutdown on Ctrl+C

### Option 2: Python Startup Script

```bash
cd talking-bi/backend
python start_server.py
```

Features:
- Automatic Redis detection
- Process monitoring and auto-restart
- Graceful shutdown handling
- Detailed logging

### Option 3: Manual (Two Terminals)

**Terminal 1 - Celery Worker:**
```bash
cd talking-bi/backend
celery -A tasks.celery_app worker --loglevel=info --concurrency=2
```

**Terminal 2 - FastAPI Server:**
```bash
cd talking-bi/backend
python main.py
```

### Option 4: Without Celery (Development)

If you don't need background tasks:

```bash
cd talking-bi/backend
python main.py
```

Pipeline will run synchronously (blocking).

## How It Works

### Background Pipeline Execution

When a dataset is uploaded:

1. **Synchronous Path (No Redis):**
   - Upload → Clean → Analyze → Generate Dashboard
   - User waits for entire pipeline to complete
   - Timeout risk on large files (60s)

2. **Asynchronous Path (With Celery):**
   - Upload → Queue task → Return immediately
   - Pipeline runs in background
   - Frontend polls for progress
   - No timeout risk

### Pipeline Stages

The pipeline runs through these stages with progress updates:

```
uploaded    →  5%   Initial upload complete
cleaning    → 15%   Data cleaning in progress
schema      → 25%   Schema detection
kpi         → 45%   KPI calculation
visualization → 60%  Chart generation
insights    → 75%   Insight generation
eval        → 90%   Validation
complete    → 100%  Pipeline complete
```

### Task Configuration

From `tasks/celery_app.py`:

```python
task_soft_time_limit=300      # 5 min soft limit
task_time_limit=600           # 10 min hard limit
task_acks_late=True           # Ensure task not lost
worker_prefetch_multiplier=1  # One task per worker
max_retries=3                 # Retry failed tasks
```

## Monitoring

### Check Celery Status

```bash
# List active tasks
celery -A tasks.celery_app inspect active

# Check worker stats
celery -A tasks.celery_app inspect stats

# Check registered tasks
celery -A tasks.celery_app inspect registered
```

### Check Redis

```bash
# Connect to Redis CLI
redis-cli

# Check queue length
LLEN celery

# Monitor commands
MONITOR
```

### API Endpoints

```bash
# Check pipeline status
GET /api/pipeline/status/{dataset_id}/once

# Response:
{
  "status": "kpi",
  "progress": 45,
  "error": null
}
```

## Configuration

### Environment Variables

Add to `.env`:

```env
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Celery Settings

Edit `tasks/celery_app.py` to customize:

```python
celery_app.conf.update(
    task_soft_time_limit=300,     # Adjust timeout
    worker_prefetch_multiplier=1, # Tasks per worker
    task_acks_late=True,          # Reliability
)
```

## Troubleshooting

### Redis Connection Error

```
Error: Redis connection refused
```

**Solution:**
1. Check if Redis is running: `redis-cli ping`
2. Start Redis: `redis-server` (Windows) or `sudo systemctl start redis` (Linux)
3. Check port: Redis should be on `localhost:6379`

### Celery Worker Not Starting

```
Error: No module named 'tasks'
```

**Solution:**
1. Ensure you're in the `backend` directory
2. Check Python path: `echo $PYTHONPATH`
3. Run from correct directory: `cd talking-bi/backend`

### Tasks Not Executing

```
Tasks queued but not processing
```

**Solution:**
1. Check worker is running: `celery -A tasks.celery_app inspect active`
2. Check Redis queue: `redis-cli LLEN celery`
3. Restart worker: Kill and restart Celery process

### Windows Pool Issues

```
Warning: Soft timeouts not supported
```

**Solution:**
Use `--pool=solo` on Windows:
```bash
celery -A tasks.celery_app worker --pool=solo --loglevel=info
```

## Production Deployment

### Using Supervisor (Linux)

Create `/etc/supervisor/conf.d/talking-bi.conf`:

```ini
[program:talking-bi-celery]
command=/path/to/venv/bin/celery -A tasks.celery_app worker --loglevel=info --concurrency=4
directory=/path/to/talking-bi/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/talking-bi/celery.log

[program:talking-bi-api]
command=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
directory=/path/to/talking-bi/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/talking-bi/api.log
```

### Using Systemd (Linux)

Create `/etc/systemd/system/talking-bi-celery.service`:

```ini
[Unit]
Description=Talking BI Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
WorkingDirectory=/path/to/talking-bi/backend
ExecStart=/path/to/venv/bin/celery -A tasks.celery_app worker --loglevel=info --concurrency=4 --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable talking-bi-celery
sudo systemctl start talking-bi-celery
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  celery:
    build: ./backend
    command: celery -A tasks.celery_app worker --loglevel=info --concurrency=4
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0

  api:
    build: ./backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - celery
    environment:
      - REDIS_URL=redis://redis:6379/0

volumes:
  redis-data:
```

## Performance Tuning

### Concurrency

Adjust based on CPU cores:

```bash
# 2 workers (default)
celery -A tasks.celery_app worker --concurrency=2

# 4 workers (more throughput)
celery -A tasks.celery_app worker --concurrency=4

# Auto-scale (2-8 workers)
celery -A tasks.celery_app worker --autoscale=8,2
```

### Memory Management

For large datasets:

```python
# In celery_app.py
celery_app.conf.update(
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks
    worker_max_memory_per_child=500000,  # 500MB limit
)
```

### Task Priorities

```python
# High priority task
run_pipeline_task.apply_async(
    args=[dataset_id],
    priority=9  # 0-9, higher = more priority
)
```

## Best Practices

1. **Always run Redis in production** - Don't rely on synchronous execution
2. **Monitor task failures** - Set up alerts for failed tasks
3. **Use task retries** - Network issues are common
4. **Set timeouts** - Prevent runaway tasks
5. **Log everything** - Essential for debugging
6. **Scale workers** - Add more workers for high load
7. **Use task routing** - Separate queues for different task types

## Quick Reference

```bash
# Start everything (Windows)
start.bat

# Start everything (Linux/Mac)
./start.sh

# Check Redis
redis-cli ping

# Check Celery workers
celery -A tasks.celery_app inspect active

# Purge all tasks
celery -A tasks.celery_app purge

# Stop all workers
pkill -f "celery worker"
```

---

**Last Updated:** March 25, 2026  
**Version:** 1.0.0

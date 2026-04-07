#!/usr/bin/env python3
"""
Unified startup script for Talking BI
Starts both FastAPI server and Celery workers in the background
"""

import subprocess
import sys
import os
import time
import signal
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Store process references
processes = []


def cleanup_processes():
    """Cleanup all spawned processes"""
    logger.info("Shutting down all processes...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            try:
                proc.kill()
            except:
                pass
    logger.info("All processes terminated")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("\nReceived interrupt signal, shutting down...")
    cleanup_processes()
    sys.exit(0)


def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        logger.info("✓ Redis is running")
        return True
    except Exception as e:
        logger.warning(f"⚠ Redis not available: {e}")
        logger.warning("  Celery background tasks will not work")
        logger.warning("  To install Redis:")
        logger.warning("    - Windows: Download from https://github.com/microsoftarchive/redis/releases")
        logger.warning("    - Linux: sudo apt-get install redis-server")
        logger.warning("    - Mac: brew install redis")
        return False


def start_celery_worker():
    """Start Celery worker in background"""
    logger.info("Starting Celery worker...")
    
    # Celery command
    cmd = [
        sys.executable, "-m", "celery",
        "-A", "tasks.celery_app",
        "worker",
        "--loglevel=info",
        "--concurrency=2",
        "--pool=solo" if sys.platform == "win32" else "--pool=prefork"
    ]
    
    try:
        # Start Celery in background
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(proc)
        
        # Wait a bit and check if it started
        time.sleep(2)
        if proc.poll() is None:
            logger.info("✓ Celery worker started (PID: {})".format(proc.pid))
            return proc
        else:
            logger.error("✗ Celery worker failed to start")
            return None
    except Exception as e:
        logger.error(f"✗ Failed to start Celery: {e}")
        return None


def start_fastapi():
    """Start FastAPI server"""
    logger.info("Starting FastAPI server...")
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    try:
        proc = subprocess.Popen(cmd)
        processes.append(proc)
        logger.info("✓ FastAPI server started (PID: {})".format(proc.pid))
        return proc
    except Exception as e:
        logger.error(f"✗ Failed to start FastAPI: {e}")
        return None


def main():
    """Main startup routine"""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("\n" + "="*80)
    print("🚀 TALKING BI - Unified Startup")
    print("="*80 + "\n")
    
    # Check Redis availability
    redis_available = check_redis()
    
    # Start Celery worker (if Redis available)
    celery_proc = None
    if redis_available:
        celery_proc = start_celery_worker()
        if celery_proc:
            # Give Celery time to fully start
            time.sleep(3)
    else:
        logger.warning("⚠ Skipping Celery worker (Redis not available)")
        logger.warning("  Pipeline will run synchronously")
    
    # Start FastAPI server
    fastapi_proc = start_fastapi()
    
    if not fastapi_proc:
        logger.error("Failed to start FastAPI server")
        cleanup_processes()
        sys.exit(1)
    
    print("\n" + "="*80)
    print("✅ TALKING BI - All Services Running")
    print("="*80)
    print("🌐 API Server:    http://localhost:8000")
    print("📚 API Docs:      http://localhost:8000/docs")
    print("💡 Health Check:  http://localhost:8000/health")
    if celery_proc:
        print("🔴 Celery Worker: Running (2 concurrent tasks)")
    else:
        print("⚠  Celery Worker: Not running (Redis unavailable)")
    print("="*80)
    print("\nPress Ctrl+C to stop all services\n")
    
    # Monitor processes
    try:
        while True:
            time.sleep(1)
            
            # Check if FastAPI is still running
            if fastapi_proc.poll() is not None:
                logger.error("FastAPI server stopped unexpectedly")
                break
            
            # Check if Celery is still running (if it was started)
            if celery_proc and celery_proc.poll() is not None:
                logger.warning("Celery worker stopped unexpectedly")
                # Try to restart it
                logger.info("Attempting to restart Celery worker...")
                celery_proc = start_celery_worker()
    
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_processes()


if __name__ == "__main__":
    main()

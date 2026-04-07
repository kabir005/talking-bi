#!/usr/bin/env python3
"""
Simple script to run FastAPI + Celery worker in the same process
Uses threading to run both simultaneously
"""

import threading
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_redis():
    """Check if Redis is available"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        return True
    except:
        return False


def run_celery_worker():
    """Run Celery worker in a thread"""
    logger.info("Starting Celery worker thread...")
    
    try:
        from celery import Celery
        from celery.bin import worker
        from tasks.celery_app import celery_app
        
        # Create worker instance
        celery_worker = worker.worker(app=celery_app)
        
        # Configure worker
        options = {
            'loglevel': 'INFO',
            'concurrency': 2,
            'pool': 'solo' if sys.platform == 'win32' else 'prefork',
        }
        
        # Start worker (blocking call)
        celery_worker.run(**options)
        
    except Exception as e:
        logger.error(f"Celery worker error: {e}")


def run_fastapi():
    """Run FastAPI server"""
    logger.info("Starting FastAPI server...")
    
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload when running with Celery
        log_level="info"
    )


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("🚀 TALKING BI - Starting with Celery Integration")
    print("="*80 + "\n")
    
    # Check Redis
    if not check_redis():
        logger.error("❌ Redis is not running!")
        logger.error("   Please start Redis first:")
        logger.error("   - Windows: redis-server.exe")
        logger.error("   - Linux/Mac: redis-server")
        logger.error("\n   Or run without Celery: python main.py")
        sys.exit(1)
    
    logger.info("✓ Redis is running")
    
    # Start Celery worker in background thread
    celery_thread = threading.Thread(target=run_celery_worker, daemon=True)
    celery_thread.start()
    
    # Give Celery time to start
    import time
    time.sleep(3)
    
    print("\n" + "="*80)
    print("✅ Services Started")
    print("="*80)
    print("🌐 API Server:    http://localhost:8000")
    print("📚 API Docs:      http://localhost:8000/docs")
    print("🔴 Celery Worker: Running in background thread")
    print("="*80)
    print("\nPress Ctrl+C to stop\n")
    
    # Start FastAPI (blocking)
    try:
        run_fastapi()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()

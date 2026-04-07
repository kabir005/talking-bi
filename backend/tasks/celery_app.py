"""
celery_app.py — Celery application configuration.
Uses Redis as broker and result backend.
"""

from celery import Celery
import os

# Allow override via environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "talking_bi",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.pipeline_task"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,           # ensure task not lost if worker dies
    worker_prefetch_multiplier=1,  # one task per worker at a time (heavy tasks)
    task_soft_time_limit=300,      # 5 min soft limit → send warning
    task_time_limit=600,           # 10 min hard limit → kill task
    result_expires=3600,           # results expire after 1 hour
)

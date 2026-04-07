"""
pipeline_status.py — Centralized pipeline progress updater.
Called by Celery tasks and the upload router to write status to SQLite.
The SSE endpoint reads these values and streams them to the frontend.
"""

import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import SQLITE_DB_PATH

logger = logging.getLogger(__name__)

# Async engine for status updates from async code
_async_engine = create_async_engine(
    f"sqlite+aiosqlite:///{SQLITE_DB_PATH}", echo=False, future=True
)
_AsyncSession = sessionmaker(_async_engine, class_=AsyncSession, expire_on_commit=False)


async def update_pipeline_status(dataset_id: str, status: str, progress: int, error: str = None):
    """Update pipeline status in DB. Safe to call from async code."""
    try:
        async with _AsyncSession() as session:
            error_clause = f", pipeline_error = '{error}'" if error else ""
            await session.execute(
                text(
                    f"UPDATE datasets SET pipeline_status = :status, pipeline_progress = :progress"
                    f"{error_clause} WHERE id = :id"
                ),
                {"status": status, "progress": progress, "id": dataset_id},
            )
            await session.commit()
            logger.info(f"Pipeline [{dataset_id}] → {status} ({progress}%)")
    except Exception as e:
        logger.error(f"Failed to update pipeline status for {dataset_id}: {e}")


def update_pipeline_status_sync(dataset_id: str, status: str, progress: int, error: str = None):
    """Synchronous version — for use inside Celery tasks (non-async context)."""
    from sqlalchemy import create_engine
    try:
        engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}")
        with engine.connect() as conn:
            error_clause = f", pipeline_error = '{error}'" if error else ""
            conn.execute(
                text(
                    f"UPDATE datasets SET pipeline_status = :status, pipeline_progress = :progress"
                    f"{error_clause} WHERE id = :id"
                ),
                {"status": status, "progress": progress, "id": dataset_id},
            )
            conn.commit()
        engine.dispose()
        logger.info(f"[sync] Pipeline [{dataset_id}] → {status} ({progress}%)")
    except Exception as e:
        logger.error(f"[sync] Failed to update pipeline status for {dataset_id}: {e}")


async def get_pipeline_status(dataset_id: str) -> dict:
    """Read current pipeline status for a dataset."""
    try:
        async with _AsyncSession() as session:
            result = await session.execute(
                text(
                    "SELECT pipeline_status, pipeline_progress, pipeline_error "
                    "FROM datasets WHERE id = :id"
                ),
                {"id": dataset_id},
            )
            row = result.fetchone()
            if not row:
                return {"status": "not_found", "progress": 0, "error": None}
            return {
                "status": row[0] or "complete",
                "progress": row[1] or 100,
                "error": row[2],
            }
    except Exception as e:
        logger.error(f"Failed to read pipeline status for {dataset_id}: {e}")
        return {"status": "error", "progress": 0, "error": str(e)}

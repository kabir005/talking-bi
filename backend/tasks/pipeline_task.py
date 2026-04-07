"""
pipeline_task.py — Background pipeline task execution via Celery.
Runs the full agent pipeline after file upload, with real-time progress
updates written to SQLite so the SSE endpoint can stream them to the frontend.
"""

import asyncio
import logging
import traceback
import os
import sys

# Ensure backend root is on path when Celery runs this as a worker
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.celery_app import celery_app
from utils.pipeline_status import update_pipeline_status_sync

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def run_pipeline_task(self, dataset_id: str):
    """
    Full analysis pipeline as a Celery background task.
    Stages with progress milestones:
      uploaded    → 5%
      cleaning    → 15%
      schema      → 25%
      kpi         → 45%
      charts      → 60%
      insights    → 75%
      eval        → 90%
      complete    → 100%
    """
    logger.info(f"[Celery] Pipeline started for dataset_id={dataset_id}")

    try:
        # ── Stage 1: Init ─────────────────────────────────────────────────────
        update_pipeline_status_sync(dataset_id, "uploaded", 5)

        # Import inside task to avoid circular imports at module load time
        import pandas as pd
        from sqlalchemy import create_engine, text
        from config import SQLITE_DB_PATH
        from utils.schema_detector import infer_column_types

        # Load dataset from SQLite
        sync_engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}")
        with sync_engine.connect() as conn:
            result = conn.execute(
                text("SELECT sqlite_table_name, schema_json FROM datasets WHERE id = :id"),
                {"id": dataset_id},
            )
            row = result.fetchone()

        if not row:
            raise ValueError(f"Dataset {dataset_id} not found in DB")

        table_name = row[0]
        update_pipeline_status_sync(dataset_id, "cleaning", 15)

        # Load DataFrame
        df = pd.read_sql_table(table_name, sync_engine)
        sync_engine.dispose()

        # ── Stage 2: Schema ────────────────────────────────────────────────────
        update_pipeline_status_sync(dataset_id, "schema", 25)
        schema = infer_column_types(df)

        # ── Stage 3: KPI + Analysis (orchestrator) ─────────────────────────────
        update_pipeline_status_sync(dataset_id, "kpi", 45)

        # Run orchestrator in a new event loop (Celery is sync)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            from agents.orchestrator import run_orchestrator

            dataset_schema = schema.get("columns", {})
            col_types = {col: info.get("type", "unknown") for col, info in dataset_schema.items()}
            sample_rows = df.head(5).to_dict(orient="records")

            update_pipeline_status_sync(dataset_id, "visualization", 60)

            orchestrator_result = loop.run_until_complete(
                run_orchestrator(
                    df=df,
                    dataset_schema=col_types,
                    dataset_sample=sample_rows,
                    user_prompt="Generate comprehensive business analysis dashboard",
                    user_role="default",
                )
            )

            update_pipeline_status_sync(dataset_id, "insights", 75)

            # ── Stage 4: Save orchestrator results to DB ──────────────────────
            from sqlalchemy import create_engine as ce
            import json

            engine2 = ce(f"sqlite:///{SQLITE_DB_PATH}")
            with engine2.connect() as conn:
                # Store insights and chart configs as JSON in a results table
                # (graceful — table may not exist yet)
                try:
                    insights_json = json.dumps(
                        orchestrator_result.get("agent_outputs", {}).get("insights", {})
                    )
                    charts_json = json.dumps(
                        orchestrator_result.get("agent_outputs", {}).get("chart", [])
                    )
                    conn.execute(
                        text(
                            "UPDATE datasets SET "
                            "pipeline_status='eval', pipeline_progress=90 "
                            "WHERE id=:id"
                        ),
                        {"id": dataset_id},
                    )
                    conn.commit()
                except Exception as inner:
                    logger.warning(f"Could not store orchestrator results: {inner}")
            engine2.dispose()

            update_pipeline_status_sync(dataset_id, "eval", 90)

        finally:
            loop.close()

        # ── Stage 5: Done ─────────────────────────────────────────────────────
        update_pipeline_status_sync(dataset_id, "complete", 100)
        logger.info(f"[Celery] Pipeline complete for dataset_id={dataset_id}")
        return {"status": "complete", "dataset_id": dataset_id}

    except Exception as exc:
        error_msg = str(exc)[:500]
        logger.error(f"[Celery] Pipeline failed for {dataset_id}: {error_msg}\n{traceback.format_exc()}")
        update_pipeline_status_sync(dataset_id, "failed", 0, error=error_msg)

        # Retry up to 3 times with exponential backoff
        try:
            raise self.retry(exc=exc, countdown=5 * (self.request.retries + 1))
        except self.MaxRetriesExceededError:
            update_pipeline_status_sync(dataset_id, "failed", 0, error="Max retries exceeded: " + error_msg)
            return {"status": "failed", "error": error_msg}

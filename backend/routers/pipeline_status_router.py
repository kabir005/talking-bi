"""
pipeline_status_router.py — SSE endpoint for real-time pipeline progress.
GET /api/pipeline/status/{dataset_id} → EventSource stream

Frontend usage:
  const es = new EventSource(`/api/pipeline/status/${datasetId}`)
  es.onmessage = e => { const {status, progress} = JSON.parse(e.data) }
"""

import asyncio
import json
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from utils.pipeline_status import get_pipeline_status

router = APIRouter()
logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 1.5   # check DB every 1.5s
TERMINAL_STATES = {"complete", "failed", "not_found"}


@router.get("/pipeline/status/{dataset_id}")
async def stream_pipeline_status(dataset_id: str):
    """
    SSE stream that polls SQLite and pushes pipeline progress to the frontend.
    Closes automatically when status reaches 'complete' or 'failed'.
    """

    async def event_generator():
        retries = 0
        max_retries = 200  # ~5 minutes max stream time

        while retries < max_retries:
            try:
                state = await get_pipeline_status(dataset_id)
                payload = json.dumps(state)
                yield f"data: {payload}\n\n"

                if state["status"] in TERMINAL_STATES:
                    # Send a final close event then stop
                    yield f"event: done\ndata: {payload}\n\n"
                    break

            except Exception as exc:
                logger.warning(f"SSE error for {dataset_id}: {exc}")
                error_payload = json.dumps({"status": "error", "progress": 0, "error": str(exc)})
                yield f"data: {error_payload}\n\n"
                break

            retries += 1
            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering
            "Connection": "keep-alive",
        },
    )


@router.get("/pipeline/status/{dataset_id}/once")
async def get_pipeline_status_once(dataset_id: str):
    """Non-streaming one-shot status check (for polling fallback)."""
    return await get_pipeline_status(dataset_id)

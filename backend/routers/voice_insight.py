"""
Voice-to-Insight Route
Transcribes audio → classifies intent → executes query → returns chart config.
This is the "Speech RAG" pipeline: voice in, rendered chart out.
"""

import os
import logging
import tempfile
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from fastapi import Depends
from database.db import get_db
from database.models import Dataset
from services.intent_classifier import classify_intent
from services.query_executor import execute
import base64

logger = logging.getLogger(__name__)
router = APIRouter()

_whisper_model = None


def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            model_name = os.getenv("WHISPER_MODEL", "base")
            _whisper_model = whisper.load_model(model_name)
            logger.info(f"Whisper model '{model_name}' loaded")
        except ImportError:
            logger.error("Whisper not installed. Install with: pip install openai-whisper")
            raise
    return _whisper_model


@router.post("/transcribe-and-render")
async def voice_to_insight(
    audio: UploadFile = File(...),
    dataset_id: str = "",
    db: AsyncSession = Depends(get_db)
):
    """
    Full Speech RAG pipeline:
    1. Validate audio
    2. Whisper transcription
    3. Intent classification
    4. Pandas query execution
    5. Auto chart selection
    6. Return: transcript + intent + chart_config + table_data + summary
    """
    # --- 1. Validate ---
    content = await audio.read()
    if len(content) == 0:
        raise HTTPException(400, "Empty audio file.")
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(400, "Audio too large. Max 25MB.")
    if not dataset_id:
        raise HTTPException(400, "dataset_id is required.")

    # Check RMS — reject silent audio
    try:
        import numpy as np
        audio_array = np.frombuffer(content, dtype=np.int16).astype(np.float32)
        rms = np.sqrt(np.mean(audio_array ** 2))
        if rms < 100:
            return JSONResponse({
                "success": False,
                "error": "No speech detected. Please speak clearly."
            })
    except Exception:
        pass  # If RMS check fails, proceed anyway

    # --- 2. Transcribe ---
    suffix = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        model = get_whisper()
        result = model.transcribe(tmp_path, language="en")
        transcript = result.get("text", "").strip()
        language_prob = result.get("language_probability", 1.0)
    except Exception as e:
        raise HTTPException(500, f"Transcription failed: {e}")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    if not transcript:
        return JSONResponse({
            "success": False,
            "error": "Could not understand audio. Please try again."
        })

    if language_prob < 0.6:
        return JSONResponse({
            "success": False,
            "error": f"Low confidence transcription. Heard: '{transcript}'. Please speak more clearly."
        })

    # --- 3. Load dataset ---
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(404, "Dataset not found.")
    
    if not dataset.sqlite_table_name:
        raise HTTPException(400, "Generate dashboard first before using voice queries.")

    try:
        query = f"SELECT * FROM {dataset.sqlite_table_name}"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
    except Exception as e:
        raise HTTPException(500, f"Failed to load dataset: {e}")

    # Build schema
    schema = {
        "columns": list(df.columns),
        "numerical_columns": df.select_dtypes(include=['number']).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=['object', 'category']).columns.tolist()
    }

    # --- 4. Classify intent ---
    intent = await classify_intent(transcript, schema)

    # --- 5. Execute query ---
    try:
        result_df, summary = execute(df, intent, schema)
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        result_df = df.head(10)
        summary = f"Showing first 10 rows. Query: {transcript}"

    # --- 6. Auto-select chart ---
    chart_config = _select_chart_for_voice(result_df, intent.op, transcript)

    # --- 7. Serialize result ---
    MAX_ROWS = 500
    total_rows = len(result_df)
    display_df = result_df.head(MAX_ROWS)
    records = _safe_serialize(display_df)

    return {
        "success": True,
        "transcript": transcript,
        "intent": intent.model_dump(),
        "summary": summary,
        "chart_config": chart_config,
        "result": records,
        "columns": list(display_df.columns),
        "total_rows": total_rows,
        "truncated": total_rows > MAX_ROWS,
        "suggested_tile": {
            "title": transcript[:80],
            "source": "voice",
            "chart_config": chart_config
        }
    }


@router.post("/speak-insight")
async def speak_insight(text: str):
    """Convert insight text to audio for playback."""
    if not text or not text.strip():
        raise HTTPException(400, "No text to speak.")
    
    if len(text) > 800:
        text = text[:797] + "..."

    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        
        with open(tmp_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        os.unlink(tmp_path)
        
        return {"success": True, "audio_base64": audio_b64, "format": "wav"}
    except Exception as e:
        raise HTTPException(500, f"TTS failed: {e}")


def _select_chart_for_voice(df: pd.DataFrame, op: str, query: str) -> dict | None:
    """Smart chart selection for voice query results."""
    if df is None or df.empty or len(df.columns) < 2:
        return None

    try:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        str_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = [c for c in df.columns if any(kw in c.lower() for kw in ["date", "month", "year", "week", "period"])]

        # Time series
        if date_cols and num_cols:
            return {
                "type": "line",
                "title": query[:80],
                "xKey": date_cols[0],
                "yKey": num_cols[0]
            }

        # Categorical breakdown
        if op in ("groupby", "topn", "having", "resample") and str_cols and num_cols:
            return {
                "type": "bar",
                "title": query[:80],
                "xKey": str_cols[0],
                "yKey": num_cols[0]
            }

        # Scatter for correlation
        if len(num_cols) >= 2:
            return {
                "type": "scatter",
                "title": query[:80],
                "xKey": num_cols[0],
                "yKey": num_cols[1]
            }

        # Default bar chart
        if str_cols and num_cols:
            return {
                "type": "bar",
                "title": query[:80],
                "xKey": str_cols[0],
                "yKey": num_cols[0]
            }

    except Exception as e:
        logger.warning(f"Chart selection failed: {e}")
    
    return None


def _safe_serialize(df: pd.DataFrame) -> list:
    """Serialize DataFrame to JSON-safe records."""
    records = []
    for _, row in df.iterrows():
        rec = {}
        for col, val in row.items():
            try:
                is_na = pd.isna(val) if not isinstance(val, (list, dict)) else False
            except Exception:
                is_na = False
            
            if is_na:
                rec[col] = None
            elif isinstance(val, float) and (val in (float("inf"), float("-inf"))):
                rec[col] = None
            else:
                try:
                    rec[col] = val.item() if hasattr(val, "item") else val
                except Exception:
                    rec[col] = str(val)
        records.append(rec)
    return records

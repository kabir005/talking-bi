"""
Forecast Router - Time-series forecasting endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from typing import List, Optional
from database.db import get_db
from database.models import Dataset
from agents.forecast_agent import generate_forecast, forecast_multiple_columns
import pandas as pd

router = APIRouter()


class ForecastRequest(BaseModel):
    dataset_id: str
    target_column: str
    time_column: Optional[str] = None
    periods: int = 12
    method: str = "auto"  # "auto", "linear", "ma"


class MultiForecastRequest(BaseModel):
    dataset_id: str
    target_columns: List[str]
    time_column: Optional[str] = None
    periods: int = 12


@router.post("/generate")
async def create_forecast(
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate time-series forecast for a single column
    
    Returns forecast values, confidence intervals, and metrics
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == request.dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data
    if not dataset.sqlite_table_name:
        raise HTTPException(status_code=400, detail="Dataset table not found")
    
    try:
        query = f"SELECT * FROM {dataset.sqlite_table_name}"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Generate forecast
        forecast_result = await generate_forecast(
            df=df,
            target_column=request.target_column,
            time_column=request.time_column,
            periods=request.periods,
            method=request.method
        )
        
        if "error" in forecast_result:
            raise HTTPException(status_code=400, detail=forecast_result["error"])
        
        return {
            "dataset_id": request.dataset_id,
            "target_column": request.target_column,
            **forecast_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")


@router.post("/generate-multiple")
async def create_multiple_forecasts(
    request: MultiForecastRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate forecasts for multiple columns
    
    Useful for forecasting all KPIs at once
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == request.dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data
    if not dataset.sqlite_table_name:
        raise HTTPException(status_code=400, detail="Dataset table not found")
    
    try:
        query = f"SELECT * FROM {dataset.sqlite_table_name}"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")
        
        # Generate forecasts
        forecast_results = await forecast_multiple_columns(
            df=df,
            target_columns=request.target_columns,
            time_column=request.time_column,
            periods=request.periods
        )
        
        return {
            "dataset_id": request.dataset_id,
            **forecast_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")


@router.get("/auto-detect-time/{dataset_id}")
async def auto_detect_time_column(
    dataset_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Auto-detect time/date column in dataset
    
    Returns the detected column name or null
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data
    if not dataset.sqlite_table_name:
        raise HTTPException(status_code=400, detail="Dataset table not found")
    
    try:
        query = f"SELECT * FROM {dataset.sqlite_table_name} LIMIT 100"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        
        # Detect time column
        from agents.forecast_agent import _detect_time_column
        time_col = _detect_time_column(df)
        
        return {
            "dataset_id": dataset_id,
            "time_column": time_col,
            "detected": time_col is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Time column detection failed: {str(e)}")

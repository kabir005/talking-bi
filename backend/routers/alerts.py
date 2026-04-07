"""
Alerts Router - Configure and check alerts on datasets
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from typing import List, Dict, Any, Literal, Optional
from database.db import get_db
from database.models import Dataset
from services.alert_service import AlertEngine
import pandas as pd

router = APIRouter()


class ThresholdAlertConfig(BaseModel):
    column: str
    threshold: float
    condition: Literal["above", "below", "equal"] = "below"
    alert_name: Optional[str] = None


class ConsecutiveDeclineConfig(BaseModel):
    column: str
    periods: int = 3
    min_decline_pct: float = 5.0


class AnomalyDetectionConfig(BaseModel):
    column: str
    method: Literal["zscore", "iqr", "isolation_forest"] = "zscore"
    threshold: float = 3.0


class SpikeDetectionConfig(BaseModel):
    column: str
    threshold: float = 2.0


class AlertCheckRequest(BaseModel):
    dataset_id: str
    threshold_alerts: List[ThresholdAlertConfig] = []
    consecutive_decline: List[ConsecutiveDeclineConfig] = []
    anomaly_detection: List[AnomalyDetectionConfig] = []
    missing_data_threshold: float = 10.0
    spike_detection: List[SpikeDetectionConfig] = []


@router.post("/check")
async def check_alerts(
    request: AlertCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Run alert checks on a dataset
    
    Returns all triggered alerts with severity levels
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
        
        # Convert request to config dict
        config = {
            "threshold_alerts": [alert.dict() for alert in request.threshold_alerts],
            "consecutive_decline": [alert.dict() for alert in request.consecutive_decline],
            "anomaly_detection": [alert.dict() for alert in request.anomaly_detection],
            "missing_data_threshold": request.missing_data_threshold,
            "spike_detection": [alert.dict() for alert in request.spike_detection]
        }
        
        # Run all checks
        alert_result = await AlertEngine.run_all_checks(df, config)
        
        return {
            "dataset_id": request.dataset_id,
            "dataset_name": dataset.name,
            **alert_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert check failed: {str(e)}")


@router.post("/check-threshold")
async def check_threshold_alert(
    dataset_id: str,
    column: str,
    threshold: float,
    condition: Literal["above", "below", "equal"] = "below",
    db: AsyncSession = Depends(get_db)
):
    """Quick threshold check for a single column"""
    
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data
    try:
        query = f"SELECT * FROM {dataset.sqlite_table_name}"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        
        alerts = await AlertEngine.check_threshold_alerts(
            df, column, threshold, condition
        )
        
        return {
            "dataset_id": dataset_id,
            "column": column,
            "threshold": threshold,
            "condition": condition,
            "alerts": alerts,
            "triggered": len(alerts) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-anomalies")
async def check_anomalies(
    dataset_id: str,
    column: str,
    method: Literal["zscore", "iqr", "isolation_forest"] = "zscore",
    threshold: float = 3.0,
    db: AsyncSession = Depends(get_db)
):
    """Quick anomaly check for a single column"""
    
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data
    try:
        query = f"SELECT * FROM {dataset.sqlite_table_name}"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
        
        alerts = await AlertEngine.check_anomaly_alerts(
            df, column, method, threshold
        )
        
        return {
            "dataset_id": dataset_id,
            "column": column,
            "method": method,
            "threshold": threshold,
            "alerts": alerts,
            "anomaly_detected": len(alerts) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_alert_templates():
    """Get pre-configured alert templates"""
    return {
        "templates": [
            {
                "name": "Revenue Monitoring",
                "description": "Monitor revenue drops and spikes",
                "config": {
                    "threshold_alerts": [
                        {"column": "Revenue", "threshold": 50000, "condition": "below"}
                    ],
                    "consecutive_decline": [
                        {"column": "Revenue", "periods": 3, "min_decline_pct": 5.0}
                    ],
                    "spike_detection": [
                        {"column": "Revenue", "threshold": 2.0}
                    ]
                }
            },
            {
                "name": "Sales Performance",
                "description": "Track sales metrics and anomalies",
                "config": {
                    "threshold_alerts": [
                        {"column": "Sales", "threshold": 100, "condition": "below"}
                    ],
                    "anomaly_detection": [
                        {"column": "Sales", "method": "zscore", "threshold": 3.0}
                    ]
                }
            },
            {
                "name": "Data Quality",
                "description": "Monitor data completeness",
                "config": {
                    "missing_data_threshold": 10.0
                }
            }
        ]
    }

"""
Scenario Modeling Route
Multi-parameter what-if simulation with real-time KPI recalculation.
"""

import logging
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from database.db import get_db
from database.models import Dataset

logger = logging.getLogger(__name__)
router = APIRouter()


class SliderParam(BaseModel):
    """One adjustable parameter in the scenario."""
    column: str
    label: str
    change_pct: float = Field(ge=-100.0, le=500.0)
    change_type: str = "multiply"


class ScenarioRequest(BaseModel):
    dataset_id: str
    parameters: List[SliderParam]
    target_columns: Optional[List[str]] = None


class ScenarioResult(BaseModel):
    baseline_kpis: Dict[str, Any]
    projected_kpis: Dict[str, Any]
    delta_kpis: Dict[str, Any]
    chart_configs: List[Dict]
    narrative: str


@router.post("/simulate", response_model=ScenarioResult)
async def simulate_scenario(req: ScenarioRequest, db: AsyncSession = Depends(get_db)):
    """
    Apply parameter changes to a copy of the dataset,
    recalculate KPIs, return before/after comparison.
    """
    # Load dataset
    result = await db.execute(select(Dataset).where(Dataset.id == req.dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(404, "Dataset not found.")
    
    if not dataset.sqlite_table_name:
        raise HTTPException(400, "Generate dashboard first.")

    try:
        query = f"SELECT * FROM {dataset.sqlite_table_name}"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        df_baseline = pd.DataFrame(rows, columns=columns)
    except Exception as e:
        raise HTTPException(500, f"Failed to load dataset: {e}")

    # Get numeric columns
    numeric_cols = df_baseline.select_dtypes(include=['number']).columns.tolist()

    # Validate parameters
    for param in req.parameters:
        if param.column not in df_baseline.columns:
            raise HTTPException(422, f"Column '{param.column}' not found.")
        if param.column not in numeric_cols:
            raise HTTPException(422, f"Column '{param.column}' is not numeric.")

    # Apply changes to a copy
    df_projected = df_baseline.copy()
    for param in req.parameters:
        if param.change_type == "multiply":
            multiplier = 1.0 + (param.change_pct / 100.0)
            df_projected[param.column] = df_projected[param.column] * multiplier
        elif param.change_type == "add":
            delta = df_baseline[param.column].mean() * (param.change_pct / 100.0)
            df_projected[param.column] = df_projected[param.column] + delta
        elif param.change_type == "set":
            df_projected[param.column] = param.change_pct

    # Compute KPIs
    target_cols = req.target_columns or numeric_cols[:5]
    baseline_kpis = _compute_kpis(df_baseline, target_cols)
    projected_kpis = _compute_kpis(df_projected, target_cols)

    # Compute deltas
    delta_kpis = {}
    for label in baseline_kpis:
        b_total = baseline_kpis[label].get("total") or 0
        p_total = projected_kpis.get(label, {}).get("total") or 0
        if b_total != 0:
            delta_kpis[label] = round((p_total - b_total) / abs(b_total) * 100, 2)
        else:
            delta_kpis[label] = 0.0

    # Build comparison charts
    chart_configs = _build_comparison_charts(df_baseline, df_projected, target_cols)

    # Generate narrative
    narrative = _generate_scenario_narrative(req.parameters, delta_kpis)

    return ScenarioResult(
        baseline_kpis=baseline_kpis,
        projected_kpis=projected_kpis,
        delta_kpis=delta_kpis,
        chart_configs=chart_configs,
        narrative=narrative
    )


@router.get("/parameters/{dataset_id}")
async def get_scenario_parameters(dataset_id: str, db: AsyncSession = Depends(get_db)):
    """Return suggested slider parameters for this dataset."""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(404, "Dataset not found.")

    try:
        query = f"SELECT * FROM {dataset.sqlite_table_name}"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(rows, columns=columns)
    except Exception as e:
        raise HTTPException(500, f"Failed to load dataset: {e}")

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    suggested = numeric_cols[:5]

    params = []
    for col in suggested:
        params.append({
            "column": col,
            "label": col.replace("_", " ").title(),
            "min_pct": -50,
            "max_pct": 100,
            "default_pct": 0,
            "step": 1,
            "current_mean": float(df[col].mean()) if not df[col].isna().all() else 0,
            "change_type": "multiply"
        })

    targets = [c for c in numeric_cols if c not in suggested][:3]

    return {
        "parameters": params,
        "watch_columns": targets,
        "note": "Adjust sliders to simulate business scenarios. KPIs update in real-time."
    }


def _compute_kpis(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
    """Compute KPIs for given columns."""
    kpis = {}
    for col in columns:
        if col not in df.columns:
            continue
        try:
            kpis[col] = {
                "total": float(df[col].sum()),
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std())
            }
        except Exception:
            kpis[col] = {"total": 0, "mean": 0, "median": 0, "std": 0}
    return kpis


def _build_comparison_charts(
    df_baseline: pd.DataFrame,
    df_projected: pd.DataFrame,
    target_cols: List[str]
) -> List[Dict]:
    """Build side-by-side comparison charts."""
    charts = []
    for col in target_cols[:3]:
        if col not in df_baseline.columns:
            continue
        try:
            charts.append({
                "type": "comparison_bar",
                "title": f"{col.replace('_', ' ').title()} — Baseline vs Projected",
                "data": [
                    {"label": "Baseline", "value": round(float(df_baseline[col].sum()), 2)},
                    {"label": "Projected", "value": round(float(df_projected[col].sum()), 2)}
                ],
                "xKey": "label",
                "yKey": "value"
            })
        except Exception as e:
            logger.warning(f"Comparison chart failed for {col}: {e}")
    return charts


def _generate_scenario_narrative(params: List[SliderParam], delta_kpis: Dict[str, float]) -> str:
    """Fast rule-based narrative."""
    if not params or not delta_kpis:
        return "No significant impact detected with current parameters."

    param_desc = ", ".join(
        f"{p.label} {'+' if p.change_pct >= 0 else ''}{p.change_pct:.0f}%"
        for p in params
        if p.change_pct != 0
    )
    
    if not param_desc:
        return "No changes applied yet. Drag a slider to simulate."

    biggest_delta_label = max(delta_kpis, key=lambda k: abs(delta_kpis[k]))
    biggest_delta_val = delta_kpis[biggest_delta_label]
    direction = "increase" if biggest_delta_val > 0 else "decrease"

    return (
        f"With {param_desc}, the model projects a {abs(biggest_delta_val):.1f}% "
        f"{direction} in {biggest_delta_label}."
    )

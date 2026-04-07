"""NL Query Route — POST /api/nl-query/
Natural language to pandas execution pipeline.
Integrates with existing dataset storage and chart generator."""

import logging
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from database.db import get_db
from database.models import Dataset
from services.intent_classifier import classify_intent
from services.query_executor import execute

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_TABLE_ROWS = 500


class NLQueryRequest(BaseModel):
    dataset_id: str
    query: str


def _build_bar_chart(result: pd.DataFrame, x_col: str, y_col: str, title: str, top_n: int = 20) -> dict:
    """Build bar chart config"""
    df_chart = result.head(top_n)
    return {
        "type": "bar",
        "title": title,
        "data": {
            "labels": df_chart[x_col].astype(str).tolist(),
            "datasets": [{
                "label": y_col,
                "data": df_chart[y_col].tolist()
            }]
        }
    }


def _build_line_chart(result: pd.DataFrame, x_col: str, y_col: str, title: str) -> dict:
    """Build line chart config"""
    return {
        "type": "line",
        "title": title,
        "data": {
            "labels": result[x_col].astype(str).tolist(),
            "datasets": [{
                "label": y_col,
                "data": result[y_col].tolist()
            }]
        }
    }


def _build_pie_chart(result: pd.DataFrame, label_col: str, value_col: str, title: str) -> dict:
    """Build pie chart config"""
    df_chart = result.head(10)
    return {
        "type": "pie",
        "title": title,
        "data": {
            "labels": df_chart[label_col].astype(str).tolist(),
            "datasets": [{
                "data": df_chart[value_col].tolist()
            }]
        }
    }


def _build_scatter(result: pd.DataFrame, x_col: str, y_col: str, title: str) -> dict:
    """Build scatter chart config"""
    return {
        "type": "scatter",
        "title": title,
        "data": {
            "datasets": [{
                "label": f"{x_col} vs {y_col}",
                "data": [{"x": row[x_col], "y": row[y_col]} for _, row in result.iterrows()]
            }]
        }
    }


def _build_histogram(result: pd.DataFrame, col: str, title: str) -> dict:
    """Build histogram config"""
    return {
        "type": "bar",
        "title": title,
        "data": {
            "labels": result[col].astype(str).tolist(),
            "datasets": [{
                "label": col,
                "data": result[col].tolist()
            }]
        }
    }


def _auto_chart(result: pd.DataFrame, intent_op: str, query: str) -> dict | None:
    """Select best chart for query result."""
    if result.empty or len(result.columns) < 2:
        return None
    
    try:
        cols = list(result.columns)
        num_cols = result.select_dtypes(include="number").columns.tolist()
        str_cols = result.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = [c for c in cols if any(kw in c.lower() for kw in ["date", "period", "month", "year", "week"])]
        
        # Time series → line chart
        if date_cols and num_cols:
            return _build_line_chart(result, date_cols[0], num_cols[0], query)
        
        # Groupby/topn → bar chart
        if intent_op in ("groupby", "topn", "having", "value_counts") and str_cols and num_cols:
            return _build_bar_chart(result, str_cols[0], num_cols[0], query, top_n=20)
        
        # Correlation → scatter
        if intent_op == "corr" and len(num_cols) >= 2:
            return _build_scatter(result, num_cols[0], num_cols[1], query)
        
        # Describe → histogram
        if intent_op == "describe" and num_cols:
            return _build_histogram(result.select_dtypes("number").iloc[:, 0].to_frame(), num_cols[0], query)
        
        # Default: bar chart if we have categorical + numeric
        if str_cols and num_cols:
            return _build_bar_chart(result, str_cols[0], num_cols[0], query, top_n=20)
        
    except Exception as e:
        logger.warning(f"Auto chart failed: {e}")
    
    return None


@router.post("/")
async def run_nl_query(req: NLQueryRequest, db: AsyncSession = Depends(get_db)):
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty.")
    
    if len(req.query) > 500:
        raise HTTPException(400, "Query too long (max 500 chars).")
    
    # Load dataset using existing DB layer
    result = await db.execute(select(Dataset).where(Dataset.id == req.dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(404, "Dataset not found.")
    
    if not dataset.schema_json:
        raise HTTPException(400, "Run /api/dashboards/generate/{dataset_id} first to process the dataset.")
    
    # Load data from SQLite table
    table_name = dataset.sqlite_table_name
    
    if not table_name:
        raise HTTPException(400, "Dataset table not found in database")
    
    try:
        query = f"SELECT * FROM {table_name}"
        result = await db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        
        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
    except Exception as e:
        raise HTTPException(500, f"Failed to load dataset: {e}")
    
    schema = dataset.schema_json
    
    # Classify intent
    intent = await classify_intent(req.query, schema)
    
    # Execute query
    result_df, summary = execute(df, intent, schema)
    
    # Prepare response
    total_rows = len(result_df)
    display_df = result_df.head(MAX_TABLE_ROWS)
    
    records = []
    for _, row in display_df.iterrows():
        rec = {}
        for col, val in row.items():
            try:
                is_na = pd.isna(val) if not isinstance(val, (list, dict)) else False
            except Exception:
                is_na = False
            
            if is_na:
                rec[col] = None
            elif isinstance(val, float) and (val == float("inf") or val == float("-inf")):
                rec[col] = None
            else:
                try:
                    rec[col] = val.item() if hasattr(val, "item") else val
                except Exception:
                    rec[col] = str(val)
        records.append(rec)
    
    # Auto-generate chart
    chart = _auto_chart(result_df, intent.op, req.query)
    
    return {
        "success": True,
        "query": req.query,
        "intent": intent.model_dump(),
        "result": records,
        "total_rows": total_rows,
        "displayed_rows": len(records),
        "truncated": total_rows > MAX_TABLE_ROWS,
        "columns": list(display_df.columns),
        "summary": summary,
        "chart_config": chart
    }

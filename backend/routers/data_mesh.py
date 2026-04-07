"""
Data Mesh Route — Multi-Dataset Cross-Correlation Analysis
"""

import logging
import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from database.db import get_db
from database.models import Dataset
from utils.llm import call_llm

logger = logging.getLogger(__name__)
router = APIRouter()


class MergeConfig(BaseModel):
    dataset_id_a: str
    dataset_id_b: str
    join_key_a: str
    join_key_b: str
    join_type: str = "inner"
    user_question: Optional[str] = None


class JoinSuggestion(BaseModel):
    col_a: str
    col_b: str
    confidence: float
    reason: str


@router.post("/suggest-joins")
async def suggest_join_keys(
    dataset_id_a: str,
    dataset_id_b: str,
    db: AsyncSession = Depends(get_db)
):
    """Auto-detect candidate join columns between two datasets."""
    # Load datasets
    result_a = await db.execute(select(Dataset).where(Dataset.id == dataset_id_a))
    dataset_a = result_a.scalar_one_or_none()
    
    result_b = await db.execute(select(Dataset).where(Dataset.id == dataset_id_b))
    dataset_b = result_b.scalar_one_or_none()
    
    if not dataset_a:
        raise HTTPException(404, f"Dataset A ({dataset_id_a}) not found.")
    if not dataset_b:
        raise HTTPException(404, f"Dataset B ({dataset_id_b}) not found.")
    
    try:
        # Load dataframes
        query_a = f"SELECT * FROM {dataset_a.sqlite_table_name}"
        result = await db.execute(text(query_a))
        rows_a = result.fetchall()
        columns_a = result.keys()
        df_a = pd.DataFrame(rows_a, columns=columns_a)
        
        query_b = f"SELECT * FROM {dataset_b.sqlite_table_name}"
        result = await db.execute(text(query_b))
        rows_b = result.fetchall()
        columns_b = result.keys()
        df_b = pd.DataFrame(rows_b, columns=columns_b)
    except Exception as e:
        raise HTTPException(500, f"Failed to load datasets: {e}")
    
    suggestions = []
    for col_a in df_a.columns:
        for col_b in df_b.columns:
            confidence, reason = _score_join_pair(df_a, df_b, col_a, col_b)
            if confidence > 0.3:
                suggestions.append(JoinSuggestion(
                    col_a=col_a,
                    col_b=col_b,
                    confidence=round(confidence, 2),
                    reason=reason
                ))
    
    suggestions.sort(key=lambda x: x.confidence, reverse=True)
    
    return {
        "suggestions": [s.model_dump() for s in suggestions[:5]],
        "dataset_a_name": dataset_a.name,
        "dataset_b_name": dataset_b.name,
        "dataset_a_cols": list(df_a.columns),
        "dataset_b_cols": list(df_b.columns),
    }


@router.post("/analyze")
async def cross_dataset_analysis(
    config: MergeConfig,
    db: AsyncSession = Depends(get_db)
):
    """Perform cross-dataset correlation analysis."""
    # Load datasets
    result_a = await db.execute(select(Dataset).where(Dataset.id == config.dataset_id_a))
    dataset_a = result_a.scalar_one_or_none()
    
    result_b = await db.execute(select(Dataset).where(Dataset.id == config.dataset_id_b))
    dataset_b = result_b.scalar_one_or_none()
    
    if not dataset_a or not dataset_b:
        raise HTTPException(404, "One or both datasets not found.")
    
    try:
        # Load dataframes
        query_a = f"SELECT * FROM {dataset_a.sqlite_table_name}"
        result = await db.execute(text(query_a))
        rows_a = result.fetchall()
        columns_a = result.keys()
        df_a = pd.DataFrame(rows_a, columns=columns_a)
        
        query_b = f"SELECT * FROM {dataset_b.sqlite_table_name}"
        result = await db.execute(text(query_b))
        rows_b = result.fetchall()
        columns_b = result.keys()
        df_b = pd.DataFrame(rows_b, columns=columns_b)
    except Exception as e:
        raise HTTPException(500, f"Failed to load: {e}")
    
    # Validate join keys
    if config.join_key_a not in df_a.columns:
        raise HTTPException(422, f"Join key '{config.join_key_a}' not in Dataset A.")
    if config.join_key_b not in df_b.columns:
        raise HTTPException(422, f"Join key '{config.join_key_b}' not in Dataset B.")
    
    # Rename join key in B to match A
    df_b_renamed = df_b.rename(columns={config.join_key_b: config.join_key_a})
    
    # Merge
    df_merged = pd.merge(
        df_a, df_b_renamed,
        on=config.join_key_a,
        how=config.join_type,
        suffixes=("_A", "_B")
    )
    
    if df_merged.empty:
        return {
            "success": False,
            "error": "No matching rows found. Try a different join key or join type.",
            "merged_rows": 0
        }
    
    # Cap for analysis
    if len(df_merged) > 50000:
        df_merged = df_merged.sample(50000, random_state=42)
    
    # Cross-dataset correlation
    num_cols = df_merged.select_dtypes(include="number").columns.tolist()
    correlations = []
    
    if len(num_cols) >= 2:
        corr_matrix = df_merged[num_cols].corr(numeric_only=True)
        cols_a = [c for c in num_cols if c.endswith("_A") or (c in df_a.columns and c not in df_b.columns)]
        cols_b = [c for c in num_cols if c.endswith("_B") or (c in df_b.columns and c not in df_a.columns)]
        
        for ca in cols_a[:5]:
            for cb in cols_b[:5]:
                if ca in corr_matrix.index and cb in corr_matrix.columns:
                    r = corr_matrix.loc[ca, cb]
                    if not pd.isna(r) and abs(r) > 0.3:
                        correlations.append({
                            "col_a": ca,
                            "col_b": cb,
                            "r": round(float(r), 3),
                            "strength": "strong" if abs(r) > 0.7 else "moderate",
                            "direction": "positive" if r > 0 else "negative"
                        })
        
        correlations.sort(key=lambda x: abs(x["r"]), reverse=True)
    
    # Build cross-dataset chart
    cross_chart = None
    if correlations:
        top = correlations[0]
        try:
            temp = df_merged[[top["col_a"], top["col_b"]]].dropna().sample(
                min(500, len(df_merged)), random_state=42
            )
            cross_chart = {
                "type": "scatter",
                "title": f"Cross-Dataset: {top['col_a']} vs {top['col_b']} (r={top['r']})",
                "data": [
                    {"x": float(row[top["col_a"]]), "y": float(row[top["col_b"]])}
                    for _, row in temp.iterrows()
                ],
                "xKey": "x",
                "yKey": "y"
            }
        except Exception:
            pass
    
    # LLM narration
    narrative = await _narrate_cross_analysis(
        correlations=correlations,
        merged_rows=len(df_merged),
        name_a=dataset_a.name,
        name_b=dataset_b.name,
        user_question=config.user_question
    )
    
    # Generate insights
    insights = _generate_correlation_insights(
        correlations=correlations,
        merged_rows=len(df_merged),
        total_rows_a=len(df_a),
        total_rows_b=len(df_b),
        name_a=dataset_a.name,
        name_b=dataset_b.name
    )
    
    return {
        "success": True,
        "merged_rows": len(df_merged),
        "correlations": correlations[:10],
        "top_correlation": correlations[0] if correlations else None,
        "cross_chart": cross_chart,
        "narrative": narrative,
        "insights": insights,
        "merged_columns": list(df_merged.columns),
        "datasets": {
            "a": {"name": dataset_a.name, "rows": len(df_a)},
            "b": {"name": dataset_b.name, "rows": len(df_b)}
        }
    }


def _score_join_pair(df_a: pd.DataFrame, df_b: pd.DataFrame, col_a: str, col_b: str):
    """Score how likely two columns are good join keys."""
    score = 0.0
    reasons = []
    
    # Exact name match
    if col_a.lower() == col_b.lower():
        score += 0.5
        reasons.append("exact name match")
    # Similar name
    elif col_a.lower() in col_b.lower() or col_b.lower() in col_a.lower():
        score += 0.3
        reasons.append("similar name")
    
    # Same dtype
    if df_a[col_a].dtype == df_b[col_b].dtype:
        score += 0.2
        reasons.append("same dtype")
    
    # Overlapping values
    try:
        vals_a = set(df_a[col_a].dropna().astype(str).head(100))
        vals_b = set(df_b[col_b].dropna().astype(str).head(100))
        if vals_a and vals_b:
            overlap = len(vals_a & vals_b) / max(len(vals_a), len(vals_b))
            if overlap > 0.5:
                score += 0.3
                reasons.append(f"{overlap:.0%} value overlap")
            elif overlap > 0.2:
                score += 0.1
                reasons.append(f"{overlap:.0%} partial overlap")
    except Exception:
        pass
    
    return min(score, 1.0), ", ".join(reasons) or "low similarity"


async def _narrate_cross_analysis(
    correlations, merged_rows, name_a, name_b, user_question
):
    """LLM narration of cross-dataset findings."""
    if not correlations:
        return f"No significant cross-dataset correlations found between {name_a} and {name_b} after merging {merged_rows:,} rows."
    
    corr_text = "\n".join([
        f"- {c['col_a']} vs {c['col_b']}: r={c['r']} ({c['strength']} {c['direction']} correlation)"
        for c in correlations[:5]
    ])
    
    question_line = f"\nUser question: {user_question}" if user_question else ""
    
    prompt = f"""You are a business intelligence analyst. Two datasets were merged ({merged_rows:,} matching rows):
Dataset A: {name_a}
Dataset B: {name_b}{question_line}

Cross-dataset correlations found:
{corr_text}

Write a 2-3 sentence business insight explaining what these correlations mean.
Be specific about which datasets and columns are correlated. State whether the user's question can be answered.
Do not invent data not in the correlations above."""
    
    try:
        return await call_llm(
            messages=[{"role": "user", "content": prompt}],
            system="You are a concise, accurate business intelligence analyst. Never hallucinate data.",
        )
    except Exception:
        top = correlations[0]
        return f"Found a {top['strength']} {top['direction']} correlation (r={top['r']}) between {top['col_a']} ({name_a}) and {top['col_b']} ({name_b})."


def _generate_correlation_insights(
    correlations: List[Dict],
    merged_rows: int,
    total_rows_a: int,
    total_rows_b: int,
    name_a: str,
    name_b: str
) -> List[Dict[str, str]]:
    """Generate actionable insights from correlation analysis"""
    insights = []
    
    # Join success rate
    join_rate = (merged_rows / min(total_rows_a, total_rows_b)) * 100 if min(total_rows_a, total_rows_b) > 0 else 0
    
    if join_rate < 50:
        insights.append({
            "type": "data_quality",
            "severity": "medium",
            "title": "Low Join Match Rate",
            "message": f"Only {join_rate:.1f}% of rows matched between datasets ({merged_rows:,} out of {min(total_rows_a, total_rows_b):,})",
            "recommendation": "Check if join keys are correct. Low match rate may indicate data quality issues or incorrect key selection."
        })
    elif join_rate > 90:
        insights.append({
            "type": "data_quality",
            "severity": "low",
            "title": "Excellent Join Match Rate",
            "message": f"{join_rate:.1f}% of rows matched successfully ({merged_rows:,} rows)",
            "recommendation": "High match rate indicates good data quality and correct join key selection."
        })
    
    # Strong correlations
    strong_corrs = [c for c in correlations if abs(c['r']) > 0.7]
    if strong_corrs:
        top = strong_corrs[0]
        insights.append({
            "type": "correlation",
            "severity": "high",
            "title": f"Strong Correlation Detected",
            "message": f"{top['col_a']} and {top['col_b']} have a {top['strength']} {top['direction']} correlation (r={top['r']})",
            "recommendation": f"This strong relationship suggests {top['col_a']} from {name_a} can predict or is influenced by {top['col_b']} from {name_b}. Consider using this for forecasting or root cause analysis."
        })
    
    # Moderate correlations
    moderate_corrs = [c for c in correlations if 0.4 < abs(c['r']) <= 0.7]
    if moderate_corrs and not strong_corrs:
        insights.append({
            "type": "correlation",
            "severity": "medium",
            "title": "Moderate Correlations Found",
            "message": f"Found {len(moderate_corrs)} moderate correlations between datasets",
            "recommendation": "These relationships may be useful for analysis but aren't strong enough for reliable predictions. Investigate further with domain knowledge."
        })
    
    # Negative correlations
    negative_corrs = [c for c in correlations if c['r'] < -0.5]
    if negative_corrs:
        top_neg = negative_corrs[0]
        insights.append({
            "type": "correlation",
            "severity": "medium",
            "title": "Inverse Relationship Detected",
            "message": f"{top_neg['col_a']} and {top_neg['col_b']} move in opposite directions (r={top_neg['r']})",
            "recommendation": f"When {top_neg['col_a']} increases, {top_neg['col_b']} tends to decrease. This inverse relationship could indicate trade-offs or competing factors."
        })
    
    # No significant correlations
    if not correlations:
        insights.append({
            "type": "correlation",
            "severity": "low",
            "title": "No Significant Correlations",
            "message": f"No strong correlations found between {name_a} and {name_b}",
            "recommendation": "The datasets may be independent, or correlations may be non-linear. Try different join keys or consider time-lagged analysis."
        })
    
    # Data coverage insight
    if len(correlations) > 5:
        insights.append({
            "type": "summary",
            "severity": "low",
            "title": "Rich Cross-Dataset Relationships",
            "message": f"Discovered {len(correlations)} significant correlations across datasets",
            "recommendation": "Multiple relationships detected. Prioritize strong correlations for business decisions and further investigation."
        })
    
    return insights

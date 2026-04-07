from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from database.db import get_db
from database.models import Dataset
from typing import List, Dict, Any, Optional
import pandas as pd

router = APIRouter()


class DrillDownRequest(BaseModel):
    dataset_id: str
    column: str
    value: Optional[str] = None
    parent_filters: Optional[Dict[str, str]] = None


class DrillDownLevel(BaseModel):
    column: str
    values: List[Dict[str, Any]]
    total_count: int


@router.post("/levels")
async def get_drill_down_levels(
    request: DrillDownRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get available drill-down levels for a column.
    Returns unique values and their counts.
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == request.dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data from SQLite
    table_name = dataset.sqlite_table_name
    query = f"SELECT * FROM {table_name}"
    result = await db.execute(text(query))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty")
    
    # Apply parent filters if provided
    if request.parent_filters:
        for col, val in request.parent_filters.items():
            if col in df.columns:
                df = df[df[col].astype(str) == str(val)]
    
    # Get unique values for the requested column
    if request.column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{request.column}' not found")
    
    # Group by column and count
    value_counts = df[request.column].value_counts().reset_index()
    value_counts.columns = ['value', 'count']
    
    # Convert to list of dicts
    values = []
    for _, row in value_counts.iterrows():
        values.append({
            'value': str(row['value']),
            'count': int(row['count']),
            'percentage': round((row['count'] / len(df)) * 100, 2)
        })
    
    return {
        'column': request.column,
        'values': values,
        'total_count': len(df),
        'unique_count': len(values)
    }


@router.post("/data")
async def get_drill_down_data(
    request: DrillDownRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get filtered data for a specific drill-down level.
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == request.dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data from SQLite
    table_name = dataset.sqlite_table_name
    query = f"SELECT * FROM {table_name}"
    result = await db.execute(text(query))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty")
    
    # Apply parent filters
    if request.parent_filters:
        for col, val in request.parent_filters.items():
            if col in df.columns:
                df = df[df[col].astype(str) == str(val)]
    
    # Apply current level filter
    if request.value:
        if request.column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{request.column}' not found")
        df = df[df[request.column].astype(str) == str(request.value)]
    
    # Get summary statistics
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != '_is_outlier']
    
    summary = {}
    for col in numeric_cols[:5]:  # Top 5 numeric columns
        summary[col] = {
            'sum': float(df[col].sum()),
            'mean': float(df[col].mean()),
            'median': float(df[col].median()),
            'min': float(df[col].min()),
            'max': float(df[col].max())
        }
    
    return {
        'row_count': len(df),
        'summary': summary,
        'sample_data': df.head(10).to_dict('records')
    }


@router.post("/suggest-next")
async def suggest_next_drill_down(
    request: DrillDownRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Suggest the next best column to drill down into.
    Based on cardinality and data distribution.
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == request.dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data from SQLite
    table_name = dataset.sqlite_table_name
    query = f"SELECT * FROM {table_name}"
    result = await db.execute(text(query))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty")
    
    # Apply filters
    if request.parent_filters:
        for col, val in request.parent_filters.items():
            if col in df.columns:
                df = df[df[col].astype(str) == str(val)]
    
    if request.value and request.column in df.columns:
        df = df[df[request.column].astype(str) == str(request.value)]
    
    # Analyze columns for drill-down potential
    suggestions = []
    
    # Get categorical columns (excluding already used ones)
    used_columns = set(request.parent_filters.keys() if request.parent_filters else [])
    if request.column:
        used_columns.add(request.column)
    
    for col in df.columns:
        if col in used_columns or col == '_is_outlier':
            continue
        
        # Check if column is categorical or has reasonable cardinality
        unique_count = df[col].nunique()
        total_count = len(df)
        
        # Good drill-down candidates: 2-50 unique values
        if 2 <= unique_count <= 50:
            cardinality_ratio = unique_count / total_count
            
            # Calculate distribution entropy (how evenly distributed)
            value_counts = df[col].value_counts()
            distribution_score = 1 - (value_counts.max() / total_count)  # Higher = more even
            
            suggestions.append({
                'column': col,
                'unique_count': int(unique_count),
                'cardinality_ratio': round(cardinality_ratio, 3),
                'distribution_score': round(distribution_score, 3),
                'score': round((1 - cardinality_ratio) * distribution_score * 100, 2)
            })
    
    # Sort by score (descending)
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'suggestions': suggestions[:5],  # Top 5 suggestions
        'current_level': request.column,
        'current_value': request.value
    }


@router.post("/time-drill")
async def time_drill_down(
    dataset_id: str,
    time_column: str,
    granularity: str,  # year, quarter, month, week, day
    filters: Optional[Dict[str, str]] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Specialized drill-down for time-based columns.
    Supports: year -> quarter -> month -> week -> day
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data from SQLite
    table_name = dataset.sqlite_table_name
    query = f"SELECT * FROM {table_name}"
    result = await db.execute(text(query))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty")
    
    # Apply filters
    if filters:
        for col, val in filters.items():
            if col in df.columns:
                df = df[df[col].astype(str) == str(val)]
    
    # Check if time column exists
    if time_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{time_column}' not found")
    
    # Convert to datetime
    try:
        df[time_column] = pd.to_datetime(df[time_column])
    except:
        raise HTTPException(status_code=400, detail=f"Column '{time_column}' is not a valid date column")
    
    # Extract time components based on granularity
    if granularity == 'year':
        df['_time_group'] = df[time_column].dt.year
    elif granularity == 'quarter':
        df['_time_group'] = df[time_column].dt.to_period('Q').astype(str)
    elif granularity == 'month':
        df['_time_group'] = df[time_column].dt.to_period('M').astype(str)
    elif granularity == 'week':
        df['_time_group'] = df[time_column].dt.to_period('W').astype(str)
    elif granularity == 'day':
        df['_time_group'] = df[time_column].dt.date.astype(str)
    else:
        raise HTTPException(status_code=400, detail="Invalid granularity. Use: year, quarter, month, week, or day")
    
    # Group by time and get counts
    time_groups = df.groupby('_time_group').size().reset_index(name='count')
    time_groups = time_groups.sort_values('_time_group')
    
    # Get numeric summaries
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != '_is_outlier']
    
    summaries = []
    for _, row in time_groups.iterrows():
        period_data = df[df['_time_group'] == row['_time_group']]
        
        period_summary = {
            'period': str(row['_time_group']),
            'count': int(row['count'])
        }
        
        # Add numeric summaries
        for col in numeric_cols[:3]:  # Top 3 numeric columns
            period_summary[f'{col}_sum'] = float(period_data[col].sum())
            period_summary[f'{col}_mean'] = float(period_data[col].mean())
        
        summaries.append(period_summary)
    
    return {
        'granularity': granularity,
        'time_column': time_column,
        'periods': summaries,
        'total_periods': len(summaries)
    }

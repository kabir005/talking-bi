from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from database.db import get_db
from database.models import Dataset
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

router = APIRouter()


class FilterConfig(BaseModel):
    column: str
    operator: str  # equals, contains, greater_than, less_than, between, in
    value: Any
    type: str  # string, number, date


class ApplyFiltersRequest(BaseModel):
    dataset_id: str
    filters: List[FilterConfig]
    return_data: bool = False
    limit: Optional[int] = 1000


class FilterSuggestion(BaseModel):
    column: str
    suggested_values: List[Any]
    value_counts: Dict[str, int]


@router.post("/apply")
async def apply_filters(
    request: ApplyFiltersRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Apply filters to dataset and return filtered data or summary.
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
    
    original_count = len(df)
    
    # Apply each filter
    for filter_config in request.filters:
        col = filter_config.column
        op = filter_config.operator
        val = filter_config.value
        col_type = filter_config.type
        
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{col}' not found")
        
        # Apply filter based on operator and type
        try:
            if col_type == 'number':
                # Convert column to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
                val_numeric = float(val) if not isinstance(val, list) else [float(v) for v in val]
                
                if op == 'equals':
                    df = df[df[col] == val_numeric]
                elif op == 'greater_than':
                    df = df[df[col] > val_numeric]
                elif op == 'less_than':
                    df = df[df[col] < val_numeric]
                elif op == 'between':
                    if isinstance(val_numeric, list) and len(val_numeric) == 2:
                        df = df[(df[col] >= val_numeric[0]) & (df[col] <= val_numeric[1])]
                    else:
                        raise HTTPException(status_code=400, detail="Between operator requires array of 2 values")
                elif op == 'in':
                    if isinstance(val_numeric, list):
                        df = df[df[col].isin(val_numeric)]
                    else:
                        raise HTTPException(status_code=400, detail="In operator requires array of values")
            
            elif col_type == 'date':
                # Convert column to datetime
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
                if isinstance(val, list):
                    val_dates = [pd.to_datetime(v) for v in val]
                else:
                    val_dates = pd.to_datetime(val)
                
                if op == 'equals':
                    df = df[df[col].dt.date == val_dates.date()]
                elif op == 'greater_than':
                    df = df[df[col] > val_dates]
                elif op == 'less_than':
                    df = df[df[col] < val_dates]
                elif op == 'between':
                    if isinstance(val_dates, list) and len(val_dates) == 2:
                        df = df[(df[col] >= val_dates[0]) & (df[col] <= val_dates[1])]
                    else:
                        raise HTTPException(status_code=400, detail="Between operator requires array of 2 dates")
            
            else:  # string
                df[col] = df[col].astype(str)
                val_str = str(val) if not isinstance(val, list) else [str(v) for v in val]
                
                if op == 'equals':
                    df = df[df[col] == val_str]
                elif op == 'contains':
                    df = df[df[col].str.contains(val_str, case=False, na=False)]
                elif op == 'in':
                    if isinstance(val_str, list):
                        df = df[df[col].isin(val_str)]
                    else:
                        raise HTTPException(status_code=400, detail="In operator requires array of values")
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error applying filter on '{col}': {str(e)}")
    
    filtered_count = len(df)
    
    # Prepare response
    response = {
        'original_count': original_count,
        'filtered_count': filtered_count,
        'rows_removed': original_count - filtered_count,
        'percentage_remaining': round((filtered_count / original_count) * 100, 2) if original_count > 0 else 0
    }
    
    # Add summary statistics
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != '_is_outlier']
    
    summary = {}
    for col in numeric_cols[:5]:
        summary[col] = {
            'sum': float(df[col].sum()),
            'mean': float(df[col].mean()),
            'median': float(df[col].median()),
            'min': float(df[col].min()),
            'max': float(df[col].max())
        }
    
    response['summary'] = summary
    
    # Return data if requested
    if request.return_data:
        limit = min(request.limit, 1000)  # Max 1000 rows
        response['data'] = df.head(limit).to_dict('records')
    
    return response


@router.post("/validate")
async def validate_filter(
    dataset_id: str,
    filter_config: FilterConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate a filter configuration before applying.
    Returns whether the filter is valid and how many rows it would affect.
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
        return {'valid': False, 'error': 'Dataset is empty'}
    
    # Check if column exists
    if filter_config.column not in df.columns:
        return {'valid': False, 'error': f"Column '{filter_config.column}' not found"}
    
    # Try to apply filter
    try:
        original_count = len(df)
        col = filter_config.column
        
        # Apply filter (simplified validation)
        if filter_config.type == 'number':
            df[col] = pd.to_numeric(df[col], errors='coerce')
            val = float(filter_config.value) if not isinstance(filter_config.value, list) else filter_config.value
        elif filter_config.type == 'date':
            df[col] = pd.to_datetime(df[col], errors='coerce')
        else:
            df[col] = df[col].astype(str)
        
        # Count non-null values after conversion
        valid_count = df[col].notna().sum()
        
        return {
            'valid': True,
            'total_rows': original_count,
            'valid_values': int(valid_count),
            'null_values': original_count - int(valid_count),
            'estimated_result_count': int(valid_count)  # Rough estimate
        }
    
    except Exception as e:
        return {'valid': False, 'error': str(e)}


@router.get("/suggestions/{dataset_id}/{column}")
async def get_filter_suggestions(
    dataset_id: str,
    column: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get suggested filter values for a column.
    Returns top N most common values.
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
    
    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")
    
    # Get value counts
    value_counts = df[column].value_counts().head(limit)
    
    suggestions = []
    value_count_dict = {}
    
    for val, count in value_counts.items():
        suggestions.append(str(val))
        value_count_dict[str(val)] = int(count)
    
    return {
        'column': column,
        'suggested_values': suggestions,
        'value_counts': value_count_dict,
        'total_unique': int(df[column].nunique()),
        'total_rows': len(df)
    }


@router.post("/range")
async def get_filter_range(
    dataset_id: str,
    column: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the range of values for a numeric or date column.
    Useful for setting up range filters.
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
    
    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' not found")
    
    # Try numeric first
    try:
        df[column] = pd.to_numeric(df[column], errors='coerce')
        df_clean = df[df[column].notna()]
        
        if len(df_clean) > 0:
            return {
                'column': column,
                'type': 'number',
                'min': float(df_clean[column].min()),
                'max': float(df_clean[column].max()),
                'mean': float(df_clean[column].mean()),
                'median': float(df_clean[column].median()),
                'quartiles': {
                    'q1': float(df_clean[column].quantile(0.25)),
                    'q2': float(df_clean[column].quantile(0.50)),
                    'q3': float(df_clean[column].quantile(0.75))
                }
            }
    except:
        pass
    
    # Try date
    try:
        df[column] = pd.to_datetime(df[column], errors='coerce')
        df_clean = df[df[column].notna()]
        
        if len(df_clean) > 0:
            return {
                'column': column,
                'type': 'date',
                'min': df_clean[column].min().isoformat(),
                'max': df_clean[column].max().isoformat(),
                'range_days': (df_clean[column].max() - df_clean[column].min()).days
            }
    except:
        pass
    
    # String column
    return {
        'column': column,
        'type': 'string',
        'unique_count': int(df[column].nunique()),
        'most_common': df[column].value_counts().head(5).to_dict()
    }


@router.post("/combine")
async def combine_filters(
    dataset_id: str,
    filter_groups: List[List[FilterConfig]],
    logic: str = "AND",  # AND or OR
    db: AsyncSession = Depends(get_db)
):
    """
    Combine multiple filter groups with AND/OR logic.
    Each group is a list of filters that are ANDed together.
    Groups are combined with the specified logic.
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
    
    original_count = len(df)
    
    if logic == "AND":
        # Apply all filter groups sequentially (AND logic)
        for group in filter_groups:
            for filter_config in group:
                # Apply filter (simplified - reuse logic from apply_filters)
                col = filter_config.column
                if col in df.columns:
                    # Apply basic filter
                    if filter_config.operator == 'equals':
                        df = df[df[col].astype(str) == str(filter_config.value)]
    
    else:  # OR logic
        # Apply each group separately and union results
        result_dfs = []
        for group in filter_groups:
            temp_df = df.copy()
            for filter_config in group:
                col = filter_config.column
                if col in temp_df.columns:
                    if filter_config.operator == 'equals':
                        temp_df = temp_df[temp_df[col].astype(str) == str(filter_config.value)]
            result_dfs.append(temp_df)
        
        # Union all results
        if result_dfs:
            df = pd.concat(result_dfs).drop_duplicates()
    
    filtered_count = len(df)
    
    return {
        'original_count': original_count,
        'filtered_count': filtered_count,
        'logic': logic,
        'groups_applied': len(filter_groups)
    }

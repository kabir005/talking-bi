"""
Dataset Diff Router - Compare two datasets
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from typing import List, Optional
from database.db import get_db
from database.models import Dataset
from services.dataset_diff_service import DatasetDiffService
import pandas as pd

router = APIRouter()


class DatasetDiffRequest(BaseModel):
    dataset1_id: str
    dataset2_id: str
    compare_distributions: bool = True


class ColumnDistributionRequest(BaseModel):
    dataset1_id: str
    dataset2_id: str
    column: str


class RowComparisonRequest(BaseModel):
    dataset1_id: str
    dataset2_id: str
    key_columns: Optional[List[str]] = None


@router.post("/compare")
async def compare_datasets(
    request: DatasetDiffRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate comprehensive diff report for two datasets
    
    Returns:
        Schema diff, KPI diff, distribution comparison
    """
    # Get datasets
    result1 = await db.execute(select(Dataset).where(Dataset.id == request.dataset1_id))
    dataset1 = result1.scalar_one_or_none()
    
    result2 = await db.execute(select(Dataset).where(Dataset.id == request.dataset2_id))
    dataset2 = result2.scalar_one_or_none()
    
    if not dataset1:
        raise HTTPException(status_code=404, detail=f"Dataset 1 not found: {request.dataset1_id}")
    if not dataset2:
        raise HTTPException(status_code=404, detail=f"Dataset 2 not found: {request.dataset2_id}")
    
    # Load data
    try:
        query1 = f"SELECT * FROM {dataset1.sqlite_table_name}"
        result = await db.execute(text(query1))
        rows1 = result.fetchall()
        columns1 = result.keys()
        df1 = pd.DataFrame(rows1, columns=columns1)
        
        query2 = f"SELECT * FROM {dataset2.sqlite_table_name}"
        result = await db.execute(text(query2))
        rows2 = result.fetchall()
        columns2 = result.keys()
        df2 = pd.DataFrame(rows2, columns=columns2)
        
        if df1.empty or df2.empty:
            raise HTTPException(status_code=400, detail="One or both datasets are empty")
        
        # Generate diff report
        diff_report = await DatasetDiffService.generate_diff_report(
            df1, df2,
            dataset1.name,
            dataset2.name
        )
        
        return {
            "dataset1": {
                "id": dataset1.id,
                "name": dataset1.name,
                "rows": len(df1),
                "columns": len(df1.columns)
            },
            "dataset2": {
                "id": dataset2.id,
                "name": dataset2.name,
                "rows": len(df2),
                "columns": len(df2.columns)
            },
            "diff_report": diff_report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/compare-column")
async def compare_column_distribution(
    request: ColumnDistributionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare distribution of a specific column between two datasets
    """
    # Get datasets
    result1 = await db.execute(select(Dataset).where(Dataset.id == request.dataset1_id))
    dataset1 = result1.scalar_one_or_none()
    
    result2 = await db.execute(select(Dataset).where(Dataset.id == request.dataset2_id))
    dataset2 = result2.scalar_one_or_none()
    
    if not dataset1 or not dataset2:
        raise HTTPException(status_code=404, detail="One or both datasets not found")
    
    # Load data
    try:
        query1 = f"SELECT * FROM {dataset1.sqlite_table_name}"
        result = await db.execute(text(query1))
        rows1 = result.fetchall()
        columns1 = result.keys()
        df1 = pd.DataFrame(rows1, columns=columns1)
        
        query2 = f"SELECT * FROM {dataset2.sqlite_table_name}"
        result = await db.execute(text(query2))
        rows2 = result.fetchall()
        columns2 = result.keys()
        df2 = pd.DataFrame(rows2, columns=columns2)
        
        # Compare distribution
        distribution = await DatasetDiffService.compare_distributions(
            df1, df2, request.column
        )
        
        return {
            "dataset1_name": dataset1.name,
            "dataset2_name": dataset2.name,
            "distribution": distribution
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Column comparison failed: {str(e)}")


@router.post("/compare-rows")
async def compare_rows(
    request: RowComparisonRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Find common and unique rows between two datasets
    """
    # Get datasets
    result1 = await db.execute(select(Dataset).where(Dataset.id == request.dataset1_id))
    dataset1 = result1.scalar_one_or_none()
    
    result2 = await db.execute(select(Dataset).where(Dataset.id == request.dataset2_id))
    dataset2 = result2.scalar_one_or_none()
    
    if not dataset1 or not dataset2:
        raise HTTPException(status_code=404, detail="One or both datasets not found")
    
    # Load data
    try:
        query1 = f"SELECT * FROM {dataset1.sqlite_table_name}"
        result = await db.execute(text(query1))
        rows1 = result.fetchall()
        columns1 = result.keys()
        df1 = pd.DataFrame(rows1, columns=columns1)
        
        query2 = f"SELECT * FROM {dataset2.sqlite_table_name}"
        result = await db.execute(text(query2))
        rows2 = result.fetchall()
        columns2 = result.keys()
        df2 = pd.DataFrame(rows2, columns=columns2)
        
        # Compare rows
        row_comparison = await DatasetDiffService.find_common_rows(
            df1, df2, request.key_columns
        )
        
        return {
            "dataset1_name": dataset1.name,
            "dataset2_name": dataset2.name,
            "row_comparison": row_comparison
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Row comparison failed: {str(e)}")


@router.get("/schema-diff/{dataset1_id}/{dataset2_id}")
async def get_schema_diff(
    dataset1_id: str,
    dataset2_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Quick schema comparison (no data loading)
    """
    # Get datasets
    result1 = await db.execute(select(Dataset).where(Dataset.id == dataset1_id))
    dataset1 = result1.scalar_one_or_none()
    
    result2 = await db.execute(select(Dataset).where(Dataset.id == dataset2_id))
    dataset2 = result2.scalar_one_or_none()
    
    if not dataset1 or not dataset2:
        raise HTTPException(status_code=404, detail="One or both datasets not found")
    
    # Load minimal data (just columns)
    try:
        query1 = f"SELECT * FROM {dataset1.sqlite_table_name} LIMIT 1"
        result = await db.execute(text(query1))
        columns1 = list(result.keys())
        
        query2 = f"SELECT * FROM {dataset2.sqlite_table_name} LIMIT 1"
        result = await db.execute(text(query2))
        columns2 = list(result.keys())
        
        # Compare
        added = list(set(columns2) - set(columns1))
        removed = list(set(columns1) - set(columns2))
        common = list(set(columns1) & set(columns2))
        
        return {
            "dataset1": {
                "id": dataset1.id,
                "name": dataset1.name,
                "columns": columns1,
                "column_count": len(columns1)
            },
            "dataset2": {
                "id": dataset2.id,
                "name": dataset2.name,
                "columns": columns2,
                "column_count": len(columns2)
            },
            "diff": {
                "added_columns": added,
                "removed_columns": removed,
                "common_columns": common,
                "schema_match": len(added) == 0 and len(removed) == 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema comparison failed: {str(e)}")

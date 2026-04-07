from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from database.db import get_db
from database.models import Dataset
from typing import List
import pandas as pd

router = APIRouter()


@router.get("")
async def list_datasets(db: AsyncSession = Depends(get_db)):
    """List all datasets"""
    result = await db.execute(select(Dataset).order_by(Dataset.created_at.desc()))
    datasets = result.scalars().all()
    
    return [
        {
            "id": ds.id,
            "name": ds.name,
            "source_type": ds.source_type,
            "row_count": ds.row_count,
            "column_count": ds.column_count,
            "created_at": ds.created_at.isoformat() if ds.created_at else None
        }
        for ds in datasets
    ]


@router.get("/{dataset_id}")
async def get_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    """Get dataset metadata and schema"""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return {
        "id": dataset.id,
        "name": dataset.name,
        "source_type": dataset.source_type,
        "source_path": dataset.source_path,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "schema": dataset.schema_json,
        "sample": dataset.sample_json,
        "cleaning_log": dataset.cleaning_log,
        "created_at": dataset.created_at.isoformat() if dataset.created_at else None
    }


@router.get("/{dataset_id}/preview")
async def preview_dataset(
    dataset_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get first N rows of dataset"""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not dataset.sqlite_table_name:
        raise HTTPException(status_code=400, detail="Dataset table not found")
    
    # Query data from SQLite table
    query = f"SELECT * FROM {dataset.sqlite_table_name} LIMIT {limit}"
    result = await db.execute(text(query))
    rows = result.fetchall()
    
    # Get column names
    columns = result.keys()
    
    # Convert to list of dicts
    data = [dict(zip(columns, row)) for row in rows]
    
    return {
        "columns": list(columns),
        "data": data,
        "total_rows": dataset.row_count
    }


@router.get("/{dataset_id}/data")
async def get_dataset_data(
    dataset_id: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get dataset rows (alias for preview)"""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not dataset.sqlite_table_name:
        raise HTTPException(status_code=400, detail="Dataset table not found")
    
    # Query data from SQLite table
    query = f"SELECT * FROM {dataset.sqlite_table_name} LIMIT {limit}"
    result = await db.execute(text(query))
    rows = result.fetchall()
    
    # Get column names
    columns = result.keys()
    
    # Convert to list of dicts
    data = [dict(zip(columns, row)) for row in rows]
    
    return {
        "columns": list(columns),
        "rows": data,  # Use 'rows' key for compatibility
        "total_rows": dataset.row_count
    }


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    """Delete dataset and associated data"""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Drop SQLite table
    if dataset.sqlite_table_name:
        try:
            await db.execute(text(f"DROP TABLE IF EXISTS {dataset.sqlite_table_name}"))
        except:
            pass
    
    # Delete dataset record
    await db.delete(dataset)
    await db.commit()
    
    return {"message": "Dataset deleted successfully"}


@router.post("/{dataset_id}/remove-outliers")
async def remove_outliers(dataset_id: str, db: AsyncSession = Depends(get_db)):
    """Remove flagged outlier rows from dataset"""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not dataset.sqlite_table_name:
        raise HTTPException(status_code=400, detail="Dataset table not found")
    
    # Delete rows where _is_outlier = 1
    delete_query = f"DELETE FROM {dataset.sqlite_table_name} WHERE _is_outlier = 1"
    await db.execute(text(delete_query))
    
    # Update row count
    count_query = f"SELECT COUNT(*) FROM {dataset.sqlite_table_name}"
    result = await db.execute(text(count_query))
    new_count = result.scalar()
    
    dataset.row_count = new_count
    await db.commit()
    
    return {
        "message": "Outliers removed successfully",
        "new_row_count": new_count
    }


@router.post("/{dataset_id}/drop-column")
async def drop_column(
    dataset_id: str,
    column_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Drop a column from dataset"""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not dataset.sqlite_table_name:
        raise HTTPException(status_code=400, detail="Dataset table not found")
    
    # SQLite doesn't support DROP COLUMN directly, need to recreate table
    # For simplicity, we'll just update the schema JSON
    if dataset.schema_json and column_name in dataset.schema_json:
        del dataset.schema_json[column_name]
        dataset.column_count = len(dataset.schema_json)
        await db.commit()
    
    return {"message": f"Column {column_name} marked as dropped"}

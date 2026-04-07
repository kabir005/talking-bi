"""
Doc2Chart Router - Upload and extract tables from documents and images
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from database.models import Dataset
from services.doc2chart_service import Doc2ChartService
from typing import List, Optional
import uuid
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Upload directory
UPLOAD_DIR = Path("backend/data")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    merge_strategy: str = "concat",
    db: AsyncSession = Depends(get_db)
):
    """
    Upload PDF, DOCX, or image and extract tables
    
    Args:
        file: Document or image file
        merge_strategy: 'concat' or 'join' (for multiple tables)
        
    Returns:
        Dataset info with extracted tables
    """
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    supported = Doc2ChartService.get_supported_formats()
    all_formats = supported["documents"] + supported["images"]
    
    if file_ext not in all_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: {all_formats}"
        )
    
    # Save uploaded file
    file_id = str(uuid.uuid4())
    temp_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    
    try:
        # Save file
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Saved document: {temp_path}")
        
        # Extract tables
        tables = await Doc2ChartService.auto_detect_and_extract(str(temp_path))
        
        if not tables:
            raise HTTPException(status_code=400, detail="No tables found in document")
        
        logger.info(f"Extracted {len(tables)} table(s) from {file.filename}")
        
        # Merge tables if multiple
        if len(tables) > 1:
            df = await Doc2ChartService.merge_tables(tables, merge_strategy)
            table_info = f"{len(tables)} tables merged"
        else:
            df = tables[0]
            table_info = "1 table"
        
        # Save as CSV
        csv_path = UPLOAD_DIR / f"{file_id}.csv"
        df.to_csv(csv_path, index=False)
        
        # Create dataset record
        dataset = Dataset(
            id=file_id,
            name=file.filename,
            file_path=str(csv_path),
            row_count=len(df),
            column_count=len(df.columns),
            file_size=os.path.getsize(csv_path),
            sqlite_table_name=f"dataset_{file_id.replace('-', '_')}"
        )
        
        db.add(dataset)
        await db.commit()
        await db.refresh(dataset)
        
        # Clean up temp file
        if temp_path.exists():
            os.remove(temp_path)
        
        return {
            "dataset_id": dataset.id,
            "name": dataset.name,
            "rows": dataset.row_count,
            "columns": dataset.column_count,
            "table_info": table_info,
            "source_type": file_ext,
            "columns_list": df.columns.tolist(),
            "preview": df.head(5).to_dict(orient='records')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        # Clean up on error
        if temp_path.exists():
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@router.post("/extract-tables")
async def extract_tables_only(
    file: UploadFile = File(...)
):
    """
    Extract tables from document without saving to database
    
    Returns:
        List of tables as JSON
    """
    file_ext = Path(file.filename).suffix.lower()
    supported = Doc2ChartService.get_supported_formats()
    all_formats = supported["documents"] + supported["images"]
    
    if file_ext not in all_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}"
        )
    
    # Save temp file
    file_id = str(uuid.uuid4())
    temp_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    
    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Extract tables
        tables = await Doc2ChartService.auto_detect_and_extract(str(temp_path))
        
        if not tables:
            raise HTTPException(status_code=400, detail="No tables found")
        
        # Convert to JSON
        result = []
        for i, df in enumerate(tables, 1):
            result.append({
                "table_number": i,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "source": df.attrs.get('source', f"Table {i}"),
                "preview": df.head(10).to_dict(orient='records')
            })
        
        return {
            "filename": file.filename,
            "tables_found": len(tables),
            "tables": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Table extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up
        if temp_path.exists():
            os.remove(temp_path)


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    formats = Doc2ChartService.get_supported_formats()
    return {
        "formats": formats,
        "all_extensions": formats["documents"] + formats["images"] + formats["spreadsheets"]
    }

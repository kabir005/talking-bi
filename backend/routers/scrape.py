from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from database.db import get_db
from database.models import Dataset
from agents.scrape_agent import scrape_url
from agents.cleaning_agent import run_cleaning
from utils.schema_detector import infer_column_types
from utils.serializers import dataframe_to_dict
from config import SQLITE_DB_PATH
import pandas as pd
import uuid

router = APIRouter()


class ScrapeRequest(BaseModel):
    url: str
    extract_tables: bool = True
    max_pages: int = 1


@router.post("/url")
async def scrape_url_endpoint(request: ScrapeRequest, db: AsyncSession = Depends(get_db)):
    """Scrape data from URL and create dataset"""
    
    try:
        # Scrape URL
        scrape_result = await scrape_url(
            request.url,
            request.extract_tables,
            request.max_pages
        )
        
        if scrape_result["errors"]:
            raise HTTPException(status_code=400, detail=scrape_result["errors"][0])
        
        if not scrape_result["dataframes"] or len(scrape_result["dataframes"]) == 0:
            raise HTTPException(
                status_code=404,
                detail="No tables found on the page"
            )
        
        # Use first dataframe
        df = scrape_result["dataframes"][0]
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Scraped table is empty")
        
        # Infer schema
        schema = infer_column_types(df)
        
        # Run cleaning agent (handles all data cleaning)
        cleaned_df, cleaning_report = await run_cleaning(df)
        
        if cleaned_df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty after cleaning")
        
        # Create table name
        dataset_id = str(uuid.uuid4())
        table_name = f"dataset_{dataset_id.replace('-', '_')}"
        
        # Use pandas to_sql for reliable data insertion
        from sqlalchemy import create_engine
        from config import SQLITE_DB_PATH
        
        # Create sync engine for pandas
        sync_engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}")
        
        # Convert datetime columns to string for SQLite compatibility
        for col in cleaned_df.columns:
            if pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
                cleaned_df[col] = cleaned_df[col].astype(str)
        
        # Save to SQLite using pandas (much more reliable)
        cleaned_df.to_sql(
            name=table_name,
            con=sync_engine,
            if_exists='replace',
            index=False,
            chunksize=1000
        )
        
        sync_engine.dispose()
        
        print(f"✓ Saved {len(cleaned_df)} rows to table {table_name}")
        
        # Verify data was saved
        result = await db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        row_count = result.scalar()
        print(f"✓ Verified {row_count} rows in database")
        
        if row_count == 0:
            raise HTTPException(status_code=500, detail="Data insertion failed - table is empty")
        
        # Create dataset record
        dataset = Dataset(
            id=dataset_id,
            name=f"Scraped from {request.url[:50]}",
            source_type="url",
            source_path=request.url,
            row_count=row_count,
            column_count=len(cleaned_df.columns),
            schema_json=schema,
            sample_json=dataframe_to_dict(cleaned_df, max_rows=5)["data"],
            cleaning_log=cleaning_report["cleaning_log"],
            sqlite_table_name=table_name
        )
        
        db.add(dataset)
        await db.commit()
        await db.refresh(dataset)
        
        return {
            "dataset_id": dataset.id,
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "schema": schema,
            "sample": dataset.sample_json,
            "cleaning_report": cleaning_report,
            "scrape_metadata": scrape_result["metadata"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in scrape endpoint: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

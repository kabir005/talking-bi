from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import pandas as pd
import uuid
import os
from database.db import get_db
from database.models import Dataset
from utils.schema_detector import infer_column_types
from utils.serializers import dataframe_to_dict
from agents.cleaning_agent import run_cleaning
from config import DATA_DIR, MAX_FILE_SIZE_MB

router = APIRouter()


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload CSV, Excel, or JSON file.
    Automatically cleans data and stores in SQLite.
    """
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB"
        )
    
    # Check file extension
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    ext = filename.lower().split('.')[-1]
    if ext not in ['csv', 'xlsx', 'xls', 'json']:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload CSV, Excel, or JSON"
        )
    
    # Save file temporarily
    file_id = str(uuid.uuid4())
    temp_path = os.path.join(DATA_DIR, f"{file_id}.{ext}")
    
    try:
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        print(f"\n{'='*80}")
        print(f"UPLOAD PROCESSING START - {filename}")
        print(f"{'='*80}")
        
        # Read file into DataFrame
        if ext == 'csv':
            # Try different encodings and delimiters
            try:
                df = pd.read_csv(temp_path, encoding='utf-8', low_memory=False)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(temp_path, encoding='latin-1', low_memory=False)
                except:
                    try:
                        df = pd.read_csv(temp_path, encoding='iso-8859-1', low_memory=False)
                    except:
                        df = pd.read_csv(temp_path, encoding='utf-8', sep=None, engine='python', low_memory=False)
            except:
                try:
                    df = pd.read_csv(temp_path, encoding='utf-8', sep=None, engine='python', low_memory=False)
                except:
                    df = pd.read_csv(temp_path, encoding='latin-1', sep=None, engine='python', low_memory=False)
        elif ext in ['xlsx', 'xls']:
            df = pd.read_excel(temp_path)
        elif ext == 'json':
            df = pd.read_json(temp_path)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="File appears to be empty")
        
        print(f"Initial DataFrame shape: {df.shape}")
        print(f"Initial columns: {df.columns.tolist()}")
        print(f"Initial dtypes:\n{df.dtypes}")
        print(f"\nFirst 3 rows:\n{df.head(3)}")
        
        # Remove unnamed columns
        unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed:')]
        if unnamed_cols:
            print(f"\nRemoving unnamed columns: {unnamed_cols}")
            df = df.drop(columns=unnamed_cols)
        
        # Remove empty columns
        empty_cols = [col for col in df.columns if df[col].isna().all()]
        if empty_cols:
            print(f"Removing empty columns: {empty_cols}")
            df = df.drop(columns=empty_cols)
        
        # Remove whitespace-only columns
        cols_to_drop = []
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    if df[col].astype(str).str.strip().eq('').all():
                        cols_to_drop.append(col)
                except:
                    pass
        if cols_to_drop:
            print(f"Removing whitespace-only columns: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop)
        
        df = df.reset_index(drop=True)
        
        print(f"\nDataFrame shape after cleanup: {df.shape}")
        print(f"Columns after cleanup: {df.columns.tolist()}")
        
        if df.empty or len(df.columns) == 0:
            raise HTTPException(status_code=400, detail="No valid data columns found in file")
        
        # CRITICAL: Convert numeric columns BEFORE cleaning
        print(f"\n{'='*80}")
        print(f"NUMERIC CONVERSION")
        print(f"{'='*80}")
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Remove common formatting
                    cleaned = df[col].astype(str).str.replace(',', '').str.replace('$', '').str.replace('€', '').str.replace('£', '').str.strip()
                    numeric_series = pd.to_numeric(cleaned, errors='coerce')
                    non_null = numeric_series.notna().sum()
                    total = len(df[col])
                    
                    if non_null > total * 0.5:
                        df[col] = numeric_series
                        print(f"✓ Converted '{col}' to numeric ({non_null}/{total} values)")
                except:
                    pass
        
        print(f"\nDtypes after conversion:\n{df.dtypes}")
        print(f"\nSample after conversion:\n{df.head(3)}")
        
        # Infer schema
        schema = infer_column_types(df)
        
        # Run cleaning
        print(f"\n{'='*80}")
        print(f"RUNNING CLEANING AGENT")
        print(f"{'='*80}")
        cleaned_df, cleaning_report = await run_cleaning(df)
        print(f"Cleaning complete. Final shape: {cleaned_df.shape}")
        
        # Create table
        table_name = f"dataset_{file_id.replace('-', '_')}"
        
        print(f"\n{'='*80}")
        print(f"STORING IN DATABASE")
        print(f"{'='*80}")
        print(f"Table: {table_name}")
        
        # Note: Table will be created by pandas to_sql
        print(f"Column types:")
        for col in cleaned_df.columns:
            dtype = cleaned_df[col].dtype
            print(f"  {col} → {dtype}")
        
        # Insert data using pandas to_sql (more reliable)
        print(f"Inserting {len(cleaned_df)} rows...")
        
        # Convert datetime columns to string for SQLite compatibility
        df_to_insert = cleaned_df.copy()
        for col in df_to_insert.columns:
            if pd.api.types.is_datetime64_any_dtype(df_to_insert[col]):
                df_to_insert[col] = df_to_insert[col].astype(str)
        
        # Use synchronous connection for pandas to_sql
        from sqlalchemy import create_engine
        from config import SQLITE_DB_PATH
        
        # Create synchronous engine for pandas
        sync_url = f"sqlite:///{SQLITE_DB_PATH}"
        sync_engine = create_engine(sync_url)
        
        try:
            # Insert using pandas to_sql (handles all data types properly)
            df_to_insert.to_sql(
                table_name,
                sync_engine,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=1000
            )
            inserted = len(df_to_insert)
            print(f"✓ Inserted {inserted} rows using pandas to_sql")
        except Exception as e:
            print(f"✗ Error inserting data: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to insert data: {str(e)}")
        finally:
            sync_engine.dispose()
        
        # Refresh the async session to see the changes
        await db.commit()
        
        # Verify
        verify = await db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = verify.scalar()
        print(f"✓ Verified {count} rows in database")
        
        # Sample
        sample = await db.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
        rows = sample.fetchall()
        print(f"\nSample from database:")
        for i, r in enumerate(rows):
            print(f"  Row {i+1}: {dict(r._mapping)}")
        
        print(f"\n{'='*80}")
        print(f"UPLOAD COMPLETE")
        print(f"{'='*80}\n")
        
        # Create dataset record
        dataset = Dataset(
            id=file_id,
            name=filename,
            source_type="file",
            source_path=temp_path,
            row_count=count,
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
            "cleaning_report": cleaning_report
        }
    
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        import traceback
        print(f"ERROR in upload_file: {str(e)}")
        print(traceback.format_exc())
        
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

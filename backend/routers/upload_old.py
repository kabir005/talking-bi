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
        
        # Read file into DataFrame
        if ext == 'csv':
            # Try different encodings and delimiters - CRITICAL FIX
            try:
                # First try with standard settings
                df = pd.read_csv(temp_path, encoding='utf-8', low_memory=False)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(temp_path, encoding='latin-1', low_memory=False)
                except:
                    try:
                        df = pd.read_csv(temp_path, encoding='iso-8859-1', low_memory=False)
                    except:
                        # Try with different delimiter
                        df = pd.read_csv(temp_path, encoding='utf-8', sep=None, engine='python', low_memory=False)
            except:
                # Last resort - try to detect delimiter
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
        
        # Remove unnamed columns (these are usually index columns or empty columns)
        unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed:')]
        if unnamed_cols:
            print(f"Removing unnamed columns: {unnamed_cols}")
            df = df.drop(columns=unnamed_cols)
        
        # Remove completely empty columns
        empty_cols = [col for col in df.columns if df[col].isna().all()]
        if empty_cols:
            print(f"Removing empty columns: {empty_cols}")
            df = df.drop(columns=empty_cols)
        
        # Remove columns with only whitespace or empty strings
        cols_to_drop = []
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    if df[col].astype(str).str.strip().eq('').all():
                        print(f"Removing whitespace-only column: {col}")
                        cols_to_drop.append(col)
                except:
                    pass
        
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
        
        # Reset index to avoid index column issues
        df = df.reset_index(drop=True)
        
        print(f"DataFrame shape after cleanup: {df.shape}")
        print(f"Columns after cleanup: {df.columns.tolist()}")
        print(f"Sample data:\n{df.head(2)}")
        
        if df.empty or len(df.columns) == 0:
            raise HTTPException(status_code=400, detail="No valid data columns found in file")
        
        # Infer schema
        schema = infer_column_types(df)
        print(f"Schema detected: {schema}")
        
        # Run cleaning agent
        cleaned_df, cleaning_report = await run_cleaning(df)
        
        # Create table name
        table_name = f"dataset_{file_id.replace('-', '_')}"
        
        # Convert numeric columns BEFORE storing
        # This ensures proper type detection
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    numeric_series = pd.to_numeric(cleaned_df[col], errors='coerce')
                    non_null_count = numeric_series.notna().sum()
                    total_count = len(cleaned_df[col])
                    
                    # If more than 80% can be converted, treat as numeric
                    if non_null_count > total_count * 0.8:
                        cleaned_df[col] = numeric_series
                        print(f"Converted column '{col}' to numeric")
                except:
                    pass
        
        print(f"DataFrame dtypes after conversion:\n{cleaned_df.dtypes}")
        
        # Store in SQLite
        # Use raw SQL to create table and insert data
        await db.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        
        # Create table dynamically - DON'T sanitize column names, keep original
        columns_sql = []
        for col in cleaned_df.columns:
            dtype = cleaned_df[col].dtype
            
            if 'int' in str(dtype):
                sql_type = 'INTEGER'
            elif 'float' in str(dtype):
                sql_type = 'REAL'
            elif 'datetime' in str(dtype):
                sql_type = 'TEXT'
            elif 'bool' in str(dtype):
                sql_type = 'INTEGER'
            else:
                sql_type = 'TEXT'
            
            # Keep original column name with quotes to handle spaces/special chars
            columns_sql.append(f'"{col}" {sql_type}')
        
        create_table_sql = f"CREATE TABLE {table_name} ({', '.join(columns_sql)})"
        await db.execute(text(create_table_sql))
        
        # Insert data
        for _, row in cleaned_df.iterrows():
            values = []
            for val in row:
                if pd.isna(val):
                    values.append('NULL')
                elif isinstance(val, str):
                    escaped_val = val.replace("'", "''")
                    values.append(f"'{escaped_val}'")
                else:
                    values.append(str(val))
            
            insert_sql = f"INSERT INTO {table_name} VALUES ({', '.join(values)})"
            try:
                await db.execute(text(insert_sql))
            except Exception as insert_error:
                print(f"Insert error: {insert_error}")
                pass  # Skip rows that fail to insert
        
        await db.commit()
        
        # Create dataset record
        dataset = Dataset(
            id=file_id,
            name=filename,
            source_type="file",
            source_path=temp_path,
            row_count=len(cleaned_df),
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
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Log the full error for debugging
        import traceback
        print(f"ERROR in upload_file: {str(e)}")
        print(traceback.format_exc())
        
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

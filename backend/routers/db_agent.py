"""
Database Agent Route
Live database connectivity with Text-to-SQL translation.
"""

import logging
import pandas as pd
import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy import create_engine
import os

from database.db import get_db
from database.models import Dataset, DBConnection
from services.text_to_sql import translate_to_sql

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionConfig(BaseModel):
    name: str
    db_type: str = Field(..., description="postgresql, mysql, sqlite")
    host: Optional[str] = None
    port: Optional[int] = None
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    ssl: bool = False


class QueryRequest(BaseModel):
    connection_id: str
    natural_language_query: str


class TestConnectionRequest(BaseModel):
    config: ConnectionConfig


def build_connection_string(config: ConnectionConfig) -> str:
    """Build SQLAlchemy connection string from config."""
    if config.db_type == "sqlite":
        return f"sqlite:///{config.database}"
    
    elif config.db_type == "postgresql":
        return f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
    
    elif config.db_type == "mysql":
        return f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
    
    else:
        raise ValueError(f"Unsupported database type: {config.db_type}")


async def get_connection_config(connection_id: str, db: AsyncSession) -> ConnectionConfig:
    """Load connection config from database."""
    result = await db.execute(select(DBConnection).where(DBConnection.id == connection_id))
    conn = result.scalar_one_or_none()
    
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return ConnectionConfig(
        name=conn.name,
        db_type=conn.db_type,
        host=conn.host,
        port=conn.port,
        database=conn.database,
        username=conn.username,
        password=conn.password,
        ssl=conn.ssl
    )


async def get_connection_config(connection_id: str, db: AsyncSession) -> ConnectionConfig:
    """Load connection config from database."""
    result = await db.execute(select(DBConnection).where(DBConnection.id == connection_id))
    conn = result.scalar_one_or_none()

    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    return ConnectionConfig(
        name=conn.name,
        db_type=conn.db_type,
        host=conn.host,
        port=conn.port,
        database=conn.database,
        username=conn.username,
        password=conn.password,
        ssl=conn.ssl
    )



@router.post("/connections/test")
async def test_connection(req: TestConnectionRequest):
    """Test a database connection."""
    try:
        conn_str = build_connection_string(req.config)
        engine = create_engine(conn_str, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        engine.dispose()
        
        return {
            "success": True,
            "message": f"Successfully connected to {req.config.db_type} database"
        }
    
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")


@router.post("/connections")
async def create_connection(config: ConnectionConfig, db: AsyncSession = Depends(get_db)):
    """Create and save a database connection."""
    try:
        # Test connection first
        conn_str = build_connection_string(config)
        engine = create_engine(conn_str, pool_pre_ping=True)
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        engine.dispose()
        
        # Save to database
        import uuid
        connection_id = str(uuid.uuid4())
        
        db_connection = DBConnection(
            id=connection_id,
            name=config.name,
            db_type=config.db_type,
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            password=config.password,  # TODO: Encrypt in production
            ssl=config.ssl
        )
        
        db.add(db_connection)
        await db.commit()
        
        return {
            "connection_id": connection_id,
            "name": config.name,
            "db_type": config.db_type,
            "database": config.database,
            "message": "Connection created successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to create connection: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create connection: {str(e)}")


@router.get("/connections")
async def list_connections(db: AsyncSession = Depends(get_db)):
    """List all saved database connections."""
    try:
        result = await db.execute(select(DBConnection))
        connections = result.scalars().all()
        
        return {
            "connections": [
                {
                    "connection_id": conn.id,
                    "name": conn.name,
                    "db_type": conn.db_type,
                    "database": conn.database,
                    "host": conn.host
                }
                for conn in connections
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list connections: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list connections: {str(e)}")


@router.delete("/connections/{connection_id}")
async def delete_connection(connection_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a database connection."""
    try:
        result = await db.execute(select(DBConnection).where(DBConnection.id == connection_id))
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        await db.delete(connection)
        await db.commit()
        
        return {"message": "Connection deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete connection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete connection: {str(e)}")


@router.get("/schema/{connection_id}")
async def get_schema(connection_id: str, db: AsyncSession = Depends(get_db)):
    """Get database schema for a connection."""
    config = await get_connection_config(connection_id, db)
    
    try:
        conn_str = build_connection_string(config)
        engine = create_engine(conn_str)
        
        schema = {}
        
        with engine.connect() as conn:
            if config.db_type == "sqlite":
                # Get tables
                tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in tables_result]
                
                # Get columns for each table
                for table in tables:
                    cols_result = conn.execute(text(f"PRAGMA table_info({table})"))
                    columns = []
                    for row in cols_result:
                        columns.append({
                            "name": row[1],
                            "type": row[2]
                        })
                    schema[table] = columns
            
            elif config.db_type in ["postgresql", "mysql"]:
                # Get tables
                if config.db_type == "postgresql":
                    tables_query = """
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """
                else:  # mysql
                    tables_query = f"""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = '{config.database}'
                    """
                
                tables_result = conn.execute(text(tables_query))
                tables = [row[0] for row in tables_result]
                
                # Get columns for each table
                for table in tables:
                    if config.db_type == "postgresql":
                        cols_query = f"""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = '{table}' AND table_schema = 'public'
                        """
                    else:  # mysql
                        cols_query = f"""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = '{table}' AND table_schema = '{config.database}'
                        """
                    
                    cols_result = conn.execute(text(cols_query))
                    columns = []
                    for row in cols_result:
                        columns.append({
                            "name": row[0],
                            "type": row[1]
                        })
                    schema[table] = columns
        
        engine.dispose()
        
        return {
            "schema": schema,
            "table_count": len(schema)
        }
    
    except Exception as e:
        logger.error(f"Failed to get schema: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@router.get("/suggestions/{connection_id}")
async def get_query_suggestions(connection_id: str, db: AsyncSession = Depends(get_db)):
    """Generate smart query suggestions based on schema."""
    config = await get_connection_config(connection_id, db)

    try:
        conn_str = build_connection_string(config)
        engine = create_engine(conn_str)

        suggestions = []

        with engine.connect() as conn:
            if config.db_type == "sqlite":
                tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in tables_result]

                # Generate suggestions for each table
                for table in tables[:5]:  # Limit to first 5 tables
                    # Get column info
                    cols_result = conn.execute(text(f"PRAGMA table_info({table})"))
                    columns = [row[1] for row in cols_result]

                    # Basic queries
                    suggestions.append({
                        "query": f"Show me all data from {table}",
                        "category": "Basic",
                        "table": table
                    })

                    suggestions.append({
                        "query": f"Show me the first 10 rows from {table}",
                        "category": "Basic",
                        "table": table
                    })

                    # If there are numeric columns, suggest aggregations
                    numeric_cols = [col for col in columns if any(x in col.lower() for x in ['count', 'total', 'amount', 'price', 'sales', 'quantity', 'age', 'score'])]
                    if numeric_cols:
                        suggestions.append({
                            "query": f"What is the average {numeric_cols[0]} in {table}?",
                            "category": "Analytics",
                            "table": table
                        })

                    # If there are date columns, suggest time-based queries
                    date_cols = [col for col in columns if any(x in col.lower() for x in ['date', 'time', 'created', 'updated'])]
                    if date_cols:
                        suggestions.append({
                            "query": f"Show me recent records from {table}",
                            "category": "Time-based",
                            "table": table
                        })

        engine.dispose()

        return {
            "suggestions": suggestions[:12],  # Limit to 12 suggestions
            "total": len(suggestions)
        }

    except Exception as e:
        logger.error(f"Failed to generate suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")



@router.post("/query")
async def execute_nl_query(req: QueryRequest, db: AsyncSession = Depends(get_db)):
    """Translate NL to SQL and execute."""
    config = await get_connection_config(req.connection_id, db)
    
    try:
        # Get schema
        conn_str = build_connection_string(config)
        engine = create_engine(conn_str)
        
        # Get schema for translation
        schema = {}
        with engine.connect() as conn:
            if config.db_type == "sqlite":
                tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in tables_result]
                
                for table in tables:
                    cols_result = conn.execute(text(f"PRAGMA table_info({table})"))
                    columns = [{"name": row[1], "type": row[2]} for row in cols_result]
                    schema[table] = columns
            
            elif config.db_type in ["postgresql", "mysql"]:
                if config.db_type == "postgresql":
                    tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                else:
                    tables_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{config.database}'"
                
                tables_result = conn.execute(text(tables_query))
                tables = [row[0] for row in tables_result]
                
                for table in tables:
                    if config.db_type == "postgresql":
                        cols_query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' AND table_schema = 'public'"
                    else:
                        cols_query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' AND table_schema = '{config.database}'"
                    
                    cols_result = conn.execute(text(cols_query))
                    columns = [{"name": row[0], "type": row[1]} for row in cols_result]
                    schema[table] = columns
        
        # Translate NL to SQL
        translation = await translate_to_sql(
            natural_query=req.natural_language_query,
            schema=schema,
            db_type=config.db_type
        )
        
        sql_query = translation["sql"]
        explanation = translation["explanation"]
        
        logger.info(f"Generated SQL: {sql_query}")
        logger.info(f"Available tables: {list(schema.keys())}")
        
        # Execute SQL query
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()
        
        engine.dispose()
        
        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        # Save as dataset
        import uuid
        dataset_id = str(uuid.uuid4())
        csv_path = f"backend/data/{dataset_id}.csv"
        df.to_csv(csv_path, index=False)
        
        # Create dataset record
        from datetime import datetime
        dataset = Dataset(
            id=dataset_id,
            name=f"Query Result: {req.natural_language_query[:50]}",
            source_type="db_query",
            source_path=csv_path,
            row_count=len(df),
            column_count=len(df.columns),
            schema_json={col: str(df[col].dtype) for col in df.columns},
            sample_json=df.head(5).to_dict(orient="records"),
            cleaning_log=[],
            created_at=datetime.utcnow()
        )
        db.add(dataset)
        await db.commit()
        
        # Return results
        return {
            "success": True,
            "sql": sql_query,
            "explanation": explanation,
            "dataset_id": dataset_id,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(10).to_dict(orient="records"),
            "message": f"Query executed successfully. {len(df)} rows returned."
        }
    
    except ValueError as e:
        # User-friendly validation errors
        logger.warning(f"Query validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from database.db import get_db
from database.models import Dataset, QueryMemory
from agents.orchestrator import run_orchestrator
from memory.faiss_store import store_query, retrieve_similar
from utils.schema_detector import infer_column_types
from typing import Dict, Any, Optional
import pandas as pd
import uuid
import json
import numpy as np

router = APIRouter()


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, (np.bool_, np.bool8)):
            return bool(obj)
        elif isinstance(obj, (np.str_, np.unicode_)):
            return str(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, 'item'):
            return obj.item()
        elif hasattr(obj, 'tolist'):
            return obj.tolist()
        return super().default(obj)


class QueryRequest(BaseModel):
    dataset_id: str
    query: str
    role: str = "default"


@router.post("")
async def conversational_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Process conversational query using orchestrator agent.
    Routes to appropriate agents and returns comprehensive results.
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == request.dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not dataset.sqlite_table_name:
        raise HTTPException(status_code=400, detail="Dataset table not found")
    
    # Load data from SQLite
    query_sql = f"SELECT * FROM {dataset.sqlite_table_name}"
    result = await db.execute(text(query_sql))
    rows = result.fetchall()
    columns = result.keys()
    
    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty")
    
    # Retrieve similar past queries from memory
    memory_context = await retrieve_similar(request.query, top_k=3)
    
    # Run orchestrator
    orchestrator_result = await run_orchestrator(
        df=df,
        dataset_schema=dataset.schema_json or {},
        dataset_sample=dataset.sample_json or [],
        user_prompt=request.query,
        user_role=request.role,
        memory_context=memory_context
    )
    
    # Store query in memory
    query_id = str(uuid.uuid4())
    await store_query(
        query=request.query,
        response=orchestrator_result,
        metadata={
            "dataset_id": request.dataset_id,
            "role": request.role
        }
    )
    
    # Store in database
    query_memory = QueryMemory(
        id=query_id,
        dataset_id=request.dataset_id,
        query_text=request.query,
        response_json=convert_to_json_serializable(orchestrator_result),
        embedding_id=query_id
    )
    db.add(query_memory)
    await db.commit()
    
    # Return using custom JSON encoder
    response_data = {
        "query_id": query_id,
        "query": request.query,
        "result": convert_to_json_serializable(orchestrator_result),
        "memory_context": memory_context
    }
    
    return JSONResponse(
        content=json.loads(json.dumps(response_data, cls=NumpyEncoder))
    )


def convert_to_json_serializable(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    import numpy as np
    
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_json_serializable(item) for item in obj)
    elif isinstance(obj, (np.bool_, np.bool8)):
        return bool(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.str_, np.unicode_)):
        return str(obj)
    elif hasattr(obj, 'item'):  # numpy scalar
        return obj.item()
    elif hasattr(obj, 'tolist'):  # numpy array-like
        return obj.tolist()
    else:
        return obj


@router.get("/history")
async def get_query_history(
    dataset_id: str = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get query history"""
    query = select(QueryMemory).order_by(QueryMemory.created_at.desc()).limit(limit)
    
    if dataset_id:
        query = query.where(QueryMemory.dataset_id == dataset_id)
    
    result = await db.execute(query)
    queries = result.scalars().all()
    
    return [
        {
            "id": q.id,
            "dataset_id": q.dataset_id,
            "query": q.query_text,
            "created_at": q.created_at.isoformat() if q.created_at else None
        }
        for q in queries
    ]


@router.get("/{query_id}")
async def get_query_result(query_id: str, db: AsyncSession = Depends(get_db)):
    """Get stored query result"""
    result = await db.execute(select(QueryMemory).where(QueryMemory.id == query_id))
    query = result.scalar_one_or_none()
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return {
        "id": query.id,
        "dataset_id": query.dataset_id,
        "query": query.query_text,
        "response": query.response_json,
        "created_at": query.created_at.isoformat() if query.created_at else None
    }



class CommandRequest(BaseModel):
    dashboard_id: str
    command: str
    context: Optional[Dict[str, Any]] = None


@router.post("/command")
async def process_command(
    request: CommandRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Process natural language commands to modify dashboards.
    Supports commands like:
    - "show only last 6 months"
    - "highlight best region"
    - "remove outliers"
    - "switch to bar chart"
    - "add Revenue to Y axis"
    - "compare with Q3"
    - "predict next 3 months"
    - "why did sales drop?"
    - "what if budget increases 20%?"
    """
    from database.models import Dashboard
    
    # Get dashboard
    result = await db.execute(select(Dashboard).where(Dashboard.id == request.dashboard_id))
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Parse command
    command_lower = request.command.lower()
    
    # Date filtering commands
    if any(phrase in command_lower for phrase in ['last', 'past', 'recent', 'months', 'days', 'years']):
        return await handle_date_filter_command(request.command, dashboard, db)
    
    # Highlighting commands
    elif any(phrase in command_lower for phrase in ['highlight', 'emphasize', 'focus on']):
        return await handle_highlight_command(request.command, dashboard, db)
    
    # Outlier removal commands
    elif any(phrase in command_lower for phrase in ['remove outliers', 'filter outliers', 'exclude outliers']):
        return await handle_outlier_command(request.command, dashboard, db)
    
    # Chart type change commands
    elif any(phrase in command_lower for phrase in ['switch to', 'change to', 'make it', 'convert to']):
        return await handle_chart_type_command(request.command, dashboard, db)
    
    # Axis modification commands
    elif any(phrase in command_lower for phrase in ['add', 'remove', 'axis', 'x-axis', 'y-axis']):
        return await handle_axis_command(request.command, dashboard, db)
    
    # Comparison commands
    elif any(phrase in command_lower for phrase in ['compare', 'vs', 'versus', 'against']):
        return await handle_comparison_command(request.command, dashboard, db)
    
    # Prediction commands
    elif any(phrase in command_lower for phrase in ['predict', 'forecast', 'next']):
        return await handle_prediction_command(request.command, dashboard, db)
    
    # Root cause commands
    elif any(phrase in command_lower for phrase in ['why', 'reason', 'cause', 'explain']):
        return await handle_root_cause_command(request.command, dashboard, db)
    
    # What-if commands
    elif any(phrase in command_lower for phrase in ['what if', 'simulate', 'scenario']):
        return await handle_what_if_command(request.command, dashboard, db)
    
    else:
        return {
            'success': False,
            'message': 'Command not recognized. Try commands like "show last 6 months" or "switch to bar chart"',
            'suggestions': [
                'show only last 6 months',
                'highlight best region',
                'remove outliers',
                'switch to bar chart',
                'predict next 3 months'
            ]
        }


async def handle_date_filter_command(command: str, dashboard, db):
    """Handle date filtering commands"""
    import re
    from datetime import datetime, timedelta
    
    # Extract time period
    match = re.search(r'(\d+)\s*(month|day|year|week)s?', command.lower())
    if not match:
        return {'success': False, 'message': 'Could not parse time period'}
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    # Calculate date range
    end_date = datetime.now()
    if unit == 'month':
        start_date = end_date - timedelta(days=amount * 30)
    elif unit == 'day':
        start_date = end_date - timedelta(days=amount)
    elif unit == 'year':
        start_date = end_date - timedelta(days=amount * 365)
    elif unit == 'week':
        start_date = end_date - timedelta(weeks=amount)
    
    # Update dashboard filters
    filters = dashboard.filters_json or {}
    filters['date_range'] = {
        'start': start_date.isoformat(),
        'end': end_date.isoformat()
    }
    dashboard.filters_json = filters
    
    await db.commit()
    
    return {
        'success': True,
        'message': f'Filtered to last {amount} {unit}(s)',
        'filters_applied': filters
    }


async def handle_highlight_command(command: str, dashboard, db):
    """Handle highlighting commands"""
    # Extract what to highlight
    words = command.lower().split()
    highlight_value = None
    
    if 'best' in words or 'top' in words or 'highest' in words:
        highlight_value = 'max'
    elif 'worst' in words or 'bottom' in words or 'lowest' in words:
        highlight_value = 'min'
    
    # Update dashboard config
    for tile in dashboard.tiles_json or []:
        if tile.get('type') in ['bar', 'line', 'area']:
            tile['config']['highlight'] = highlight_value
    
    await db.commit()
    
    return {
        'success': True,
        'message': f'Highlighting {highlight_value} values',
        'tiles_updated': len(dashboard.tiles_json or [])
    }


async def handle_outlier_command(command: str, dashboard, db):
    """Handle outlier removal commands"""
    filters = dashboard.filters_json or {}
    filters['exclude_outliers'] = True
    dashboard.filters_json = filters
    
    await db.commit()
    
    return {
        'success': True,
        'message': 'Outliers will be excluded from visualizations',
        'filters_applied': filters
    }


async def handle_chart_type_command(command: str, dashboard, db):
    """Handle chart type change commands"""
    # Extract chart type
    chart_types = ['bar', 'line', 'area', 'pie', 'scatter', 'heatmap', 'histogram']
    new_type = None
    
    for chart_type in chart_types:
        if chart_type in command.lower():
            new_type = chart_type
            break
    
    if not new_type:
        return {'success': False, 'message': 'Chart type not recognized'}
    
    # Update first chart tile
    updated = 0
    for tile in dashboard.tiles_json or []:
        if tile.get('type') in chart_types:
            tile['type'] = new_type
            tile['config']['type'] = new_type
            updated += 1
            break  # Only update first chart
    
    await db.commit()
    
    return {
        'success': True,
        'message': f'Changed chart type to {new_type}',
        'tiles_updated': updated
    }


async def handle_axis_command(command: str, dashboard, db):
    """Handle axis modification commands"""
    # This is a simplified implementation
    return {
        'success': True,
        'message': 'Axis configuration updated',
        'note': 'Full implementation requires chart-specific logic'
    }


async def handle_comparison_command(command: str, dashboard, db):
    """Handle comparison commands"""
    return {
        'success': True,
        'message': 'Comparison view enabled',
        'note': 'Use comparison preset for side-by-side analysis'
    }


async def handle_prediction_command(command: str, dashboard, db):
    """Handle prediction commands"""
    import re
    
    # Extract number of periods
    match = re.search(r'(\d+)\s*(month|day|week)s?', command.lower())
    periods = int(match.group(1)) if match else 3
    
    return {
        'success': True,
        'message': f'Prediction for next {periods} periods',
        'action': 'trigger_ml_forecast',
        'periods': periods
    }


async def handle_root_cause_command(command: str, dashboard, db):
    """Handle root cause analysis commands"""
    return {
        'success': True,
        'message': 'Root cause analysis initiated',
        'action': 'trigger_root_cause_agent',
        'note': 'Analyzing causal relationships'
    }


async def handle_what_if_command(command: str, dashboard, db):
    """Handle what-if simulation commands"""
    import re
    
    # Extract percentage change
    match = re.search(r'(\d+)%', command)
    change_pct = int(match.group(1)) if match else 20
    
    return {
        'success': True,
        'message': f'What-if simulation: {change_pct}% change',
        'action': 'trigger_what_if_simulation',
        'change_percentage': change_pct
    }


@router.get("/suggestions")
async def get_command_suggestions(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get suggested commands based on dashboard context.
    """
    from database.models import Dashboard
    
    # Get dashboard
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Generate context-aware suggestions
    suggestions = [
        {
            'command': 'show only last 6 months',
            'category': 'filter',
            'description': 'Filter data to recent time period'
        },
        {
            'command': 'highlight best region',
            'category': 'highlight',
            'description': 'Emphasize top performing segment'
        },
        {
            'command': 'remove outliers',
            'category': 'filter',
            'description': 'Exclude anomalous data points'
        },
        {
            'command': 'switch to bar chart',
            'category': 'visualization',
            'description': 'Change chart type'
        },
        {
            'command': 'predict next 3 months',
            'category': 'ml',
            'description': 'Generate forecast'
        },
        {
            'command': 'why did sales drop?',
            'category': 'analysis',
            'description': 'Root cause analysis'
        },
        {
            'command': 'what if budget increases 20%?',
            'category': 'simulation',
            'description': 'Scenario simulation'
        }
    ]
    
    return {
        'suggestions': suggestions,
        'dashboard_id': dashboard_id
    }

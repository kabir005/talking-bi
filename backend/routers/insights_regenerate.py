"""
Router to regenerate insights for existing dashboards
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from database.db import get_db
from database.models import Dashboard, Dataset
from agents.analyst_agent import run_analysis
from agents.insight_agent import generate_insights
from agents.strategist_agent import generate_recommendations
from agents.critic_agent import run_critic_validation
import pandas as pd

router = APIRouter()


@router.post("/dashboards/{dashboard_id}/regenerate-insights")
async def regenerate_insights(dashboard_id: str, db: AsyncSession = Depends(get_db)):
    """
    Regenerate insights and recommendations for an existing dashboard.
    This adds insights and recommendations tiles if they don't exist.
    """
    
    # Get dashboard
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dashboard.dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load data from SQLite table
    table_name = dataset.sqlite_table_name
    query = f"SELECT * FROM {table_name}"
    result = await db.execute(text(query))
    rows = result.fetchall()
    columns = result.keys()
    
    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty")
    
    # Identify numeric columns for KPI analysis
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != '_is_outlier']
    
    # Identify time column if exists
    time_col = None
    for col in df.columns:
        if dataset.schema_json.get(col) in ['datetime', 'year']:
            time_col = col
            break
    
    # Run statistical analysis
    analysis_result = await run_analysis(df, numeric_cols[:5], time_col)
    
    # Run validation
    validation_result = await run_critic_validation(analysis_result, df, dataset.schema_json)
    
    # Generate insights
    insights_data = await generate_insights(
        analysis_result,
        validation_result,
        dataset.name,
        use_llm=False  # Use rule-based for reliability
    )
    
    # Generate recommendations
    recommendations_data = await generate_recommendations(
        validation_result.get("validated_insights", []),
        analysis_result.get("kpis", {}),
        analysis_result.get("correlations", []),
        analysis_result.get("trends", {})
    )
    
    # Get existing tiles
    tiles = dashboard.tiles_json or []
    
    # Remove old insights and recommendations tiles if they exist
    tiles = [t for t in tiles if t.get('type') not in ['insights', 'recommendations']]
    
    # Add new insights tile
    import uuid
    insights_tile_id = str(uuid.uuid4())
    tiles.append({
        "id": insights_tile_id,
        "type": "insights",
        "title": "Key Insights",
        "data": insights_data
    })
    
    # Add new recommendations tile
    recommendations_tile_id = str(uuid.uuid4())
    tiles.append({
        "id": recommendations_tile_id,
        "type": "recommendations",
        "title": "Strategic Recommendations",
        "data": {"recommendations": recommendations_data}
    })
    
    # Update dashboard
    dashboard.tiles_json = tiles
    await db.commit()
    await db.refresh(dashboard)
    
    return {
        "success": True,
        "dashboard_id": dashboard_id,
        "insights_generated": len(insights_data.get('key_insights', [])),
        "recommendations_generated": len(recommendations_data),
        "message": "Insights and recommendations regenerated successfully"
    }

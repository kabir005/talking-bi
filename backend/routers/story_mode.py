"""
Story Mode Router - Generate executive narratives
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from database.db import get_db
from database.models import Dashboard
from services.story_mode_service import StoryModeService

router = APIRouter()


class ExecutiveSummaryRequest(BaseModel):
    dataset_name: str
    kpis: Dict[str, Any]
    insights: List[Dict[str, Any]]
    trends: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None


class InsightStoryRequest(BaseModel):
    insight: Dict[str, Any]
    context: Optional[str] = None


class TrendNarrativeRequest(BaseModel):
    column: str
    trend_type: str
    values: List[float]
    dates: Optional[List[str]] = None


@router.post("/executive-summary")
async def generate_executive_summary(request: ExecutiveSummaryRequest):
    """
    Generate 3-paragraph executive summary
    
    Returns:
        Executive narrative with paragraphs
    """
    try:
        summary = await StoryModeService.generate_executive_summary(
            dataset_name=request.dataset_name,
            kpis=request.kpis,
            insights=request.insights,
            trends=request.trends,
            recommendations=request.recommendations
        )
        
        return {
            "dataset_name": request.dataset_name,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@router.get("/dashboard-story/{dashboard_id}")
async def get_dashboard_story(
    dashboard_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate executive summary for a dashboard
    
    Returns:
        Executive narrative based on dashboard data
    """
    # Get dashboard
    result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    try:
        # Extract data from dashboard
        kpis = dashboard.kpis or {}
        insights = dashboard.insights or []
        
        # Generate summary
        summary = await StoryModeService.generate_executive_summary(
            dataset_name=dashboard.name,
            kpis=kpis,
            insights=insights,
            trends=None,
            recommendations=None
        )
        
        return {
            "dashboard_id": dashboard_id,
            "dashboard_name": dashboard.name,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")


@router.post("/insight-story")
async def generate_insight_story(request: InsightStoryRequest):
    """
    Generate narrative for a single insight
    
    Returns:
        Narrative explanation of the insight
    """
    try:
        story = await StoryModeService.generate_insight_story(
            insight=request.insight,
            context=request.context or ""
        )
        
        return {
            "insight": request.insight,
            "story": story
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight story generation failed: {str(e)}")


@router.post("/trend-narrative")
async def generate_trend_narrative(request: TrendNarrativeRequest):
    """
    Generate narrative for a trend
    
    Returns:
        Trend narrative
    """
    try:
        narrative = await StoryModeService.generate_trend_narrative(
            column=request.column,
            trend_type=request.trend_type,
            values=request.values,
            dates=request.dates
        )
        
        return {
            "column": request.column,
            "trend_type": request.trend_type,
            "narrative": narrative
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend narrative generation failed: {str(e)}")

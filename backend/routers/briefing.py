"""
Briefing Route
Configure and manage automated briefings.
"""

import logging
import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from database.db import get_db
from database.models import Dataset
from services.scheduler import schedule_briefing, unschedule_briefing, get_next_run_time
from services.briefing_generator import generate_briefing_content
from services.email_service import send_briefing_email

logger = logging.getLogger(__name__)
router = APIRouter()


class BriefingConfig(BaseModel):
    name: str
    dataset_id: str
    recipients: List[EmailStr]
    schedule: str
    timezone: str = "UTC"
    include_kpis: bool = True
    include_trends: bool = True
    include_anomalies: bool = True


class BriefingResponse(BaseModel):
    briefing_id: str
    name: str
    dataset_id: str
    recipients: List[str]
    schedule: str
    timezone: str
    next_run: Optional[str] = None
    created_at: str


# In-memory storage (in production, use database)
_briefings: dict[str, dict] = {}


@router.post("/briefings")
async def create_briefing(config: BriefingConfig, db: AsyncSession = Depends(get_db)):
    """Create a new scheduled briefing."""
    try:
        # Validate dataset exists
        result = await db.execute(select(Dataset).where(Dataset.id == config.dataset_id))
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Generate briefing ID
        briefing_id = str(uuid.uuid4())
        
        # Schedule briefing
        schedule_briefing(
            briefing_id=briefing_id,
            dataset_id=config.dataset_id,
            recipients=config.recipients,
            schedule=config.schedule,
            timezone=config.timezone,
            config={
                "name": config.name,
                "include_kpis": config.include_kpis,
                "include_trends": config.include_trends,
                "include_anomalies": config.include_anomalies
            }
        )
        
        # Store briefing config
        briefing_data = {
            "briefing_id": briefing_id,
            "name": config.name,
            "dataset_id": config.dataset_id,
            "dataset_name": dataset.name,
            "recipients": config.recipients,
            "schedule": config.schedule,
            "timezone": config.timezone,
            "include_kpis": config.include_kpis,
            "include_trends": config.include_trends,
            "include_anomalies": config.include_anomalies,
            "created_at": datetime.utcnow().isoformat()
        }
        _briefings[briefing_id] = briefing_data
        
        # Get next run time
        next_run = get_next_run_time(briefing_id)
        
        return {
            **briefing_data,
            "next_run": next_run.isoformat() if next_run else None,
            "message": "Briefing created and scheduled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create briefing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create briefing: {str(e)}")


@router.get("/briefings")
async def list_briefings():
    """List all configured briefings."""
    briefings = []
    
    for briefing_id, data in _briefings.items():
        next_run = get_next_run_time(briefing_id)
        briefings.append({
            **data,
            "next_run": next_run.isoformat() if next_run else None
        })
    
    return {"briefings": briefings}


@router.get("/briefings/{briefing_id}")
async def get_briefing(briefing_id: str):
    """Get a specific briefing."""
    if briefing_id not in _briefings:
        raise HTTPException(status_code=404, detail="Briefing not found")
    
    data = _briefings[briefing_id]
    next_run = get_next_run_time(briefing_id)
    
    return {
        **data,
        "next_run": next_run.isoformat() if next_run else None
    }


@router.delete("/briefings/{briefing_id}")
async def delete_briefing(briefing_id: str):
    """Delete a scheduled briefing."""
    if briefing_id not in _briefings:
        raise HTTPException(status_code=404, detail="Briefing not found")
    
    # Remove from scheduler
    unschedule_briefing(briefing_id)
    
    # Delete from storage
    del _briefings[briefing_id]
    
    return {"message": "Briefing deleted successfully"}


@router.post("/briefings/{briefing_id}/send-now")
async def send_briefing_now(briefing_id: str, db: AsyncSession = Depends(get_db)):
    """Manually trigger a briefing."""
    if briefing_id not in _briefings:
        raise HTTPException(status_code=404, detail="Briefing not found")
    
    briefing = _briefings[briefing_id]
    
    try:
        # Generate content
        content = await generate_briefing_content(
            dataset_id=briefing["dataset_id"],
            config={
                "name": briefing["name"],
                "include_kpis": briefing["include_kpis"],
                "include_trends": briefing["include_trends"],
                "include_anomalies": briefing["include_anomalies"]
            }
        )
        
        # Send email
        await send_briefing_email(
            recipients=briefing["recipients"],
            subject=content["subject"],
            html_body=content["html"],
            pdf_attachment=content["pdf"],
            pdf_filename=content["pdf_filename"]
        )
        
        return {
            "success": True,
            "message": f"Briefing sent to {len(briefing['recipients'])} recipients"
        }
        
    except Exception as e:
        logger.error(f"Failed to send briefing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send briefing: {str(e)}")


@router.get("/schedules/presets")
async def get_schedule_presets():
    """Get common schedule presets."""
    return {
        "presets": [
            {"label": "Daily at 8:00 AM", "cron": "0 8 * * *", "description": "Every day at 8:00 AM"},
            {"label": "Weekdays at 7:00 AM", "cron": "0 7 * * 1-5", "description": "Monday-Friday at 7:00 AM"},
            {"label": "Weekly on Monday at 9:00 AM", "cron": "0 9 * * 1", "description": "Every Monday at 9:00 AM"},
            {"label": "Monthly on 1st at 10:00 AM", "cron": "0 10 1 * *", "description": "First day of month at 10:00 AM"},
            {"label": "Every 6 hours", "cron": "0 */6 * * *", "description": "Every 6 hours"},
        ]
    }

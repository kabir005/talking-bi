from sqlalchemy import select, func
from database.models import UserPreference
from database.db import AsyncSessionLocal
from typing import Dict, List


PREFERENCE_WEIGHTS = {
    "chart_type_change": 2,
    "axis_column_set": 1,
    "preset_selected": 3,
    "filter_added": 1,
    "tile_deleted": -1,
    "drill_down_used": 1,
    "insight_expanded": 2,
    "ml_triggered": 2,
    "export_type": 1,
    "role_selected": 3,
}


async def log_preference(action_type: str, from_value: str, to_value: str):
    """Log a user preference action"""
    weight = PREFERENCE_WEIGHTS.get(action_type, 1.0)
    
    async with AsyncSessionLocal() as session:
        preference = UserPreference(
            action_type=action_type,
            from_value=from_value,
            to_value=to_value,
            weight=weight
        )
        session.add(preference)
        await session.commit()


async def get_top_preferences(limit: int = 10) -> List[Dict]:
    """Get top preferences by aggregated weight"""
    async with AsyncSessionLocal() as session:
        # Group by action_type and to_value, sum weights
        stmt = select(
            UserPreference.action_type,
            UserPreference.to_value,
            func.sum(UserPreference.weight).label('total_weight'),
            func.count(UserPreference.id).label('count')
        ).group_by(
            UserPreference.action_type,
            UserPreference.to_value
        ).order_by(
            func.sum(UserPreference.weight).desc()
        ).limit(limit)
        
        result = await session.execute(stmt)
        rows = result.all()
        
        return [
            {
                "action_type": row.action_type,
                "preferred_value": row.to_value,
                "total_weight": float(row.total_weight),
                "count": row.count
            }
            for row in rows
        ]


async def get_chart_type_preference() -> str:
    """Get most preferred chart type"""
    async with AsyncSessionLocal() as session:
        stmt = select(
            UserPreference.to_value,
            func.sum(UserPreference.weight).label('total_weight')
        ).where(
            UserPreference.action_type == 'chart_type_change'
        ).group_by(
            UserPreference.to_value
        ).order_by(
            func.sum(UserPreference.weight).desc()
        ).limit(1)
        
        result = await session.execute(stmt)
        row = result.first()
        
        return row.to_value if row else "line"


async def get_preset_preference() -> str:
    """Get most preferred dashboard preset"""
    async with AsyncSessionLocal() as session:
        stmt = select(
            UserPreference.to_value,
            func.sum(UserPreference.weight).label('total_weight')
        ).where(
            UserPreference.action_type == 'preset_selected'
        ).group_by(
            UserPreference.to_value
        ).order_by(
            func.sum(UserPreference.weight).desc()
        ).limit(1)
        
        result = await session.execute(stmt)
        row = result.first()
        
        return row.to_value if row else "executive"

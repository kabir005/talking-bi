from fastapi import APIRouter

router = APIRouter()

@router.get("/dashboard/{dashboard_id}")
async def export_dashboard(dashboard_id: str):
    return {"message": "Dashboard export", "dashboard_id": dashboard_id}

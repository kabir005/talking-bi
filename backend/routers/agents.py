from fastapi import APIRouter

router = APIRouter()

@router.post("/clean/{dataset_id}")
async def trigger_cleaning_agent(dataset_id: str):
    return {"message": "Cleaning agent triggered", "dataset_id": dataset_id}

@router.post("/analyze/{dataset_id}")
async def trigger_analyst_agent(dataset_id: str):
    return {"message": "Analyst agent triggered", "dataset_id": dataset_id}

@router.post("/insights/{dataset_id}")
async def trigger_insight_agent(dataset_id: str):
    return {"message": "Insight agent triggered", "dataset_id": dataset_id}

@router.post("/root-cause")
async def trigger_root_cause_agent():
    return {"message": "Root cause agent triggered"}

@router.get("/status/{run_id}")
async def get_agent_status(run_id: str):
    return {"run_id": run_id, "status": "completed"}

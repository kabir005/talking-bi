"""
conversation.py — REST endpoint for multi-turn conversational BI queries.
POST /api/conversation/chat
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from agents.conversation_agent import converse

router = APIRouter()


class ConversationRequest(BaseModel):
    dataset_id: str
    query: str
    history: List[Dict] = []
    schema: dict = {}
    kpis: Optional[dict] = None


class ConversationResponse(BaseModel):
    answer: str
    history: List[Dict]
    dataset_id: str
    context_used: bool = False
    rag_context: str = ""
    turns_in_context: int = 0


@router.post("/chat", response_model=ConversationResponse)
async def chat(req: ConversationRequest):
    """
    Multi-turn conversational BI query.
    Maintains sliding-window history; caller passes history back each turn.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = await converse(
        query=req.query,
        dataset_id=req.dataset_id,
        schema=req.schema,
        history=req.history,
        kpis=req.kpis,
    )
    
    return {
        "answer": result.get("answer", ""),
        "history": result.get("history", []),
        "dataset_id": req.dataset_id,
        "context_used": result.get("context_used", False),
        "rag_context": result.get("rag_context", ""),
        "turns_in_context": result.get("turns_in_context", 0)
    }

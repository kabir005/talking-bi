from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from database.db import get_db
from database.models import QueryMemory, UserPreference
from memory.faiss_store import search_similar, add_to_index
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

router = APIRouter()


class QueryMemoryCreate(BaseModel):
    dataset_id: str
    query_text: str
    response_json: Dict[str, Any]


class PreferenceCreate(BaseModel):
    action_type: str
    from_value: str
    to_value: str
    weight: float = 1.0


@router.get("/queries")
async def get_query_history(
    dataset_id: Optional[str] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get query history, optionally filtered by dataset.
    Returns most recent queries first.
    """
    query = select(QueryMemory).order_by(desc(QueryMemory.created_at))
    
    if dataset_id:
        query = query.where(QueryMemory.dataset_id == dataset_id)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    memories = result.scalars().all()
    
    queries = []
    for memory in memories:
        # Extract summary from response if available
        response_summary = None
        if memory.response_json:
            if isinstance(memory.response_json, dict):
                response_summary = memory.response_json.get('summary') or memory.response_json.get('intent')
        
        queries.append({
            'id': memory.id,
            'dataset_id': memory.dataset_id,
            'query_text': memory.query_text,
            'response_summary': response_summary,
            'created_at': memory.created_at.isoformat() if memory.created_at else None
        })
    
    return {'queries': queries, 'total': len(queries)}


@router.get("/similar")
async def get_similar_queries(
    q: str,
    dataset_id: Optional[str] = None,
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Find similar queries using semantic search (FAISS).
    """
    try:
        # Search in FAISS index
        similar_ids = await search_similar(q, limit=limit * 2)  # Get more to filter
        
        if not similar_ids:
            return {'similar_queries': [], 'total': 0}
        
        # Get full query details from database
        query = select(QueryMemory).where(QueryMemory.embedding_id.in_(similar_ids))
        
        if dataset_id:
            query = query.where(QueryMemory.dataset_id == dataset_id)
        
        result = await db.execute(query)
        memories = result.scalars().all()
        
        # Sort by original FAISS order
        memory_dict = {m.embedding_id: m for m in memories}
        sorted_memories = [memory_dict[id] for id in similar_ids if id in memory_dict]
        
        similar_queries = []
        for memory in sorted_memories[:limit]:
            response_summary = None
            if memory.response_json and isinstance(memory.response_json, dict):
                response_summary = memory.response_json.get('summary') or memory.response_json.get('intent')
            
            similar_queries.append({
                'id': memory.id,
                'query_text': memory.query_text,
                'response_summary': response_summary,
                'created_at': memory.created_at.isoformat() if memory.created_at else None
            })
        
        return {'similar_queries': similar_queries, 'total': len(similar_queries)}
    
    except Exception as e:
        # Fallback to text-based search if FAISS fails
        query = select(QueryMemory).where(
            QueryMemory.query_text.contains(q)
        ).order_by(desc(QueryMemory.created_at)).limit(limit)
        
        if dataset_id:
            query = query.where(QueryMemory.dataset_id == dataset_id)
        
        result = await db.execute(query)
        memories = result.scalars().all()
        
        similar_queries = []
        for memory in memories:
            response_summary = None
            if memory.response_json and isinstance(memory.response_json, dict):
                response_summary = memory.response_json.get('summary') or memory.response_json.get('intent')
            
            similar_queries.append({
                'id': memory.id,
                'query_text': memory.query_text,
                'response_summary': response_summary,
                'created_at': memory.created_at.isoformat() if memory.created_at else None
            })
        
        return {'similar_queries': similar_queries, 'total': len(similar_queries)}


@router.post("/queries")
async def save_query(
    request: QueryMemoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Save a query to memory and add to FAISS index.
    """
    try:
        # Add to FAISS index and get embedding ID
        embedding_id = await add_to_index(request.query_text)
        
        # Save to database
        memory = QueryMemory(
            dataset_id=request.dataset_id,
            query_text=request.query_text,
            response_json=request.response_json,
            embedding_id=embedding_id
        )
        
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        
        return {
            'id': memory.id,
            'embedding_id': embedding_id,
            'message': 'Query saved to memory'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save query: {str(e)}")


@router.delete("/queries/{query_id}")
async def delete_query(
    query_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a query from memory.
    """
    result = await db.execute(select(QueryMemory).where(QueryMemory.id == query_id))
    memory = result.scalar_one_or_none()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Query not found")
    
    await db.delete(memory)
    await db.commit()
    
    return {'message': 'Query deleted from memory'}


@router.get("/preferences")
async def get_user_preferences(
    action_type: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user preferences, optionally filtered by action type.
    Returns preferences sorted by weight (most important first).
    """
    query = select(UserPreference).order_by(desc(UserPreference.weight))
    
    if action_type:
        query = query.where(UserPreference.action_type == action_type)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    preferences = result.scalars().all()
    
    prefs = []
    for pref in preferences:
        prefs.append({
            'id': pref.id,
            'action_type': pref.action_type,
            'from_value': pref.from_value,
            'to_value': pref.to_value,
            'weight': pref.weight,
            'created_at': pref.created_at.isoformat() if pref.created_at else None
        })
    
    return {'preferences': prefs, 'total': len(prefs)}


@router.post("/preferences")
async def save_preference(
    request: PreferenceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Save a user preference (e.g., chart type change, axis swap).
    If preference already exists, increase its weight.
    """
    # Check if preference already exists
    result = await db.execute(
        select(UserPreference).where(
            UserPreference.action_type == request.action_type,
            UserPreference.from_value == request.from_value,
            UserPreference.to_value == request.to_value
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Increase weight
        existing.weight += request.weight
        await db.commit()
        await db.refresh(existing)
        
        return {
            'id': existing.id,
            'weight': existing.weight,
            'message': 'Preference weight increased'
        }
    else:
        # Create new preference
        preference = UserPreference(
            action_type=request.action_type,
            from_value=request.from_value,
            to_value=request.to_value,
            weight=request.weight
        )
        
        db.add(preference)
        await db.commit()
        await db.refresh(preference)
        
        return {
            'id': preference.id,
            'weight': preference.weight,
            'message': 'Preference saved'
        }


@router.get("/preferences/suggest")
async def suggest_based_on_preferences(
    action_type: str,
    from_value: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Suggest a value based on user preferences.
    Returns the most common 'to_value' for a given 'from_value' and action type.
    """
    result = await db.execute(
        select(UserPreference).where(
            UserPreference.action_type == action_type,
            UserPreference.from_value == from_value
        ).order_by(desc(UserPreference.weight))
    )
    preferences = result.scalars().all()
    
    if not preferences:
        return {'suggestion': None, 'confidence': 0}
    
    # Get top suggestion
    top_pref = preferences[0]
    total_weight = sum(p.weight for p in preferences)
    confidence = (top_pref.weight / total_weight) * 100 if total_weight > 0 else 0
    
    return {
        'suggestion': top_pref.to_value,
        'confidence': round(confidence, 2),
        'alternatives': [
            {'value': p.to_value, 'weight': p.weight}
            for p in preferences[1:4]  # Top 3 alternatives
        ]
    }


@router.delete("/preferences/{preference_id}")
async def delete_preference(
    preference_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user preference.
    """
    result = await db.execute(select(UserPreference).where(UserPreference.id == preference_id))
    preference = result.scalar_one_or_none()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    await db.delete(preference)
    await db.commit()
    
    return {'message': 'Preference deleted'}


@router.post("/preferences/reset")
async def reset_preferences(
    action_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset user preferences, optionally filtered by action type.
    """
    if action_type:
        result = await db.execute(
            select(UserPreference).where(UserPreference.action_type == action_type)
        )
    else:
        result = await db.execute(select(UserPreference))
    
    preferences = result.scalars().all()
    
    for pref in preferences:
        await db.delete(pref)
    
    await db.commit()
    
    return {
        'message': f'Reset {len(preferences)} preferences',
        'count': len(preferences)
    }


@router.get("/stats")
async def get_memory_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics about query memory and preferences.
    """
    # Count queries
    query_result = await db.execute(select(QueryMemory))
    total_queries = len(query_result.scalars().all())
    
    # Count preferences
    pref_result = await db.execute(select(UserPreference))
    total_preferences = len(pref_result.scalars().all())
    
    # Get unique datasets
    dataset_result = await db.execute(
        select(QueryMemory.dataset_id).distinct()
    )
    unique_datasets = len(dataset_result.scalars().all())
    
    # Get preference types
    type_result = await db.execute(
        select(UserPreference.action_type).distinct()
    )
    preference_types = type_result.scalars().all()
    
    return {
        'total_queries': total_queries,
        'total_preferences': total_preferences,
        'unique_datasets': unique_datasets,
        'preference_types': list(preference_types)
    }

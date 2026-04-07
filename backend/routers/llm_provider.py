"""
LLM Provider Router - Manage LLM provider settings
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.ollama_service import OllamaService, UnifiedLLMService
import os

router = APIRouter()


class LLMTestRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 100


@router.get("/status")
async def get_llm_status():
    """
    Get status of all LLM providers
    
    Returns:
        Provider availability and configuration
    """
    try:
        status = await UnifiedLLMService.get_provider_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get LLM status: {str(e)}")


@router.get("/ollama/models")
async def list_ollama_models():
    """
    List available Ollama models
    
    Returns:
        List of model names
    """
    try:
        if not await OllamaService.is_available():
            raise HTTPException(status_code=503, detail="Ollama is not available")
        
        models = await OllamaService.list_models()
        return {
            "models": models,
            "count": len(models),
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.post("/test")
async def test_llm(request: LLMTestRequest):
    """
    Test LLM generation with a prompt
    
    Returns:
        Generated response and metadata
    """
    try:
        response = await UnifiedLLMService.call_llm(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            provider=request.provider
        )
        
        # Get actual provider used
        status = await UnifiedLLMService.get_provider_status()
        
        return {
            "prompt": request.prompt,
            "response": response,
            "provider_used": status["current_provider"],
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM test failed: {str(e)}")


@router.get("/privacy-mode")
async def get_privacy_mode():
    """
    Check if privacy mode (local LLM) is enabled
    
    Returns:
        Privacy mode status
    """
    ollama_available = await OllamaService.is_available()
    provider = os.getenv("LLM_PROVIDER", "auto")
    
    privacy_mode = (provider == "ollama") or (provider == "auto" and ollama_available)
    
    return {
        "privacy_mode_enabled": privacy_mode,
        "using_local_llm": ollama_available,
        "provider": provider,
        "description": "Privacy mode uses local Ollama instead of cloud APIs"
    }

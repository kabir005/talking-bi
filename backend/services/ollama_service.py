"""
Ollama Service - Local LLM support for privacy mode
"""

import logging
import os
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")


class OllamaService:
    """Local LLM service using Ollama"""
    
    @staticmethod
    async def is_available() -> bool:
        """Check if Ollama is running"""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama not available: {str(e)}")
            return False
    
    @staticmethod
    async def list_models() -> list:
        """List available Ollama models"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [model["name"] for model in data.get("models", [])]
                return []
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {str(e)}")
            return []
    
    @staticmethod
    async def generate(
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        system: Optional[str] = None
    ) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: User prompt
            model: Model name (defaults to OLLAMA_MODEL env var)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: System prompt
            
        Returns:
            Generated text
        """
        model = model or OLLAMA_MODEL
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system:
                payload["system"] = system
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Ollama generation failed: {str(e)}")
            raise
    
    @staticmethod
    async def chat(
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Chat completion using Ollama
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            
        Returns:
            Assistant response
        """
        model = model or OLLAMA_MODEL
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/api/chat",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("message", {}).get("content", "")
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Ollama chat failed: {str(e)}")
            raise
    
    @staticmethod
    async def embed(text: str, model: str = "llama2") -> list:
        """
        Generate embeddings using Ollama
        
        Args:
            text: Text to embed
            model: Model name
            
        Returns:
            Embedding vector
        """
        try:
            payload = {
                "model": model,
                "prompt": text
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/api/embeddings",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("embedding", [])
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Ollama embedding failed: {str(e)}")
            raise


class UnifiedLLMService:
    """
    Unified LLM service that routes to Groq or Ollama based on configuration
    """
    
    @staticmethod
    async def call_llm(
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        system: Optional[str] = None,
        provider: Optional[str] = None
    ) -> str:
        """
        Call LLM with automatic provider selection
        
        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            system: System prompt
            provider: Force specific provider ('groq', 'ollama', or None for auto)
            
        Returns:
            Generated text
        """
        # Determine provider
        if provider is None:
            provider = os.getenv("LLM_PROVIDER", "auto")
        
        # Auto mode: try Ollama first if available, fallback to Groq
        if provider == "auto":
            if await OllamaService.is_available():
                provider = "ollama"
                logger.info("Using Ollama (local) for LLM")
            else:
                provider = "groq"
                logger.info("Using Groq (cloud) for LLM")
        
        # Route to appropriate provider
        if provider == "ollama":
            try:
                return await OllamaService.generate(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system=system
                )
            except Exception as e:
                logger.warning(f"Ollama failed, falling back to Groq: {str(e)}")
                provider = "groq"
        
        if provider == "groq":
            # Use existing Groq service
            from services.llm_service import call_llm as groq_call_llm
            return await groq_call_llm(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        raise ValueError(f"Unknown LLM provider: {provider}")
    
    @staticmethod
    async def get_provider_status() -> Dict[str, Any]:
        """Get status of all LLM providers"""
        groq_available = bool(os.getenv("GROQ_API_KEY"))
        ollama_available = await OllamaService.is_available()
        
        current_provider = os.getenv("LLM_PROVIDER", "auto")
        if current_provider == "auto":
            current_provider = "ollama" if ollama_available else "groq"
        
        ollama_models = []
        if ollama_available:
            ollama_models = await OllamaService.list_models()
        
        return {
            "current_provider": current_provider,
            "groq": {
                "available": groq_available,
                "configured": groq_available
            },
            "ollama": {
                "available": ollama_available,
                "base_url": OLLAMA_BASE_URL,
                "default_model": OLLAMA_MODEL,
                "models": ollama_models
            }
        }

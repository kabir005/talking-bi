"""
LLM Service
Wrapper for LLM API calls.
"""

import os
import logging
from groq import AsyncGroq

logger = logging.getLogger(__name__)


async def call_llm(prompt: str, model: str = "llama-3.3-70b-versatile", temperature: float = 0.7, max_tokens: int = 1000) -> str:
    """
    Call LLM with the given prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        model: Model name (default: llama-3.3-70b-versatile)
        temperature: Temperature for generation (0-1)
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated text response
    """
    try:
        client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise

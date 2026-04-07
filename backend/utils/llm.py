import os
import json
import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from config import GROQ_API_KEY

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
PRIMARY_MODEL = "llama-3.3-70b-versatile"  # Updated to supported model
FALLBACK_MODEL = "llama-3.1-8b-instant"


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
async def call_llm(
    messages: list[dict],
    system: str = "",
    model: str = PRIMARY_MODEL,
    json_mode: bool = False
) -> str:
    """
    Call Groq API with automatic retry and fallback.
    If PRIMARY_MODEL rate-limits, falls back to FALLBACK_MODEL.
    Returns string content of response.
    If json_mode=True, sets response_format to json_object.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY not configured. Please set it in .env file.")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)
    
    payload = {
        "model": model,
        "messages": full_messages,
        "max_tokens": 2048,
        "temperature": 0.1,
    }
    
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(GROQ_BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error {e.response.status_code}: {e.response.text[:200]}")
            # Rate limited or model unavailable — fall back to smaller model
            if (e.response.status_code == 429 or e.response.status_code == 503) and model == PRIMARY_MODEL:
                logger.info(f"Falling back to {FALLBACK_MODEL}")
                return await call_llm(messages, system, FALLBACK_MODEL, json_mode)
            raise
        except httpx.TimeoutException as e:
            logger.error(f"Timeout error: {e}")
            # Timeout — try fallback model
            if model == PRIMARY_MODEL:
                logger.info(f"Timeout, falling back to {FALLBACK_MODEL}")
                return await call_llm(messages, system, FALLBACK_MODEL, json_mode)
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {type(e).__name__}: {e}")
            raise

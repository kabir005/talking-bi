"""
Conversation Agent - Multi-turn conversational queries with context memory
Maintains sliding window of last 6 turns for context-aware responses
"""

from typing import List, Dict, Any
import logging
from services.rag_service import retrieve_context
from utils.llm import call_llm

logger = logging.getLogger(__name__)

MAX_HISTORY = 6  # Sliding window size


async def converse(
    query: str,
    dataset_id: str,
    schema: Dict[str, str],
    history: List[Dict[str, str]],
    kpis: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Process a conversational query with context from previous turns
    
    Args:
        query: User's current question
        dataset_id: Dataset being queried
        schema: Dataset schema (column names and types)
        history: Previous conversation turns [{"role": "user/assistant", "content": "..."}]
        kpis: Optional KPI data for context
    
    Returns:
        {
            "answer": str,
            "history": List[Dict],  # Updated history
            "context_used": bool,
            "rag_context": str
        }
    """
    try:
        # Retrieve relevant context from RAG
        rag_context = await retrieve_context(query, dataset_id, n_results=3)
        
        # Build system message with schema and context
        system_content = f"""You are a data analysis assistant helping users understand their dataset.

Dataset Schema:
{_format_schema(schema)}

"""
        
        if kpis:
            system_content += f"\nKey Performance Indicators:\n{_format_kpis(kpis)}\n"
        
        if rag_context:
            system_content += f"\nRelevant Context:\n{rag_context}\n"
        
        system_content += """
Instructions:
- Answer questions about the data clearly and concisely
- Reference specific columns and values when relevant
- If the user refers to "last query" or "previous", use conversation history
- If you don't have enough information, ask clarifying questions
- Format numbers appropriately (use commas for thousands)
"""
        
        # Build messages with sliding window history
        messages = [{"role": "system", "content": system_content}]
        
        # Add last N turns from history (sliding window)
        recent_history = history[-MAX_HISTORY:] if len(history) > MAX_HISTORY else history
        messages.extend(recent_history)
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        # Call LLM
        response = await call_llm(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        # Update history
        updated_history = history + [
            {"role": "user", "content": query},
            {"role": "assistant", "content": response}
        ]
        
        return {
            "answer": response,
            "history": updated_history,
            "context_used": bool(rag_context),
            "rag_context": rag_context,
            "turns_in_context": len(recent_history) // 2
        }
        
    except Exception as e:
        logger.error(f"Conversation error: {e}")
        
        # Fallback response
        return {
            "answer": f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question.",
            "history": history + [
                {"role": "user", "content": query},
                {"role": "assistant", "content": "Error occurred"}
            ],
            "context_used": False,
            "rag_context": "",
            "error": str(e)
        }


def _format_schema(schema: Dict[str, str]) -> str:
    """Format schema for display"""
    lines = []
    for col, dtype in schema.items():
        lines.append(f"  - {col}: {dtype}")
    return "\n".join(lines)


def _format_kpis(kpis: Dict[str, Any]) -> str:
    """Format KPIs for display"""
    lines = []
    for col, data in list(kpis.items())[:5]:  # Top 5 KPIs
        kpi_line = f"  - {col}:"
        if "total" in data:
            kpi_line += f" Total={data['total']:.2f}"
        if "mean" in data:
            kpi_line += f" Avg={data['mean']:.2f}"
        if "median" in data:
            kpi_line += f" Median={data['median']:.2f}"
        lines.append(kpi_line)
    return "\n".join(lines)


async def summarize_conversation(history: List[Dict[str, str]]) -> str:
    """
    Generate a summary of the conversation so far
    Useful for long conversations to compress context
    """
    if not history:
        return "No conversation history yet."
    
    try:
        # Extract user queries and assistant responses
        conversation_text = "\n".join([
            f"{msg['role'].title()}: {msg['content']}"
            for msg in history[-10:]  # Last 10 messages
        ])
        
        messages = [
            {
                "role": "system",
                "content": "Summarize the following conversation in 2-3 sentences, focusing on key questions asked and insights discovered."
            },
            {
                "role": "user",
                "content": conversation_text
            }
        ]
        
        summary = await call_llm(messages, temperature=0.5, max_tokens=150)
        return summary
        
    except Exception as e:
        logger.error(f"Error summarizing conversation: {e}")
        return "Unable to generate summary."

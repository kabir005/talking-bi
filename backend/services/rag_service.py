"""
RAG (Retrieval-Augmented Generation) Service
Stores dataset context in ChromaDB and retrieves relevant chunks for LLM queries
"""

import pandas as pd
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Global ChromaDB collection
_chroma_collection = None


async def init_rag():
    """Initialize ChromaDB collection for RAG"""
    global _chroma_collection
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./data/chroma"
        ))
        
        _chroma_collection = client.get_or_create_collection(
            name="dataset_context",
            metadata={"description": "Dataset context for RAG"}
        )
        
        logger.info("✓ RAG service initialized with ChromaDB")
        return True
        
    except Exception as e:
        logger.warning(f"⚠ RAG service not available: {e}")
        return False


async def index_dataset(
    dataset_id: str,
    df: pd.DataFrame,
    schema: Dict[str, str],
    insights: List[Dict[str, Any]],
    kpis: Dict[str, Any] = None
) -> bool:
    """
    Chunk and store dataset context in ChromaDB for RAG
    
    Args:
        dataset_id: Unique dataset identifier
        df: DataFrame with data
        schema: Column name to type mapping
        insights: List of generated insights
        kpis: Optional KPI dictionary
    
    Returns:
        True if indexing successful, False otherwise
    """
    if _chroma_collection is None:
        logger.warning("ChromaDB not initialized, skipping RAG indexing")
        return False
    
    try:
        # Build context chunks
        chunks = []
        metadatas = []
        ids = []
        
        # Chunk 1: Schema information
        schema_text = f"Dataset has {len(schema)} columns: {', '.join(schema.keys())}. "
        schema_text += f"Column types: {', '.join([f'{k}={v}' for k, v in schema.items()])}"
        chunks.append(schema_text)
        metadatas.append({"type": "schema", "dataset_id": dataset_id})
        ids.append(f"{dataset_id}_schema")
        
        # Chunk 2: Data summary
        summary_text = f"Dataset contains {len(df)} rows and {len(df.columns)} columns. "
        
        # Add numeric column stats
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            summary_text += f"Numeric columns: {', '.join(numeric_cols[:5])}. "
        
        # Add sample data
        sample_data = df.head(3).to_string(index=False)
        summary_text += f"Sample data:\n{sample_data}"
        
        chunks.append(summary_text)
        metadatas.append({"type": "summary", "dataset_id": dataset_id})
        ids.append(f"{dataset_id}_summary")
        
        # Chunk 3-N: KPIs
        if kpis:
            for i, (col, kpi_data) in enumerate(list(kpis.items())[:5]):
                kpi_text = f"KPI for {col}: "
                if "total" in kpi_data:
                    kpi_text += f"Total = {kpi_data['total']:.2f}, "
                if "mean" in kpi_data:
                    kpi_text += f"Average = {kpi_data['mean']:.2f}, "
                if "median" in kpi_data:
                    kpi_text += f"Median = {kpi_data['median']:.2f}, "
                if "min" in kpi_data and "max" in kpi_data:
                    kpi_text += f"Range = {kpi_data['min']:.2f} to {kpi_data['max']:.2f}"
                
                chunks.append(kpi_text)
                metadatas.append({"type": "kpi", "dataset_id": dataset_id, "column": col})
                ids.append(f"{dataset_id}_kpi_{i}")
        
        # Chunk N+1 onwards: Insights
        for i, insight in enumerate(insights[:10]):  # Limit to 10 insights
            insight_text = insight.get("text", "")
            if insight_text:
                chunks.append(insight_text)
                metadatas.append({
                    "type": "insight",
                    "dataset_id": dataset_id,
                    "category": insight.get("category", "general")
                })
                ids.append(f"{dataset_id}_insight_{i}")
        
        # Store in ChromaDB
        if chunks:
            _chroma_collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"✓ Indexed {len(chunks)} chunks for dataset {dataset_id}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error indexing dataset {dataset_id}: {e}")
        return False


async def retrieve_context(
    query: str,
    dataset_id: str,
    n_results: int = 3
) -> str:
    """
    Retrieve top-k relevant chunks for a query using semantic search
    
    Args:
        query: User query text
        dataset_id: Dataset to search within
        n_results: Number of results to retrieve
    
    Returns:
        Concatenated context string
    """
    if _chroma_collection is None:
        logger.warning("ChromaDB not initialized, returning empty context")
        return ""
    
    try:
        results = _chroma_collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"dataset_id": dataset_id}
        )
        
        if results and results['documents'] and len(results['documents']) > 0:
            context = "\n\n".join(results['documents'][0])
            logger.info(f"✓ Retrieved {len(results['documents'][0])} context chunks")
            return context
        
        return ""
        
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return ""


async def delete_dataset_context(dataset_id: str) -> bool:
    """Delete all context chunks for a dataset"""
    if _chroma_collection is None:
        return False
    
    try:
        # Get all IDs for this dataset
        results = _chroma_collection.get(
            where={"dataset_id": dataset_id}
        )
        
        if results and results['ids']:
            _chroma_collection.delete(ids=results['ids'])
            logger.info(f"✓ Deleted {len(results['ids'])} chunks for dataset {dataset_id}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error deleting context for dataset {dataset_id}: {e}")
        return False

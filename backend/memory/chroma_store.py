from config import CHROMA_DB_PATH
from typing import List, Dict

# Try to import optional dependencies
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

# Global client
chroma_client = None
collection = None


async def init_chroma():
    """Initialize ChromaDB client and collection"""
    global chroma_client, collection
    
    if not CHROMA_AVAILABLE:
        raise ImportError("ChromaDB not available")
    
    chroma_client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    collection = chroma_client.get_or_create_collection(
        name="talking_bi_memory",
        metadata={"description": "Query and response memory for Talking BI"}
    )


async def store_document(doc_id: str, text: str, metadata: dict):
    """Store a document in ChromaDB"""
    global collection
    
    if not CHROMA_AVAILABLE or collection is None:
        return  # Silently skip if not available
    
    collection.add(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata]
    )


async def query_documents(query_text: str, n_results: int = 3) -> List[Dict]:
    """Query similar documents from ChromaDB"""
    global collection
    
    if not CHROMA_AVAILABLE or collection is None or collection.count() == 0:
        return []  # Return empty list if not available
    
    results = collection.query(
        query_texts=[query_text],
        n_results=min(n_results, collection.count())
    )
    
    # Format results
    formatted = []
    if results['ids'] and len(results['ids'][0]) > 0:
        for i in range(len(results['ids'][0])):
            formatted.append({
                "id": results['ids'][0][i],
                "document": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
    
    return formatted

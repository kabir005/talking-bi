import os
from typing import List, Dict
from config import FAISS_INDEX_PATH, MODELS_DIR

# Try to import optional dependencies
try:
    import faiss
    import numpy as np
    import pickle
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# Global variables
model = None
index = None
metadata_store = {}  # Maps index ID to metadata


async def init_faiss():
    """Initialize FAISS index and sentence transformer model"""
    global model, index, metadata_store
    
    if not FAISS_AVAILABLE:
        raise ImportError("FAISS and sentence-transformers not available")
    
    # Load sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=MODELS_DIR)
    
    # Load or create FAISS index
    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
        # Load metadata
        metadata_path = FAISS_INDEX_PATH + ".metadata"
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                metadata_store = pickle.load(f)
    else:
        # Create new index (384 dimensions for all-MiniLM-L6-v2)
        index = faiss.IndexFlatL2(384)
        metadata_store = {}


async def store_query(query: str, response: dict, metadata: dict) -> str:
    """
    Encode query, add to FAISS index, return internal ID
    """
    global model, index, metadata_store
    
    if not FAISS_AVAILABLE or model is None:
        return "0"  # Return dummy ID if not available
    
    # Generate embedding
    embedding = model.encode([query])[0]
    embedding = np.array([embedding]).astype('float32')
    
    # Add to index
    current_id = index.ntotal
    index.add(embedding)
    
    # Store metadata
    metadata_store[current_id] = {
        "query": query,
        "response": response,
        "metadata": metadata
    }
    
    # Save index and metadata
    faiss.write_index(index, FAISS_INDEX_PATH)
    metadata_path = FAISS_INDEX_PATH + ".metadata"
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata_store, f)
    
    return str(current_id)


async def retrieve_similar(query: str, top_k: int = 3) -> List[Dict]:
    """
    Find top-k most similar past queries, return their responses as context
    """
    global model, index, metadata_store
    
    if not FAISS_AVAILABLE or model is None or index.ntotal == 0:
        return []  # Return empty list if not available
    
    # Generate embedding for query
    embedding = model.encode([query])[0]
    embedding = np.array([embedding]).astype('float32')
    
    # Search
    k = min(top_k, index.ntotal)
    distances, indices = index.search(embedding, k)
    
    # Retrieve metadata
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        if idx in metadata_store:
            result = metadata_store[idx].copy()
            result["similarity_score"] = float(1 / (1 + distance))  # Convert distance to similarity
            results.append(result)
    
    return results


# Aliases for backward compatibility
search_similar = retrieve_similar
add_to_index = store_query

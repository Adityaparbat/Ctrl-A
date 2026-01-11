"""
Embedding Module - Semantic Embeddings for GraphRAG
This module provides semantic embedding functionality using SentenceTransformers.
Used for:
1. Query embedding for semantic search
2. Domain similarity checking
3. Node content embedding for vector storage in Neo4j
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union

# Load pre-trained sentence transformer model
# Using all-MiniLM-L6-v2: lightweight, fast, good for semantic similarity
# Dimension: 384
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Initialize model (loaded once, reused)
_model = None


def get_embedding_model() -> SentenceTransformer:
    """Get or initialize the embedding model (singleton pattern)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def encode_text(text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """
    Encode text(s) into embedding vector(s).
    
    Args:
        text: Single string or list of strings to encode
    
    Returns:
        Single embedding vector (list of floats) or list of embedding vectors
        Dimension: 384 (all-MiniLM-L6-v2)
    """
    model = get_embedding_model()
    
    if isinstance(text, str):
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    else:
        embeddings = model.encode(text, convert_to_numpy=True)
        return embeddings.tolist()


def compute_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two embedding vectors.
    
    Args:
        vec1: First embedding vector
        vec2: Second embedding vector
    
    Returns:
        Cosine similarity score (0.0 to 1.0)
    """
    vec1_arr = np.array(vec1)
    vec2_arr = np.array(vec2)
    
    dot_product = np.dot(vec1_arr, vec2_arr)
    norm1 = np.linalg.norm(vec1_arr)
    norm2 = np.linalg.norm(vec2_arr)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    return float(similarity)


def batch_encode_texts(texts: List[str]) -> List[List[float]]:
    """
    Encode multiple texts efficiently in a batch.
    
    Args:
        texts: List of strings to encode
    
    Returns:
        List of embedding vectors
    """
    return encode_text(texts)

"""
ChromaDB configuration and shared utilities.

This module provides a centralized way to configure and initialize ChromaDB
components, eliminating code duplication across different modules.
"""

import os
import logging
from typing import Optional, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from src.utils.config import DB_DIR

# Set up logging
logger = logging.getLogger(__name__)

class ChromaDBConfig:
    """ChromaDB configuration and client management."""
    
    # Default configuration
    DEFAULT_DB_PATH = DB_DIR
    DEFAULT_COLLECTION_NAME = "disability_schemes"
    DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    def __init__(self, 
                 db_path: str = DEFAULT_DB_PATH,
                 collection_name: str = DEFAULT_COLLECTION_NAME,
                 embedding_model: str = DEFAULT_EMBEDDING_MODEL):
        """
        Initialize ChromaDB configuration.
        
        Args:
            db_path (str): Path to the ChromaDB directory
            collection_name (str): Name of the collection to use
            embedding_model (str): Name of the embedding model to use
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Initialize components
        self._client: Optional[chromadb.PersistentClient] = None
        self._embedding_func: Optional[embedding_functions.SentenceTransformerEmbeddingFunction] = None
        self._collection: Optional[chromadb.Collection] = None
    
    def get_client(self) -> chromadb.PersistentClient:
        """Get or create ChromaDB client."""
        if self._client is None:
            try:
                self._client = chromadb.PersistentClient(path=self.db_path)
                logger.info(f"ChromaDB client initialized at: {self.db_path}")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB client: {e}")
                raise RuntimeError(f"Could not initialize ChromaDB client: {e}")
        return self._client
    
    def get_embedding_function(self) -> embedding_functions.SentenceTransformerEmbeddingFunction:
        """Get or create embedding function."""
        if self._embedding_func is None:
            try:
                self._embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=self.embedding_model
                )
                logger.info(f"Embedding function initialized with model: {self.embedding_model}")
            except Exception as e:
                logger.error(f"Failed to initialize embedding function: {e}")
                raise RuntimeError(f"Could not initialize embedding function: {e}")
        return self._embedding_func
    
    def get_collection(self) -> chromadb.Collection:
        """Get or create ChromaDB collection."""
        if self._collection is None:
            try:
                client = self.get_client()
                embedding_func = self.get_embedding_function()
                
                self._collection = client.get_or_create_collection(
                    name=self.collection_name,
                    embedding_function=embedding_func
                )
                logger.info(f"Collection '{self.collection_name}' initialized")
            except Exception as e:
                logger.error(f"Failed to initialize collection: {e}")
                raise RuntimeError(f"Could not initialize collection: {e}")
        return self._collection
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.
        
        Returns:
            Dict[str, Any]: Collection information including count
        """
        try:
            collection = self.get_collection()
            count = collection.count()
            return {
                "collection_name": self.collection_name,
                "total_schemes": count,
                "db_path": self.db_path,
                "embedding_model": self.embedding_model,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
    
    def reset_collection(self) -> None:
        """Reset the collection (delete and recreate)."""
        try:
            client = self.get_client()
            # Delete existing collection if it exists
            try:
                client.delete_collection(name=self.collection_name)
                logger.info(f"Deleted existing collection: {self.collection_name}")
            except Exception:
                # Collection might not exist, which is fine
                pass
            
            # Reset internal state
            self._collection = None
            
            # Recreate collection
            self.get_collection()
            logger.info(f"Collection '{self.collection_name}' reset successfully")
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            raise RuntimeError(f"Could not reset collection: {e}")


# Global configuration instance
_config_instance: Optional[ChromaDBConfig] = None

def get_chroma_config() -> ChromaDBConfig:
    """Get the global ChromaDB configuration instance (singleton pattern)."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ChromaDBConfig()
    return _config_instance

def get_chroma_client() -> chromadb.PersistentClient:
    """Get ChromaDB client using global configuration."""
    config = get_chroma_config()
    return config.get_client()

def get_embedding_function() -> embedding_functions.SentenceTransformerEmbeddingFunction:
    """Get embedding function using global configuration."""
    config = get_chroma_config()
    return config.get_embedding_function()

def get_chroma_collection() -> chromadb.Collection:
    """Get ChromaDB collection using global configuration."""
    config = get_chroma_config()
    return config.get_collection()

def get_collection_info() -> Dict[str, Any]:
    """Get collection information using global configuration."""
    config = get_chroma_config()
    return config.get_collection_info()

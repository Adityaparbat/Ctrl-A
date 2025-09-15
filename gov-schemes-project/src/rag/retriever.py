import logging
from typing import List, Dict, Optional, Any
from src.rag.chroma_config import get_chroma_collection, get_collection_info

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBRetriever:
    """ChromaDB-based retriever for disability schemes."""
    
    def __init__(self):
        """Initialize the ChromaDB retriever using shared configuration."""
        self.collection = get_chroma_collection()
        logger.info("ChromaDB retriever initialized using shared configuration")
    
    def query_schemes(self, user_query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search the vector DB for relevant disability schemes.
        
        Args:
            user_query (str): The search query from user
            top_k (int): Number of results to return (must be positive)
            
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing scheme information
            
        Raises:
            ValueError: If user_query is empty or top_k is invalid
            RuntimeError: If ChromaDB query fails
        """
        # Input validation
        if not user_query or not user_query.strip():
            raise ValueError("User query cannot be empty")
        
        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        
        if self.collection is None:
            raise RuntimeError("ChromaDB collection not initialized")
        
        try:
            # Perform the query
            results = self.collection.query(
                query_texts=[user_query.strip()],
                n_results=min(top_k, 100)  # Cap at 100 to prevent excessive results
            )
            
            # Validate results structure
            if not results or "documents" not in results or "metadatas" not in results:
                logger.warning("Query returned empty or malformed results")
                return []
            
            documents = results["documents"][0] if results["documents"] else []
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            
            if not documents or not metadatas:
                logger.info("No schemes found for the given query")
                return []
            
            # Process results with error handling
            output = []
            for doc, meta in zip(documents, metadatas):
                try:
                    # Safely extract metadata with defaults
                    scheme_info = {
                        "name_and_desc": doc or "No description available",
                        "state": meta.get("state", "Unknown"),
                        "disability_type": meta.get("disability_type", "Not specified"),
                        "support_type": meta.get("support_type", "Not specified"),
                        "apply_link": meta.get("apply_link", "No link available"),
                        "eligibility": meta.get("eligibility"),
                        "benefits": meta.get("benefits"),
                        "contact_info": meta.get("contact_info"),
                        "validity_period": meta.get("validity_period")
                    }
                    output.append(scheme_info)
                    
                except Exception as e:
                    logger.warning(f"Error processing scheme result: {e}")
                    continue
            
            logger.info(f"Successfully retrieved {len(output)} schemes for query: '{user_query}'")
            return output
            
        except Exception as e:
            logger.error(f"ChromaDB query failed: {e}")
            raise RuntimeError(f"Failed to query schemes: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.
        
        Returns:
            Dict[str, Any]: Collection information including count
        """
        return get_collection_info()


# Global retriever instance
_retriever_instance: Optional[ChromaDBRetriever] = None

def get_retriever() -> ChromaDBRetriever:
    """Get the global retriever instance (singleton pattern)."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = ChromaDBRetriever()
    return _retriever_instance

def query_schemes(user_query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function to query schemes using the global retriever.
    
    Args:
        user_query (str): The search query from user
        top_k (int): Number of results to return
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing scheme information
    """
    retriever = get_retriever()
    return retriever.query_schemes(user_query, top_k)

# Example usage
if __name__ == "__main__":
    try:
        # Test the retriever
        retriever = get_retriever()
        
        # Get collection info
        info = retriever.get_collection_info()
        print(f"📊 Collection Info: {info}")
        
        # Test query
        query = "financial aid for visually impaired in Karnataka"
        print(f"\n🔍 Searching for: '{query}'")
        
        schemes = query_schemes(query, top_k=5)
        
        if schemes:
            print(f"\n✅ Found {len(schemes)} schemes:")
            for i, s in enumerate(schemes, 1):
                print(f"{i}. {s['name_and_desc']}")
                print(f"   State: {s['state']} | Type: {s['disability_type']} | Support: {s['support_type']}")
                print(f"   Apply: {s['apply_link']}\n")
        else:
            print("❌ No schemes found for the given query")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Example usage failed: {e}")

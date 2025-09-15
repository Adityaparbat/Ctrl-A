import os
import json
import logging
import time
from typing import List, Dict, Any, Optional
from src.utils.config import DATA_PATH
from src.rag.chroma_config import get_chroma_collection, get_collection_info

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """ChromaDB-based vector store for disability schemes."""
    
    def __init__(self):
        """Initialize the vector store using shared configuration."""
        self.collection = get_chroma_collection()
        logger.info("Vector store initialized using shared configuration")
    
    def load_data(self, data_path: str = DATA_PATH) -> Dict[str, Any]:
        """
        Load schemes JSON file with error handling.
        
        Args:
            data_path (str): Path to the JSON data file
            
        Returns:
            Dict[str, Any]: Loaded JSON data
            
        Raises:
            FileNotFoundError: If the data file doesn't exist
            ValueError: If the JSON is invalid or missing required fields
        """
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Validate data structure
            if not isinstance(data, dict):
                raise ValueError("Data file must contain a JSON object")
            
            if "schemes" not in data:
                raise ValueError("Data file must contain a 'schemes' field")
            
            if not isinstance(data["schemes"], list):
                raise ValueError("'schemes' field must be a list")
            
            logger.info(f"Successfully loaded {len(data['schemes'])} schemes from {data_path}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in data file: {e}")
            raise ValueError(f"Invalid JSON in data file: {e}")
        except Exception as e:
            logger.error(f"Failed to load data file: {e}")
            raise
    
    def populate_vector_db(self, data_path: str = DATA_PATH, clear_existing: bool = False) -> int:
        """
        Insert scheme data into Chroma vector DB.
        
        Args:
            data_path (str): Path to the JSON data file
            clear_existing (bool): Whether to clear existing data before adding new data
            
        Returns:
            int: Number of schemes inserted
            
        Raises:
            RuntimeError: If ChromaDB operations fail
        """
        if self.collection is None:
            raise RuntimeError("ChromaDB collection not initialized")
        
        try:
            # Load data
            data = self.load_data(data_path)
            
            # Clear existing data if requested
            if clear_existing:
                try:
                    # Get all existing IDs and delete them
                    existing = self.collection.get()
                    if existing["ids"]:
                        self.collection.delete(ids=existing["ids"])
                        logger.info("Cleared existing data from collection")
                except Exception as e:
                    logger.warning(f"Could not clear existing data: {e}")
            
            # Prepare data for insertion
            ids, documents, metadatas = [], [], []
            
            for i, scheme in enumerate(data["schemes"]):
                try:
                    # Validate required fields
                    required_fields = ["name", "description", "state", "disability_type", "support_type", "apply_link"]
                    missing_fields = [field for field in required_fields if field not in scheme or not scheme[field]]
                    
                    if missing_fields:
                        logger.warning(f"Scheme {i} missing fields: {missing_fields}, skipping")
                        continue
                    
                    # Create document text
                    doc_text = f"{scheme['name']} - {scheme['description']}"
                    
                    # Create metadata
                    metadata = {
                        "state": str(scheme["state"]),
                        "disability_type": str(scheme["disability_type"]),
                        "support_type": str(scheme["support_type"]),
                        "apply_link": str(scheme["apply_link"])
                    }
                    
                    # Add optional fields if they exist
                    if "eligibility" in scheme:
                        metadata["eligibility"] = str(scheme["eligibility"])
                    if "benefits" in scheme:
                        metadata["benefits"] = str(scheme["benefits"])
                    if "contact_info" in scheme:
                        metadata["contact_info"] = str(scheme["contact_info"])
                    if "validity_period" in scheme:
                        metadata["validity_period"] = str(scheme["validity_period"])
                    
                    ids.append(f"scheme_{i}")
                    documents.append(doc_text)
                    metadatas.append(metadata)
                    
                except Exception as e:
                    logger.warning(f"Error processing scheme {i}: {e}, skipping")
                    continue
            
            if not ids:
                logger.warning("No valid schemes found to insert")
                return 0
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"✅ Successfully inserted {len(ids)} schemes into ChromaDB!")
            return len(ids)
            
        except Exception as e:
            logger.error(f"Failed to populate vector DB: {e}")
            raise RuntimeError(f"Failed to populate vector DB: {e}")
    
    def search_schemes(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Search schemes by text query with error handling.
        
        Args:
            query (str): Search query
            top_k (int): Number of results to return
            
        Returns:
            Dict[str, Any]: Search results from ChromaDB
            
        Raises:
            ValueError: If query is empty or top_k is invalid
            RuntimeError: If ChromaDB query fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        
        if self.collection is None:
            raise RuntimeError("ChromaDB collection not initialized")
        
        try:
            results = self.collection.query(
                query_texts=[query.strip()],
                n_results=min(top_k, 100)  # Cap at 100
            )
            
            logger.info(f"Search completed for query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            raise RuntimeError(f"Failed to search schemes: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.
        
        Returns:
            Dict[str, Any]: Collection information
        """
        return get_collection_info()
    
    def get_all_schemes(self) -> List[Dict[str, Any]]:
        """
        Get all schemes from the collection.
        
        Returns:
            List[Dict[str, Any]]: List of all schemes with metadata
        """
        if self.collection is None:
            raise RuntimeError("ChromaDB collection not initialized")
        
        try:
            # Get all documents from collection
            results = self.collection.get()
            
            schemes = []
            if results["ids"]:
                for i, (doc_id, doc, metadata) in enumerate(zip(
                    results["ids"], 
                    results["documents"], 
                    results["metadatas"]
                )):
                    # Parse document text to extract name and description
                    doc_parts = doc.split(" - ", 1)
                    name = doc_parts[0] if doc_parts else "Unknown Scheme"
                    description = doc_parts[1] if len(doc_parts) > 1 else ""
                    
                    scheme = {
                        "id": doc_id,
                        "name": name,
                        "description": description,
                        **metadata
                    }
                    schemes.append(scheme)
            
            return schemes
            
        except Exception as e:
            logger.error(f"Failed to get all schemes: {e}")
            raise RuntimeError(f"Failed to get all schemes: {e}")
    
    def add_scheme(self, scheme_data: Dict[str, Any]) -> str:
        """
        Add a new scheme to the collection.
        
        Args:
            scheme_data (Dict[str, Any]): Scheme data to add
            
        Returns:
            str: ID of the added scheme
        """
        if self.collection is None:
            raise RuntimeError("ChromaDB collection not initialized")
        
        try:
            # Generate unique ID
            scheme_id = f"scheme_{int(time.time() * 1000)}"
            
            # Create document text
            doc_text = f"{scheme_data['name']} - {scheme_data['description']}"
            
            # Create metadata
            metadata = {
                "state": str(scheme_data.get("state", "")),
                "disability_type": str(scheme_data.get("disability_type", "")),
                "support_type": str(scheme_data.get("support_type", "")),
                "apply_link": str(scheme_data.get("apply_link", ""))
            }
            
            # Add optional fields
            for field in ["eligibility", "benefits", "contact_info", "validity_period"]:
                if field in scheme_data and scheme_data[field]:
                    metadata[field] = str(scheme_data[field])
            
            # Add to collection
            self.collection.add(
                ids=[scheme_id],
                documents=[doc_text],
                metadatas=[metadata]
            )
            
            logger.info(f"Added new scheme: {scheme_data['name']}")
            return scheme_id
            
        except Exception as e:
            logger.error(f"Failed to add scheme: {e}")
            raise RuntimeError(f"Failed to add scheme: {e}")
    
    def update_scheme(self, scheme_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update an existing scheme.
        
        Args:
            scheme_id (str): ID of the scheme to update
            update_data (Dict[str, Any]): Updated scheme data
            
        Returns:
            bool: True if successful, False if scheme not found
        """
        if self.collection is None:
            raise RuntimeError("ChromaDB collection not initialized")
        
        try:
            # Check if scheme exists
            existing = self.collection.get(ids=[scheme_id])
            if not existing["ids"]:
                return False
            
            # Get current data
            current_doc = existing["documents"][0]
            current_metadata = existing["metadatas"][0]
            
            # Update document text if name or description changed
            if "name" in update_data or "description" in update_data:
                name = update_data.get("name", current_doc.split(" - ")[0])
                description = update_data.get("description", current_doc.split(" - ", 1)[1] if " - " in current_doc else "")
                new_doc = f"{name} - {description}"
            else:
                new_doc = current_doc
            
            # Update metadata
            new_metadata = current_metadata.copy()
            for field, value in update_data.items():
                if field not in ["name", "description"] and value is not None:
                    new_metadata[field] = str(value)
            
            # Update in collection (ChromaDB doesn't have direct update, so we delete and re-add)
            self.collection.delete(ids=[scheme_id])
            self.collection.add(
                ids=[scheme_id],
                documents=[new_doc],
                metadatas=[new_metadata]
            )
            
            logger.info(f"Updated scheme: {scheme_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update scheme {scheme_id}: {e}")
            raise RuntimeError(f"Failed to update scheme: {e}")
    
    def delete_scheme(self, scheme_id: str) -> bool:
        """
        Delete a scheme from the collection.
        
        Args:
            scheme_id (str): ID of the scheme to delete
            
        Returns:
            bool: True if successful, False if scheme not found
        """
        if self.collection is None:
            raise RuntimeError("ChromaDB collection not initialized")
        
        try:
            # Check if scheme exists
            existing = self.collection.get(ids=[scheme_id])
            if not existing["ids"]:
                return False
            
            # Delete from collection
            self.collection.delete(ids=[scheme_id])
            
            logger.info(f"Deleted scheme: {scheme_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete scheme {scheme_id}: {e}")
            raise RuntimeError(f"Failed to delete scheme: {e}")


# Global vector store instance
_vector_store_instance: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:
    """Get the global vector store instance (singleton pattern)."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance

# Convenience functions for backward compatibility
def load_data(data_path: str = DATA_PATH) -> Dict[str, Any]:
    """Load schemes JSON file."""
    store = get_vector_store()
    return store.load_data(data_path)

def populate_vector_db(data_path: str = DATA_PATH, clear_existing: bool = False) -> int:
    """Insert scheme data into Chroma vector DB."""
    store = get_vector_store()
    return store.populate_vector_db(data_path, clear_existing)

def search_schemes(query: str, top_k: int = 3) -> Dict[str, Any]:
    """Search schemes by text query."""
    store = get_vector_store()
    return store.search_schemes(query, top_k)

if __name__ == "__main__":
    try:
        # Initialize vector store
        store = get_vector_store()
        
        # Get collection info
        info = store.get_collection_info()
        print(f"📊 Collection Info: {info}")
        
        # Populate DB (clear existing data first)
        print("\n🔄 Populating vector database...")
        count = populate_vector_db(clear_existing=True)
        print(f"✅ Inserted {count} schemes")
        
        # Example query
        query = "education support for visually impaired in Maharashtra"
        print(f"\n🔍 Searching for: '{query}'")
        
        results = search_schemes(query, top_k=3)
        
        if results and "documents" in results and results["documents"]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else []
            
            print(f"\n✅ Found {len(documents)} results:")
            for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
                print(f"{i}. {doc}")
                if meta:
                    print(f"   State: {meta.get('state', 'Unknown')} | Type: {meta.get('disability_type', 'Unknown')}")
                    print(f"   Apply: {meta.get('apply_link', 'No link')}\n")
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Example usage failed: {e}")

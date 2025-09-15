#!/usr/bin/env python3
"""
Test script for the Disability Schemes Discovery System.

This script tests the core functionality of the system to ensure
everything is working correctly.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from src.rag.chroma_config import get_chroma_config
        from src.rag.retriever import get_retriever
        from src.rag.vector_store import get_vector_store
        from src.models.scheme_models import SearchRequest, SearchResponse
        from src.utils.data_processor import DataProcessor
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_data_processing():
    """Test data processing functionality."""
    print("🧪 Testing data processing...")
    
    try:
        from src.utils.data_processor import DataProcessor
        
        # Test data cleaning
        test_text = "  This   is   a   test   text  with   extra   spaces  "
        cleaned = DataProcessor.clean_text(test_text)
        assert cleaned == "This is a test text with extra spaces"
        
        # Test scheme validation
        test_scheme = {
            "name": "Test Scheme",
            "description": "A test scheme for validation",
            "state": "Test State",
            "disability_type": "visual_impairment",
            "support_type": "financial",
            "apply_link": "https://example.com"
        }
        
        validated = DataProcessor.validate_scheme_data(test_scheme)
        assert validated["name"] == "Test Scheme"
        
        print("✅ Data processing tests passed")
        return True
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False

def test_chroma_config():
    """Test ChromaDB configuration."""
    print("🧪 Testing ChromaDB configuration...")
    
    try:
        from src.rag.chroma_config import get_chroma_config
        
        config = get_chroma_config()
        info = config.get_collection_info()
        
        print(f"✅ ChromaDB config loaded: {info}")
        return True
    except Exception as e:
        print(f"❌ ChromaDB config test failed: {e}")
        return False

def test_retriever():
    """Test the retriever functionality."""
    print("🧪 Testing retriever...")
    
    try:
        from src.rag.retriever import get_retriever
        
        retriever = get_retriever()
        
        # Test with a simple query
        results = retriever.query_schemes("education support", top_k=3)
        
        print(f"✅ Retriever test passed, found {len(results)} results")
        return True
    except Exception as e:
        print(f"❌ Retriever test failed: {e}")
        return False

def test_vector_store():
    """Test the vector store functionality."""
    print("🧪 Testing vector store...")
    
    try:
        from src.rag.vector_store import get_vector_store
        
        store = get_vector_store()
        
        # Test data loading
        data = store.load_data()
        assert "schemes" in data
        assert len(data["schemes"]) > 0
        
        print(f"✅ Vector store test passed, loaded {len(data['schemes'])} schemes")
        return True
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def test_api_models():
    """Test API model validation."""
    print("🧪 Testing API models...")
    
    try:
        from src.models.scheme_models import SearchRequest, SearchResponse, DisabilityType, SupportType
        
        # Test enum values
        assert DisabilityType.VISUAL_IMPAIRMENT == "visual_impairment"
        assert SupportType.FINANCIAL == "financial"
        
        # Test search request validation
        search_req = SearchRequest(
            query="test query",
            top_k=5,
            state="Karnataka",
            disability_type=DisabilityType.VISUAL_IMPAIRMENT,
            support_type=SupportType.EDUCATIONAL
        )
        
        assert search_req.query == "test query"
        assert search_req.top_k == 5
        
        print("✅ API models test passed")
        return True
    except Exception as e:
        print(f"❌ API models test failed: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("🏛️ Disability Schemes Discovery System - Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_data_processing,
        test_chroma_config,
        test_vector_store,
        test_retriever,
        test_api_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

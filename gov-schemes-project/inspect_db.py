import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rag.vector_store import get_vector_store
from src.utils.config import get_settings

def inspect_db():
    print("🔍 Inspecting ChromaDB Content...")
    try:
        store = get_vector_store()
        schemes = store.get_all_schemes()
        
        print(f"✅ Retrieved {len(schemes)} schemes")
        
        if not schemes:
            print("⚠️ Database is empty!")
            return

        print("\n📊 Sample Scheme Data (First 3):")
        for i, scheme in enumerate(schemes[:3]):
            print(f"\n--- Scheme {i+1} ---")
            print(f"Name: {scheme.get('name')}")
            print(f"State: {scheme.get('state')}")
            print(f"Disability: {scheme.get('disability_type')}")
            print(f"Deadline: {scheme.get('deadline')}")
            print(f"Raw Metadata keys: {list(scheme.keys())}")
            
    except Exception as e:
        print(f"❌ Error inspecting DB: {e}")

if __name__ == "__main__":
    inspect_db()

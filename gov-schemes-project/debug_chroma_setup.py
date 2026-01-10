import sys
import os

print("Testing ChromaDB Setup...")

try:
    print("Attempting to import pysqlite3...")
    import pysqlite3
    print(f"pysqlite3 imported: {pysqlite3}")
    print(f"pysqlite3 version: {getattr(pysqlite3, 'version', 'unknown')}")
    print(f"pysqlite3 sqlite_version: {getattr(pysqlite3, 'sqlite_version', 'unknown')}")
except ImportError as e:
    print(f"Failed to import pysqlite3: {e}")

try:
    # Manual patch attempt
    import sqlite3
    print(f"Original sqlite3 version: {sqlite3.sqlite_version}")
    
    if 'pysqlite3' in sys.modules:
        sys.modules['sqlite3'] = sys.modules['pysqlite3']
        print("Patched sqlite3 with pysqlite3")
    
    import chromadb
    print(f"ChromaDB imported: {chromadb.__version__}")
    
    print("Attempting to create Client...")
    client = chromadb.PersistentClient(path="./test_db")
    print("Client created successfully!")
    
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()

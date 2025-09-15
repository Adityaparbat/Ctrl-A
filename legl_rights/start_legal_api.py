#!/usr/bin/env python3
"""
Startup script for the Digital Rights Legal Database API
"""

import os
import sys
import subprocess
import time

def check_neo4j_connection():
    """Check if Neo4j is accessible"""
    try:
        from neo4j import GraphDatabase
        
        # Get connection details from environment or use defaults
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        driver = GraphDatabase.driver(uri, auth=(username, password))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        print("✅ Neo4j connection successful!")
        return True
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        print("\nPlease ensure:")
        print("1. Neo4j is running (default: bolt://localhost:7687)")
        print("2. Username/password are correct (default: neo4j/password)")
        print("3. Set environment variables if using different credentials:")
        print("   export NEO4J_URI='bolt://localhost:7687'")
        print("   export NEO4J_USERNAME='neo4j'")
        print("   export NEO4J_PASSWORD='your_password'")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    print("🚀 Starting Digital Rights Legal Database API")
    print("=" * 60)
    
    # Check dependencies
    if not install_dependencies():
        return
    
    # Check Neo4j connection
    if not check_neo4j_connection():
        print("\n⚠️  You can still start the API, but database operations will fail.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    print("\n🌐 Starting FastAPI server...")
    print("📋 Available endpoints:")
    print("   • GET  /        - API information")
    print("   • GET  /health  - Health check")
    print("   • GET  /setup   - Initialize database")
    print("   • POST /ask     - Ask questions")
    print("\n🔗 API will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the FastAPI server
    try:
        subprocess.run([sys.executable, "legl_rights/legal_data.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")

if __name__ == "__main__":
    main()
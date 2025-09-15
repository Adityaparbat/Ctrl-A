#!/usr/bin/env python3
"""
Startup script for the Disability Schemes Discovery System.

This script provides an easy way to start the application with proper
configuration and error handling.
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_requirements():
    """Check if all required packages are installed."""
    try:
        import fastapi
        import chromadb
        import sentence_transformers
        import uvicorn
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_data_file():
    """Check if the data file exists."""
    data_file = Path("data/disability_schemes.json")
    if data_file.exists():
        print("✅ Data file found")
        return True
    else:
        print("❌ Data file not found: data/disability_schemes.json")
        print("Please ensure the data file exists with the correct format")
        return False

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = ["data", "data/chroma_db", "static", "logs"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Directories created/verified")

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler()
        ]
    )
    print("✅ Logging configured")

def populate_database():
    """Populate the database with sample data."""
    try:
        from src.rag.vector_store import get_vector_store
        
        print("🔄 Populating database with sample data...")
        store = get_vector_store()
        count = store.populate_vector_db(clear_existing=True)
        print(f"✅ Database populated with {count} schemes")
        return True
    except Exception as e:
        print(f"❌ Failed to populate database: {e}")
        return False

def start_server():
    """Start the FastAPI server."""
    try:
        print("🚀 Starting Disability Schemes Discovery System...")
        print("📍 Web Interface: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Import and run the app
        from src.main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main function to start the application."""
    print("🏛️ Disability Schemes Discovery System")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup logging
    setup_logging()
    
    # Check data file
    if not check_data_file():
        print("⚠️  Warning: Data file not found. Some features may not work.")
        response = input("Do you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Populate database
    if check_data_file():
        populate_database()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()

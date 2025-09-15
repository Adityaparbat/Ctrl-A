#!/usr/bin/env python3
"""
Script to start the gov-schemes-project server for the Ctrl-A admin panel.
This script helps start the FastAPI server that provides the schemes API.
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_server_running():
    """Check if the server is already running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the gov-schemes-project server."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Path to the gov-schemes-project
    gov_schemes_path = project_root / "gov-schemes-project"
    
    if not gov_schemes_path.exists():
        print("❌ Error: gov-schemes-project directory not found!")
        print(f"Expected path: {gov_schemes_path}")
        return False
    
    # Change to the gov-schemes-project directory
    os.chdir(gov_schemes_path)
    
    print("🚀 Starting gov-schemes-project server...")
    print(f"📁 Working directory: {gov_schemes_path}")
    
    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "src.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Waiting for server to start...")
        
        # Wait for server to start (max 30 seconds)
        for i in range(30):
            time.sleep(1)
            if check_server_running():
                print("✅ Server started successfully!")
                print("🌐 Server URL: http://localhost:8000")
                print("📚 API Documentation: http://localhost:8000/docs")
                print("🔍 Health Check: http://localhost:8000/health")
                print("\n💡 The server is now running in the background.")
                print("   You can now use the admin panel to manage schemes.")
                print("   Press Ctrl+C to stop this script (server will continue running).")
                
                # Keep the script running to show it's active
                try:
                    while True:
                        time.sleep(1)
                        if not check_server_running():
                            print("❌ Server stopped unexpectedly!")
                            break
                except KeyboardInterrupt:
                    print("\n🛑 Stopping server...")
                    process.terminate()
                    process.wait()
                    print("✅ Server stopped.")
                
                return True
        
        print("❌ Server failed to start within 30 seconds")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🏛️  GOV-SCHEMES-PROJECT SERVER STARTER")
    print("=" * 60)
    
    if check_server_running():
        print("✅ Server is already running at http://localhost:8000")
        print("🔍 Health Check: http://localhost:8000/health")
        return
    
    if start_server():
        print("✅ Server startup completed successfully!")
    else:
        print("❌ Failed to start server. Please check the error messages above.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure you're in the correct directory")
        print("   2. Check if port 8000 is already in use")
        print("   3. Ensure all dependencies are installed")
        print("   4. Check the gov-schemes-project directory structure")

if __name__ == "__main__":
    main()

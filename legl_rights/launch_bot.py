#!/usr/bin/env python3
"""
Digital Rights Bot Launcher
Starts both the API backend and the web interface
"""

import subprocess
import sys
import time
import os
from threading import Thread

def start_api():
    """Start the API backend"""
    print("🚀 Starting API backend...")
    subprocess.run([sys.executable, "simple_legal_api.py"])

def start_web_interface():
    """Start the web interface"""
    print("🌐 Starting web interface...")
    subprocess.run([sys.executable, "web_interface.py"])

def main():
    print("🤖 Digital Rights Bot Launcher")
    print("=" * 50)
    print("This will start:")
    print("• API Backend on: http://localhost:8000")
    print("• Web Interface on: http://localhost:8001")
    print("\nChoose an option:")
    print("1. Start Web Interface only (recommended)")
    print("2. Start API Backend only")
    print("3. Start Both (for development)")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n🌐 Starting Web Interface...")
            print("📱 Open your browser and go to: http://localhost:8001")
            print("⏹️  Press Ctrl+C to stop")
            start_web_interface()
            break
            
        elif choice == "2":
            print("\n🚀 Starting API Backend...")
            print("🔗 API available at: http://localhost:8000")
            print("📖 API docs at: http://localhost:8000/docs")
            print("⏹️  Press Ctrl+C to stop")
            start_api()
            break
            
        elif choice == "3":
            print("\n🚀 Starting both services...")
            print("This is for development - you'll need to stop both manually")
            
            # Start API in background thread
            api_thread = Thread(target=start_api, daemon=True)
            api_thread.start()
            
            # Wait a moment for API to start
            time.sleep(3)
            
            # Start web interface (this will block)
            start_web_interface()
            break
            
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
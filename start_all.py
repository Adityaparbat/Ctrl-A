import subprocess
import sys
import time
import os

def start_all():
    print("🚀 Starting ALL Ctrl-A Components...")
    
    # 1. Start Frontend (Flask)
    print("   [1/3] Launching Frontend (Port 5000)...")
    frontend = subprocess.Popen(["start", "cmd", "/k", "python run_server.py"], shell=True, cwd="Ctrl-A")
    
    # 2. Start Scheme API (FastAPI)
    print("   [2/3] Launching Scheme API (Port 8002)...")
    # Using the existing starter script for better reliability
    scheme_api = subprocess.Popen(["start", "cmd", "/k", "python start_gov_schemes_server.py"], shell=True, cwd="Ctrl-A")
    
    # 3. Start Chatbot (FastAPI)
    print("   [3/3] Launching Chatbot AI (Port 8003)...")
    chatbot = subprocess.Popen(["start", "cmd", "/k", "python start_chatbot.py"], shell=True, cwd=".")
    
    print("\n✅ All servers are starting in separate windows!")
    print("---------------------------------------------------")
    print("📱 Frontend & Dashboard: http://localhost:5000")
    print("🧠 Scheme API (Backend): http://localhost:8002")
    print("🤖 Chatbot API (Backend): http://localhost:8003")
    print("---------------------------------------------------")
    print("Do not close this window or the other server windows.")

if __name__ == "__main__":
    start_all()

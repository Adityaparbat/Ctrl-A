import subprocess
import time
import os
import sys

def start_all():
    print("🚀 Starting ALL Ctrl-A Components...")

    # 1. Start Frontend (PUBLIC)
    print("   [1/3] Launching Frontend (Public)...")
    subprocess.Popen(["python", "run_server.py"], cwd="Ctrl-A")

    # 2. Start Scheme API (Internal)
    print("   [2/3] Launching Scheme API (Internal)...")
    subprocess.Popen(["python", "start_gov_schemes_server.py"], cwd="Ctrl-A")

    # 3. Start Chatbot API (Internal)
    print("   [3/3] Launching Chatbot AI (Internal)...")
    subprocess.Popen(["python", "start_chatbot.py"], cwd=".")

    print("\n✅ All servers launched.")
    print("⚠️ Render will expose ONLY the frontend.")

    # Keep process alive
    while True:
        time.sleep(1000)

if __name__ == "__main__":
    start_all()

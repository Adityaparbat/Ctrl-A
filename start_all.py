import subprocess
import time
import os
import sys

def start_all():
    print("🚀 Starting ALL Ctrl-A Components...")

    # 1. Start Frontend (PUBLIC) - Must bind to Render's PORT
    print("   [1/3] Launching Frontend (Public)...")
    env = os.environ.copy()
    # Pipe output to main process stdout/stderr so it shows in Render logs
    frontend = subprocess.Popen(["python", "run_server.py"], cwd="Ctrl-A", env=env, stdout=sys.stdout, stderr=sys.stderr)

    # 2. Start Scheme API (Internal - Port 8002)
    print("   [2/3] Launching Scheme API (Internal)...")
    scheme_api = subprocess.Popen(["python", "start_gov_schemes_server.py"], cwd="Ctrl-A", stdout=sys.stdout, stderr=sys.stderr)

    # 3. Start Chatbot API (Internal - Port 8003)
    print("   [3/3] Launching Chatbot AI (Internal)...")
    chatbot = subprocess.Popen(["python", "start_chatbot.py"], cwd=".", stdout=sys.stdout, stderr=sys.stderr)

    print("\n✅ All servers launched. Monitoring for crashes...")
    print("⚠️ Render will expose ONLY the frontend.")

    # Monitor processes
    while True:
        if frontend.poll() is not None:
            print(f"❌ Frontend crashed with code {frontend.returncode}!")
            sys.exit(frontend.returncode)
        if scheme_api.poll() is not None:
            print(f"❌ Scheme API crashed with code {scheme_api.returncode}!")
        if chatbot.poll() is not None:
            print(f"❌ Chatbot crashed with code {chatbot.returncode}!")
        
        time.sleep(1)

if __name__ == "__main__":
    start_all()

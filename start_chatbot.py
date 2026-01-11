import subprocess
import sys
import os
import time
from pathlib import Path

def start_chatbot():
    """Start the chatbot server on port 8003."""
    # Get project root
    project_root = Path(__file__).parent
    chatbot_dir = project_root / "explore_schemes" / "disability-scheme-chatbot"

    if not chatbot_dir.exists():
        print(f"❌ Error: Chatbot directory not found at {chatbot_dir}")
        return

    print(f"🚀 Starting Chatbot Server from {chatbot_dir}...")
    os.chdir(chatbot_dir)

    # Run uvicorn on port 8003
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8003", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Chatbot server stopped.")
    except Exception as e:
        print(f"❌ Error starting chatbot: {e}")

if __name__ == "__main__":
    start_chatbot()

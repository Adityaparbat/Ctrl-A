#!/usr/bin/env python3
"""
Script to run the sign language recognition server.

This script starts the Flask server that integrates with the existing prediction.py
for sign language detection.
"""

import os
import sys
import subprocess

def main():
    print("🎯 Starting Sign Language Recognition Server...")
    print("=" * 50)
    
    # Check if model.p exists
    if not os.path.exists('./models/model.p'):
        print("❌ Error: model.p file not found!")
        print("Please ensure the trained model file is in the current directory.")
        print("The model.p file should be generated from training the sign language model.")
        return 1
    
    # Check if required packages are installed
    try:
        import flask
        import flask_socketio
        import cv2
        import mediapipe
        import numpy
        import pickle
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install required packages:")
        print("pip install flask flask-socketio opencv-python mediapipe numpy")
        return 1
    
    # Start the server
    try:
        print("🚀 Starting server on http://localhost:5001")
        print("📱 Sign language detection interface: http://localhost:5001")
        print("🔄 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Import and run the server
        from sign_language_server import app, socketio
        socketio.run(app, debug=True, host='0.0.0.0', port=5001)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Ctrl-A Authentication Server
Run this script to start the authentication server for the Ctrl-A platform.
"""

import os
import sys
from auth_server import app

if __name__ == '__main__':
    print("🚀 Starting Ctrl-A Authentication Server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🏠 Landing page: http://localhost:5000/landing")
    print("🔐 Login page: http://localhost:5000/login")
    print("📝 Signup page: http://localhost:5000/signup")
    print("📊 Dashboard: http://localhost:5000/dashboard")
    print("\n" + "="*50)
    print("Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

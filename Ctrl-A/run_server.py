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
    print("🌐 Server will be publicly available on Render")
    print("\n" + "="*50)

    try:
        port = int(os.environ.get("PORT", 5000))  # Render injects PORT
        app.run(
            debug=False,               # MUST be False on Render
            host='0.0.0.0',            # REQUIRED
            port=port                  # REQUIRED
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

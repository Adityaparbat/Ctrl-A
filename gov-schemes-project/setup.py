#!/usr/bin/env python3
"""
Setup script for the Disability Schemes Discovery System.

This script automates the installation and setup process.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_virtual_environment():
    """Create a virtual environment."""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def activate_virtual_environment():
    """Get the activation command for the virtual environment."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_requirements():
    """Install required packages."""
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    commands = [
        f"{pip_cmd} install --upgrade pip",
        f"{pip_cmd} install -r requirements.txt"
    ]
    
    for command in commands:
        if not run_command(command, f"Running: {command}"):
            return False
    
    return True

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    directories = ["data", "data/chroma_db", "static", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def create_env_file():
    """Create a .env file with default settings."""
    env_content = """# Disability Schemes Discovery System Configuration

# Data paths
DATA_PATH=data/disability_schemes.json
DB_DIR=data/chroma_db

# API settings
API_TITLE=Disability Schemes Discovery System
API_VERSION=1.0.0

# Server settings
HOST=0.0.0.0
PORT=8000
DEBUG=False

# ChromaDB settings
COLLECTION_NAME=disability_schemes
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Search settings
DEFAULT_TOP_K=5
MAX_TOP_K=50
MIN_SIMILARITY_SCORE=0.0

# Logging
LOG_LEVEL=INFO
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Created .env file with default settings")
    else:
        print("✅ .env file already exists")
    
    return True

def test_installation():
    """Test if the installation was successful."""
    print("🧪 Testing installation...")
    
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    return run_command(f"{python_cmd} test_system.py", "Running system tests")

def print_next_steps():
    """Print instructions for next steps."""
    print("\n" + "="*60)
    print("🎉 Installation completed successfully!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Start the application:")
    print("   python run.py")
    print("   OR")
    print("   python src/main.py")
    
    print("\n3. Access the system:")
    print("   🌐 Web Interface: http://localhost:8000")
    print("   📚 API Documentation: http://localhost:8000/docs")
    print("   🔧 Alternative Docs: http://localhost:8000/redoc")
    
    print("\n4. Test the system:")
    print("   python test_system.py")
    
    print("\n📖 For more information, see README.md")
    print("="*60)

def main():
    """Main setup function."""
    print("🏛️ Disability Schemes Discovery System - Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("⚠️  Installation completed but tests failed")
        print("You can still try running the application with: python run.py")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()

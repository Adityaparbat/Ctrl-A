#!/bin/bash

echo "🏛️ Disability Schemes Discovery System - Unix Setup"
echo "====================================================="

echo ""
echo "🐍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "✅ Python found"
echo ""
echo "🚀 Starting setup..."
python3 setup.py

echo ""
echo "Setup completed! Press Enter to exit..."
read

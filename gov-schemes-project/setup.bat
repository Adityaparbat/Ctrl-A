@echo off
echo 🏛️ Disability Schemes Discovery System - Windows Setup
echo =====================================================

echo.
echo 🐍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.
echo 🚀 Starting setup...
python setup.py

echo.
echo Press any key to exit...
pause >nul

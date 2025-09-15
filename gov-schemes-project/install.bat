@echo off
echo Setting up Government Schemes Project...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Create necessary directories
if not exist "data\chroma_db" (
    echo Creating data directory...
    mkdir data\chroma_db
)

if not exist "static" (
    echo Creating static directory...
    mkdir static
)

echo.
echo Installation complete!
echo.
echo To run the application:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run the server: python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
echo 3. Open browser: http://127.0.0.1:8000
echo.
pause

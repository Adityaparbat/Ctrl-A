@echo off
echo Starting Government Schemes Server...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set Python path
set PYTHONPATH=%CD%

REM Run the server
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

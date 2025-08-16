@echo off
echo Starting Database Manager (Simple Version)...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install simple dependencies
echo Installing simple dependencies...
pip install -r requirements-simple.txt

REM Start the simple application
echo Starting the simple application...
python start-simple.py

pause 
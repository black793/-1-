@echo off
echo Starting YouTube Subscribers Boost - Python Version...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher
    pause
    exit /b 1
)

echo Python found! Starting application...
echo.

REM Install requirements if needed
echo Installing required packages...
pip install requests selenium webdriver-manager

REM Run the application
python youtube_boost.py

pause

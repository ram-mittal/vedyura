@echo off
echo 🌿 Starting Vedyura Ayurvedic Healthcare Platform...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Run setup check
echo 🔧 Running setup check...
python setup.py

echo.
echo 🚀 Starting the application...
echo 📱 Open your browser and go to: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python app.py %*

pause
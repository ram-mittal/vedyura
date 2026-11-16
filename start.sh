#!/bin/bash

echo "🌿 Starting Vedyura Ayurvedic Healthcare Platform..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

# Run setup check
echo "🔧 Running setup check..."
python3 setup.py

echo
echo "🚀 Starting the application..."
echo "📱 Open your browser and go to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo

# Start the Flask application
if [ "$1" == "--dev" ]; then
    python3 app.py --dev
elif command -v gunicorn &> /dev/null; then
    echo "Starting with Gunicorn (production)..."
    gunicorn --config gunicorn.conf.py wsgi:app
else
    python3 app.py "$@"
fi
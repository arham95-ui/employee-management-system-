#!/bin/bash
# Employee Tracker - Run Script
# Usage: chmod +x run.sh && ./run.sh

echo "=========================================="
echo "  EMPLOYEE TRACKER"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    echo "Please install Python 3.6+"
    exit 1
fi

# Check Tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Tkinter not found!"
    echo "Installing Tkinter..."
    brew install python-tk
fi

# Run the app
echo "🚀 Starting Employee Tracker..."
python3 employee_tracker.py
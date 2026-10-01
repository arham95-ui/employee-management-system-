#!/bin/bash
# Simple build script for Employee Tracker

echo "=========================================="
echo "  EMPLOYEE TRACKER - BUILD"
echo "=========================================="
echo ""

# Activate virtual environment if exists
if [ -d ".venv" ]; then
    echo "✓ Activating virtual environment..."
    source .venv/bin/activate
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

# Install PyInstaller if needed
echo "✓ Checking PyInstaller..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "  Installing PyInstaller..."
    python3 -m pip install pyinstaller
fi

# Clean
echo "✓ Cleaning old builds..."
rm -rf dist build *.spec

# Build
echo "✓ Building executable..."
echo "  This takes 2-3 minutes..."

python3 -m PyInstaller \
    --onefile \
    --name=EmployeeTracker \
    --clean \
    --noconfirm \
    --hidden-import=sqlite3 \
    --hidden-import=tkinter \
    --hidden-import=threading \
    --hidden-import=queue \
    --hidden-import=csv \
    --hidden-import=datetime \
    employee_tracker.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ BUILD SUCCESSFUL!"
    echo "=========================================="
    echo ""
    echo "Run: ./dist/EmployeeTracker"
    echo ""
else
    echo ""
    echo "❌ BUILD FAILED!"
    echo "Run directly: python3 employee_tracker.py"
    exit 1
fi
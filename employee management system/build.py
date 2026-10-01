#!/usr/bin/env python3
"""
Final Build Script - No setup.py required
Copy and paste this file
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("="*60)
    print("  EMPLOYEE TRACKER - BUILD SYSTEM")
    print("="*60)
    print()
    
    # Step 1: Install PyInstaller
    print("📦 Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller', '--quiet'])
        print("✅ PyInstaller installed")
    except:
        print("❌ Failed to install PyInstaller")
        print("   Run: pip3 install pyinstaller")
        return
    
    # Step 2: Clean old builds
    print("\n🧹 Cleaning old builds...")
    for folder in ['dist', 'build']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Removed: {folder}")
    for file in Path('.').glob('*.spec'):
        file.unlink()
        print(f"   Removed: {file}")
    
    # Step 3: Build executable
    print("\n🔨 Building executable (this takes 2-3 minutes)...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name=EmployeeTracker',
        '--clean',
        '--noconfirm',
        '--hidden-import=sqlite3',
        '--hidden-import=tkinter',
        '--hidden-import=threading',
        '--hidden-import=queue',
        '--hidden-import=csv',
        '--hidden-import=datetime',
        'employee_tracker.py'
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Build successful!")
    except:
        print("❌ Build failed!")
        print("   Try running directly: python3 employee_tracker.py")
        return
    
    # Step 4: Show result
    print("\n" + "="*60)
    print("✅ BUILD COMPLETE!")
    print("="*60)
    
    exe_path = Path('dist/EmployeeTracker')
    if exe_path.exists():
        size = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n📁 Executable: {exe_path}")
        print(f"📊 Size: {size:.2f} MB")
        print("\n▶️  To run:")
        print("   ./dist/EmployeeTracker")
    else:
        print("\n⚠️  Executable not found, but you can still run:")
        print("   python3 employee_tracker.py")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Employee Tracker - Build Installer
Simple and fast build script
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(text):
    print(f"\n▶ {text}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print_success(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print_info("PyInstaller not found. Installing...")
        try:
            # Install with progress
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "pyinstaller", "--progress-bar", "on"
            ])
            print_success("PyInstaller installed successfully!")
            return True
        except Exception as e:
            print_error(f"Failed to install PyInstaller: {e}")
            print_info("Please install manually: pip install pyinstaller")
            return False

def clean_build():
    """Clean previous builds"""
    print_step("Cleaning previous builds...")
    
    dirs = ['dist', 'build']
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  Removed: {d}")
    
    files = Path('.').glob('*.spec')
    for f in files:
        f.unlink()
        print(f"  Removed: {f}")
    
    print_success("Cleanup complete")

def build_executable():
    """Build the executable"""
    print_step("Building executable...")
    print_info("This will take 2-3 minutes...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=EmployeeTracker",
        "--clean",
        "--noconfirm",
        "--log-level=ERROR",
        "--hidden-import=sqlite3",
        "--hidden-import=tkinter",
        "--hidden-import=threading",
        "--hidden-import=queue",
        "--hidden-import=csv",
        "--hidden-import=datetime",
        "employee_tracker.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print_success("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Build failed with error: {e}")
        return False
    except KeyboardInterrupt:
        print_error("Build cancelled by user")
        return False

def create_package():
    """Create installer package"""
    print_step("Creating installer package...")
    
    # Create installer_package directory
    package_dir = Path('installer_package')
    package_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_source = Path('dist/EmployeeTracker')
    exe_dest = package_dir / 'EmployeeTracker'
    
    if exe_source.exists():
        shutil.copy2(exe_source, exe_dest)
        size_mb = exe_source.stat().st_size / (1024 * 1024)
        print_success(f"Copied executable ({size_mb:.1f} MB)")
    else:
        print_error("Executable not found!")
        return False
    
    # Create README
    readme_path = package_dir / 'README.txt'
    with open(readme_path, 'w') as f:
        f.write("""
═══════════════════════════════════════
  EMPLOYEE TRACKER SYSTEM
═══════════════════════════════════════

INSTALLATION:
-------------
1. Run EmployeeTracker (executable)
2. No installation required
3. Database created automatically

FEATURES:
---------
✓ Employee Management
✓ Attendance Tracking
✓ Search & Filter
✓ Export to CSV
✓ Multi-threading

SYSTEM REQUIREMENTS:
-------------------
✓ macOS 10.13 or later
✓ No additional dependencies

SUPPORT:
--------
For issues: support@example.com

═══════════════════════════════════════
""")
    print_success("Created README.txt")
    
    return True

def build_installer():
    """Main build function"""
    print("="*60)
    print("  EMPLOYEE TRACKER - BUILDER")
    print("="*60)
    
    # Check PyInstaller
    if not check_pyinstaller():
        print_error("Cannot proceed without PyInstaller")
        return False
    
    # Clean
    clean_build()
    
    # Build
    if not build_executable():
        print_error("Build failed!")
        return False
    
    # Create package
    if not create_package():
        print_error("Failed to create package!")
        return False
    
    # Success
    print("\n" + "="*60)
    print_success("BUILD COMPLETE!")
    print("="*60)
    print(f"\n📁 Package created: installer_package/")
    print(f"📄 Run: ./installer_package/EmployeeTracker")
    print(f"\nOr run directly: python3 employee_tracker.py")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = build_installer()
    sys.exit(0 if success else 1)
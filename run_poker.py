#!/usr/bin/env python3
"""
Poker Training System Launcher
==============================

This script launches the Poker Training System GUI from the root directory.
It automatically handles the correct working directory and Python path setup.

Usage:
    python3 run_poker.py

Requirements:
    - Run from the Poker project root directory
    - Virtual environment should be activated
    - All dependencies installed via requirements.txt
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Poker Training System GUI."""
    
    # Get the project root directory (where this script is located)
    project_root = Path(__file__).parent.absolute()
    backend_dir = project_root / "backend"
    
    # Verify backend directory exists
    if not backend_dir.exists():
        print("❌ Error: backend directory not found!")
        print(f"   Expected: {backend_dir}")
        print("   Make sure you're running this script from the Poker project root.")
        sys.exit(1)
    
    # Verify main_gui.py exists
    main_gui_path = backend_dir / "main_gui.py"
    if not main_gui_path.exists():
        print("❌ Error: main_gui.py not found!")
        print(f"   Expected: {main_gui_path}")
        sys.exit(1)
    
    # Print startup info
    print("🚀 Launching Poker Training System...")
    print(f"📁 Project Root: {project_root}")
    print(f"📁 Backend Dir:  {backend_dir}")
    print(f"🐍 Python:      {sys.executable}")
    print("-" * 60)
    
    try:
        # Change to backend directory and run the GUI
        os.chdir(backend_dir)
        
        # Execute main_gui.py in the backend directory
        result = subprocess.run([
            sys.executable, "main_gui.py"
        ], cwd=backend_dir)
        
        # Return the exit code from the GUI application
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
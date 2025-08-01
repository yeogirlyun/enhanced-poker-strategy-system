#!/usr/bin/env python3
"""
Poker Strategy Development System Launcher
Run this script from the project root to start the application.
"""

import os
import sys

def main():
    """Launch the poker application."""
    # Change to the backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # Add the backend directory to Python path
    sys.path.insert(0, backend_dir)
    
    # Import and run the main GUI
    try:
        from main_gui import main as run_app
        print("🚀 Starting Poker Strategy Development System...")
        run_app()
    except ImportError as e:
        print(f"❌ Error importing main_gui: {e}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
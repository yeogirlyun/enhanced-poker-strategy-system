#!/usr/bin/env python3
"""
PokerPro Trainer Launcher

Launches the poker application with proper app name for macOS.
"""

import sys
import os
import platform

def main():
    """Launch PokerPro Trainer with proper app name."""
    
    # Set the app name for macOS
    if platform.system() == "Darwin":
        # Set process name
        try:
            import setproctitle
            setproctitle.setproctitle("PokerPro Trainer")
            print("✅ Set process name to 'PokerPro Trainer'")
        except ImportError:
            # Fallback: modify argv
            if len(sys.argv) > 0:
                sys.argv[0] = "PokerPro Trainer"
            print("⚠️  Using fallback method for app name")
    
    # Set environment variable
    os.environ['POKERPRO_APP_NAME'] = 'PokerPro Trainer'
    
    # Import and run the main GUI
    try:
        from main_gui import main as run_gui
        print("🚀 Launching PokerPro Trainer...")
        run_gui()
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
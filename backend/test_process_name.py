#!/usr/bin/env python3
"""
Test Process Name Change

Tests if the process name can be changed for macOS.
"""

import platform
import sys
import os

def main():
    """Test process name change."""
    print("🎯 TESTING PROCESS NAME CHANGE")
    print("=" * 40)
    
    print(f"Platform: {platform.system()}")
    print(f"Original argv[0]: {sys.argv[0]}")
    
    if platform.system() == "Darwin":
        print("✅ macOS detected")
        
        # Try setproctitle
        try:
            import setproctitle
            setproctitle.setproctitle("PokerPro Trainer")
            print("✅ Successfully set process name to 'PokerPro Trainer'")
        except ImportError:
            print("❌ setproctitle not available")
        except Exception as e:
            print(f"❌ Error setting process name: {e}")
        
        # Try argv method
        try:
            if len(sys.argv) > 0:
                sys.argv[0] = "PokerPro Trainer"
            print("✅ Modified argv[0] to 'PokerPro Trainer'")
        except Exception as e:
            print(f"❌ Error modifying argv: {e}")
        
        # Set environment variable
        os.environ['POKERPRO_APP_NAME'] = 'PokerPro Trainer'
        print("✅ Set environment variable POKERPRO_APP_NAME")
        
        print(f"Current argv[0]: {sys.argv[0]}")
        print(f"Environment variable: {os.environ.get('POKERPRO_APP_NAME', 'Not set')}")
        
    else:
        print("ℹ️  Not macOS - process name change not needed")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Run: python3 launch_pokerpro.py")
    print("2. Check if the menu bar shows 'PokerPro Trainer'")
    print("3. If not, try restarting the terminal/IDE")

if __name__ == "__main__":
    main() 
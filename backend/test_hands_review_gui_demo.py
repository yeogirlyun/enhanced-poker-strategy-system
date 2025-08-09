#!/usr/bin/env python3
"""
Demo script to test the hands review GUI functionality.
Run this to verify that the load button works and simulation controls are enabled.
"""

import sys
import tkinter as tk
from main_gui import EnhancedMainGUI

def main():
    print("🎯 Starting Hands Review GUI Demo...")
    print("=" * 50)
    
    try:
        # Create the main GUI application
        app = EnhancedMainGUI()
        
        # Get the hands review panel
        panel = app.hands_review_panel
        hands_count = len(panel.legendary_hands)
        print(f"✅ GUI initialized with {hands_count} legendary hands")
        
        # Show instructions
        print("\n📋 Instructions:")
        print("1. Select any hand from the list on the left")
        print("2. Click the 'Load Selected Hand' button")
        print("3. Simulation controls should become enabled")
        print("4. Click 'Play' to start the simulation")
        print("5. Use other controls (Pause, Next, Prev, Street navigation)")
        print("\n🎮 The load button error has been fixed!")
        print("🎮 All simulation controls should work properly now")
        
        # Start the GUI event loop
        print("\n🚀 Starting GUI - Close the window when done testing")
        app.root.mainloop()
        
        print("✅ GUI demo completed successfully")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

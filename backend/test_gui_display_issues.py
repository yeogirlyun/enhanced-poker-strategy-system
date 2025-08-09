#!/usr/bin/env python3
"""
Test script to verify GUI display issues including:
- Canvas sizing
- Bet graphics visibility
- Card display after preflop
- Animation functionality

Run this and test the actual GUI behavior.
"""

import sys
import tkinter as tk
from main_gui import EnhancedMainGUI

def main():
    print("🎯 GUI Display Issues Test")
    print("=" * 50)
    
    try:
        # Create the GUI
        app = EnhancedMainGUI()
        
        print("📋 Instructions for testing:")
        print("1. Go to 'Hands Review (130 Legendary)' tab")
        print("2. Select a heads-up hand (e.g., 'GEN-003 - Dwan Eastgate Triple Barrel')")
        print("3. Click 'Load Selected Hand'")
        print("4. Check:")
        print("   - Does the table show 2 seats (not 6)?")
        print("   - Are player cards visible?")
        print("   - Do you see bet amounts in front of players?")
        print("5. Click 'Next' to execute actions and check:")
        print("   - Do bet amounts update and animate?")
        print("   - Do you hear sounds?")
        print("   - Are cards still visible after preflop?")
        print("6. Try the 'Play' button for auto-advance")
        
        print("\n🚀 Starting GUI...")
        app.root.mainloop()
        
        print("✅ GUI test completed")
        return 0
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

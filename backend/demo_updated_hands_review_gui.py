#!/usr/bin/env python3
"""
Demo Script: Updated Hands Review GUI

This script demonstrates the updated hands review tab in the main GUI
that now uses our validated 130-hand JSON database.
"""

import tkinter as tk
from main_gui import EnhancedMainGUI

def demo_hands_review_gui():
    """Demo the updated hands review GUI."""
    print("🎯 LAUNCHING UPDATED HANDS REVIEW GUI DEMO")
    print("=" * 50)
    print()
    print("✨ FEATURES DEMONSTRATED:")
    print("  🎯 130 Legendary Hands from validated JSON database")
    print("  🔧 FPSM-based simulation engine")
    print("  🎮 Interactive poker game widget")
    print("  ✅ All previously failing hands now working")
    print("  🏆 Complete heads-up collection included")
    print()
    print("📋 INSTRUCTIONS:")
    print("  1. Click on 'Hands Review (130 Legendary)' tab")
    print("  2. Select any hand from the list")
    print("  3. Click 'Load Hand' to begin simulation")
    print("  4. Watch the FPSM + RPGW in action!")
    print()
    print("🚀 Starting GUI...")
    
    try:
        # Create main GUI
        app = EnhancedMainGUI()
        
        # Get hands count for verification
        hands_count = len(app.hands_review_panel.legendary_hands)
        print(f"✅ Successfully loaded {hands_count} legendary hands")
        
        # Find and select the hands review tab
        for i in range(app.notebook.index('end')):
            tab_text = app.notebook.tab(i, 'text')
            if 'Hands Review' in tab_text:
                app.notebook.select(i)
                print(f"📋 Auto-selected hands review tab: '{tab_text}'")
                break
        
        print("🎮 GUI is ready! Explore the hands review functionality.")
        print("🔍 Try loading different hands to test the system.")
        
        # Start the GUI
        app.root.mainloop()
        
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    demo_hands_review_gui()

if __name__ == "__main__":
    main()

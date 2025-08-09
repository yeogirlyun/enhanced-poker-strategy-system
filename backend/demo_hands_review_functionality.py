#!/usr/bin/env python3
"""
Demo: Hands Review Functionality

This script demonstrates how to use the hands review tab:
1. Select a hand from the list
2. Click "Load Hand" to begin simulation
3. Watch the FPSM + RPGW in action
"""

import tkinter as tk
from main_gui import EnhancedMainGUI

def demo_hands_review():
    """Demo the hands review functionality."""
    print("🎯 HANDS REVIEW FUNCTIONALITY DEMO")
    print("=" * 40)
    print()
    print("📋 INSTRUCTIONS:")
    print("  1. The GUI will open to the 'Hands Review (130 Legendary)' tab")
    print("  2. You'll see a list of 130 legendary poker hands")
    print("  3. Click on any hand to see its details")
    print("  4. Click '▶️ Load Hand' to start the simulation")
    print("  5. The FPSM will create the poker game widget")
    print("  6. You can then interact with the poker simulation")
    print()
    print("🎮 FEATURES:")
    print("  ✅ 130 legendary hands from poker history")
    print("  ✅ Hand details with lessons and context")
    print("  ✅ Interactive FPSM + RPGW simulation")
    print("  ✅ Real-time poker game visualization")
    print("  ✅ Reset functionality to try different hands")
    print()
    print("🚀 Starting GUI...")
    
    try:
        # Create main GUI
        app = EnhancedMainGUI()
        
        # Auto-select hands review tab
        for i in range(app.notebook.index('end')):
            tab_text = app.notebook.tab(i, 'text')
            if 'Hands Review' in tab_text:
                app.notebook.select(i)
                print(f"📋 Auto-selected: '{tab_text}'")
                break
        
        hands_count = len(app.hands_review_panel.legendary_hands)
        print(f"✅ Loaded {hands_count} legendary hands")
        print()
        print("🎯 GUI ready! Try the following:")
        print("  • Click on any hand in the left list")
        print("  • Read the hand details below the list")
        print("  • Click '▶️ Load Hand' to start simulation")
        print("  • Use '🔄 Reset' to try another hand")
        
        # Start the GUI
        app.root.mainloop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_hands_review()

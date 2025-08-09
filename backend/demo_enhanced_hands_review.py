#!/usr/bin/env python3
"""
Demo: Enhanced Hands Review Panel

This script demonstrates the full-featured hands review interface with
complete simulation controls, step-by-step progression, and interactive features.
"""

import tkinter as tk
from main_gui import EnhancedMainGUI

def demo_enhanced_hands_review():
    """Demo the enhanced hands review functionality."""
    print("🎯 ENHANCED HANDS REVIEW DEMO")
    print("=" * 40)
    print()
    print("🎮 NEW FEATURES AVAILABLE:")
    print("  ✅ Play/Pause simulation controls")
    print("  ✅ Step-by-step action progression (Next/Previous)")
    print("  ✅ Street navigation (Preflop, Flop, Turn, River)")
    print("  ✅ Auto-play mode with timing controls")
    print("  ✅ Progress tracking and action counter")
    print("  ✅ Current action display")
    print("  ✅ Hand details with game information")
    print("  ✅ Enhanced 3-panel layout")
    print()
    print("📋 HOW TO USE:")
    print("  1. LEFT PANEL: Select any hand from 130 legendary hands")
    print("  2. CENTER PANEL: Use simulation controls")
    print("     • 'Load Selected Hand' - Initialize the hand")
    print("     • 'Play/Pause' - Control automatic playback")
    print("     • 'Next/Prev' - Step through actions manually")
    print("     • Street buttons - Jump to specific streets")
    print("     • Auto-play checkbox - Enable automatic progression")
    print("  3. RIGHT PANEL: Watch the poker game simulation")
    print()
    print("🎲 EXAMPLE WORKFLOW:")
    print("  • Select 'GEN-001: Moneymaker Farha Legendary Bluff'")
    print("  • Click 'Load Selected Hand'")
    print("  • Use 'Next' to step through each action")
    print("  • Or click 'Play' with Auto-play enabled")
    print("  • Jump to 'River' to see the famous bluff")
    print("  • Reset and try another hand!")
    print()
    print("🚀 Starting Enhanced GUI...")
    
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
        print("🎯 ENHANCED GUI READY!")
        print("  📚 Left: Hand selection and details")
        print("  🎮 Center: Full simulation controls")
        print("  🎰 Right: Interactive poker game")
        print()
        print("💡 TIP: Try the step-by-step controls to learn poker strategy!")
        
        # Start the GUI
        app.root.mainloop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_enhanced_hands_review()

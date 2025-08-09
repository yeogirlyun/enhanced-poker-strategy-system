#!/usr/bin/env python3
"""
Test Next Button Fix
====================

This script tests if the Next button properly stops at the end of the hand
instead of restarting from the beginning.
"""

import sys
import os
import tkinter as tk

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.components.enhanced_fpsm_hands_review_panel import EnhancedFPSMHandsReviewPanel

def test_next_button_fix():
    """Test that Next button stops at end instead of restarting."""
    print("🧪 Testing Next Button Fix")
    print("=" * 30)
    
    root = tk.Tk()
    root.title("Next Button Fix Test")
    root.geometry("1400x900")
    
    panel = EnhancedFPSMHandsReviewPanel(root)
    panel.pack(fill=tk.BOTH, expand=True)
    
    # Override next_action to add debug
    original_next_action = panel.next_action
    button_presses = 0
    
    def debug_next_action():
        nonlocal button_presses
        button_presses += 1
        print(f"\n🔘 NEXT BUTTON PRESS #{button_presses}")
        print(f"   Before: action_index = {panel.current_action_index}")
        
        if hasattr(panel, 'hand_actions'):
            total_actions = sum(len(actions) for actions in panel.hand_actions.values())
            print(f"   Total actions available: {total_actions}")
        
        result = original_next_action()
        
        print(f"   After: action_index = {panel.current_action_index}")
        print(f"   Status: {panel.status_label.cget('text')}")
        
        return result
    
    panel.next_action = debug_next_action
    
    print("\n📋 Instructions:")
    print("1. Select any hand (e.g., GEN-005)")
    print("2. Click 'Load Selected Hand'")
    print("3. Keep clicking 'Next' until end")
    print("4. Verify it stops and doesn't restart")
    print("5. Console will show debug info")
    
    root.mainloop()

if __name__ == "__main__":
    test_next_button_fix()

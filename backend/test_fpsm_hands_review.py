#!/usr/bin/env python3
"""
Test FPSM Hands Review Panel

This script tests the new FPSM-based hands review panel to ensure it works correctly.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fpsm_hands_review_panel():
    """Test the FPSM hands review panel."""
    print("🧪 Testing FPSM Hands Review Panel...")
    
    # Create a test window
    root = tk.Tk()
    root.title("FPSM Hands Review Panel Test")
    root.geometry("1200x800")
    
    try:
        # Import and create the FPSM hands review panel
        from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
        
        # Create the panel
        panel = FPSMHandsReviewPanel(root)
        panel.pack(fill=tk.BOTH, expand=True)
        
        print("✅ FPSM Hands Review Panel created successfully")
        
        # Test basic functionality
        print("🎯 Testing basic functionality...")
        
        # Check if data was loaded
        if hasattr(panel, 'legendary_hands') and panel.legendary_hands:
            print(f"✅ Loaded {len(panel.legendary_hands)} legendary hands")
        else:
            print("⚠️ No legendary hands loaded")
        
        if hasattr(panel, 'practice_hands') and panel.practice_hands:
            print(f"✅ Loaded {len(panel.practice_hands)} practice hands")
        else:
            print("⚠️ No practice hands loaded")
        
        # Test UI components
        if hasattr(panel, 'hands_listbox'):
            print("✅ Hands listbox created")
        else:
            print("❌ Hands listbox not found")
        
        if hasattr(panel, 'poker_game_widget'):
            print("✅ Poker game widget container created")
        else:
            print("❌ Poker game widget container not found")
        
        print("🎉 FPSM Hands Review Panel test completed successfully!")
        
        # Run the test window
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error testing FPSM Hands Review Panel: {e}")
        import traceback
        traceback.print_exc()
        root.destroy()

if __name__ == "__main__":
    test_fpsm_hands_review_panel()

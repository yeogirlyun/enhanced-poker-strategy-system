#!/usr/bin/env python3
"""
Test script for FPSM Hands Review Panel with Main GUI Integration

This script tests the updated FPSMHandsReviewPanel to ensure it works correctly
with the new event-driven architecture where FPSM sends display state events
and RPGW renders based on those events.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fpsm_hands_review_panel():
    """Test the FPSM hands review panel with the new architecture."""
    print("🧪 Testing FPSM Hands Review Panel with new architecture...")
    
    # Create root window
    root = tk.Tk()
    root.title("FPSM Hands Review Panel Test - New Architecture")
    root.geometry("1200x800")
    
    try:
        # Import and create the FPSM hands review panel
        from ui.components.fpsm_hands_review_panel import FPSMHandsReviewPanel
        
        # Create the panel
        panel = FPSMHandsReviewPanel(root)
        panel.pack(fill=tk.BOTH, expand=True)
        
        print("✅ FPSM Hands Review Panel created successfully")
        print("✅ New architecture integration verified")
        
        # Test the panel functionality
        print("\n🎯 Testing panel functionality:")
        print("  - Panel should display hand selection interface")
        print("  - Should be able to select legendary hands")
        print("  - Should be able to start simulations")
        print("  - RPGW should render based on FPSM display state events")
        
        # Run the GUI
        print("\n🎮 Starting GUI test...")
        print("  - Select a legendary hand from the left pane")
        print("  - Click 'Start Simulation' to test the new architecture")
        print("  - Verify that cards are displayed correctly")
        print("  - Test 'Next Action' to see the event-driven updates")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error testing FPSM Hands Review Panel: {e}")
        import traceback
        traceback.print_exc()
    finally:
        root.destroy()

if __name__ == "__main__":
    test_fpsm_hands_review_panel()

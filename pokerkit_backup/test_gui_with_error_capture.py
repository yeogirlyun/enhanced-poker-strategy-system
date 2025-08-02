#!/usr/bin/env python3
"""
Test script to run the actual GUI and capture console errors.
"""

import sys
import os
import traceback
import tkinter as tk
from practice_session_ui import PracticeSessionUI
from gui_models import StrategyData

def test_gui_with_error_capture():
    """Test the GUI and capture any console errors."""
    try:
        print("=== GUI Error Capture Test ===")
        
        # Create root window
        root = tk.Tk()
        root.title("Error Capture Test")
        
        # Load strategy data
        strategy_data = StrategyData()
        if os.path.exists("modern_strategy.json"):
            strategy_data.load_strategy_from_file("modern_strategy.json")
        
        # Create practice session UI
        ps = PracticeSessionUI(root, strategy_data)
        ps.pack(fill=tk.BOTH, expand=True)
        
        # Update GUI
        root.update()
        
        print("GUI created successfully. Testing start_new_hand...")
        
        # Test start_new_hand with error capture
        try:
            ps.start_new_hand()
            print("✓ start_new_hand completed without errors")
        except Exception as e:
            print(f"❌ Error in start_new_hand: {e}")
            traceback.print_exc()
        
        # Test update_display with error capture
        try:
            ps.update_display()
            print("✓ update_display completed without errors")
        except Exception as e:
            print(f"❌ Error in update_display: {e}")
            traceback.print_exc()
        
        # Update GUI again
        root.update()
        
        print("✓ All tests completed")
        
        # Keep window open for manual testing
        print("GUI is ready for manual testing. Close the window when done.")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_gui_with_error_capture() 
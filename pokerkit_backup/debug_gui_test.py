#!/usr/bin/env python3
"""
Debug script to test GUI integration and catch errors.
"""

import tkinter as tk
from practice_session_ui import PracticeSessionUI
import traceback

def test_gui():
    """Test the GUI with error handling."""
    try:
        print("Creating root window...")
        root = tk.Tk()
        
        print("Creating PracticeSessionUI...")
        ps = PracticeSessionUI(root, None)
        print("✓ PracticeSessionUI created successfully")
        
        print("Starting new hand...")
        ps.start_new_hand()
        print("✓ New hand started successfully")
        
        print("Getting game info...")
        game_info = ps.state_machine.get_game_info()
        print(f"✓ Game info: {len(game_info['players'])} players, pot: ${game_info['pot']:.2f}")
        
        print("Updating display...")
        ps.update_display()
        print("✓ Display updated successfully")
        
        print("Destroying window...")
        root.destroy()
        print("✓ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_gui() 
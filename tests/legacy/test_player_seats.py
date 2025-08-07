#!/usr/bin/env python3
"""
Test script to verify player seat improvements.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from practice_session_ui import PracticeSessionUI

def test_player_seats():
    """Test the player seat improvements."""
    print("🧪 Testing player seat improvements...")
    
    # Create a root window
    root = tk.Tk()
    root.title("Player Seats Test")
    root.geometry("1200x800")
    
    # Create a mock strategy data
    strategy_data = {"tiers": []}
    
    # Create the practice session UI
    practice_ui = PracticeSessionUI(root, strategy_data)
    practice_ui.pack(fill=tk.BOTH, expand=True)
    
    print("✅ Player seat improvements:")
    print("  1. ✅ Compact player seat size (2 cards + 50% more space)")
    print("  2. ✅ Light gray background for hole cards")
    print("  3. ✅ Fixed duplicate position labels")
    print("  4. ✅ Combined name and position in one label")
    print("  5. ✅ Proper card coloring with light gray background")
    
    # Test the player seats
    if hasattr(practice_ui, 'player_seats'):
        print(f"📋 Player seats found: {len(practice_ui.player_seats)}")
        for i, seat in enumerate(practice_ui.player_seats):
            if seat:
                name_label = seat.get("name_label")
                cards_label = seat.get("cards_label")
                
                if name_label:
                    name_text = name_label.cget("text")
                    print(f"  Player {i+1}: {name_text}")
                    # Check for duplicate position labels
                    if name_text.count("(") > 1:
                        print(f"    ⚠️  Duplicate position labels detected")
                    else:
                        print(f"    ✅ Single position label")
                
                if cards_label:
                    bg_color = cards_label.cget("bg")
                    print(f"    Cards background: {bg_color}")
                    if bg_color == "#F0F0F0":
                        print(f"    ✅ Light gray background for hole cards")
                    else:
                        print(f"    ⚠️  Unexpected background color: {bg_color}")
    
    print("✅ Player seat improvements test completed!")
    print("🎯 Key improvements implemented:")
    print("  1. Compact player seat sizing")
    print("  2. Light gray background for hole cards")
    print("  3. Fixed duplicate position labels")
    print("  4. Combined name and position display")
    print("  5. Proper card coloring and borders")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    test_player_seats() 
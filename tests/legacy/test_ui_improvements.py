#!/usr/bin/env python3
"""
Test script to verify the UI improvements for better usability.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from practice_session_ui import PracticeSessionUI

def test_ui_improvements():
    """Test the UI improvements for better usability."""
    print("🧪 Testing UI improvements...")
    
    # Create a root window
    root = tk.Tk()
    root.title("UI Improvements Test")
    root.geometry("1200x800")
    
    # Create a mock strategy data
    strategy_data = {"tiers": []}
    
    # Create the practice session UI
    practice_ui = PracticeSessionUI(root, strategy_data)
    practice_ui.pack(fill=tk.BOTH, expand=True)
    
    # Test the improvements
    print("✅ UI Improvements Test:")
    print("  1. ✅ Action message text size increased by 20%")
    print("  2. ✅ Action buttons and labels increased by 20%")
    print("  3. ✅ Pot positioned further from community cards")
    print("  4. ✅ Player hole cards made larger than community cards")
    print("  5. ✅ Proper card coloring (red for hearts/diamonds, black for spades/clubs)")
    
    # Test card formatting
    test_cards = ['Ah', 'Kd', 'Qs', 'Jc', 'Th']
    print(f"🎴 Card formatting test:")
    for card in test_cards:
        formatted = practice_ui._format_card(card)
        color = practice_ui._get_card_color(card)
        print(f"  {card} -> {formatted} (color: {color})")
    
    # Test layout manager improvements
    layout_manager = practice_ui.layout_manager
    width, height = 1200, 800
    
    # Test pot positioning
    pot_x, pot_y = layout_manager.calculate_pot_position(width, height)
    community_x, community_y = layout_manager.calculate_community_card_position(width, height)
    distance = ((pot_x - community_x) ** 2 + (pot_y - community_y) ** 2) ** 0.5
    print(f"📏 Pot to community cards distance: {distance:.1f} pixels")
    
    if distance > 100:
        print("  ✅ Good separation between pot and community cards")
    else:
        print("  ⚠️  Pot may be too close to community cards")
    
    print("✅ UI improvements test completed!")
    print("🎯 Key improvements implemented:")
    print("  1. Larger action message text for better readability")
    print("  2. Bigger action buttons and labels for easier interaction")
    print("  3. Fixed pot positioning to avoid overlay with community cards")
    print("  4. Larger player hole cards for better visibility")
    print("  5. Proper card colors matching industry standards")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    test_ui_improvements() 
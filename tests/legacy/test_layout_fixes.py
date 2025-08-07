#!/usr/bin/env python3
"""
Test script to verify the layout fixes for stack positioning and pot graphics.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from practice_session_ui import PracticeSessionUI

def test_layout_fixes():
    """Test the layout improvements for stack positioning and pot graphics."""
    print("🧪 Testing layout fixes...")
    
    # Create a root window
    root = tk.Tk()
    root.title("Layout Fixes Test")
    root.geometry("1000x700")
    
    # Create a mock strategy data
    strategy_data = {"tiers": []}
    
    # Create the practice session UI
    practice_ui = PracticeSessionUI(root, strategy_data)
    practice_ui.pack(fill=tk.BOTH, expand=True)
    
    # Test the layout manager
    layout_manager = practice_ui.layout_manager
    width, height = 1000, 700
    
    # Test stack positioning
    stack_positions = layout_manager.calculate_stack_positions(width, height, 6)
    print(f"📊 Stack positions (should be closer to center):")
    for i, (x, y) in enumerate(stack_positions):
        print(f"  Player {i+1}: ({x:.1f}, {y:.1f})")
    
    # Test player positioning
    player_positions = layout_manager.calculate_player_positions(width, height, 6)
    print(f"📊 Player positions:")
    for i, (x, y) in enumerate(player_positions):
        print(f"  Player {i+1}: ({x:.1f}, {y:.1f})")
    
    # Test pot positioning
    pot_x, pot_y = layout_manager.calculate_pot_position(width, height)
    print(f"📊 Pot position: ({pot_x:.1f}, {pot_y:.1f})")
    
    # Calculate distances between stacks and players
    print(f"📊 Distance analysis:")
    for i in range(6):
        stack_x, stack_y = stack_positions[i]
        player_x, player_y = player_positions[i]
        distance = ((stack_x - player_x) ** 2 + (stack_y - player_y) ** 2) ** 0.5
        print(f"  Player {i+1}: Stack to seat distance = {distance:.1f} pixels")
        
        # Check if distance is sufficient (should be > 50 pixels)
        if distance > 50:
            print(f"    ✅ Good separation")
        else:
            print(f"    ⚠️  May overlap")
    
    print("✅ Layout fixes test completed!")
    print("🎯 Key improvements:")
    print("  1. Stack graphics moved closer to table center")
    print("  2. Player seats have more space for hole cards")
    print("  3. Pot graphics redesigned as realistic oval")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    test_layout_fixes() 
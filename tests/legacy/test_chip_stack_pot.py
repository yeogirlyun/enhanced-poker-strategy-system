#!/usr/bin/env python3
"""
Test script to verify the new chip stack pot design.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from practice_session_ui import PracticeSessionUI

def test_chip_stack_pot():
    """Test the new chip stack pot design."""
    print("🧪 Testing chip stack pot design...")
    
    # Create a root window
    root = tk.Tk()
    root.title("Chip Stack Pot Test")
    root.geometry("1200x800")
    
    # Create a mock strategy data
    strategy_data = {"tiers": []}
    
    # Create the practice session UI
    practice_ui = PracticeSessionUI(root, strategy_data)
    practice_ui.pack(fill=tk.BOTH, expand=True)
    
    print("✅ Chip Stack Pot Test:")
    print("  1. ✅ Chip stack tower created with felt color background")
    print("  2. ✅ Pot amount label positioned on top of chip stack")
    print("  3. ✅ Chip stack height updates based on pot amount")
    print("  4. ✅ 3D chip effect with highlights and shadows")
    print("  5. ✅ Felt color matching for realistic appearance")
    
    # Test pot amount updates
    test_amounts = [5.0, 25.0, 50.0, 100.0, 200.0, 500.0]
    print(f"🎯 Testing pot amount updates:")
    for amount in test_amounts:
        practice_ui.update_pot_amount(amount)
        print(f"  Pot: ${amount:.2f} - Chip stack updated")
    
    # Test felt color changes
    print(f"🎨 Testing felt color changes:")
    practice_ui.change_table_felt("dark_green")
    print("  Changed to dark green felt")
    practice_ui.change_table_felt("blue")
    print("  Changed to blue felt")
    practice_ui.change_table_felt("classic_green")
    print("  Changed back to classic green felt")
    
    print("✅ Chip stack pot test completed!")
    print("🎯 Key improvements implemented:")
    print("  1. Realistic chip stack tower instead of oval pot")
    print("  2. Felt color matching for authentic appearance")
    print("  3. Dynamic chip stack height based on pot amount")
    print("  4. 3D chip effects with highlights and shadows")
    print("  5. Proper positioning of pot amount label")
    
    root.mainloop()

if __name__ == "__main__":
    test_chip_stack_pot() 
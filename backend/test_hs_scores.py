#!/usr/bin/env python3
"""
Test to verify HS scores are displayed in the hand grid
"""
import tkinter as tk
from gui_models import StrategyData
from hand_grid import HandGridWidget

def test_hs_scores():
    """Test that HS scores are displayed in the grid."""
    print("Testing HS score display in hand grid...")
    
    # Create root window
    root = tk.Tk()
    root.title("HS Score Test")
    root.geometry("800x600")
    
    # Create strategy data with some HS values
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()
    
    # Add some HS data to the strategy
    strategy_data.strategy_dict = {
        "hand_strength_tables": {
            "preflop": {
                "AA": 50, "KK": 48, "QQ": 46, "JJ": 44,
                "AKs": 42, "AKo": 40, "AQs": 38, "AJo": 36,
                "TT": 34, "99": 32, "KQs": 30, "AJs": 28,
                "88": 26, "77": 24, "AQo": 22, "KJo": 20,
                "66": 18, "55": 16, "44": 14, "A7s": 12,
                "33": 10, "22": 8, "A4s": 6, "A3s": 4
            }
        }
    }
    
    # Create hand grid
    def on_hand_click(hand, is_selected):
        print(f"Hand clicked: {hand}, selected: {is_selected}")
    
    hand_grid = HandGridWidget(root, strategy_data, on_hand_click)
    
    print("HS Score Test Setup Complete")
    print("- HS scores should be visible on larger font sizes")
    print("- Smaller font sizes show only hand names")
    print("- Test by changing font size with +/- buttons")
    
    root.mainloop()

if __name__ == "__main__":
    test_hs_scores() 
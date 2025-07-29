#!/usr/bin/env python3
"""
Test to verify Hybrid HS Score Approach
- Grid: HS scores in corner for larger fonts
- Tier Panel: Detailed HS breakdown with ranges
"""
import tkinter as tk
from gui_models import StrategyData
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def test_hybrid_hs_approach():
    """Test the hybrid HS score approach."""
    print("Testing Hybrid HS Score Approach...")
    print("Features to test:")
    print("1. Grid: HS scores visible on larger font sizes")
    print("2. Tier Panel: Detailed HS breakdown with ranges")
    print("3. Both components working together")
    
    # Create root window
    root = tk.Tk()
    root.title("Hybrid HS Score Test")
    root.geometry("1200x800")
    
    # Create strategy data with comprehensive HS values
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()
    
    # Add comprehensive HS data to the strategy
    strategy_data.strategy_dict = {
        "hand_strength_tables": {
            "preflop": {
                # Elite tier (HS 40-50)
                "AA": 50, "KK": 48, "QQ": 46, "JJ": 44,
                "AKs": 42, "AKo": 40, "AQs": 38,
                
                # Premium tier (HS 30-39)
                "TT": 39, "99": 37, "AJo": 35, "KQs": 33,
                "AJs": 31, "KJs": 29, "QJs": 27, "JTs": 25,
                "ATs": 23, "KQo": 21,
                
                # Gold tier (HS 20-29)
                "88": 29, "77": 27, "AQo": 25, "KJo": 23,
                "A9s": 21, "A8s": 19, "KTs": 17, "QTs": 15,
                "J9s": 13,
                
                # Silver tier (HS 10-19)
                "66": 19, "55": 17, "44": 15, "A7s": 13,
                "A6s": 11, "A5s": 9, "K9s": 7, "Q9s": 5,
                "J8s": 3, "T9s": 1,
                
                # Bronze tier (HS 1-9)
                "33": 9, "22": 7, "A4s": 5, "A3s": 3,
                "A2s": 1, "K8s": 8, "Q8s": 6, "J7s": 4,
                "T8s": 2, "98s": 0
            }
        }
    }
    
    # Create main container
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Left side: Hand Grid
    grid_frame = tk.LabelFrame(main_frame, text="Hand Grid with HS Scores", 
                              font=("Arial", 12, "bold"))
    grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    
    def on_hand_click(hand, is_selected):
        print(f"Hand clicked: {hand}, selected: {is_selected}")
    
    hand_grid = HandGridWidget(grid_frame, strategy_data, on_hand_click)
    
    # Right side: Tier Panel
    tier_frame = tk.LabelFrame(main_frame, text="Tier Details with HS Breakdown", 
                              font=("Arial", 12, "bold"))
    tier_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
    
    def on_tier_change():
        print("Tier data changed")
    
    def on_tier_select(selected_tiers):
        print(f"Tier selection changed: {len(selected_tiers)} tiers selected")
        for tier in selected_tiers:
            print(f"  - {tier.name}: {len(tier.hands)} hands")
    
    tier_panel = TierPanel(tier_frame, strategy_data, on_tier_change, on_tier_select)
    
    # Instructions
    instructions = tk.Label(root, text="Hybrid HS Score Test Instructions:\n"
                                      "1. Increase font size to see HS scores in grid\n"
                                      "2. Select tiers to see detailed HS breakdown\n"
                                      "3. Check both grid and tier panel for HS info",
                          font=("Arial", 10), fg="blue")
    instructions.pack(side=tk.BOTTOM, pady=5)
    
    print("Hybrid HS Score Test Setup Complete")
    print("- Grid shows HS scores on larger fonts")
    print("- Tier panel shows detailed HS breakdown")
    print("- Test by changing font size and selecting tiers")
    
    root.mainloop()

if __name__ == "__main__":
    test_hybrid_hs_approach() 
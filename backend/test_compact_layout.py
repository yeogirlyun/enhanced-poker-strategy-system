#!/usr/bin/env python3
"""
Test to verify the compact layout works well
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def test_compact_layout():
    """Test the compact layout with aligned tier panel and grid."""
    root = tk.Tk()
    root.title("Test Compact Layout")
    root.geometry("1400x900")  # Larger window to test layout
    root.configure(bg=THEME["bg"])
    
    # Setup styles
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background=THEME["bg"], foreground=THEME["fg"], 
                   font=(THEME["font_family"], THEME["font_size"]))
    style.configure('Dark.TFrame', background=THEME["bg_dark"])
    style.configure('Dark.TLabel', background=THEME["bg_dark"], foreground=THEME["fg"])
    style.configure('Dark.TLabelframe', background=THEME["bg_dark"], bordercolor=THEME["bg_light"])
    style.configure('Dark.TLabelframe.Label', background=THEME["bg_dark"], foreground=THEME["fg"])
    style.configure('Dark.TButton', background=THEME["bg_light"], foreground=THEME["fg"], borderwidth=1)
    style.map('Dark.TButton', background=[('active', THEME["accent"])])
    
    # Create strategy data
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()
    
    # Create main frame
    main_frame = ttk.Frame(root, style='Dark.TFrame')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Create hand grid (left side, takes most space)
    grid_frame = ttk.Frame(main_frame, style='Dark.TFrame')
    grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    
    hand_grid = HandGridWidget(grid_frame, strategy_data)
    
    # Create tier panel (right side, compact)
    tier_frame = ttk.Frame(main_frame, style='Dark.TFrame')
    tier_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
    
    def on_tier_change():
        print("Tier data changed")
    
    def on_tier_select(selected_tiers):
        print(f"\n{'='*50}")
        print(f"TIER SELECTION: {len(selected_tiers)} tiers")
        for tier in selected_tiers:
            print(f"  {tier.name}: {tier.hands}")
        print(f"{'='*50}")
        hand_grid.highlight_tiers(selected_tiers)
    
    tier_panel = TierPanel(tier_frame, strategy_data, on_tier_change, on_tier_select)
    
    # Add test buttons
    test_frame = ttk.LabelFrame(main_frame, text="Layout Test", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def test_layout():
        """Test the compact layout functionality."""
        print("\n" + "="*60)
        print("TESTING COMPACT LAYOUT")
        print("="*60)
        
        # Test tier selection
        print("1. Testing tier selection in compact layout")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0)  # Elite tier
        tier_panel._on_listbox_select(None)
        
        # Test font size changes
        print("2. Testing font size changes in compact layout")
        hand_grid.increase_grid_size()
        hand_grid.increase_grid_size()
        
        # Test multiple tier selection
        print("3. Testing multiple tier selection in compact layout")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0, 2)  # Elite and Gold
        tier_panel._on_listbox_select(None)
        
        print("4. Compact layout test complete")
    
    def test_strategy_loading():
        """Test strategy loading in compact layout."""
        print("\n" + "="*60)
        print("TESTING STRATEGY LOADING IN COMPACT LAYOUT")
        print("="*60)
        
        # Load baseline strategy
        if strategy_data.load_strategy_from_file("baseline_strategy.json"):
            hand_grid._render_grid()
            tier_panel._update_tier_list()
            tier_panel._update_counts()
            print("Successfully loaded baseline strategy in compact layout")
        else:
            print("Failed to load baseline strategy")
    
    ttk.Button(test_frame, text="Test Layout", command=test_layout, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test Strategy Loading", command=test_strategy_loading, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(main_frame, 
                           text="Compact Layout Test Instructions:\n1. Verify tier panel is aligned with grid on the right side\n2. Check that the layout uses window space efficiently\n3. Test tier selection and highlighting work correctly\n4. Verify font size controls work in compact layout\n5. Test strategy file loading in the new layout",
                           style='Dark.TLabel', justify=tk.LEFT)
    instructions.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_compact_layout() 
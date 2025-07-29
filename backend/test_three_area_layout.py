#!/usr/bin/env python3
"""
Test to verify the new three-area layout works well
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def test_three_area_layout():
    """Test the new three-area layout."""
    root = tk.Tk()
    root.title("Test Three-Area Layout")
    root.geometry("1600x1000")  # Larger window to test layout
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
    
    # Create main container
    main_container = ttk.Frame(root, style='Dark.TFrame')
    main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # TOP AREA: Menu and controls
    top_frame = ttk.LabelFrame(main_container, text="Application Controls", style='Dark.TLabelframe')
    top_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Top row: Strategy and file controls
    strategy_row = ttk.Frame(top_frame, style='Dark.TFrame')
    strategy_row.pack(fill=tk.X, padx=5, pady=2)
    
    # Strategy file info
    ttk.Label(strategy_row, text="Strategy:", style='Dark.TLabel').pack(side=tk.LEFT)
    strategy_label = ttk.Label(strategy_row, text="Default Strategy", style='Dark.TLabel')
    strategy_label.pack(side=tk.LEFT, padx=5)
    
    # File operation buttons
    ttk.Button(strategy_row, text="New", width=8, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
    ttk.Button(strategy_row, text="Open", width=8, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
    ttk.Button(strategy_row, text="Save", width=8, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
    
    # Top row: Grid controls
    grid_controls_row = ttk.Frame(top_frame, style='Dark.TFrame')
    grid_controls_row.pack(fill=tk.X, padx=5, pady=2)
    
    # Font size controls
    ttk.Label(grid_controls_row, text="Grid Size:", style='Dark.TLabel').pack(side=tk.LEFT)
    ttk.Button(grid_controls_row, text="-", width=4, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
    
    font_size_label = ttk.Label(grid_controls_row, text="Large", style='Dark.TLabel')
    font_size_label.pack(side=tk.LEFT, padx=5)
    
    ttk.Button(grid_controls_row, text="+", width=4, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
    
    # Grid control buttons
    ttk.Button(grid_controls_row, text="Clear Highlights", width=12, style='Dark.TButton').pack(side=tk.LEFT, padx=10)
    ttk.Button(grid_controls_row, text="Force Clear", width=10, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
    

    
    # MAIN CONTENT AREA: Grid and Tiers
    content_frame = ttk.Frame(main_container, style='Dark.TFrame')
    content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # LEFT AREA: Hand grid (takes most space)
    grid_frame = ttk.Frame(content_frame, style='Dark.TFrame')
    grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    
    hand_grid = HandGridWidget(grid_frame, strategy_data)
    
    # RIGHT AREA: Tiers/HS/Decision table panel (compact)
    right_panel_frame = ttk.Frame(content_frame, style='Dark.TFrame')
    right_panel_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
    
    def on_tier_change():
        print("Tier data changed")
    
    def on_tier_select(selected_tiers):
        print(f"\n{'='*50}")
        print(f"TIER SELECTION: {len(selected_tiers)} tiers")
        for tier in selected_tiers:
            print(f"  {tier.name}: {tier.hands}")
        print(f"{'='*50}")
        hand_grid.highlight_tiers(selected_tiers)
    
    tier_panel = TierPanel(right_panel_frame, strategy_data, on_tier_change, on_tier_select)
    
    # Add test buttons
    test_frame = ttk.LabelFrame(main_container, text="Three-Area Layout Test", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def test_layout():
        """Test the three-area layout functionality."""
        print("\n" + "="*60)
        print("TESTING THREE-AREA LAYOUT")
        print("="*60)
        
        # Test tier selection
        print("1. Testing tier selection in three-area layout")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0)  # Elite tier
        tier_panel._on_listbox_select(None)
        
        # Test font size changes
        print("2. Testing font size changes in three-area layout")
        hand_grid.increase_grid_size()
        hand_grid.increase_grid_size()
        
        # Test multiple tier selection
        print("3. Testing multiple tier selection in three-area layout")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0, 2)  # Elite and Gold
        tier_panel._on_listbox_select(None)
        
        print("4. Three-area layout test complete")
    
    def test_strategy_loading():
        """Test strategy loading in three-area layout."""
        print("\n" + "="*60)
        print("TESTING STRATEGY LOADING IN THREE-AREA LAYOUT")
        print("="*60)
        
        # Load baseline strategy
        if strategy_data.load_strategy_from_file("baseline_strategy.json"):
            hand_grid._render_grid()
            tier_panel._update_tier_list()
            tier_panel._update_counts()
            strategy_label.configure(text="baseline_strategy.json")
            print("Successfully loaded baseline strategy in three-area layout")
        else:
            print("Failed to load baseline strategy")
    
    ttk.Button(test_frame, text="Test Layout", command=test_layout, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test Strategy Loading", command=test_strategy_loading, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(main_container, 
                           text="Three-Area Layout Test Instructions:\n1. Verify top menu area contains all controls\n2. Check that grid panel is on the left and takes most space\n3. Verify tiers/strategy panel is on the right with more space\n4. Test tier selection and highlighting work correctly\n5. Verify font size controls work in the top menu area\n6. Test strategy file loading in the new layout",
                           style='Dark.TLabel', justify=tk.LEFT)
    instructions.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_three_area_layout() 
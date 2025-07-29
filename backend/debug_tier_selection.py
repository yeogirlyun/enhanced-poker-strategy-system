#!/usr/bin/env python3
"""
Debug script for tier selection clearing
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def debug_tier_selection():
    """Debug the tier selection clearing functionality."""
    root = tk.Tk()
    root.title("Tier Selection Debug")
    root.geometry("1200x700")
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
    
    # Create strategy data with default tiers
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()
    
    # Create main frame
    main_frame = ttk.Frame(root, style='Dark.TFrame')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Create hand grid
    hand_grid = HandGridWidget(main_frame, strategy_data)
    
    # Create tier panel
    def on_tier_change():
        print("Tier data changed")
        hand_grid.update_hand_colors()
    
    def on_tier_select(selected_tiers):
        print(f"Selected tiers: {[t.name for t in selected_tiers]}")
        print(f"Number of tiers: {len(selected_tiers)}")
        for tier in selected_tiers:
            print(f"  {tier.name}: {tier.hands}")
        hand_grid.highlight_tiers(selected_tiers)
    
    tier_panel = TierPanel(main_frame, strategy_data, on_tier_change, on_tier_select)
    
    # Add debug controls
    debug_frame = ttk.LabelFrame(main_frame, text="Debug Controls", style='Dark.TLabelframe')
    debug_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def clear_all():
        print("Clearing all highlights")
        hand_grid.clear_all_highlights()
    
    def test_single_tier():
        print("Testing single tier selection")
        # Simulate selecting the first tier
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0)
        tier_panel._on_listbox_select(None)
    
    def test_multi_tier():
        print("Testing multi tier selection")
        # Simulate selecting first two tiers
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0, 1)
        tier_panel._on_listbox_select(None)
    
    def test_no_selection():
        print("Testing no selection")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel._on_listbox_select(None)
    
    ttk.Button(debug_frame, text="Clear All", command=clear_all, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(debug_frame, text="Test Single Tier", command=test_single_tier, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(debug_frame, text="Test Multi Tier", command=test_multi_tier, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(debug_frame, text="Test No Selection", command=test_no_selection, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    # Add instructions
    instructions = ttk.Label(main_frame, 
                           text="Debug Instructions:\n1. Use debug buttons to test tier selection\n2. Check console for debug output\n3. Observe grid highlighting behavior",
                           style='Dark.TLabel', justify=tk.LEFT)
    instructions.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    debug_tier_selection() 
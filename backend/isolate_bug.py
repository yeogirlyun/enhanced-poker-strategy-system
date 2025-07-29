#!/usr/bin/env python3
"""
Minimal test to isolate the tier selection bug
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def isolate_bug():
    """Minimal test to isolate the tier selection bug."""
    root = tk.Tk()
    root.title("Isolate Tier Selection Bug")
    root.geometry("800x600")
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
    
    # Create hand grid
    hand_grid = HandGridWidget(main_frame, strategy_data)
    
    # Create tier panel
    def on_tier_change():
        print("Tier data changed")
    
    def on_tier_select(selected_tiers):
        print(f"\n{'='*60}")
        print(f"TIER SELECTION CALLBACK")
        print(f"Number of tiers: {len(selected_tiers)}")
        for tier in selected_tiers:
            print(f"  {tier.name}: {tier.hands}")
        print(f"Calling hand_grid.highlight_tiers...")
        hand_grid.highlight_tiers(selected_tiers)
        print(f"{'='*60}\n")
    
    tier_panel = TierPanel(main_frame, strategy_data, on_tier_change, on_tier_select)
    
    # Add test buttons
    test_frame = ttk.LabelFrame(main_frame, text="Test Buttons", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def test_silver_only():
        """Test selecting only Silver tier."""
        print("\n" + "="*60)
        print("TESTING SILVER TIER ONLY")
        print("="*60)
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(3)  # Silver tier
        tier_panel._on_listbox_select(None)
    
    def test_elite_only():
        """Test selecting only Elite tier."""
        print("\n" + "="*60)
        print("TESTING ELITE TIER ONLY")
        print("="*60)
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0)  # Elite tier
        tier_panel._on_listbox_select(None)
    
    def test_clear_all():
        """Test clearing all selections."""
        print("\n" + "="*60)
        print("TESTING CLEAR ALL")
        print("="*60)
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel._on_listbox_select(None)
    
    def force_clear():
        """Force clear all highlights."""
        print("\n" + "="*60)
        print("FORCE CLEAR ALL HIGHLIGHTS")
        print("="*60)
        hand_grid.force_clear_highlights()
    
    ttk.Button(test_frame, text="Test Silver Only", command=test_silver_only, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test Elite Only", command=test_elite_only, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Clear All", command=test_clear_all, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Force Clear", command=force_clear, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(main_frame, 
                           text="Bug Isolation Test:\n1. Click 'Test Silver Only' - should see ONLY Silver hands highlighted\n2. Click 'Test Elite Only' - should see ONLY Elite hands highlighted\n3. Click 'Clear All' - should see no highlights\n4. Watch console output for debug info",
                           style='Dark.TLabel', justify=tk.LEFT)
    instructions.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    isolate_bug() 
#!/usr/bin/env python3
"""
Test to verify the new GTO Wizard-style color scheme and tier selection clearing
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def test_new_colors():
    """Test the new GTO Wizard-style color scheme and tier selection clearing."""
    root = tk.Tk()
    root.title("Test New GTO Wizard Colors")
    root.geometry("1000x700")
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
        print(f"\n{'='*50}")
        print(f"TIER SELECTION: {len(selected_tiers)} tiers")
        for tier in selected_tiers:
            print(f"  {tier.name}: {tier.hands}")
        print(f"{'='*50}")
        hand_grid.highlight_tiers(selected_tiers)
    
    tier_panel = TierPanel(main_frame, strategy_data, on_tier_change, on_tier_select)
    
    # Add test buttons
    test_frame = ttk.LabelFrame(main_frame, text="Color Test", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def test_sequence():
        """Test the complete sequence with new colors."""
        print("\n" + "="*60)
        print("NEW COLOR TEST SEQUENCE")
        print("="*60)
        
        # Step 1: Select Bronze tier
        print("\nStep 1: Selecting Bronze tier")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(4)  # Bronze tier
        tier_panel._on_listbox_select(None)
        
        # Step 2: Select Elite tier (should clear Bronze)
        print("\nStep 2: Selecting Elite tier (should clear Bronze)")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0)  # Elite tier
        tier_panel._on_listbox_select(None)
        
        # Step 3: Select Silver tier (should clear Elite)
        print("\nStep 3: Selecting Silver tier (should clear Elite)")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(3)  # Silver tier
        tier_panel._on_listbox_select(None)
        
        # Step 4: Clear all
        print("\nStep 4: Clearing all selections")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel._on_listbox_select(None)
        
        print("\n" + "="*60)
        print("NEW COLOR TEST COMPLETE")
        print("="*60)
    
    def test_multiple_tiers():
        """Test multiple tier selection with new colors."""
        print("\n" + "="*60)
        print("TESTING MULTIPLE TIER SELECTION")
        print("="*60)
        
        # Select multiple tiers
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0, 2)  # Elite and Gold
        tier_panel._on_listbox_select(None)
    
    ttk.Button(test_frame, text="Test Color Sequence", command=test_sequence, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test Multiple Tiers", command=test_multiple_tiers, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(main_frame, 
                           text="New Color Test Instructions:\n1. Click 'Test Color Sequence' to test tier selection with new colors\n2. Watch console output for debug info\n3. Observe that only selected tiers are highlighted with new GTO Wizard colors\n4. Previous selections should be completely cleared when selecting new tiers",
                           style='Dark.TLabel', justify=tk.LEFT)
    instructions.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_new_colors() 
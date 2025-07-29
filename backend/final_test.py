#!/usr/bin/env python3
"""
Final test to verify tier selection clearing fix
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def final_test():
    """Final test to verify the tier selection clearing fix."""
    root = tk.Tk()
    root.title("Final Tier Selection Test")
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
        print(f"\n{'='*50}")
        print(f"TIER SELECTION CALLBACK")
        print(f"Selected tiers: {[t.name for t in selected_tiers]}")
        print(f"Number of tiers: {len(selected_tiers)}")
        for tier in selected_tiers:
            print(f"  {tier.name}: {tier.hands}")
        print(f"Calling hand_grid.highlight_tiers...")
        hand_grid.highlight_tiers(selected_tiers)
        print(f"{'='*50}\n")
    
    tier_panel = TierPanel(main_frame, strategy_data, on_tier_change, on_tier_select)
    
    # Add test buttons
    test_frame = ttk.LabelFrame(main_frame, text="Test Sequence", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def test_sequence():
        """Test the complete sequence to verify the fix."""
        print("\n" + "="*60)
        print("STARTING TEST SEQUENCE")
        print("="*60)
        
        # Step 1: Clear all
        print("\nStep 1: Clearing all selections")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel._on_listbox_select(None)
        
        # Step 2: Select Elite only
        print("\nStep 2: Selecting Elite tier only")
        tier_panel.tier_listbox.selection_set(0)  # Elite tier
        tier_panel._on_listbox_select(None)
        
        # Step 3: Select Silver only (should clear Elite)
        print("\nStep 3: Selecting Silver tier only (should clear Elite)")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(3)  # Silver tier
        tier_panel._on_listbox_select(None)
        
        # Step 4: Select multiple tiers
        print("\nStep 4: Selecting multiple tiers")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0, 2)  # Elite and Gold
        tier_panel._on_listbox_select(None)
        
        # Step 5: Clear all
        print("\nStep 5: Clearing all selections")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel._on_listbox_select(None)
        
        print("\n" + "="*60)
        print("TEST SEQUENCE COMPLETED")
        print("="*60)
    
    def force_clear():
        """Force clear all highlights."""
        print("\nForce clearing all highlights")
        hand_grid.force_clear_highlights()
    
    ttk.Button(test_frame, text="Run Test Sequence", command=test_sequence, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Force Clear", command=force_clear, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(main_frame, 
                           text="Test Instructions:\n1. Click 'Run Test Sequence' to test the fix\n2. Watch console output for debug info\n3. Observe that only selected tiers are highlighted\n4. Previous selections should be cleared when selecting new tiers",
                           style='Dark.TLabel', justify=tk.LEFT)
    instructions.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    final_test() 
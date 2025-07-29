#!/usr/bin/env python3
"""
Test to verify the new count features work correctly
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def test_count_features():
    """Test the count features."""
    root = tk.Tk()
    root.title("Test Count Features")
    root.geometry("1200x800")
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
    test_frame = ttk.LabelFrame(main_frame, text="Count Features Test", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def test_single_tier():
        """Test single tier selection."""
        print("\n" + "="*60)
        print("TESTING SINGLE TIER SELECTION")
        print("="*60)
        
        # Select Bronze tier
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(4)  # Bronze tier
        tier_panel._on_listbox_select(None)
        
        # Check counts
        total_hands = tier_panel.get_total_hands_count()
        selected_hands = tier_panel.get_selected_hands_count()
        print(f"Total hands: {total_hands}")
        print(f"Selected hands: {selected_hands}")
    
    def test_multiple_tiers():
        """Test multiple tier selection."""
        print("\n" + "="*60)
        print("TESTING MULTIPLE TIER SELECTION")
        print("="*60)
        
        # Select Elite and Gold tiers
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0, 2)  # Elite and Gold
        tier_panel._on_listbox_select(None)
        
        # Check counts
        total_hands = tier_panel.get_total_hands_count()
        selected_hands = tier_panel.get_selected_hands_count()
        print(f"Total hands: {total_hands}")
        print(f"Selected hands: {selected_hands}")
    
    def test_clear_selection():
        """Test clearing selection."""
        print("\n" + "="*60)
        print("TESTING CLEAR SELECTION")
        print("="*60)
        
        # Clear selection
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel._on_listbox_select(None)
        
        # Check counts
        total_hands = tier_panel.get_total_hands_count()
        selected_hands = tier_panel.get_selected_hands_count()
        print(f"Total hands: {total_hands}")
        print(f"Selected hands: {selected_hands}")
    
    def show_statistics():
        """Show current statistics."""
        print("\n" + "="*60)
        print("CURRENT STATISTICS")
        print("="*60)
        
        total_hands = tier_panel.get_total_hands_count()
        selected_hands = tier_panel.get_selected_hands_count()
        selected_tiers = tier_panel.get_selected_tiers()
        
        print(f"Total playable hands: {total_hands}")
        print(f"Currently selected: {selected_hands}")
        print(f"Selected tiers: {len(selected_tiers)}")
        for tier in selected_tiers:
            print(f"  - {tier.name}: {len(tier.hands)} hands")
    
    ttk.Button(test_frame, text="Test Single Tier", command=test_single_tier, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test Multiple Tiers", command=test_multiple_tiers, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test Clear Selection", command=test_clear_selection, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Show Statistics", command=show_statistics, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(main_frame, 
                           text="Count Features Test Instructions:\n1. Click test buttons to verify count functionality\n2. Watch console output for debug info\n3. Check that 'Total Playable Hands' shows correct count\n4. Check that 'Selected Cards' updates when tiers are selected\n5. Verify tier details show correct information",
                           style='Dark.TLabel', justify=tk.LEFT)
    instructions.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_count_features() 
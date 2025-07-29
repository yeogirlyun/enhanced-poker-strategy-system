#!/usr/bin/env python3
"""
Test to verify that non-selected tier cards are still visible
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def test_visibility_fix():
    """Test that non-selected tier cards are still visible."""
    root = tk.Tk()
    root.title("Test Visibility Fix")
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
    test_frame = ttk.LabelFrame(main_frame, text="Visibility Test", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def test_single_tier():
        """Test single tier selection - other cards should still be visible."""
        print("\n" + "="*60)
        print("TESTING SINGLE TIER SELECTION")
        print("="*60)
        print("Expected: Selected tier cards highlighted, others show general colors")
        
        # Select Bronze tier
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(4)  # Bronze tier
        tier_panel._on_listbox_select(None)
    
    def test_multiple_tiers():
        """Test multiple tier selection - other cards should still be visible."""
        print("\n" + "="*60)
        print("TESTING MULTIPLE TIER SELECTION")
        print("="*60)
        print("Expected: Selected tier cards highlighted, others show general colors")
        
        # Select Elite and Gold tiers
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0, 2)  # Elite and Gold
        tier_panel._on_listbox_select(None)
    
    def test_clear_selection():
        """Test clearing selection - all cards should show general colors."""
        print("\n" + "="*60)
        print("TESTING CLEAR SELECTION")
        print("="*60)
        print("Expected: All cards show general tier colors")
        
        # Clear selection
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel._on_listbox_select(None)
    
    def test_font_size():
        """Test font size controls."""
        print("\n" + "="*60)
        print("TESTING FONT SIZE CONTROLS")
        print("="*60)
        
        # Increase font size
        hand_grid.increase_grid_size()
        print("Font size increased")
        
        # Decrease font size
        hand_grid.decrease_grid_size()
        print("Font size decreased")
    
    ttk.Button(test_frame, text="Test Single Tier", command=test_single_tier, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test Multiple Tiers", command=test_multiple_tiers, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test Clear Selection", command=test_clear_selection, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test Font Size", command=test_font_size, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(main_frame, 
                           text="Visibility Test Instructions:\n1. Click 'Test Single Tier' - should see selected tier highlighted, others still visible\n2. Click 'Test Multiple Tiers' - should see selected tiers highlighted, others still visible\n3. Click 'Test Clear Selection' - should see all cards with general colors\n4. Check that non-selected cards are not grayed out but show their tier colors",
                           style='Dark.TLabel', justify=tk.LEFT)
    instructions.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_visibility_fix() 
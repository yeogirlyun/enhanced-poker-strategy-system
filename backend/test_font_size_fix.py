#!/usr/bin/env python3
"""
Test to verify that font size changes don't interfere with tier selection
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def test_font_size_fix():
    """Test that font size changes don't interfere with tier selection."""
    root = tk.Tk()
    root.title("Test Font Size Fix")
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
    test_frame = ttk.LabelFrame(main_frame, text="Font Size Test", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def test_sequence():
        """Test the complete sequence with font size changes."""
        print("\n" + "="*60)
        print("FONT SIZE TEST SEQUENCE")
        print("="*60)
        
        # Step 1: Select Silver tier
        print("\nStep 1: Selecting Silver tier")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(3)  # Silver tier
        tier_panel._on_listbox_select(None)
        
        # Step 2: Increase font size (should preserve Silver highlighting)
        print("\nStep 2: Increasing font size (should preserve Silver highlighting)")
        hand_grid.increase_grid_size()
        
        # Step 3: Increase font size again
        print("\nStep 3: Increasing font size again")
        hand_grid.increase_grid_size()
        
        # Step 4: Select Elite tier (should clear Silver and show only Elite)
        print("\nStep 4: Selecting Elite tier (should clear Silver and show only Elite)")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(0)  # Elite tier
        tier_panel._on_listbox_select(None)
        
        # Step 5: Decrease font size (should preserve Elite highlighting)
        print("\nStep 5: Decreasing font size (should preserve Elite highlighting)")
        hand_grid.decrease_grid_size()
        
        # Step 6: Clear all
        print("\nStep 6: Clearing all selections")
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel._on_listbox_select(None)
        
        print("\n" + "="*60)
        print("FONT SIZE TEST COMPLETE")
        print("="*60)
    
    def test_font_sizes():
        """Test all font sizes."""
        print("\n" + "="*60)
        print("TESTING ALL FONT SIZES")
        print("="*60)
        
        # Select Silver tier first
        tier_panel.tier_listbox.selection_clear(0, tk.END)
        tier_panel.tier_listbox.selection_set(3)  # Silver tier
        tier_panel._on_listbox_select(None)
        
        # Test all font sizes
        for i in range(len(hand_grid.strategy_data.tiers)):
            print(f"\nTesting font size {i+1}/{len(hand_grid.strategy_data.tiers)}")
            hand_grid.grid_size_index = i
            hand_grid.create_hand_grid()
            hand_grid.highlight_tiers([hand_grid.strategy_data.tiers[3]])  # Silver tier
    
    ttk.Button(test_frame, text="Test Font Size Sequence", command=test_sequence, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(test_frame, text="Test All Font Sizes", command=test_font_sizes, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(main_frame, 
                           text="Font Size Test Instructions:\n1. Click 'Test Font Size Sequence' to test with font size changes\n2. Watch console output for debug info\n3. Observe that tier highlighting is preserved during font size changes\n4. Previous selections should be cleared when selecting new tiers",
                           style='Dark.TLabel', justify=tk.LEFT)
    instructions.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_font_size_fix() 
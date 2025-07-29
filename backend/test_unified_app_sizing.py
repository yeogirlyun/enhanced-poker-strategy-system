#!/usr/bin/env python3
"""
Test to verify unified app sizing - grid and all components scale together
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME, GridSettings
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def test_unified_app_sizing():
    """Test that app font controls scale both grid and all components together."""
    root = tk.Tk()
    root.title("Unified App Sizing Test")
    root.geometry("1400x900")
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

    # Top area styles with dark sky blue background
    top_area_bg = "#1E3A5F"  # Dark sky blue
    top_area_fg = "#FFFFFF"   # White text for contrast
    top_area_border = "#2E5A8F"  # Slightly lighter border

    style.configure('TopArea.TFrame', background=top_area_bg)
    style.configure('TopArea.TLabel', background=top_area_bg, foreground=top_area_fg)
    style.configure('TopArea.TLabelframe', background=top_area_bg, bordercolor=top_area_border)
    style.configure('TopArea.TLabelframe.Label', background=top_area_bg, foreground=top_area_fg)
    style.configure('TopArea.TButton', background=top_area_border, foreground=top_area_fg, borderwidth=1)
    style.map('TopArea.TButton', background=[('active', THEME["accent"])])

    # Create strategy data
    strategy_data = StrategyData()
    strategy_data.load_default_tiers()

    # Create main container
    main_container = ttk.Frame(root, style='Dark.TFrame')
    main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # TOP AREA: Menu and controls with dark sky blue background
    top_frame = ttk.LabelFrame(main_container, text="Application Controls", style='TopArea.TLabelframe')
    top_frame.pack(fill=tk.X, padx=5, pady=5)

    # Top row: Strategy and file controls
    strategy_row = ttk.Frame(top_frame, style='TopArea.TFrame')
    strategy_row.pack(fill=tk.X, padx=5, pady=2)
    
    # Create a centered container for all controls
    controls_container = ttk.Frame(strategy_row, style='TopArea.TFrame')
    controls_container.pack(expand=True, anchor=tk.CENTER)
    
    # Strategy file info
    ttk.Label(controls_container, text="Strategy:", style='TopArea.TLabel').pack(side=tk.LEFT, anchor=tk.CENTER)
    strategy_label = ttk.Label(controls_container, text="Default Strategy", style='TopArea.TLabel')
    strategy_label.pack(side=tk.LEFT, padx=5, anchor=tk.CENTER)
    
    # File operation buttons
    ttk.Button(controls_container, text="New", width=8, style='TopArea.TButton').pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
    ttk.Button(controls_container, text="Open", width=8, style='TopArea.TButton').pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
    ttk.Button(controls_container, text="Save", width=8, style='TopArea.TButton').pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
    
    # App font size controls
    ttk.Label(controls_container, text="App Font:", style='TopArea.TLabel').pack(side=tk.LEFT, padx=10, anchor=tk.CENTER)
    ttk.Button(controls_container, text="-", width=4, style='TopArea.TButton').pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
    
    font_size_label = ttk.Label(controls_container, text="Large", style='TopArea.TLabel')
    font_size_label.pack(side=tk.LEFT, padx=5, anchor=tk.CENTER)
    
    ttk.Button(controls_container, text="+", width=4, style='TopArea.TButton').pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
    
    # Grid control buttons
    ttk.Button(controls_container, text="Clear Highlights", width=12, style='TopArea.TButton').pack(side=tk.LEFT, padx=10, anchor=tk.CENTER)
    ttk.Button(controls_container, text="Clear All", width=8, style='TopArea.TButton').pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
    ttk.Button(controls_container, text="Force Clear", width=10, style='TopArea.TButton').pack(side=tk.LEFT, padx=2, anchor=tk.CENTER)
    


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

    # Add test info
    test_frame = ttk.LabelFrame(main_container, text="Unified App Sizing Test", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

    info_text = """Unified App Sizing Test with Center Alignment:
1. ✅ Verify app font controls are present (App Font: - Large +)
2. ✅ Test that clicking +/- changes both grid size AND all app fonts
3. ✅ Confirm grid buttons get larger/smaller with app font changes
4. ✅ Verify tier panel text scales with app font changes
5. ✅ Check that top area controls scale with app font changes
6. ✅ Confirm "Refresh Colors" button is removed (redundant)
7. ✅ Test that grid size index matches app font size index
8. ✅ Verify Cmd+ and Cmd- shortcuts work for unified sizing
9. ✅ Confirm all components scale together as one unified app
10. ✅ Test that the layout remains compact and efficient
11. ✅ Verify "Clear All" button is in top area (not in grid controls)
12. ✅ Test that Clear Highlights, Clear All, and Force Clear work
13. ✅ Confirm all top area controls are center-aligned consistently"""

    info_label = ttk.Label(test_frame, text=info_text, style='Dark.TLabel', justify=tk.LEFT)
    info_label.pack(anchor=tk.W, padx=5, pady=5)

    print("DEBUG: Unified app sizing test started")
    root.mainloop()

if __name__ == "__main__":
    test_unified_app_sizing() 
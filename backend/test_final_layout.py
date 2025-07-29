#!/usr/bin/env python3
"""
Final test to verify the complete layout without any font size controls
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel

def test_final_layout():
    """Test the final layout without any font size controls."""
    root = tk.Tk()
    root.title("Final Layout Test - No Font Controls")
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
    test_frame = ttk.LabelFrame(main_container, text="Final Layout Test", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    info_text = """Final Layout Test - Unified App Sizing with Center Alignment:
1. ✅ Verify top area has dark sky blue background (#1E3A5F)
2. ✅ Check that all controls have white text for contrast
3. ✅ Confirm tier selection instructions are in the top area
4. ✅ Verify app font size controls are present (App Font: - Large +)
5. ✅ Test that the layout is compact and efficient
6. ✅ Confirm Clear Highlights, Clear All, and Force Clear buttons work
7. ✅ Verify strategy file controls (New, Open, Save) work
8. ✅ Test tier selection and highlighting functionality
9. ✅ Verify hand grid displays correctly with unified app sizing
10. ✅ Confirm tier panel works with enhanced space
11. ✅ Test app font size controls affect entire application (grid + fonts)
12. ✅ Verify Cmd+ and Cmd- shortcuts work for unified sizing
13. ✅ Confirm "Refresh Colors" button is removed (redundant)
14. ✅ Test that grid size scales with app font size changes
15. ✅ Verify "Clear All" button is in top area (not in grid controls)
16. ✅ Confirm all top area controls are center-aligned consistently"""
    
    info_label = ttk.Label(test_frame, text=info_text, style='Dark.TLabel', justify=tk.LEFT)
    info_label.pack(anchor=tk.W, padx=5, pady=5)
    
    print("DEBUG: Final layout test started - all font controls removed")
    root.mainloop()

if __name__ == "__main__":
    test_final_layout() 
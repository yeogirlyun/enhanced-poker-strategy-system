#!/usr/bin/env python3
"""
Test to verify the new top area styling with dark sky blue background
"""

import tkinter as tk
from tkinter import ttk
from gui_models import StrategyData, THEME

def test_top_area_styling():
    """Test the new top area styling with dark sky blue background."""
    root = tk.Tk()
    root.title("Test Top Area Styling")
    root.geometry("1200x800")
    root.configure(bg=THEME["bg"])
    
    # Setup styles
    style = ttk.Style(root)
    style.theme_use('clam')
    
    # Dark theme colors
    style.configure('.', background=THEME["bg"], foreground=THEME["fg"], 
                   font=(THEME["font_family"], THEME["font_size"]))
    
    # Dark theme styles
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
    
    # Create main container
    main_container = ttk.Frame(root, style='Dark.TFrame')
    main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # TOP AREA: Menu and controls with dark sky blue background
    top_frame = ttk.LabelFrame(main_container, text="Application Controls", style='TopArea.TLabelframe')
    top_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Top row: Strategy and file controls
    strategy_row = ttk.Frame(top_frame, style='TopArea.TFrame')
    strategy_row.pack(fill=tk.X, padx=5, pady=2)
    
    # Strategy file info
    ttk.Label(strategy_row, text="Strategy:", style='TopArea.TLabel').pack(side=tk.LEFT)
    strategy_label = ttk.Label(strategy_row, text="Default Strategy", style='TopArea.TLabel')
    strategy_label.pack(side=tk.LEFT, padx=5)
    
    # File operation buttons
    ttk.Button(strategy_row, text="New", width=8, style='TopArea.TButton').pack(side=tk.LEFT, padx=2)
    ttk.Button(strategy_row, text="Open", width=8, style='TopArea.TButton').pack(side=tk.LEFT, padx=2)
    ttk.Button(strategy_row, text="Save", width=8, style='TopArea.TButton').pack(side=tk.LEFT, padx=2)
    
    # Grid control buttons
    ttk.Button(strategy_row, text="Clear Highlights", width=12, style='TopArea.TButton').pack(side=tk.LEFT, padx=10)
    ttk.Button(strategy_row, text="Force Clear", width=10, style='TopArea.TButton').pack(side=tk.LEFT, padx=2)
    

    
    # MAIN CONTENT AREA: Grid and Tiers
    content_frame = ttk.Frame(main_container, style='Dark.TFrame')
    content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # LEFT AREA: Hand grid (takes most space)
    grid_frame = ttk.Frame(content_frame, style='Dark.TFrame')
    grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    
    # Simulate grid area
    grid_label = ttk.Label(grid_frame, text="Hand Grid Area\n(Left side - takes most space)", 
                          style='Dark.TLabel', justify=tk.CENTER)
    grid_label.pack(fill=tk.BOTH, expand=True)
    
    # RIGHT AREA: Tiers/HS/Decision table panel (compact)
    right_panel_frame = ttk.Frame(content_frame, style='Dark.TFrame')
    right_panel_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
    
    # Simulate tier panel area
    tier_label = ttk.Label(right_panel_frame, text="Tiers & Strategy\nManagement Area\n(Right side - compact)", 
                          style='Dark.TLabel', justify=tk.CENTER)
    tier_label.pack(fill=tk.BOTH, expand=True)
    
    # Add test info
    test_frame = ttk.LabelFrame(main_container, text="Top Area Styling Test", style='Dark.TLabelframe')
    test_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    info_text = """Top Area Styling Test:
1. Verify top area has dark sky blue background (#1E3A5F)
2. Check that all controls in top area have white text for contrast
3. Confirm tier selection instructions are in the top area
4. Verify no font size controls are present (all removed for space efficiency)
5. Test that the layout is compact and efficient
6. Confirm Clear Highlights and Force Clear buttons work properly
7. Verify strategy file controls (New, Open, Save) work correctly"""
    
    info_label = ttk.Label(test_frame, text=info_text, style='Dark.TLabel', justify=tk.LEFT)
    info_label.pack(anchor=tk.W, padx=5, pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_top_area_styling() 
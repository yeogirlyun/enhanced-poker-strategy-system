# filename: main_gui.py
"""
Main Application for the Advanced Poker Strategy Development GUI

This script assembles and coordinates the various UI components, acting as
the main entry point for the application.

REVISION HISTORY:
================
Version 1.0 (2025-07-29) - Initial Modular Version
- Created as part of a major refactoring from a monolithic file.
- Instantiates and manages the HandGridWidget, TierPanel, and data models.
- Handles communication between child widgets using callbacks.
"""

import tkinter as tk
from tkinter import ttk
from typing import List

# Import the new, modular components
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel
from dialogs import AboutDialog # Example menu item

class PokerStrategyGUI:
    """The main application window that coordinates all GUI components."""

    def __init__(self):
        # --- Main Window Setup ---
        self.root = tk.Tk()
        self.root.title("Advanced Poker Strategy Development GUI - Modular Edition")
        self.root.geometry("1200x800")
        self.root.configure(bg=THEME["bg"])
        self._setup_styles()
        self._setup_menu()

        # --- Data Model ---
        # A central place to hold the application's state
        self.strategy_data = StrategyData()
        self.strategy_data.load_default_tiers()

        # --- Main Layout ---
        # A PanedWindow allows the user to resize the left and right panels
        paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_frame = ttk.Frame(paned_window, style='Dark.TFrame')
        paned_window.add(left_frame, weight=2)
        
        right_frame = ttk.Frame(paned_window, style='Dark.TFrame')
        paned_window.add(right_frame, weight=1)

        # --- Instantiate and Connect Widgets ---
        # The HandGrid needs to know about the strategy data and can notify of hand clicks
        self.hand_grid = HandGridWidget(left_frame, self.strategy_data, on_hand_click=self._on_hand_click)
        
        # The TierPanel also uses the strategy data and needs to communicate
        # back to the main app when things change.
        self.tier_panel = TierPanel(
            left_frame, 
            self.strategy_data,
            on_tier_change=self._on_tier_data_change,
            on_tier_select=self._on_tier_selection_change
        )
        
        # Placeholder for the right panel (decision tables would go here)
        ttk.Label(right_frame, text="Decision Tables Panel", style='Dark.TLabel').pack(pady=20)

    def _setup_styles(self):
        """Configures the dark theme for ttk widgets."""
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('.', background=THEME["bg"], foreground=THEME["fg"], font=(THEME["font_family"], THEME["font_size"]))
        style.configure('Dark.TFrame', background=THEME["bg_dark"])
        style.configure('Dark.TLabel', background=THEME["bg_dark"], foreground=THEME["fg"])
        style.configure('Dark.TLabelframe', background=THEME["bg_dark"], bordercolor=THEME["bg_light"])
        style.configure('Dark.TLabelframe.Label', background=THEME["bg_dark"], foreground=THEME["fg"])
        style.configure('Dark.TButton', background=THEME["bg_light"], foreground=THEME["fg"], borderwidth=1)
        style.map('Dark.TButton', background=[('active', THEME["accent"])])
        style.configure('Dark.Vertical.TScrollbar', background=THEME["bg_light"], troughcolor=THEME["bg_dark"])
        
    def _setup_menu(self):
        """Creates the main application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Strategy", state=tk.DISABLED)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    # --- Callback Methods (The "Glue") ---
    def _on_hand_click(self, hand: str, is_selected: bool):
        """Callback from HandGrid when a hand is clicked."""
        print(f"Hand {hand} {'selected' if is_selected else 'deselected'}")
        # Future: Could trigger tier assignment or other actions

    def _on_tier_selection_change(self, selected_tiers: List):
        """Callback from TierPanel when the listbox selection changes."""
        self.hand_grid.highlight_tiers(selected_tiers)

    def _on_tier_data_change(self):
        """Callback from TierPanel when tiers are added, removed, or edited."""
        self.hand_grid.update_hand_colors()
        
    def _show_about(self):
        """Shows the About dialog window."""
        AboutDialog(self.root)

    def run(self):
        """Starts the Tkinter main event loop."""
        self.root.mainloop()

if __name__ == '__main__':
    app = PokerStrategyGUI()
    app.run()
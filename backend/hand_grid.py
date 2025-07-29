# filename: hand_grid.py
"""
Hand Grid Widget for Strategy Development GUI

Handles the visual poker hand grid display and interactions.

REVISION HISTORY:
================
Version 1.0 (2025-07-29) - Initial Version
- Created by extracting the hand grid logic from the monolithic GUI file.
- Manages the display, coloring, selection, and highlighting of the 13x13 hand matrix.
- Communicates with the main app via a data model and callbacks.
"""

import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, Canvas, Scrollbar, Frame
from typing import Dict, Set, List, Optional, Callable
from gui_models import StrategyData, THEME, HandFormatHelper, GridSettings

class HandGridWidget:
    """
    Manages the visual grid of poker hands and its interactions.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Encapsulates all logic for creating, updating, and interacting with the hand grid.
    - Handles hand selection and tier-based color rendering.
    """
    def __init__(self, parent_frame, strategy_data: StrategyData, on_hand_click: Callable = None):
        self.parent = parent_frame
        self.strategy_data = strategy_data
        self.on_hand_click = on_hand_click
        self.hand_widgets: Dict[str, tk.Button] = {}
        self.selected_hands: Set[str] = set()
        self.current_highlight_mode: Optional[str] = None
        self.grid_size_index = 1  # Default to "Medium"
        self.base_font = tkFont.Font(family=THEME["font_family"], size=THEME["font_size"])

        self._setup_ui()
        self.create_hand_grid()
        self.update_hand_colors()

    def _setup_ui(self):
        """Sets up the main frame and scrollable canvas for the grid."""
        self.grid_frame = ttk.LabelFrame(self.parent, text="Hand Strength Grid", style='Dark.TLabelframe')
        self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add controls
        self._setup_controls()
        
        # Setup canvas
        self._setup_canvas()

    def _setup_controls(self):
        """Setup grid control buttons."""
        controls_frame = ttk.Frame(self.grid_frame, style='Dark.TFrame')
        controls_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Size controls
        ttk.Label(controls_frame, text="Grid Size:", style='Dark.TLabel').pack(side=tk.LEFT)
        size_frame = ttk.Frame(controls_frame, style='Dark.TFrame')
        size_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(size_frame, text="-", width=3, 
                  command=self.decrease_grid_size, style='Dark.TButton').pack(side=tk.LEFT)
        
        self.size_label = ttk.Label(size_frame, text="Medium", width=12, 
                                   anchor="center", relief="sunken", borderwidth=1, style='Dark.TLabel')
        self.size_label.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(size_frame, text="+", width=3, 
                  command=self.increase_grid_size, style='Dark.TButton').pack(side=tk.LEFT)
        
        # Refresh button
        ttk.Button(controls_frame, text="Refresh Colors", 
                  command=self.update_hand_colors, style='Dark.TButton').pack(side=tk.RIGHT, padx=5)

    def _setup_canvas(self):
        """Setup scrollable canvas for hand grid."""
        self.grid_canvas = Canvas(self.grid_frame, bg=THEME["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.grid_frame, orient=tk.VERTICAL, 
                                 command=self.grid_canvas.yview, style='Dark.Vertical.TScrollbar')
        
        self.hand_frame = Frame(self.grid_canvas, bg=THEME["bg_dark"])
        self.grid_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas_window = self.grid_canvas.create_window(
            (0, 0), window=self.hand_frame, anchor='nw'
        )

    def create_hand_grid(self):
        """Creates or recreates the 13x13 grid of hand buttons."""
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        self.hand_widgets.clear()

        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        size_settings = GridSettings.get_size_config(
            GridSettings.get_all_sizes()[self.grid_size_index]
        )
        
        # Create header row
        tk.Label(self.hand_frame, text="", width=size_settings['label_width'], 
                bg='lightgray', font=size_settings['font']).grid(row=0, column=0)
        
        for i, rank in enumerate(ranks):
            tk.Label(self.hand_frame, text=rank, width=size_settings['label_width'], 
                    bg='lightgray', font=size_settings['font']).grid(row=0, column=i+1)
        
        # Create hand buttons
        for i, rank1 in enumerate(ranks):
            # Row header
            tk.Label(self.hand_frame, text=rank1, width=size_settings['label_width'], 
                    bg='lightgray', font=size_settings['font']).grid(row=i+1, column=0)
            
            for j, rank2 in enumerate(ranks):
                hand = self._get_hand_notation(rank1, rank2, i, j)
                
                btn = tk.Button(
                    self.hand_frame, text=hand,
                    width=size_settings['button_width'],
                    height=size_settings['button_height'],
                    font=size_settings['font'],
                    relief=tk.RAISED,
                    command=lambda h=hand: self.toggle_hand_selection(h)
                )
                btn.grid(row=i+1, column=j+1, padx=1, pady=1)
                self.hand_widgets[hand] = btn
                
                # Bind right-click for context menu
                btn.bind('<Button-3>', lambda e, h=hand: self.show_hand_menu(e, h))
        
        # Update canvas scroll region
        self.hand_frame.update_idletasks()
        self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox('all'))

    def toggle_hand_selection(self, hand: str):
        """Toggle hand selection state."""
        widget = self._find_hand_widget(hand)
        if not widget:
            return
        
        if hand in self.selected_hands:
            self.selected_hands.remove(hand)
            widget.configure(relief=tk.RAISED, borderwidth=2)
        else:
            self.selected_hands.add(hand)
            widget.configure(relief=tk.SUNKEN, borderwidth=4)
        
        # Update highlight mode
        self.current_highlight_mode = 'selection' if self.selected_hands else None
        
        # Notify parent of selection change
        if self.on_hand_click:
            self.on_hand_click(hand, bool(hand in self.selected_hands))

    def update_hand_colors(self):
        """Applies background colors to hand cells based on their assigned tier."""
        try:
            # Reset all widgets to default
            for widget in self.hand_widgets.values():
                widget.configure(bg='lightgray', borderwidth=2, relief=tk.RAISED)
            
            # Apply tier colors
            for tier in self.strategy_data.tiers:
                for hand in tier.hands:
                    widget = self._find_hand_widget(hand)
                    if widget:
                        widget.configure(bg=tier.color)
            
            # Reapply selection highlighting
            if self.current_highlight_mode == 'selection':
                for hand in self.selected_hands:
                    widget = self._find_hand_widget(hand)
                    if widget:
                        widget.configure(relief=tk.SUNKEN, borderwidth=4)
            
            self.hand_frame.update_idletasks()
            
        except Exception as e:
            print(f"Error updating hand colors: {e}")

    def highlight_tiers(self, selected_tiers: List):
        """Applies a highlight border to hands in the selected tiers."""
        self._reset_highlights()
        if not selected_tiers or len(selected_tiers) <= 1:
            return

        for i, tier in enumerate(selected_tiers):
            highlight_color = GridSettings.HIGHLIGHT_COLORS[i % len(GridSettings.HIGHLIGHT_COLORS)]
            for hand in tier.hands:
                widget = self._find_hand_widget(hand)
                if widget:
                    widget.configure(
                        highlightbackground=highlight_color,
                        highlightthickness=2,
                        relief=tk.RAISED
                    )

    def _reset_highlights(self):
        """Removes all highlight borders from the grid."""
        for widget in self.hand_widgets.values():
            widget.configure(highlightthickness=0, relief=tk.RAISED)
        self.update_hand_colors()

    def _find_hand_widget(self, hand: str) -> Optional[tk.Button]:
        """Finds a button widget for a hand, checking alternative formats."""
        # Direct lookup
        if hand in self.hand_widgets:
            return self.hand_widgets[hand]
        
        # Try alternative formats
        alternatives = HandFormatHelper.get_alternative_formats(hand)
        for alt_hand in alternatives:
            if alt_hand in self.hand_widgets:
                return self.hand_widgets[alt_hand]
        
        return None

    def _get_hand_notation(self, rank1: str, rank2: str, i: int, j: int) -> str:
        """Get hand notation based on grid position."""
        if i == j:
            return rank1 + rank2  # Pocket pairs
        elif i < j:
            return rank1 + rank2 + 's'  # Suited
        else:
            return rank2 + rank1 + 'o'  # Offsuit

    def increase_grid_size(self):
        """Increase grid size."""
        if self.grid_size_index < len(GridSettings.get_all_sizes()) - 1:
            self.grid_size_index += 1
            self._update_size_label()
            self.create_hand_grid()
            self.update_hand_colors()

    def decrease_grid_size(self):
        """Decrease grid size."""
        if self.grid_size_index > 0:
            self.grid_size_index -= 1
            self._update_size_label()
            self.create_hand_grid()
            self.update_hand_colors()

    def _update_size_label(self):
        """Update the size label text."""
        sizes = GridSettings.get_all_sizes()
        self.size_label.configure(text=sizes[self.grid_size_index])

    def get_selected_hands(self) -> Set[str]:
        """Get currently selected hands."""
        return self.selected_hands.copy()

    def clear_selection(self):
        """Clear all hand selections."""
        for hand in list(self.selected_hands):
            widget = self._find_hand_widget(hand)
            if widget:
                widget.configure(relief=tk.RAISED, borderwidth=2)
        
        self.selected_hands.clear()
        self.current_highlight_mode = None
        self.update_hand_colors()

    def show_hand_menu(self, event, hand: str):
        """Show context menu for hand (placeholder for future enhancement)."""
        # This could be enhanced to show tier assignment options
        pass
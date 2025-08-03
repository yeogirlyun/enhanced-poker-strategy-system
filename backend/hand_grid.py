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
from typing import Dict, Set, List, Optional, Callable, Tuple
from gui_models import StrategyData, THEME, HandFormatHelper, GridSettings


class HandGridWidget:
    """
    A widget that displays a 13x13 grid of poker hands with tier-based coloring.

    REVISION HISTORY:
    ================
    Version 1.0 (2025-07-29) - Initial Version
    - Created to display poker hands in a grid format.
    - Supports tier-based highlighting and hand selection.
    """

    def __init__(
        self, parent_frame, strategy_data: StrategyData, on_hand_click: Callable = None, tier_panel=None
    ):
        self.parent = parent_frame
        self.strategy_data = strategy_data
        self.on_hand_click = on_hand_click
        self.tier_panel = tier_panel
        self.hand_widgets: Dict[str, tk.Button] = {}
        self.selected_hands: Set[str] = set()
        self.current_highlight_mode: Optional[str] = None
        self.grid_size_index = (
            6  # Default to size "7" for better visibility and HS score display
        )
        self.base_font = tkFont.Font(
            family=THEME["font_family"], size=THEME["font_size"]
        )

        # Centralized state management
        self._current_tier_selection = None
        self._tier_highlighting_active = False
        self._grid_state = {
            "selected_tiers": [],
            "selected_hands": set(),
            "grid_size": 6,  # Use size "7" for better visibility and HS score display
            "needs_redraw": True,
        }


        self._setup_ui()
        self._render_grid()  # Initial render

    def _setup_ui(self):
        """Sets up the UI components."""
        # Create main frame with scrollable canvas
        self.main_frame = ttk.Frame(self.parent, style="Dark.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create canvas for scrolling
        self.grid_canvas = tk.Canvas(
            self.main_frame, bg=THEME["bg"], highlightthickness=0
        )
        self.grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.main_frame, orient=tk.VERTICAL, command=self.grid_canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.grid_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create frame inside canvas for grid
        self.hand_frame = ttk.Frame(self.grid_canvas, style="Dark.TFrame")
        self.grid_canvas.create_window((0, 0), window=self.hand_frame, anchor="nw")

        # Setup controls
        self._setup_controls()

        # Bind canvas resize
        self.hand_frame.bind(
            "<Configure>",
            lambda e: self.grid_canvas.configure(
                scrollregion=self.grid_canvas.bbox("all")
            ),
        )

    def _setup_controls(self):
        """Sets up the grid controls."""
        controls_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        controls_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Action buttons only (removed grid size controls)
        # Clear All button moved to top area for better organization

    def _render_grid(self):
        """Renders the grid with optimized partial updates."""
        if not self._grid_state["needs_redraw"]:
            return  # Skip if no changes needed
        
        
        # Check if we need to completely rebuild or just update existing widgets
        if not self.hand_widgets:
            self._render_grid_full()
        else:
            self._update_existing_widgets()
        
        # Mark as no longer needing redraw
        self._grid_state["needs_redraw"] = False
    
    def _render_grid_full(self):
        """Completely rebuilds the grid (first time or major changes)."""
        
        # Clear all existing widgets
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        
        # Get current size configuration
        sizes = GridSettings.get_all_sizes()
        current_size = sizes[self._grid_state["grid_size"]]
        size_config = GridSettings.get_size_config(current_size)
        
        # Configure base font
        self.base_font = tkFont.Font(
            family=THEME["font_family"], size=size_config["font"][1]
        )
        
        # Create grid
        ranks = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
        
        # Add row labels (left side)
        for i, rank in enumerate(ranks):
            label = tk.Label(
                self.hand_frame,
                text=rank,
                font=self.base_font,
                bg="#006400",
                fg="#ffffff",
                width=3,
                height=1,
            )
            label.grid(row=i + 1, column=0, padx=2, pady=1)
        
        # Add column labels (top)
        for j, rank in enumerate(ranks):
            label = tk.Label(
                self.hand_frame,
                text=rank,
                font=self.base_font,
                bg="#006400",
                fg="#ffffff",
                width=3,
                height=1,
            )
            label.grid(row=0, column=j + 1, padx=2, pady=1)
        
        # Create hand buttons
        for i, rank1 in enumerate(ranks):
            for j, rank2 in enumerate(ranks):
                hand = self._get_hand_notation(rank1, rank2, i, j)
                
                # Get button appearance based on current state
                bg_color, fg_color, border_color, border_width = (
                    self._get_button_appearance(hand)
                )
                
                # Create button with HS score
                button_frame = self._create_button_with_hs(
                    hand, size_config, bg_color, fg_color, border_color, border_width
                )
                
                # Add click handlers for hand selection and HS editing
                main_label = button_frame.winfo_children()[0]
                self._add_click_handlers(button_frame, main_label, hand)
                
                button_frame.grid(row=i + 1, column=j + 1, padx=1, pady=1)
                self.hand_widgets[hand] = button_frame
        
        # Update canvas scroll region
        self.hand_frame.update_idletasks()
        self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox("all"))
        
        # Bind resize event to recalculate button sizes
        self.grid_canvas.bind("<Configure>", self._on_grid_resize)
    
    def _update_existing_widgets(self):
        """Updates existing widgets without rebuilding the entire grid."""
        
        for hand, widget in self.hand_widgets.items():
            # Get current appearance
            bg_color, fg_color, border_color, border_width = (
                self._get_button_appearance(hand)
            )
            
            # Update main label (first child)
            main_label = widget.winfo_children()[0]
            main_label.configure(bg=bg_color, fg=fg_color)
            
            # Update border if needed
            if border_color:
                widget.configure(
                    highlightbackground=border_color, 
                    highlightthickness=border_width
                )
            else:
                widget.configure(highlightthickness=0)
            
            # Update HS label if it exists (second child)
            if len(widget.winfo_children()) > 1:
                hs_label = widget.winfo_children()[1]
                hs_score = self._get_hand_strength(hand)
                hs_label.configure(
                    text=str(hs_score) if hs_score else "",
                    bg=bg_color,
                    fg=fg_color
                )

    def _get_button_appearance(self, hand: str) -> Tuple[str, str, str, int]:
        """Determines the appearance of a button based on current state."""
        # Default appearance
        bg_color = "#404040"  # Dark gray background
        fg_color = "#ffffff"  # White text
        border_color = None
        border_width = 2

        # Check if hand is in selected tiers
        if self._grid_state["selected_tiers"]:
            for tier in self._grid_state["selected_tiers"]:
                if hand in tier.hands:
                    bg_color = tier.color
                    fg_color = "#000000"  # Black text for better contrast on colored backgrounds
                    border_color = "#ffffff"  # White border for selected tier hands
                    border_width = 4  # Thicker border for selected tier hands
                    break
            else:
                # Hand is not in selected tiers - apply general tier color but make it less prominent
                for tier in self.strategy_data.tiers:
                    if hand in tier.hands:
                        # Use a dimmed version of the tier color for non-selected tiers
                        bg_color = self._dim_color(
                            tier.color, 0.3
                        )  # Dim the color by 70%
                        fg_color = "#666666"  # Gray text for non-selected tiers
                        border_width = 1  # Thin border for non-selected tiers
                        break
        else:
            # No tiers selected - apply general tier colors
            for tier in self.strategy_data.tiers:
                if hand in tier.hands:
                    bg_color = tier.color
                    fg_color = "#000000"  # Black text for better contrast
                    break

        # Check if hand is selected
        if hand in self._grid_state["selected_hands"]:
            border_width = 5  # Even thicker border for individually selected hands
            border_color = "#ffff00"  # Yellow border for selected hands

        return bg_color, fg_color, border_color, border_width

    def _dim_color(self, color: str, factor: float) -> str:
        """Dim a hex color by the given factor (0.0 = black, 1.0 = original)."""
        # Remove # if present
        color = color.lstrip("#")

        # Convert to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)

        # Dim the color
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def _update_grid_state(self, **kwargs):
        """Updates the grid state and triggers a redraw."""
        self._grid_state.update(kwargs)
        self._grid_state["needs_redraw"] = True
        self._render_grid()

    def highlight_tiers(self, selected_tiers: List):
        """Updates tier selection and triggers grid redraw."""
        # Store current grid size to maintain it during highlighting
        current_grid_size = self._grid_state["grid_size"]

        # Update state and trigger redraw
        self._update_grid_state(selected_tiers=selected_tiers)

        # Ensure grid size is maintained
        self._grid_state["grid_size"] = current_grid_size

        # Update tier selection state for compatibility
        self._current_tier_selection = selected_tiers if selected_tiers else None
        self._tier_highlighting_active = bool(selected_tiers)

    def update_hand_colors(self):
        """Updates hand colors and triggers grid redraw."""
        # This method now just triggers a redraw
        self._render_grid()

    def toggle_hand_selection(self, hand: str):
        """Toggles hand selection with single-selection behavior."""
        # If clicking the same hand, deselect it
        if hand in self._grid_state["selected_hands"]:
            self._grid_state["selected_hands"].remove(hand)
            # Clear the selected hand from tier panel
            if self.tier_panel:
                self.tier_panel.clear_selected_hand()
        else:
            # Clear all other selections and select only this hand
            self._grid_state["selected_hands"].clear()
            self._grid_state["selected_hands"].add(hand)

        # Update state and trigger redraw
        self._update_grid_state(
            selected_hands=self._grid_state["selected_hands"].copy()
        )

        if self.on_hand_click:
            self.on_hand_click(hand, hand in self._grid_state["selected_hands"])

    def increase_grid_size(self):
        """Increases grid size and triggers redraw."""
        if self.grid_size_index < len(GridSettings.get_all_sizes()) - 1:
            self.grid_size_index += 1
            self._update_grid_state(grid_size=self.grid_size_index)

    def decrease_grid_size(self):
        """Decreases grid size and triggers redraw."""
        if self.grid_size_index > 0:
            self.grid_size_index -= 1
            self._update_grid_state(grid_size=self.grid_size_index)

    def _get_hand_notation(self, rank1: str, rank2: str, i: int, j: int) -> str:
        """Get hand notation based on grid position."""
        if i == j:
            return rank1 + rank2  # Pocket pairs
        elif i < j:
            return rank1 + rank2 + "s"  # Suited
        else:
            return rank2 + rank1 + "o"  # Offsuit

    def _get_hand_strength(self, hand: str) -> Optional[int]:
        """Get the hand strength (HS) score for a given hand."""
        if not self.strategy_data.strategy_dict:
            return None

        # Get hand strength from strategy data
        hand_strength_table = self.strategy_data.strategy_dict.get(
            "hand_strength_tables", {}
        ).get("preflop", {})
        return hand_strength_table.get(hand)

    def _create_button_with_hs(
        self,
        hand: str,
        size_config: Dict,
        bg_color: str,
        fg_color: str,
        border_color: str,
        border_width: int,
    ):
        """Create a button with hand name and HS score display."""
        # Create a frame to act as the button with proper dimensions
        button_frame = tk.Frame(
            self.hand_frame,
            bg=bg_color,
            relief=tk.RAISED,
            bd=border_width,
            width=size_config["button_width"],
            height=size_config["button_height"],
        )
        if border_color:
            button_frame.configure(
                relief=tk.SOLID,
                bd=border_width,
                highlightbackground=border_color,
                highlightthickness=border_width,
            )

        # Configure frame to maintain size
        button_frame.pack_propagate(False)
        button_frame.grid_propagate(False)

        # Main hand label
        hand_label = tk.Label(
            button_frame,
            text=hand,
            font=size_config["font"],
            bg=bg_color,
            fg=fg_color,
            padx=2,
            pady=1,
        )
        hand_label.pack(expand=True, fill=tk.BOTH)

        # Add click handlers and context menu
        self._add_click_handlers(button_frame, hand_label, hand)

        # HS score label (show for all font sizes with better visibility)
        hs_score = self._get_hand_strength(hand)
        if hs_score is not None:
            hs_label = tk.Label(
                button_frame,
                text=str(hs_score),
                font=(size_config["font"][0], max(size_config["font"][1] - 1, 8)),
                bg=bg_color,
                fg=fg_color,
            )
            hs_label.pack(side=tk.BOTTOM, fill=tk.X)

        return button_frame

    def get_hand_strength(self, hand: str) -> Optional[int]:
        """Public method to get hand strength for external use."""
        return self._get_hand_strength(hand)

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

    def get_selected_hands(self) -> Set[str]:
        """Get currently selected hands."""
        return self._grid_state["selected_hands"].copy()

    def clear_selection(self):
        """Clear all hand selections and trigger redraw."""
        self._update_grid_state(selected_hands=set())

    def force_clear_highlights(self):
        """Force clear all highlights and reset state."""
        self._update_grid_state(selected_tiers=[], selected_hands=set())
        self._current_tier_selection = None
        self._tier_highlighting_active = False

    def clear_all_highlights(self):
        """Clear all highlights and return to default state."""
        self._update_grid_state(selected_tiers=[], selected_hands=set())
        self._current_tier_selection = None
        self._tier_highlighting_active = False

    def _add_click_handlers(self, frame, label, hand: str):
        """Add left-click handler for hand selection and HS editing."""

        def on_left_click(event):
            """Handle left-click for hand selection and HS editing."""
            self.toggle_hand_selection(hand)
            
            # If tier panel is available, set the selected hand for HS editing
            if self.tier_panel:
                self.tier_panel.set_selected_hand(hand)

        # Bind events to both frame and label for better coverage
        for widget in [frame, label]:
            widget.bind("<Button-1>", on_left_click)

    # HS score editing is now handled by the tier panel

    def _on_grid_resize(self, event):
        """Handle grid resize events to recalculate button sizes."""
        # Only trigger if the size actually changed significantly
        if hasattr(self, "_last_grid_size"):
            if (
                abs(event.width - self._last_grid_size[0]) > 10
                or abs(event.height - self._last_grid_size[1]) > 10
            ):
                self._last_grid_size = (event.width, event.height)
                self._render_grid()
        else:
            self._last_grid_size = (event.width, event.height)

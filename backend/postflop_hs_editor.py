#!/usr/bin/env python3
"""
Postflop Hand Strength Editor Widget

This module provides a comprehensive interface for viewing and editing
postflop hand strength scores for various hand ranks and draw types.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict
from gui_models import StrategyData, THEME


class PostflopHSEditor(ttk.Frame):
    """
    A comprehensive widget for editing postflop hand strength scores.

    Features:
    - Organized categories (Made Hands, Draws, Special Situations)
    - Real-time HS score editing
    - Visual indicators for score ranges
    - Save/Reset functionality
    - Integration with existing strategy system
    """

    def __init__(self, parent, strategy_data: StrategyData):
        super().__init__(parent)
        self.strategy_data = strategy_data
        self.original_scores = {}
        self.current_scores = {}
        self.widgets = {}

        # Load current scores
        self._load_current_scores()

        # Create the interface
        self._create_widgets()
        self._populate_scores()

    def _load_current_scores(self):
        """Load current postflop HS scores from strategy data."""
        postflop_table = self.strategy_data.strategy_dict.get(
            "hand_strength_tables", {}
        ).get("postflop", {})

        self.original_scores = postflop_table.copy()
        self.current_scores = postflop_table.copy()

    def _create_widgets(self):
        """Create the main interface widgets."""
        # Main title with larger font and styling
        title_label = ttk.Label(
            self,
            text="Postflop Hand Strength Editor",
            font=(THEME["font_family"], THEME["font_size"] + 6, "bold"),
            foreground=THEME["accent"],
        )
        title_label.pack(pady=(15, 25))

        # Create notebook for organized categories with styling
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Create tabs for different categories
        self._create_made_hands_tab()
        self._create_draws_tab()
        self._create_special_situations_tab()

        # Control buttons
        self._create_control_buttons()

    def _create_made_hands_tab(self):
        """Create tab for made hands (pairs, sets, etc.)."""
        made_hands_frame = ttk.Frame(self.notebook)
        self.notebook.add(made_hands_frame, text="Made Hands")

        # Create scrollable frame
        canvas = tk.Canvas(made_hands_frame, width=500)
        scrollbar = ttk.Scrollbar(
            made_hands_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Made hands data with color coding
        made_hands = [
            ("high_card", "High Card", "Weakest hand type", "#FF6B6B"),  # Red
            ("pair", "Pair", "Basic pair", "#4ECDC4"),  # Teal
            ("top_pair", "Top Pair", "Pair with top card on board", "#45B7D1"),  # Blue
            ("over_pair", "Over Pair", "Pair higher than board", "#96CEB4"),  # Green
            ("two_pair", "Two Pair", "Two different pairs", "#FFEAA7"),  # Yellow
            ("set", "Set", "Three of a kind with pocket pair", "#DDA0DD"),  # Plum
            ("straight", "Straight", "Five consecutive cards", "#98D8C8"),  # Mint
            ("flush", "Flush", "Five cards of same suit", "#F7DC6F"),  # Gold
            ("full_house", "Full House", "Three of a kind + pair", "#BB8FCE"),  # Purple
            (
                "quads",
                "Four of a Kind",
                "Four cards of same rank",
                "#85C1E9",
            ),  # Sky Blue
            (
                "straight_flush",
                "Straight Flush",
                "Straight + flush",
                "#F8C471",
            ),  # Orange
        ]

        self._create_hand_entries(scrollable_frame, made_hands)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_draws_tab(self):
        """Create tab for drawing hands."""
        draws_frame = ttk.Frame(self.notebook)
        self.notebook.add(draws_frame, text="Draws")

        # Create scrollable frame
        canvas = tk.Canvas(draws_frame, width=500)
        scrollbar = ttk.Scrollbar(draws_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Draws data with color coding
        draws = [
            (
                "gutshot_draw",
                "Gutshot Draw",
                "Inside straight draw (4 outs)",
                "#E74C3C",
            ),  # Red
            (
                "open_ended_draw",
                "Open-Ended Draw",
                "Open straight draw (8 outs)",
                "#3498DB",
            ),  # Blue
            (
                "flush_draw",
                "Flush Draw",
                "Four cards of same suit (9 outs)",
                "#2ECC71",
            ),  # Green
            (
                "combo_draw",
                "Combo Draw",
                "Multiple draws (12+ outs)",
                "#F39C12",
            ),  # Orange
        ]

        self._create_hand_entries(scrollable_frame, draws)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_special_situations_tab(self):
        """Create tab for special situations and advanced hands."""
        special_frame = ttk.Frame(self.notebook)
        self.notebook.add(special_frame, text="Special Situations")

        # Create scrollable frame
        canvas = tk.Canvas(special_frame, width=500)
        scrollbar = ttk.Scrollbar(
            special_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Special situations data with color coding
        special_situations = [
            (
                "nut_flush_draw",
                "Nut Flush Draw",
                "Ace-high flush draw",
                "#9B59B6",
            ),  # Purple
            (
                "nut_straight_draw",
                "Nut Straight Draw",
                "Highest possible straight draw",
                "#E67E22",
            ),  # Orange
            (
                "overcard_draw",
                "Overcard Draw",
                "Drawing to overcards",
                "#1ABC9C",
            ),  # Turquoise
            (
                "backdoor_flush",
                "Backdoor Flush",
                "Flush draw with runner-runner",
                "#34495E",
            ),  # Dark Blue
            (
                "backdoor_straight",
                "Backdoor Straight",
                "Straight draw with runner-runner",
                "#7F8C8D",
            ),  # Gray
            (
                "pair_plus_draw",
                "Pair + Draw",
                "Made pair with drawing potential",
                "#E91E63",
            ),  # Pink
            (
                "set_plus_draw",
                "Set + Draw",
                "Set with flush/straight potential",
                "#FF5722",
            ),  # Deep Orange
        ]

        self._create_hand_entries(scrollable_frame, special_situations)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_hand_entries(self, parent, hand_data):
        """Create entry widgets for hand strength scores with color coding."""
        # Header with larger font
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=15, pady=10)

        # Store header labels for font size updates
        hand_type_header = ttk.Label(
            header_frame,
            text="Hand Type",
            font=(THEME["font_family"], THEME["font_size"] + 1, "bold"),
            foreground=THEME["accent"],
        )
        hand_type_header.pack(side=tk.LEFT, anchor=tk.W)

        hs_score_header = ttk.Label(
            header_frame,
            text="HS Score",
            font=(THEME["font_family"], THEME["font_size"] + 1, "bold"),
            foreground=THEME["accent"],
        )
        hs_score_header.pack(side=tk.RIGHT, anchor=tk.E)

        # Store header labels for font size updates
        if not hasattr(self, "header_labels"):
            self.header_labels = []
        self.header_labels.extend([hand_type_header, hs_score_header])

        # Separator
        ttk.Separator(parent, orient="horizontal").pack(fill=tk.X, padx=15, pady=8)

        # Create entries for each hand type
        for hand_info in hand_data:
            if len(hand_info) == 4:
                key, name, description, color = hand_info
            else:
                key, name, description = hand_info
                color = THEME["fg"]  # Default color

            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, padx=15, pady=4)

            # Hand name with color coding
            name_label = ttk.Label(
                frame,
                text=name,
                font=(THEME["font_family"], THEME["font_size"] + 1, "bold"),
                foreground=color,
            )
            name_label.pack(side=tk.LEFT, anchor=tk.W)

            # Description with larger font
            desc_label = ttk.Label(
                frame,
                text=f"({description})",
                font=(THEME["font_family"], THEME["font_size"]),
                foreground="gray",
            )
            desc_label.pack(side=tk.LEFT, anchor=tk.W, padx=(8, 0))

            # HS score entry with larger font
            score_var = tk.StringVar(value=str(self.current_scores.get(key, 0)))
            score_entry = ttk.Entry(
                frame,
                textvariable=score_var,
                width=10,
                justify=tk.CENTER,
                font=(THEME["font_family"], THEME["font_size"] + 1),
            )
            score_entry.pack(side=tk.RIGHT, padx=(15, 0))

            # Store widget reference
            self.widgets[key] = {
                "entry": score_entry,
                "var": score_var,
                "name": name,
                "description": description,
                "color": color,
            }

            # Bind validation
            score_entry.bind("<KeyRelease>", self._validate_score)
            score_entry.bind("<FocusOut>", self._update_score)

    def _create_control_buttons(self):
        """Create control buttons for save/reset functionality."""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=15, pady=15)

        # Save button with larger font
        save_btn = ttk.Button(
            button_frame,
            text="Save Changes",
            command=self._save_changes,
            style="Accent.TButton",
        )
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))

        # Reset button with larger font
        reset_btn = ttk.Button(
            button_frame, text="Reset to Original", command=self._reset_scores
        )
        reset_btn.pack(side=tk.RIGHT, padx=(8, 0))

        # Status label with larger font
        self.status_label = ttk.Label(
            button_frame,
            text="",
            font=(THEME["font_family"], THEME["font_size"] + 1),
            foreground=THEME["accent"],
        )
        self.status_label.pack(side=tk.LEFT, anchor=tk.W)

    def _validate_score(self, event=None):
        """Validate HS score input."""
        widget = event.widget
        value = widget.get()

        try:
            if value == "":
                return

            score = int(value)
            if score < 0 or score > 120:
                widget.configure(foreground="red")
                self.status_label.configure(
                    text="Score must be 0-120", foreground="red"
                )
            else:
                widget.configure(foreground="black")
                self.status_label.configure(text="", foreground="black")
        except ValueError:
            widget.configure(foreground="red")
            self.status_label.configure(text="Invalid number", foreground="red")

    def _update_score(self, event=None):
        """Update the current scores dictionary."""
        widget = event.widget
        value = widget.get()

        try:
            score = int(value) if value else 0
            if 0 <= score <= 120:
                # Find the key for this widget
                for key, widget_data in self.widgets.items():
                    if widget_data["entry"] == widget:
                        self.current_scores[key] = score
                        self._update_status()
                        break
        except ValueError:
            pass

    def _update_status(self):
        """Update the status display."""
        changed_count = sum(
            1
            for key in self.current_scores
            if self.current_scores[key] != self.original_scores.get(key, 0)
        )

        if changed_count > 0:
            self.status_label.configure(
                text=f"{changed_count} score(s) modified", foreground="blue"
            )
        else:
            self.status_label.configure(text="No changes", foreground="green")

    def _save_changes(self):
        """Save changes to the strategy data."""
        try:
            # Update the strategy data
            if "hand_strength_tables" not in self.strategy_data.strategy_dict:
                self.strategy_data.strategy_dict["hand_strength_tables"] = {}

            self.strategy_data.strategy_dict["hand_strength_tables"][
                "postflop"
            ] = self.current_scores.copy()

            # Update original scores
            self.original_scores = self.current_scores.copy()

            messagebox.showinfo(
                "Success",
                f"Postflop HS scores updated successfully!\n"
                f"Total hand types: {len(self.current_scores)}",
            )

            self._update_status()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes:\n{str(e)}")

    def _reset_scores(self):
        """Reset scores to original values."""
        if messagebox.askyesno("Confirm Reset", "Reset all scores to original values?"):
            self.current_scores = self.original_scores.copy()
            self._populate_scores()
            self._update_status()

    def _populate_scores(self):
        """Populate the entry widgets with current scores."""
        for key, widget_data in self.widgets.items():
            score = self.current_scores.get(key, 0)
            widget_data["var"].set(str(score))

    def get_current_scores(self) -> Dict[str, int]:
        """Get the current postflop HS scores."""
        return self.current_scores.copy()

    def has_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.current_scores != self.original_scores

    def update_font_size(self, font_size: int):
        """Update font size for all Postflop HS Editor components."""
        font_config = (THEME["font_family"], font_size)
        title_font = (THEME["font_family"], font_size + 6, "bold")
        header_font = (THEME["font_family"], font_size + 2, "bold")
        label_font = (THEME["font_family"], font_size + 1, "bold")
        desc_font = (THEME["font_family"], font_size)
        entry_font = (THEME["font_family"], font_size + 1)
        status_font = (THEME["font_family"], font_size + 1)

        # Update title font
        for widget in self.winfo_children():
            if isinstance(
                widget, ttk.Label
            ) and "Postflop Hand Strength Editor" in widget.cget("text"):
                widget.configure(font=title_font)
                break

        # Update all entry widgets and labels
        for key, widget_data in self.widgets.items():
            # Update entry font
            widget_data["entry"].configure(font=entry_font)

            # Find and update the name label (parent of entry)
            entry_parent = widget_data["entry"].master
            for child in entry_parent.winfo_children():
                if (
                    isinstance(child, ttk.Label)
                    and child.cget("text") == widget_data["name"]
                ):
                    child.configure(font=label_font)
                elif isinstance(child, ttk.Label) and child.cget("text").startswith(
                    "("
                ):
                    child.configure(font=desc_font)

        # Update header labels
        if hasattr(self, "header_labels"):
            header_font = (THEME["font_family"], font_size + 1, "bold")
            for header_label in self.header_labels:
                header_label.configure(font=header_font)

        # Update status label
        if hasattr(self, "status_label"):
            self.status_label.configure(font=status_font)

        print(f"DEBUG: Postflop HS Editor font size updated to {font_size}")

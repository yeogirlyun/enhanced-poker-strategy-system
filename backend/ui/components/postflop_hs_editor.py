#!/usr/bin/env python3
"""
Postflop Hand Strength Editor

Provides interface for editing postflop hand strength values.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Callable
from core.gui_models import StrategyData, THEME


class PostflopHSEditor:
    """
    Editor for postflop hand strength values.
    """

    def __init__(
        self,
        parent_frame,
        strategy_data: StrategyData,
        on_change: Optional[Callable] = None,
    ):
        self.parent = parent_frame
        self.strategy_data = strategy_data
        self.on_change = on_change
        self.current_font_size = 12


        self._setup_ui()
        self._load_current_values()

    def _setup_ui(self):
        """Sets up the postflop HS editor UI."""
        # Main frame
        self.main_frame = ttk.LabelFrame(
            self.parent, text="Postflop Hand Strength Editor", style="Dark.TLabelframe"
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create scrollable frame
        canvas = tk.Canvas(self.main_frame, bg=THEME["bg"])
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style="Dark.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create hand strength entries
        self._create_hand_strength_entries()

        # Button panel
        button_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            button_frame,
            text="Save Changes",
            command=self._save_changes,
            style="TopMenu.TButton",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame,
            text="Reset to Default",
            command=self._reset_to_default,
            style="TopMenu.TButton",
        ).pack(side=tk.LEFT, padx=5)

    def _create_hand_strength_entries(self):
        """Create entries for hand strength values."""
        # Hand strength categories
        categories = {
            "Made Hands": [
                "high_card", "pair", "top_pair", "over_pair", "two_pair",
                "set", "straight", "flush", "full_house", "quads", "straight_flush"
            ],
            "Draws": [
                "gutshot_draw", "open_ended_draw", "flush_draw", "combo_draw"
            ],
            "Special Situations": [
                "nut_flush_draw", "nut_straight_draw", "overcard_draw",
                "backdoor_flush", "backdoor_straight", "pair_plus_draw", "set_plus_draw"
            ]
        }

        self.hs_entries = {}

        for category, hands in categories.items():
            # Category label
            ttk.Label(
                self.scrollable_frame,
                text=category,
                style="Dark.TLabel",
                font=("Arial", 12, "bold")
            ).pack(anchor=tk.W, padx=10, pady=(10, 5))

            # Create frame for this category
            category_frame = ttk.Frame(self.scrollable_frame, style="Dark.TFrame")
            category_frame.pack(fill=tk.X, padx=10, pady=5)

            for i, hand in enumerate(hands):
                # Create row frame
                row_frame = ttk.Frame(category_frame, style="Dark.TFrame")
                row_frame.pack(fill=tk.X, pady=2)

                # Hand name label
                ttk.Label(
                    row_frame,
                    text=hand.replace("_", " ").title(),
                    style="Dark.TLabel",
                    width=20
                ).pack(side=tk.LEFT, padx=5)

                # Entry for HS value
                entry = ttk.Entry(row_frame, width=10, style="SkyBlue.TEntry")
                entry.pack(side=tk.LEFT, padx=5)
                self.hs_entries[hand] = entry

    def _load_current_values(self):
        """Load current hand strength values from strategy data."""
        postflop_hs = self.strategy_data.strategy_dict.get("hand_strength_tables", {}).get("postflop", {})
        
        for hand, entry in self.hs_entries.items():
            value = postflop_hs.get(hand, 0)
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

    def _save_changes(self):
        """Save changes to hand strength values."""
        try:
            # Get current postflop HS table
            postflop_hs = self.strategy_data.strategy_dict.get("hand_strength_tables", {}).get("postflop", {})
            
            # Update values from entries
            for hand, entry in self.hs_entries.items():
                value = int(entry.get())
                postflop_hs[hand] = value
            
            # Update strategy data
            if "hand_strength_tables" not in self.strategy_data.strategy_dict:
                self.strategy_data.strategy_dict["hand_strength_tables"] = {}
            self.strategy_data.strategy_dict["hand_strength_tables"]["postflop"] = postflop_hs
            
            messagebox.showinfo("Success", "Hand strength values saved successfully!")
            
            if self.on_change:
                self.on_change()
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {e}")

    def _reset_to_default(self):
        """Reset to default hand strength values."""
        if messagebox.askyesno("Reset", "Reset all hand strength values to defaults?"):
            # Default values
            defaults = {
                "high_card": 5, "pair": 15, "top_pair": 30, "over_pair": 35,
                "two_pair": 45, "set": 60, "straight": 70, "flush": 80,
                "full_house": 90, "quads": 100, "straight_flush": 120,
                "gutshot_draw": 12, "open_ended_draw": 18, "flush_draw": 20,
                "combo_draw": 35, "nut_flush_draw": 25, "nut_straight_draw": 22,
                "overcard_draw": 8, "backdoor_flush": 3, "backdoor_straight": 2,
                "pair_plus_draw": 28, "set_plus_draw": 65
            }
            
            for hand, entry in self.hs_entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, str(defaults.get(hand, 0)))

    def update_font_size(self, font_size: int):
        """Update font size for all widgets."""
        self.current_font_size = font_size
        # Update font sizes for labels and entries
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Label):
                widget.configure(font=("Arial", font_size))
            elif isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        child.configure(font=("Arial", font_size)) 
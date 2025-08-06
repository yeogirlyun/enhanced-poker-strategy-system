#!/usr/bin/env python3
"""
Decision Table Panel for Postflop Strategy Development

Provides visual editing of decision tables for flop, turn, and river.
Integrates with the existing Poker Strategy Development System.

REVISION HISTORY:
================
Version 1.0 (2025-07-29) - Initial Version
- Created decision table panel with matrix-based editing
- Supports flop, turn, and river decision tables
- Integrates with existing StrategyData model
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional, Callable
from core.gui_models import StrategyData, THEME


class DecisionTablePanel:
    """
    Panel for editing postflop decision tables with visual matrix interface.
    """

    def __init__(
        self,
        parent_frame,
        strategy_data: StrategyData,
        on_table_change: Optional[Callable] = None,
    ):
        self.parent = parent_frame
        self.strategy_data = strategy_data
        self.on_table_change = on_table_change
        self.current_street = "flop"  # Default street
        self.current_font_size = 12  # Default, will be set by update_font_size


        self._setup_ui()
        self._load_current_table()

    def _setup_ui(self):
        """Sets up the decision table UI."""
        # Main frame
        self.main_frame = ttk.LabelFrame(
            self.parent, text="Postflop Decision Tables", style="Dark.TLabelframe"
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Street tabs
        self.street_notebook = ttk.Notebook(self.main_frame)
        self.street_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs for each street
        self.street_frames = {}
        self.street_tables = {}

        for street in ["flop", "turn", "river"]:
            # Create frame for this street
            street_frame = ttk.Frame(self.street_notebook, style="Dark.TFrame")
            self.street_notebook.add(street_frame, text=street.title())
            self.street_frames[street] = street_frame

            # Create decision table for this street
            self._create_decision_table(street_frame, street)

        # Bind tab change event
        self.street_notebook.bind("<<NotebookTabChanged>>", self._on_street_tab_change)

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
        ttk.Button(
            button_frame,
            text="Export Table",
            command=self._export_table,
            style="TopMenu.TButton",
        ).pack(side=tk.LEFT, padx=5)

    def _get_positions(self):
        """Determine the list of positions dynamically from the strategy file or use a default."""
        # Try to get from num_players parameter
        num_players = self.strategy_data.strategy_dict.get("num_players", None)
        if num_players == 6:
            return ["UTG", "UTG+1", "MP", "HJ", "CO", "BTN"]
        elif num_players == 4:
            return ["UTG", "MP", "CO", "BTN"]
        # Try to get from postflop data keys
        postflop = self.strategy_data.strategy_dict.get("postflop", {})
        action_data = postflop.get("pfa", {})  # Use pfa as default
        street_data = action_data.get(self.current_street, {})
        if street_data:
            return list(street_data.keys())
        # Fallback default
        return ["UTG", "MP", "CO", "BTN"]

    def _create_decision_table(self, parent, street):
        """Creates the decision table matrix with all positions as columns and both action types as labeled frames."""
        self.table_container = ttk.Frame(parent, style="Dark.TFrame")
        self.table_container.pack(fill=tk.BOTH, expand=True)

        positions = self._get_positions()
        self.positions = positions
        parameters = ["val_thresh", "check_thresh", "sizing"]
        param_labels = ["Value Threshold", "Check Threshold", "Bet Sizing"]
        action_types = ["pfa", "caller"]
        action_labels = ["AS PFA", "AS CALLER"]
        font_config = (THEME["font_family"], self.current_font_size)
        header_font = (THEME["font_family"], self.current_font_size, "bold")

        # Header row
        ttk.Label(
            self.table_container,
            text="Action/Parameter",
            style="Dark.TLabel",
            font=header_font,
        ).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        for col, pos in enumerate(positions):
            ttk.Label(
                self.table_container,
                text=pos,
                style="Dark.TLabel",
                font=header_font,
            ).grid(row=0, column=col + 1, sticky="ew", padx=5, pady=5)

        # Entry fields for each action type, parameter and position
        if not hasattr(self, "parameter_widgets"):
            self.parameter_widgets = {}
        self.parameter_widgets[street] = {
            action: {param: {} for param in parameters} for action in action_types
        }
        current_row = 1

        for action_type, action_label in zip(action_types, action_labels):
            # Create a labeled frame for this action type
            action_frame = ttk.LabelFrame(
                self.table_container,
                text=action_label,
                style="Dark.TLabelframe",
                labelanchor="nw",
            )
            action_frame.grid(
                row=current_row,
                column=0,
                columnspan=len(positions) + 1,
                sticky="ew",
                padx=10,
                pady=10,
            )
            # Set the label font for the frame
            try:
                action_frame.option_add("*TLabelframe.Label.font", header_font)
            except Exception:
                pass

            # Parameter/entry grid inside the frame
            for row, (param, label) in enumerate(zip(parameters, param_labels)):
                ttk.Label(
                    action_frame,
                    text=label,
                    style="Dark.TLabel",
                    font=font_config,
                ).grid(row=row, column=0, sticky="ew", padx=5, pady=3)
                for col, pos in enumerate(positions):
                    value_var = tk.StringVar()
                    entry = ttk.Entry(
                        action_frame,
                        textvariable=value_var,
                        width=12,
                        style="SkyBlue.TEntry",
                        font=font_config,
                    )
                    entry.grid(row=row, column=col + 1, sticky="ew", padx=5, pady=3)
                    self.parameter_widgets[street][action_type][param][pos] = value_var
            current_row += 1

        self._load_current_table()

    def _load_current_table(self):
        """Loads the current decision table data for all positions and action types."""
        try:
            postflop_data = self.strategy_data.strategy_dict.get("postflop", {})

            for action_type in ["pfa", "caller"]:
                action_data = postflop_data.get(action_type, {})
                street_data = action_data.get(self.current_street, {})

                for pos in self.positions:
                    position_data = street_data.get(pos, {})

                    # Direct loading from PFA/Caller structure
                    for param in ["val_thresh", "check_thresh", "sizing"]:
                        value = position_data.get(param, "")
                        self.parameter_widgets[self.current_street][action_type][param][
                            pos
                        ].set(str(value))
        except Exception as e:
            # Set default values
            defaults = {"val_thresh": "35", "check_thresh": "15", "sizing": "0.75"}
            for action_type in ["pfa", "caller"]:
                for param in ["val_thresh", "check_thresh", "sizing"]:
                    for pos in self.positions:
                        self.parameter_widgets[self.current_street][action_type][param][
                            pos
                        ].set(defaults.get(param, "0"))

    def _on_street_tab_change(self, event=None):
        """Handles street tab change."""
        current_tab = self.street_notebook.select()
        tab_id = self.street_notebook.index(current_tab)
        streets = ["flop", "turn", "river"]
        self.current_street = streets[tab_id]
        self._load_current_table()

    def _save_changes(self):
        """Saves the current table changes to the strategy data for all positions and action types."""
        try:
            postflop = self.strategy_data.strategy_dict.setdefault("postflop", {})
            for action_type in ["pfa", "caller"]:
                action = postflop.setdefault(action_type, {})
                street = action.setdefault(self.current_street, {})
                for pos in self.positions:
                    new_values = {}
                    for param in ["val_thresh", "check_thresh", "sizing"]:
                        try:
                            value = float(
                                self.parameter_widgets[self.current_street][
                                    action_type
                                ][param][pos].get()
                            )
                            new_values[param] = value
                        except ValueError:
                            messagebox.showerror(
                                "Invalid Value",
                                f"Invalid value for {param} in {pos} ({action_type}): {self.parameter_widgets[self.current_street][action_type][param][pos].get()}",
                            )
                            return
                    if pos not in street:
                        street[pos] = {}
                    street[pos].update(new_values)
            if self.on_table_change:
                self.on_table_change()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")

    def _reset_to_default(self):
        """Resets the current table to default values."""
        if messagebox.askyesno(
            "Reset", "Are you sure you want to reset to default values?"
        ):
            defaults = {
                "flop": {"val_thresh": "35", "check_thresh": "15", "sizing": "0.75"},
                "turn": {"val_thresh": "40", "check_thresh": "20", "sizing": "0.8"},
                "river": {"val_thresh": "45", "check_thresh": "25", "sizing": "1.0"},
            }

            current_defaults = defaults.get(
                self.current_street,
                {"val_thresh": "30", "check_thresh": "15", "sizing": "0.75"},
            )

            for action_type in ["pfa", "caller"]:
                for param in ["val_thresh", "check_thresh", "sizing"]:
                    for pos in self.positions:
                        self.parameter_widgets[self.current_street][action_type][param][
                            pos
                        ].set(current_defaults.get(param, "0"))

    def _export_table(self):
        """Exports the current table data."""
        try:
            data = {}
            for action_type in ["pfa", "caller"]:
                for param in ["val_thresh", "check_thresh", "sizing"]:
                    for pos in self.positions:
                        data[f"{action_type}_{param}_{pos}"] = float(
                            self.parameter_widgets[self.current_street][action_type][
                                param
                            ][pos].get()
                        )

            # Create export string
            export_text = f"Decision Table Export\n"
            export_text += f"Street: {self.current_street}\n"
            export_text += f"Action Types: PFA, Caller\n\n"
            export_text += f"Parameters:\n"
            for key, value in data.items():
                export_text += f"  {key}: {value}\n"

            # Show in dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title("Export Decision Table")
            dialog.geometry("400x300")
            dialog.configure(bg=THEME["bg"])

            text_widget = tk.Text(dialog, bg=THEME["bg_dark"], fg=THEME["fg"])
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, export_text)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export table: {e}")

    def update_font_size(self, font_size: int):
        """Updates font size for all components."""
        self.current_font_size = font_size
        font_config = (THEME["font_family"], font_size)
        header_font = (THEME["font_family"], font_size, "bold")

        def recursive_update(widget):
            # Update font for labels, entries, and label frames
            if isinstance(widget, ttk.LabelFrame):
                try:
                    widget.option_add("*TLabelframe.Label.font", header_font)
                    widget.configure(labelanchor="nw")
                except Exception:
                    pass
            if isinstance(widget, ttk.Label):
                try:
                    widget.configure(font=font_config)
                except Exception:
                    pass
            if isinstance(widget, ttk.Entry):
                try:
                    widget.configure(font=font_config)
                except Exception:
                    pass
            for child in widget.winfo_children():
                recursive_update(child)

        recursive_update(self.main_frame)

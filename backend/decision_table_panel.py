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
from typing import Optional, Callable
from gui_models import StrategyData, THEME


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
        self.current_street = "preflop"  # Default street
        self.current_font_size = 14  # Default, will be set by update_font_size

        # DecisionTablePanel initialized

        self._setup_ui()
        # Don't load data here - will be loaded when tabs are first accessed

    def _setup_ui(self):
        """Sets up the decision table UI."""
        # Main frame
        self.main_frame = ttk.LabelFrame(
            self.parent, text="Decision Tables", style="Dark.TLabelframe"
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Street tabs
        self.street_notebook = ttk.Notebook(self.main_frame)
        self.street_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs for each street (including preflop)
        self.street_frames = {}
        self.street_tables = {}
        self.street_loaded = {
            "preflop": False,
            "flop": False,
            "turn": False,
            "river": False,
        }

        for street in ["preflop", "flop", "turn", "river"]:
            # Create frame for this street
            street_frame = ttk.Frame(self.street_notebook, style="Dark.TFrame")
            self.street_notebook.add(street_frame, text=street.title())
            self.street_frames[street] = street_frame

            # Create decision table for this street (but don't load data yet)
            self._create_decision_table(street_frame, street)

            # Set initial street
        self.current_street = "preflop"

        # Bind tab change event
        self.street_notebook.bind("<<NotebookTabChanged>>", self._on_street_tab_change)

        # Load ALL decision table data at startup for instant tab switching
        self._load_all_decision_tables()

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

    def _get_positions(self, street=None):
        """Determine the list of positions dynamically from the strategy file or use a default."""
        # Use provided street or current_street
        target_street = street or getattr(self, "current_street", "flop")

        # For preflop, get positions from preflop data
        if target_street == "preflop":
            preflop = self.strategy_data.strategy_dict.get("preflop", {})
            open_rules = preflop.get("open_rules", {})
            if open_rules:
                return list(open_rules.keys())
            # Fallback for preflop
            return ["UTG", "MP", "CO", "BTN", "SB"]

        # For postflop streets, get from postflop data
        postflop = self.strategy_data.strategy_dict.get("postflop", {})
        action_data = postflop.get("pfa", {})
        street_data = action_data.get(target_street, {})

        if street_data:
            return list(street_data.keys())

        # Fallback default
        return ["UTG", "MP", "CO", "BTN"]

    def _create_decision_table(self, parent, street):
        """Creates the decision table matrix with all positions as columns and both
        action types as labeled frames."""
        # Create separate container for each street
        if not hasattr(self, "table_containers"):
            self.table_containers = {}

        self.table_containers[street] = ttk.Frame(parent, style="Dark.TFrame")
        self.table_containers[street].pack(fill=tk.BOTH, expand=True)

        positions = self._get_positions(street)
        self.positions = positions

        # Set parameters based on street
        if street == "preflop":
            parameters = ["val_thresh", "sizing"]
            param_labels = ["Open Threshold", "Bet Sizing"]
            action_types = ["pfa"]
            action_labels = ["OPENING RANGES"]
        else:
            parameters = ["val_thresh", "check_thresh", "sizing"]
            param_labels = ["Value Threshold", "Check Threshold", "Bet Sizing"]
            action_types = ["pfa", "caller"]
            action_labels = ["AS PFA", "AS CALLER"]

        font_config = (THEME["font_family"], self.current_font_size)
        header_font = (THEME["font_family"], self.current_font_size, "bold")

        # Header row
        ttk.Label(
            self.table_containers[street],
            text="Action/Parameter",
            style="Dark.TLabel",
            font=header_font,
        ).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        for col, pos in enumerate(positions):
            ttk.Label(
                self.table_containers[street],
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
                self.table_containers[street],
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
                        style="SkyBlue.TEntry",
                        font=font_config,
                        width=8,
                    )
                    entry.grid(row=row, column=col + 1, sticky="ew", padx=2, pady=2)
                    self.parameter_widgets[street][action_type][param][pos] = value_var

            current_row += 2  # Add space between action types

        # All data will be loaded at startup

    def _load_all_decision_tables(self):
        """Load all decision table data for all streets at startup."""
        try:
            postflop_data = self.strategy_data.strategy_dict.get("postflop", {})
            preflop_data = self.strategy_data.strategy_dict.get("preflop", {})

            # Load data for all streets
            for street in ["preflop", "flop", "turn", "river"]:
                # Set positions for this street
                self.positions = self._get_positions(street)

                if street == "preflop":
                    # Handle preflop data structure
                    open_rules = preflop_data.get("open_rules", {})
                    for pos in self.positions:
                        position_data = open_rules.get(pos, {})

                        # Load preflop data into widgets (threshold and sizing)
                        threshold = position_data.get("threshold", "")
                        sizing = position_data.get("sizing", "")

                        # Map to decision table parameters
                        self.parameter_widgets[street]["pfa"]["val_thresh"][pos].set(
                            str(threshold)
                        )
                        self.parameter_widgets[street]["pfa"]["sizing"][pos].set(
                            str(sizing)
                        )

                        # Preflop doesn't have caller or check_thresh
                else:
                    # Handle postflop data structure
                    for action_type in ["pfa", "caller"]:
                        action_data = postflop_data.get(action_type, {})
                        street_data = action_data.get(street, {})

                        for pos in self.positions:
                            position_data = street_data.get(pos, {})

                            # Load data into widgets
                            for param in ["val_thresh", "check_thresh", "sizing"]:
                                value = position_data.get(param, "")
                                self.parameter_widgets[street][action_type][param][
                                    pos
                                ].set(str(value))

                # Mark this street as loaded
                self.street_loaded[street] = True

        except Exception as e:
            print(f"ERROR: Failed to load all decision tables: {e}")
            import traceback

            traceback.print_exc()

    def _load_current_table(self):
        """Loads the current decision table data for all positions and action types."""
        try:
            if self.current_street == "preflop":
                # Handle preflop data structure
                preflop_data = self.strategy_data.strategy_dict.get("preflop", {})
                open_rules = preflop_data.get("open_rules", {})

                for pos in self.positions:
                    position_data = open_rules.get(pos, {})

                    # Load preflop data
                    threshold = position_data.get("threshold", "")
                    sizing = position_data.get("sizing", "")

                    self.parameter_widgets[self.current_street]["pfa"]["val_thresh"][
                        pos
                    ].set(str(threshold))
                    self.parameter_widgets[self.current_street]["pfa"]["sizing"][
                        pos
                    ].set(str(sizing))
                    # Preflop doesn't have check_thresh
            else:
                # Handle postflop data structure
                postflop_data = self.strategy_data.strategy_dict.get("postflop", {})

                for action_type in ["pfa", "caller"]:
                    action_data = postflop_data.get(action_type, {})
                    street_data = action_data.get(self.current_street, {})

                    for pos in self.positions:
                        position_data = street_data.get(pos, {})

                        # Direct loading from PFA/Caller structure
                        for param in ["val_thresh", "check_thresh", "sizing"]:
                            value = position_data.get(param, "")
                            self.parameter_widgets[self.current_street][action_type][
                                param
                            ][pos].set(str(value))
        except Exception as e:
            print(f"ERROR: Failed to load decision table: {e}")
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
        streets = ["preflop", "flop", "turn", "river"]
        self.current_street = streets[tab_id]

        # All data is already loaded and all tables are pre-rendered
        # No additional operations needed - just update current street
        self.positions = self._get_positions(self.current_street)

    def _save_changes(self):
        """Saves the current table changes to the strategy data for all positions and action types."""
        try:
            postflop = self.strategy_data.strategy_dict.setdefault("postflop", {})
            preflop = self.strategy_data.strategy_dict.setdefault("preflop", {})

            # Save data for ALL streets, not just current street
            for street in ["preflop", "flop", "turn", "river"]:
                # Get positions for this street
                positions = self._get_positions(street)

                if street == "preflop":
                    # Handle preflop data structure
                    open_rules = preflop.setdefault("open_rules", {})

                    for pos in positions:
                        try:
                            threshold = float(
                                self.parameter_widgets[street]["pfa"]["val_thresh"][
                                    pos
                                ].get()
                            )
                            sizing = float(
                                self.parameter_widgets[street]["pfa"]["sizing"][
                                    pos
                                ].get()
                            )

                            open_rules[pos] = {"threshold": threshold, "sizing": sizing}
                        except ValueError:
                            print(f"Invalid preflop data for {pos}")
                else:
                    # Handle postflop data structure
                    for action_type in ["pfa", "caller"]:
                        action = postflop.setdefault(action_type, {})
                        street_data = action.setdefault(street, {})

                        for pos in positions:
                            new_values = {}
                            for param in ["val_thresh", "check_thresh", "sizing"]:
                                try:
                                    value = float(
                                        self.parameter_widgets[street][action_type][
                                            param
                                        ][pos].get()
                                    )
                                    new_values[param] = value
                                except ValueError:
                                    print(f"Invalid {param} for {pos} in {street}")
                                    continue

                            street_data[pos] = new_values

            # Notify parent of changes
            if self.on_table_change:
                self.on_table_change()

            messagebox.showinfo("Success", "Decision table changes saved!")

        except Exception as e:
            print(f"ERROR: Failed to save decision table: {e}")
            messagebox.showerror("Error", f"Failed to save changes: {e}")

    def _reset_to_default(self):
        """Resets the current table to default values."""
        if messagebox.askyesno(
            "Reset", "Are you sure you want to reset to default values?"
        ):
            defaults = {
                "preflop": {"val_thresh": "35", "check_thresh": "15", "sizing": "0.75"},
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

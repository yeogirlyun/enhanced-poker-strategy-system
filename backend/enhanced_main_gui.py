#!/usr/bin/env python3
"""
Enhanced Main GUI for Poker Strategy Development with Decision Tables

Extends the main GUI to include decision table editing for postflop strategies.

REVISION HISTORY:
===============
Version 1.0 (2025-07-29) - Initial Version
- Created enhanced main GUI with decision table integration
- Added tabbed interface for different strategy components
- Integrated decision table panel with existing components
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from gui_models import StrategyData, THEME, GridSettings
from hand_grid import HandGridWidget
from tier_panel import TierPanel
from decision_table_panel import DecisionTablePanel


class EnhancedMainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Poker Strategy Development System")

        # Set window size to 50% of screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.5)
        window_height = int(screen_height * 0.5)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Initialize strategy data
        self.strategy_data = StrategyData()

        # Try to load modern_strategy.json by default
        if os.path.exists("modern_strategy.json"):
            self.strategy_data.load_strategy_from_file("modern_strategy.json")
        else:
            # Fallback to default tiers
            self.strategy_data.load_default_tiers()

        self._setup_styles()
        self._create_menu()
        self._create_widgets()
        self._apply_initial_font_size()

    def _setup_styles(self):
        """Setup custom styles for the application."""
        style = ttk.Style()

        # Configure notebook style
        style.configure("TNotebook", background=THEME["bg"])
        style.configure(
            "TNotebook.Tab",
            background=THEME["bg_light"],
            foreground=THEME["fg"],
            padding=[10, 5],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", THEME["accent"]), ("active", THEME["bg_dark"])],
        )

        # Configure entry style
        style.configure(
            "SkyBlue.TEntry",
            fieldbackground="#87CEEB",
            foreground="#000000",
            borderwidth=2,
            relief="solid",
        )

        # Configure combobox style
        style.configure(
            "SkyBlue.TCombobox",
            fieldbackground="#87CEEB",
            foreground="#000000",
            background="#87CEEB",
            arrowcolor="#000000",
        )

        # Configure label frame style
        style.configure(
            "Dark.TLabelframe", background=THEME["bg"], foreground=THEME["fg"]
        )
        style.configure(
            "Dark.TLabelframe.Label", background=THEME["bg"], foreground=THEME["fg"]
        )

        # Configure label style
        style.configure("Dark.TLabel", background=THEME["bg"], foreground=THEME["fg"])

    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Strategy", command=self._new_strategy)
        file_menu.add_command(label="Load Strategy...", command=self._load_strategy)
        file_menu.add_separator()
        file_menu.add_command(label="Save Strategy", command=self._save_strategy)
        file_menu.add_command(
            label="Save Strategy As...", command=self._save_strategy_as
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Generate Default Strategy", command=self._generate_default_strategy
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _new_strategy(self):
        """Create a new strategy with default tiers."""
        if messagebox.askyesno(
            "New Strategy",
            "Create a new strategy with default hand strength tiers?\n\nThis will clear the current strategy.",
        ):
            self.strategy_data.load_default_tiers()
            self.strategy_data.current_strategy_file = None
            self._refresh_all_panels()
            messagebox.showinfo(
                "New Strategy", "Created new strategy with default tiers."
            )

    def _load_strategy(self):
        """Load a strategy from file."""
        filename = filedialog.askopenfilename(
            title="Load Strategy File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=".",
        )
        if filename:
            if self.strategy_data.load_strategy_from_file(filename):
                self._refresh_all_panels()
                messagebox.showinfo(
                    "Load Strategy", f"Successfully loaded strategy from '{filename}'"
                )
            else:
                messagebox.showerror(
                    "Load Strategy", f"Failed to load strategy from '{filename}'"
                )

    def _save_strategy(self):
        """Save the current strategy."""
        if self.strategy_data.current_strategy_file:
            if self.strategy_data.save_strategy_to_file(
                self.strategy_data.current_strategy_file
            ):
                messagebox.showinfo(
                    "Save Strategy",
                    f"Strategy saved to '{self.strategy_data.current_strategy_file}'",
                )
            else:
                messagebox.showerror(
                    "Save Strategy",
                    f"Failed to save strategy to '{self.strategy_data.current_strategy_file}'",
                )
        else:
            self._save_strategy_as()

    def _save_strategy_as(self):
        """Save the current strategy with a new filename."""
        filename = filedialog.asksaveasfilename(
            title="Save Strategy As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=".",
        )
        if filename:
            if self.strategy_data.save_strategy_to_file(filename):
                messagebox.showinfo("Save Strategy", f"Strategy saved to '{filename}'")
            else:
                messagebox.showerror(
                    "Save Strategy", f"Failed to save strategy to '{filename}'"
                )

    def _generate_default_strategy(self):
        """Generate a default strategy with modern PFA/Caller theory."""
        if messagebox.askyesno(
            "Generate Default Strategy",
            "Generate a new default strategy with modern PFA/Caller postflop theory?\n\n"
            "This will create a strategy with:\n"
            "• Modern hand strength tiers\n"
            "• PFA/Caller postflop decision tables\n"
            "• Position-based adjustments\n"
            "• Modern poker theory values",
        ):

            # Create new strategy with modern theory
            self.strategy_data.load_default_tiers()
            self.strategy_data.strategy_dict = (
                self.strategy_data._create_strategy_from_tiers()
            )
            self.strategy_data.current_strategy_file = None

            self._refresh_all_panels()
            messagebox.showinfo(
                "Default Strategy",
                "Generated new default strategy with modern PFA/Caller theory.\n\n"
                "Use 'Save Strategy As...' to save it to a file.",
            )

    def _show_about(self):
        """Show about dialog."""
        about_text = """Poker Strategy Development System

A comprehensive GUI for developing and editing poker strategies.

Features:
• Hand Strength Grid with tier management
• Postflop Decision Tables (PFA/Caller)
• Modern poker theory integration
• Strategy file management

Version: 2.0
Built with Python and Tkinter"""
        messagebox.showinfo("About", about_text)

    def _refresh_all_panels(self):
        """Refresh all panels with current strategy data."""
        # Refresh hand grid by re-rendering
        if hasattr(self, "hand_grid"):
            self.hand_grid._render_grid()
        # Refresh tier panel
        if hasattr(self, "tier_panel"):
            self.tier_panel._update_tier_list()
            self.tier_panel._update_counts()
        # Refresh decision table panel
        if hasattr(self, "decision_table_panel"):
            self.decision_table_panel._load_current_table()
        # Refresh overview
        if hasattr(self, "overview_text"):
            self._update_overview()

    def _create_widgets(self):
        """Create the main widgets."""
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Top frame with controls (5% height)
        self.top_frame = ttk.Frame(self.root, style="Dark.TFrame")
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Add outer border frame for stylish appearance
        outer_frame = ttk.Frame(self.top_frame, style="Dark.TFrame")
        outer_frame.pack(fill="x", padx=2, pady=2)

        # Font size control
        ttk.Label(outer_frame, text="Font Size:", style="Dark.TLabel").pack(
            side="left", padx=5
        )
        self.font_sizes = ["1", "2", "3", "4", "5", "6", "7", "8"]
        self.current_font_size_index = 3  # Start with size "4" (12pt)
        self.font_size_var = tk.StringVar(
            value=self.font_sizes[self.current_font_size_index]
        )
        font_size_combo = ttk.Combobox(
            outer_frame,
            textvariable=self.font_size_var,
            values=self.font_sizes,
            width=5,
            style="SkyBlue.TCombobox",
        )
        font_size_combo.pack(side="left", padx=5)
        font_size_combo.bind("<<ComboboxSelected>>", self._on_font_size_change)

        # Grid size control
        ttk.Label(outer_frame, text="Grid Size:", style="Dark.TLabel").pack(
            side="left", padx=5
        )
        self.grid_size_var = tk.StringVar(value="7")  # Default to size "7"
        grid_size_combo = ttk.Combobox(
            outer_frame,
            textvariable=self.grid_size_var,
            values=["1", "2", "3", "4", "5", "6", "7", "8"],
            width=5,
            style="SkyBlue.TCombobox",
        )
        grid_size_combo.pack(side="left", padx=5)
        grid_size_combo.bind("<<ComboboxSelected>>", self._on_grid_size_change)

        # Main notebook (95% height)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Tab 1: Hand Grid & Tiers
        self.hand_tier_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hand_tier_frame, text="Hand Grid & Tiers")

        # Configure grid tab layout - grid on left (60%), tier panel on right (40%)
        self.hand_tier_frame.grid_rowconfigure(0, weight=1)
        self.hand_tier_frame.grid_columnconfigure(0, weight=60)  # Grid area: 60%
        self.hand_tier_frame.grid_columnconfigure(1, weight=40)  # Tier area: 40%

        # Hand grid in left panel
        grid_frame = ttk.Frame(self.hand_tier_frame, style="Dark.TFrame")
        grid_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

        self.hand_grid = HandGridWidget(grid_frame, self.strategy_data)

        # Tier panel in right panel
        tier_panel_frame = ttk.Frame(self.hand_tier_frame, style="Dark.TFrame")
        tier_panel_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)

        self.tier_panel = TierPanel(
            tier_panel_frame,
            self.strategy_data,
            on_tier_change=self._on_tier_data_change,
            on_tier_select=self._on_tier_select,
        )

        # Tab 2: Decision Tables
        self.decision_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.decision_frame, text="Decision Tables")

        # Create decision table panel
        self.decision_table_panel = DecisionTablePanel(
            self.decision_frame, self.strategy_data
        )

        # Tab 3: Strategy Overview
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Strategy Overview")

        # Create overview text area
        self.overview_text = tk.Text(
            self.overview_frame,
            bg=THEME["bg"],
            fg=THEME["fg"],
            font=(THEME["font_family"], THEME["font_size"]),
            wrap="word",
            padx=10,
            pady=10,
        )
        self.overview_text.pack(fill="both", expand=True)

        # Initial overview update
        self._update_overview()

    def _update_overview(self):
        """Update the strategy overview text."""
        self.overview_text.delete(1.0, tk.END)

        overview = f"""STRATEGY OVERVIEW
{'='*50}

Current Strategy File: {self.strategy_data.current_strategy_file or 'None (New Strategy)'}

HAND STRENGTH TIERS:
{'-'*30}"""

        for tier in self.strategy_data.tiers:
            overview += f"\n{tier.name} (HS {tier.min_hs}-{tier.max_hs}): {len(tier.hands)} hands"
            if tier.hands:
                overview += f" - {', '.join(tier.hands[:5])}"
                if len(tier.hands) > 5:
                    overview += f" ... (+{len(tier.hands)-5} more)"

        overview += f"""

POSTFLOP STRATEGY:
{'-'*30}
Strategy Type: PFA/Caller (Modern Theory)

PFA (Position of Final Action - Aggressor):
• More aggressive betting
• Lower thresholds
• Smaller sizing

Caller (Passive Player):
• More defensive play
• Higher thresholds
• Larger sizing

POSITIONS SUPPORTED:
{'-'*30}"""

        # Get positions from strategy
        postflop_data = self.strategy_data.strategy_dict.get("postflop", {})
        pfa_data = postflop_data.get("pfa", {})
        if pfa_data:
            flop_data = pfa_data.get("flop", {})
            positions = list(flop_data.keys())
            overview += f"\n{', '.join(positions)}"

        overview += f"""

STREETS SUPPORTED:
{'-'*30}
Flop, Turn, River

TOTAL HANDS: {sum(len(tier.hands) for tier in self.strategy_data.tiers)}
TOTAL TIERS: {len(self.strategy_data.tiers)}

{'='*50}
Use the tabs above to edit different aspects of your strategy.
Use File menu to save/load strategies."""

        self.overview_text.insert(1.0, overview)

    def _on_font_size_change(self, event=None):
        """Handle font size change."""
        try:
            new_size_str = self.font_size_var.get()
            self.current_font_size_index = self.font_sizes.index(new_size_str)
            self._update_font_size()
        except (ValueError, IndexError):
            pass

    def _on_grid_size_change(self, event=None):
        """Handle grid size change."""
        try:
            new_size = self.grid_size_var.get()
            # Convert size string to 0-based index
            size_index = int(new_size) - 1
            print(f"DEBUG: Changing grid size to '{new_size}' (index: {size_index})")

            # Update grid size
            self.hand_grid.grid_size_index = size_index
            self.hand_grid._grid_state["grid_size"] = size_index
            self.hand_grid._render_grid()

            print(f"DEBUG: Grid size changed to '{new_size}'")
        except Exception as e:
            print(f"Error updating grid size: {e}")

    def _update_font_size(self):
        """Update font size across all components."""
        new_size = self.font_sizes[self.current_font_size_index]
        current_font_size = GridSettings.get_size_config(new_size)["font"][1]

        print(
            f"DEBUG: Changing font size to '{new_size}' (index: {self.current_font_size_index})"
        )

        # Update overview text
        self.overview_text.configure(font=(THEME["font_family"], current_font_size))

        # Update decision table panel
        if hasattr(self, "decision_table_panel"):
            self.decision_table_panel.update_font_size(current_font_size)

        # Update tier panel
        if hasattr(self, "tier_panel"):
            self.tier_panel.update_font_size(current_font_size)

        # Update hand grid size to match app font size
        if hasattr(self, "hand_grid"):
            self.hand_grid.grid_size_index = self.current_font_size_index
            self.hand_grid._render_grid()

        print(f"DEBUG: Font size changed to '{new_size}'")

    def _on_tier_data_change(self):
        """Handle tier data changes."""
        print(f"DEBUG: Tier data changed")
        # Update hand colors if no specific tier is selected
        if (
            hasattr(self.hand_grid, "_current_tier_selection")
            and self.hand_grid._current_tier_selection is None
        ):
            self.hand_grid.update_hand_colors()
        # Update overview
        self._update_overview()

    def _on_tier_select(self, selected_tiers):
        """Handle tier selection changes."""
        print(f"DEBUG: Tier selection changed - {len(selected_tiers)} tiers selected")
        self.hand_grid.highlight_tiers(selected_tiers)

    def _apply_initial_font_size(self):
        """Apply initial font size."""
        self._update_font_size()

    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = EnhancedMainGUI()
    app.run()

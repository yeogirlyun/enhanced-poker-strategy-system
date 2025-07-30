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
from datetime import datetime
from gui_models import StrategyData, THEME, GridSettings
from hand_grid import HandGridWidget
from tier_panel import TierPanel
from decision_table_panel import DecisionTablePanel
from postflop_hs_editor import PostflopHSEditor


class EnhancedMainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Poker Strategy Development System")

        # Set window size to 60% of screen and center it
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.60)
        window_height = int(screen_height * 0.60)
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

        # Strategy menu
        strategy_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Strategy", menu=strategy_menu)
        strategy_menu.add_command(
            label="Reset to Default", command=self._reset_to_default
        )
        strategy_menu.add_command(
            label="Clear All Changes", command=self._clear_all_changes
        )
        strategy_menu.add_separator()
        strategy_menu.add_command(
            label="Reload Current Strategy", command=self._reload_current_strategy
        )

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
            self._update_strategy_file_display()
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
                self._update_strategy_file_display()
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
                self._update_strategy_file_display()
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

    def _reset_to_default(self):
        """Reset to the original default strategy."""
        if messagebox.askyesno(
            "Reset to Default",
            "Reset to the original default strategy?\n\n"
            "This will:\n"
            "• Load the original default tiers\n"
            "• Clear all custom HS scores\n"
            "• Reset all decision table values\n"
            "• Clear any unsaved changes",
        ):
            # Load default tiers (original, not modern)
            self.strategy_data.load_default_tiers()
            self.strategy_data.current_strategy_file = None

            # Clear any custom HS scores and decision tables
            if "hand_strength_tables" in self.strategy_data.strategy_dict:
                del self.strategy_data.strategy_dict["hand_strength_tables"]
            if "postflop" in self.strategy_data.strategy_dict:
                del self.strategy_data.strategy_dict["postflop"]

            self._refresh_all_panels()
            self._update_strategy_file_display()
            messagebox.showinfo(
                "Reset Complete", "Strategy reset to original default values."
            )

    def _clear_all_changes(self):
        """Clear all unsaved changes and reload the current strategy."""
        if not self.strategy_data.current_strategy_file:
            messagebox.showinfo(
                "No File",
                "No strategy file is currently loaded.\n"
                "Use 'Load Strategy...' to load a file first.",
            )
            return

        if messagebox.askyesno(
            "Clear All Changes",
            f"Discard all unsaved changes and reload '{self.strategy_data.current_strategy_file}'?\n\n"
            "This will restore the strategy to its last saved state.",
        ):
            # Reload the current file
            if self.strategy_data.load_strategy_from_file(
                self.strategy_data.current_strategy_file
            ):
                self._refresh_all_panels()
                messagebox.showinfo(
                    "Changes Cleared",
                    f"Reloaded '{self.strategy_data.current_strategy_file}' with last saved state.",
                )
            else:
                messagebox.showerror(
                    "Error",
                    f"Failed to reload '{self.strategy_data.current_strategy_file}'",
                )

    def _reload_current_strategy(self):
        """Reload the current strategy file."""
        if not self.strategy_data.current_strategy_file:
            messagebox.showinfo(
                "No File",
                "No strategy file is currently loaded.\n"
                "Use 'Load Strategy...' to load a file first.",
            )
            return

        if messagebox.askyesno(
            "Reload Strategy",
            f"Reload '{self.strategy_data.current_strategy_file}'?\n\n"
            "This will discard any unsaved changes.",
        ):
            if self.strategy_data.load_strategy_from_file(
                self.strategy_data.current_strategy_file
            ):
                self._refresh_all_panels()
                messagebox.showinfo(
                    "Reload Complete",
                    f"Successfully reloaded '{self.strategy_data.current_strategy_file}'",
                )
            else:
                messagebox.showerror(
                    "Error",
                    f"Failed to reload '{self.strategy_data.current_strategy_file}'",
                )

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
        # Update strategy file display
        self._update_strategy_file_display()
    
    def _update_strategy_file_display(self):
        """Update the strategy file display in the top bar."""
        if hasattr(self, "strategy_file_label"):
            if self.strategy_data.current_strategy_file:
                # Show just the filename, not the full path
                filename = os.path.basename(self.strategy_data.current_strategy_file)
                self.strategy_file_label.config(text=filename)
            else:
                self.strategy_file_label.config(text="Default Strategy")

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
        self.current_font_size_index = 1  # Start with size "2" (12pt) - was size "4"
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

        # Strategy file display
        ttk.Label(outer_frame, text="Strategy:", style="Dark.TLabel").pack(
            side="left", padx=(20, 5)
        )
        self.strategy_file_label = ttk.Label(
            outer_frame, 
            text="No file loaded", 
            style="Dark.TLabel",
            foreground=THEME["accent"]
        )
        self.strategy_file_label.pack(side="left", padx=5)
        
        # Update the file display
        self._update_strategy_file_display()
        
        # Apply initial font size to strategy file label
        if hasattr(self, "strategy_file_label"):
            initial_font_size = GridSettings.get_size_config("2")["font"][1]  # Was "4"
            self.strategy_file_label.configure(
                font=(THEME["font_family"], initial_font_size)
            )

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

        # Tier panel in right panel (create first so hand grid can reference it)
        tier_panel_frame = ttk.Frame(self.hand_tier_frame, style="Dark.TFrame")
        tier_panel_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)

        self.tier_panel = TierPanel(
            tier_panel_frame,
            self.strategy_data,
            on_tier_change=self._on_tier_data_change,
            on_tier_select=self._on_tier_select,
        )

        # Hand grid in left panel
        grid_frame = ttk.Frame(self.hand_tier_frame, style="Dark.TFrame")
        grid_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

        self.hand_grid = HandGridWidget(
            grid_frame, self.strategy_data, tier_panel=self.tier_panel
        )

        # Tab 2: Postflop HS Editor
        self.postflop_hs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.postflop_hs_frame, text="Postflop HS Editor")

        # Create postflop HS editor
        self.postflop_hs_editor = PostflopHSEditor(
            self.postflop_hs_frame, self.strategy_data
        )
        self.postflop_hs_editor.pack(fill=tk.BOTH, expand=True)

        # Tab 3: Decision Tables
        self.decision_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.decision_frame, text="Decision Tables")

        # Create decision table panel
        self.decision_table_panel = DecisionTablePanel(
            self.decision_frame, self.strategy_data
        )

        # Tab 4: Strategy Overview
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Strategy Overview")

        # Create a frame for buttons
        overview_button_frame = ttk.Frame(self.overview_frame)
        overview_button_frame.pack(fill=tk.X, padx=10, pady=5)

        # Export to PDF button
        self.export_pdf_button = ttk.Button(
            overview_button_frame,
            text="Export to PDF",
            command=self._export_strategy_to_pdf,
            style="Accent.TButton",
        )
        self.export_pdf_button.pack(side=tk.RIGHT, padx=5)

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

POSTFLOP HAND STRENGTH SCORES:
{'-'*30}"""

        # Get HS scores (preflop and postflop)
        hand_strength_tables = self.strategy_data.strategy_dict.get(
            "hand_strength_tables", {}
        )
        preflop_hs_table = hand_strength_tables.get("preflop", {})
        postflop_hs_table = hand_strength_tables.get("postflop", {})

        if preflop_hs_table:
            overview += f"\nPreflop hands: {len(preflop_hs_table)}"
            overview += f"\nPreflop score range: {min(preflop_hs_table.values())}-{max(preflop_hs_table.values())}"
        else:
            overview += f"\nNo preflop HS scores defined"

        if postflop_hs_table:
            overview += f"\nPostflop hand types: {len(postflop_hs_table)}"
            overview += f"\nPostflop score range: {min(postflop_hs_table.values())}-{max(postflop_hs_table.values())}"

            # Show some key hand types
            key_hands = [
                "high_card",
                "pair",
                "top_pair",
                "flush",
                "straight",
                "flush_draw",
            ]
            overview += f"\nKey postflop hand types:"
            for hand in key_hands:
                if hand in postflop_hs_table:
                    overview += f"\n  {hand.replace('_', ' ').title()}: {postflop_hs_table[hand]}"
        else:
            overview += f"\nNo postflop HS scores defined"

        overview += f"""

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
Use File menu to save/load strategies.
Click "Export to PDF" button above to generate a comprehensive strategy report."""

        self.overview_text.insert(1.0, overview)

    def _export_strategy_to_pdf(self):
        """Export the current strategy to a comprehensive PDF report."""
        try:
            from pdf_export import export_strategy_to_pdf
            import tkinter.filedialog as filedialog

            # Get save file path
            filename = filedialog.asksaveasfilename(
                title="Export Strategy to PDF",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"poker_strategy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            )

            if filename:
                # Export to PDF
                success = export_strategy_to_pdf(self.strategy_data, filename)

                if success:
                    messagebox.showinfo(
                        "Export Successful",
                        f"Strategy report exported successfully to:\n{filename}",
                    )
                else:
                    messagebox.showerror(
                        "Export Failed",
                        "Failed to create PDF report. Please check the console for details.",
                    )

        except ImportError:
            messagebox.showerror(
                "Missing Dependency",
                "PDF export requires the 'reportlab' library.\n"
                "Please install it with: pip install reportlab",
            )
        except Exception as e:
            messagebox.showerror(
                "Export Error", f"An error occurred during export:\n{str(e)}"
            )

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

        # Update postflop HS editor
        if hasattr(self, "postflop_hs_editor"):
            self.postflop_hs_editor.update_font_size(current_font_size)

        # Update strategy file label
        if hasattr(self, "strategy_file_label"):
            self.strategy_file_label.configure(
                font=(THEME["font_family"], current_font_size)
            )

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

#!/usr/bin/env python3
"""
Enhanced Main GUI V2 for Poker Strategy Development with Status Bar

Extends the main GUI to include status bar functionality and enhanced UI features.

REVISION HISTORY:
===============
Version 2.0 (2025-07-29) - Status Bar Integration
- Added status bar with message display and auto-clear functionality
- Enhanced UI with professional theme integration
- Improved user feedback and system status display
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Dict
from datetime import datetime

from gui_models import StrategyData, THEME, FONTS, GridSettings
from hand_grid import HandGridWidget
from tier_panel import TierPanel
from decision_table_panel import DecisionTablePanel
from postflop_hs_editor import PostflopHSEditor
from strategy_optimization_panel import StrategyOptimizationPanel
from tooltips import ToolTip, RichToolTip, COMMON_TOOLTIPS


class EnhancedMainGUIV2:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Poker Strategy Development System V2")

        # Set window size to 60% of screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.6)
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

        # --- NEW: Status Bar Variable ---
        self.status_bar_text = tk.StringVar()

        self._setup_styles()
        self._create_menu()
        self._create_widgets()
        
        # --- NEW: Create the Status Bar ---
        self._create_status_bar()
        
        self._apply_initial_font_size()

    def _setup_styles(self):
        """Setup custom styles for the application."""
        style = ttk.Style()

        # Configure notebook style
        style.configure("TNotebook", background=THEME["primary_bg"])
        style.configure(
            "TNotebook.Tab",
            background=THEME["secondary_bg"],
            foreground=THEME["text"],
            padding=[10, 5],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", THEME["accent_primary"]), ("active", THEME["widget_bg"])],
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
            "Dark.TLabelframe", background=THEME["primary_bg"], foreground=THEME["text"]
        )
        style.configure(
            "Dark.TLabelframe.Label", background=THEME["primary_bg"], foreground=THEME["text"]
        )

        # Configure label style
        style.configure("Dark.TLabel", background=THEME["primary_bg"], foreground=THEME["text"])

        # Configure button styles
        style.configure(
            "TopMenu.TButton",
            background=THEME["accent_primary"],
            foreground=THEME["text"],
            borderwidth=1,
            font=FONTS["main"]
        )
        style.map(
            "TopMenu.TButton",
            background=[("active", THEME["accent_secondary"])]
        )

        # --- NEW: Status Bar Style ---
        style.configure(
            "StatusBar.TLabel",
            background=THEME["secondary_bg"],
            foreground=THEME["text_dark"],
            font=FONTS["small"],
            relief=tk.SUNKEN,
            borderwidth=1
        )

    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Strategy", command=self._new_strategy)
        file_menu.add_command(label="Load Strategy...", command=self._load_strategy)
        file_menu.add_command(label="Save Strategy", command=self._save_strategy)
        file_menu.add_command(label="Save Strategy As...", command=self._save_strategy_as)
        file_menu.add_separator()
        file_menu.add_command(label="Generate Default Strategy", command=self._generate_default_strategy)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Refresh All Panels", command=self._refresh_all_panels)
        tools_menu.add_command(label="Export Strategy to PDF", command=self._export_strategy_to_pdf)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _new_strategy(self):
        """Create a new strategy."""
        if messagebox.askyesno("New Strategy", "Create a new strategy? This will clear all current data."):
            self.strategy_data = StrategyData()
            self.strategy_data.load_default_tiers()
            self._refresh_all_panels()
            self.set_status("New strategy created successfully.")

    def _load_strategy(self):
        """Load a strategy file."""
        filename = filedialog.askopenfilename(
            title="Load Strategy File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if self.strategy_data.load_strategy_from_file(filename):
                self._refresh_all_panels()
                self.set_status(f"Loaded strategy from {os.path.basename(filename)}")
            else:
                self.set_status("Failed to load strategy file.", duration=3000)

    def _save_strategy(self):
        """Save the current strategy."""
        if self.strategy_data.current_strategy_file:
            if self.strategy_data.save_strategy_to_file(self.strategy_data.current_strategy_file):
                self.set_status(f"Saved strategy to {os.path.basename(self.strategy_data.current_strategy_file)}")
            else:
                self.set_status("Failed to save strategy.", duration=3000)
        else:
            self._save_strategy_as()

    def _save_strategy_as(self):
        """Save the current strategy with a new name."""
        filename = filedialog.asksaveasfilename(
            title="Save Strategy As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if self.strategy_data.save_strategy_to_file(filename):
                self.set_status(f"Saved strategy to {os.path.basename(filename)}")
            else:
                self.set_status("Failed to save strategy.", duration=3000)

    def _generate_default_strategy(self):
        """Generate a default strategy."""
        if messagebox.askyesno("Generate Default", "Generate a default strategy?"):
            self.strategy_data.load_default_tiers()
            self._refresh_all_panels()
            self.set_status("Generated default strategy.")

    def _show_about(self):
        """Show about dialog."""
        about_text = "Poker Strategy Development System V2\n\n"
        about_text += "A comprehensive tool for developing and testing poker strategies.\n\n"
        about_text += "Features:\n"
        about_text += "• Hand strength tier management\n"
        about_text += "• Visual hand grid with tier highlighting\n"
        about_text += "• Decision table editing\n"
        about_text += "• Strategy optimization tools\n"
        about_text += "• Practice session integration\n"
        about_text += "• Professional theme and status bar\n\n"
        about_text += "Version 2.0 - Enhanced with Status Bar"
        
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
        # Update strategy file display
        self._update_strategy_file_display()
        self.set_status("All panels refreshed.")

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
        font_size_label = ttk.Label(outer_frame, text="Font Size:", style="Dark.TLabel")
        font_size_label.pack(side="left", padx=5)
        ToolTip(font_size_label, COMMON_TOOLTIPS["font_size"])
        
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
        ToolTip(font_size_combo, COMMON_TOOLTIPS["font_size"])

        # Grid size control
        grid_size_label = ttk.Label(outer_frame, text="Grid Size:", style="Dark.TLabel")
        grid_size_label.pack(side="left", padx=5)
        ToolTip(grid_size_label, COMMON_TOOLTIPS["grid_size"])
        
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
        ToolTip(grid_size_combo, COMMON_TOOLTIPS["grid_size"])

        # Strategy file display
        strategy_label = ttk.Label(outer_frame, text="Strategy:", style="Dark.TLabel")
        strategy_label.pack(side="left", padx=10)
        ToolTip(strategy_label, COMMON_TOOLTIPS["strategy_file"])
        
        self.strategy_file_label = ttk.Label(
            outer_frame, text="Default Strategy", style="Dark.TLabel"
        )
        self.strategy_file_label.pack(side="left", padx=5)
        ToolTip(self.strategy_file_label, COMMON_TOOLTIPS["strategy_file"])

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

        # Tab 2: Postflop HS Editor
        self.postflop_hs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.postflop_hs_frame, text="Postflop HS Editor")

        self.postflop_hs_editor = PostflopHSEditor(
            self.postflop_hs_frame, self.strategy_data
        )

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

        # Create overview text area
        self.overview_text = tk.Text(
            self.overview_frame,
            bg=THEME["primary_bg"],
            fg=THEME["text"],
            font=FONTS["main"],
            wrap="word",
            padx=10,
            pady=10,
        )
        self.overview_text.pack(fill="both", expand=True)

        # Tab 5: Strategy Optimization
        optimization_frame = ttk.Frame(self.notebook)
        self.notebook.add(optimization_frame, text="Strategy Optimization")

        self.optimization_panel = StrategyOptimizationPanel(
            optimization_frame, self.strategy_data, self._on_optimization_complete
        )

        # Tab 6: Practice Session
        practice_frame = ttk.Frame(self.notebook)
        self.notebook.add(practice_frame, text="🎰 Practice Session")

        self._create_practice_session_interface(practice_frame)

        # Update strategy file display
        self._update_strategy_file_display()

    def _create_practice_session_interface(self, parent_frame):
        """Create the integrated practice session interface."""
        # Initialize practice simulator
        from poker_practice_simulator import PokerPracticeSimulator

        self.practice_simulator = PokerPracticeSimulator(self.strategy_data)

        # Create main layout
        main_frame = ttk.Frame(parent_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top control panel
        control_frame = ttk.LabelFrame(
            main_frame, text="Game Controls", style="Dark.TLabelframe"
        )
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Player count selection
        player_label = ttk.Label(control_frame, text="Players:")
        player_label.pack(side=tk.LEFT, padx=10)
        ToolTip(player_label, COMMON_TOOLTIPS["player_count"])
        
        self.player_count_var = tk.StringVar(value="6")
        player_count_combo = ttk.Combobox(
            control_frame,
            textvariable=self.player_count_var,
            values=["2", "3", "4", "5", "6", "7", "8"],
            state="readonly",
            width=5,
        )
        player_count_combo.pack(side=tk.LEFT, padx=5)
        ToolTip(player_count_combo, COMMON_TOOLTIPS["player_count"])

        # Start new hand button
        start_button = ttk.Button(
            control_frame, text="🎯 Start New Hand", command=self._start_practice_hand
        )
        start_button.pack(side=tk.RIGHT, padx=10)
        ToolTip(start_button, COMMON_TOOLTIPS["start_hand"])

        # Game area
        game_frame = ttk.Frame(main_frame)
        game_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Game state
        left_panel = ttk.Frame(game_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Game state display
        game_state_frame = ttk.LabelFrame(
            left_panel, text="Game State", style="Dark.TLabelframe"
        )
        game_state_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.game_state_text = tk.Text(
            game_state_frame,
            height=15,
            width=50,
            font=("Consolas", 10),
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            state=tk.DISABLED,
        )
        self.game_state_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right panel - Action controls and feedback
        right_panel = ttk.Frame(game_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Action frame
        action_frame = ttk.LabelFrame(
            right_panel, text="Your Action", style="Dark.TLabelframe"
        )
        action_frame.pack(fill=tk.X, pady=(0, 10))

        # Action buttons
        actions_frame = ttk.Frame(action_frame)
        actions_frame.pack(pady=10)

        self.action_var = tk.StringVar(value="check")
        actions = [
            ("Fold", "fold"),
            ("Check", "check"),
            ("Call", "call"),
            ("Bet", "bet"),
            ("Raise", "raise"),
        ]

        for text, value in actions:
            ttk.Radiobutton(
                actions_frame, text=text, variable=self.action_var, value=value
            ).pack(anchor=tk.W, pady=2)

        # Bet size entry
        bet_size_label = ttk.Label(action_frame, text="Bet Size:")
        bet_size_label.pack(pady=5)
        ToolTip(bet_size_label, COMMON_TOOLTIPS["bet_size"])
        
        self.bet_size_var = tk.StringVar(value="0")
        bet_size_entry = ttk.Entry(action_frame, textvariable=self.bet_size_var)
        bet_size_entry.pack(pady=5)
        ToolTip(bet_size_entry, COMMON_TOOLTIPS["bet_size"])

        # Submit action button
        submit_button = ttk.Button(
            action_frame, text="Submit Action", command=self._submit_practice_action
        )
        submit_button.pack(pady=10)
        ToolTip(submit_button, COMMON_TOOLTIPS["submit_action"])

        # Feedback frame
        feedback_frame = ttk.LabelFrame(
            right_panel, text="Strategy Feedback", style="Dark.TLabelframe"
        )
        feedback_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.feedback_text = tk.Text(
            feedback_frame,
            height=8,
            font=("Arial", 10),
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            state=tk.DISABLED,
        )
        self.feedback_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Stats frame
        stats_frame = ttk.LabelFrame(
            right_panel, text="Session Stats", style="Dark.TLabelframe"
        )
        stats_frame.pack(fill=tk.X)

        self.stats_text = tk.Text(
            stats_frame,
            height=4,
            font=("Arial", 9),
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            state=tk.DISABLED,
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _start_practice_hand(self):
        """Start a new practice hand."""
        try:
            player_count = int(self.player_count_var.get())
            self.practice_simulator.start_new_hand(player_count)
            self._update_practice_game_display()
            self.set_status(f"Started new practice hand with {player_count} players.")
        except Exception as e:
            self.set_status(f"Error starting practice hand: {e}", duration=3000)

    def _submit_practice_action(self):
        """Submit the player's action in the practice session."""
        try:
            action = self.action_var.get()
            bet_size = float(self.bet_size_var.get()) if self.bet_size_var.get() else 0
            
            result = self.practice_simulator.submit_action(action, bet_size)
            self._update_practice_game_display()
            self._update_practice_feedback()
            self._update_practice_stats()
            
            self.set_status(f"Action submitted: {action}")
        except Exception as e:
            self.set_status(f"Error submitting action: {e}", duration=3000)

    def _update_practice_game_display(self):
        """Update the practice game display."""
        if hasattr(self, "game_state_text"):
            self.game_state_text.config(state=tk.NORMAL)
            self.game_state_text.delete(1.0, tk.END)
            
            if hasattr(self, "practice_simulator"):
                game_state = self.practice_simulator.get_game_state()
                self.game_state_text.insert(1.0, game_state)
            
            self.game_state_text.config(state=tk.DISABLED)

    def _update_practice_feedback(self):
        """Update the practice feedback display."""
        if hasattr(self, "feedback_text") and hasattr(self, "practice_simulator"):
            self.feedback_text.config(state=tk.NORMAL)
            self.feedback_text.delete(1.0, tk.END)
            
            feedback = self.practice_simulator.get_feedback()
            self.feedback_text.insert(1.0, feedback)
            
            self.feedback_text.config(state=tk.DISABLED)

    def _update_practice_stats(self):
        """Update the practice statistics display."""
        if hasattr(self, "stats_text") and hasattr(self, "practice_simulator"):
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            
            stats = self.practice_simulator.get_stats()
            self.stats_text.insert(1.0, stats)
            
            self.stats_text.config(state=tk.DISABLED)

    def _on_optimization_complete(self, result):
        """Handle optimization completion."""
        if result:
            win_rate = result.get("win_rate", 0)
            improvement = result.get("improvement", 0)
            self.set_status(f"Optimization complete! Win rate: {win_rate:.1f}% (+{improvement:.1f}%)")
        else:
            self.set_status("Optimization completed.")

    def _update_overview(self):
        """Update the strategy overview."""
        if hasattr(self, "overview_text"):
            self.overview_text.delete(1.0, tk.END)
            
            overview = f"""STRATEGY OVERVIEW
{'='*50}

Current Strategy: {self.strategy_data.get_strategy_file_display_name()}
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TIER SUMMARY:
"""
            
            for tier in self.strategy_data.tiers:
                overview += f"\n{tier.name} (HS {tier.min_hs}-{tier.max_hs}): {len(tier.hands)} hands"
                overview += f"\n  Hands: {', '.join(tier.hands[:5])}"
                if len(tier.hands) > 5:
                    overview += f" ... and {len(tier.hands) - 5} more"
                overview += "\n"
            
            overview += f"""
TOTAL STATISTICS:
• Total Playable Hands: {sum(len(tier.hands) for tier in self.strategy_data.tiers)}
• Number of Tiers: {len(self.strategy_data.tiers)}
• Strategy File: {self.strategy_data.current_strategy_file or 'Default'}

STRATEGY FEATURES:
• Preflop hand strength evaluation
• Postflop decision tables
• Position-based adjustments
• Practice session integration
• Strategy optimization tools
"""
            
            self.overview_text.insert(1.0, overview)

    def _export_strategy_to_pdf(self):
        """Export strategy to PDF format."""
        filename = filedialog.asksaveasfilename(
            title="Export Strategy to PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            # Placeholder for PDF export functionality
            self.set_status(f"PDF export to {os.path.basename(filename)} (placeholder)")

    def _on_font_size_change(self, event=None):
        """Handle font size change."""
        try:
            new_index = int(self.font_size_var.get()) - 1
            if 0 <= new_index < len(self.font_sizes):
                self.current_font_size_index = new_index
                self._update_font_size()
                self.set_status(f"Font size changed to {self.font_sizes[new_index]}")
        except ValueError:
            pass

    def _on_grid_size_change(self, event=None):
        """Handle grid size change."""
        try:
            new_size = self.grid_size_var.get()
            if hasattr(self, "hand_grid"):
                self.hand_grid.grid_size_index = int(new_size) - 1
                self.hand_grid._update_grid_state(grid_size=int(new_size) - 1)
                self.set_status(f"Grid size changed to {new_size}")
        except ValueError:
            pass

    def _update_font_size(self):
        """Update font size for all components."""
        new_size = self.font_sizes[self.current_font_size_index]
        
        # Update styles
        self._setup_styles()
        
        # Update font size label
        self.font_size_var.set(new_size)
        
        # Update hand grid size to match app font size
        if hasattr(self, "hand_grid"):
            self.hand_grid.grid_size_index = self.current_font_size_index
            self.hand_grid._update_grid_state(grid_size=self.current_font_size_index)
        
        # Update tier panel fonts
        if hasattr(self, "tier_panel"):
            self.tier_panel.update_font_size(GridSettings.get_size_config(new_size)["font"][1])
        
        # Update decision table panel fonts
        if hasattr(self, "decision_table_panel"):
            self.decision_table_panel.update_font_size(GridSettings.get_size_config(new_size)["font"][1])
        
        # Update postflop HS editor fonts
        if hasattr(self, "postflop_hs_editor"):
            self.postflop_hs_editor.update_font_size(GridSettings.get_size_config(new_size)["font"][1])

    def _on_tier_data_change(self):
        """Handle tier data changes."""
        self.set_status("Tier data updated.")
        # Only update hand colors if no specific tier is selected
        if hasattr(self, "hand_grid") and hasattr(self.hand_grid, "_current_tier_selection"):
            if self.hand_grid._current_tier_selection is None:
                self.hand_grid.update_hand_colors()

    def _on_tier_select(self, selected_tiers):
        """Handle tier selection changes."""
        if selected_tiers:
            tier_names = [tier.name for tier in selected_tiers]
            self.set_status(f"Selected tiers: {', '.join(tier_names)}")
        else:
            self.set_status("No tiers selected.")
        
        if hasattr(self, "hand_grid"):
            self.hand_grid.highlight_tiers(selected_tiers)

    def _apply_initial_font_size(self):
        """Apply initial font size settings."""
        self._update_font_size()

    def _create_status_bar(self):
        """Creates a status bar at the bottom of the window."""
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_bar_text,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5,
            style="StatusBar.TLabel"  # Use a custom style
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.set_status("Ready.")

    def set_status(self, message, duration=5000):
        """Updates the text in the status bar."""
        self.status_bar_text.set(message)
        if duration > 0:
            self.root.after(duration, lambda: self.status_bar_text.set("Ready."))

    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = EnhancedMainGUIV2()
    app.run()


if __name__ == "__main__":
    main() 
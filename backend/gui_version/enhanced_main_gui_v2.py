#!/usr/bin/env python3
"""
Enhanced Main GUI V2 - Integrated with Upgraded Poker State Machine

This is the enhanced main GUI application that integrates the upgraded
poker state machine from the CLI project, providing advanced gameplay
features and improved strategy analysis.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

# Import GUI components
from gui_models import StrategyData, THEME
from hand_grid import HandGridWidget
from tier_panel import TierPanel
from decision_table_panel import DecisionTablePanel
from postflop_hs_editor import PostflopHSEditor
from strategy_optimization_panel import StrategyOptimizationPanel

# Import the enhanced poker state machine
from poker_state_machine_enhanced import ImprovedPokerStateMachine


class EnhancedMainGUIV2:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced Poker Strategy Development System V2")

        # Set window size to 70% of screen and center it
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.70)
        window_height = int(screen_height * 0.70)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Initialize strategy data
        self.strategy_data = StrategyData()

        # Try to load enhanced strategy by default
        if os.path.exists("modern_strategy_enhanced.json"):
            self.strategy_data.load_strategy_from_file("modern_strategy_enhanced.json")
            print("SUCCESS: Loaded enhanced strategy with advanced features")
        elif os.path.exists("modern_strategy.json"):
            self.strategy_data.load_strategy_from_file("modern_strategy.json")
            print("SUCCESS: Loaded standard strategy")
        else:
            # Load default tiers and create complete strategy
            self.strategy_data.load_default_tiers()
            # Ensure the strategy has complete decision tables
            self.strategy_data.strategy_dict = (
                self.strategy_data._create_strategy_from_tiers()
            )
            print("SUCCESS: Loaded default strategy with complete decision tables")
            print(
                f"  - Total hands: {sum(len(tier.hands) for tier in self.strategy_data.tiers)}"
            )
            print(f"  - Tiers: {len(self.strategy_data.tiers)}")
            print("  - Decision tables: Preflop, Flop, Turn, River")

        # Initialize enhanced poker state machine
        self.poker_state_machine = ImprovedPokerStateMachine(num_players=6)
        
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
            "Enhanced.TLabelframe",
            background=THEME["bg"],
            foreground=THEME["fg"],
            borderwidth=2,
            relief="solid",
        )
        style.configure(
            "Enhanced.TLabelframe.Label",
            background=THEME["bg"],
            foreground=THEME["fg"],
            font=("Arial", 12, "bold"),
        )

    def _create_menu(self):
        """Create the main menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Strategy", command=self._new_strategy)
        file_menu.add_command(label="Load Strategy", command=self._load_strategy)
        file_menu.add_command(label="Save Strategy", command=self._save_strategy)
        file_menu.add_command(label="Save Strategy As", command=self._save_strategy_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export to PDF", command=self._export_strategy_to_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Strategy menu
        strategy_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Strategy", menu=strategy_menu)
        strategy_menu.add_command(label="Generate Default Strategy", command=self._generate_default_strategy)
        strategy_menu.add_command(label="Reset to Default", command=self._reset_to_default)
        strategy_menu.add_command(label="Clear All Changes", command=self._clear_all_changes)
        strategy_menu.add_command(label="Reload Current Strategy", command=self._reload_current_strategy)

        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="Start Practice Session", command=self._start_practice_session)
        game_menu.add_command(label="Enhanced Poker Table", command=self._launch_enhanced_poker_table)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All Panels", command=self._refresh_all_panels)
        view_menu.add_command(label="Update Overview", command=self._update_overview)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _new_strategy(self):
        """Create a new strategy."""
        if messagebox.askyesno("New Strategy", "Create a new strategy? This will clear all current data."):
            self.strategy_data = StrategyData()
            self.strategy_data.load_default_tiers()
            self.strategy_data.strategy_dict = self.strategy_data._create_strategy_from_tiers()
            self._refresh_all_panels()
            messagebox.showinfo("Success", "New strategy created successfully!")

    def _load_strategy(self):
        """Load a strategy from file."""
        filename = filedialog.askopenfilename(
            title="Load Strategy",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.strategy_data.load_strategy_from_file(filename)
                self._refresh_all_panels()
                messagebox.showinfo("Success", f"Strategy loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load strategy: {e}")

    def _save_strategy(self):
        """Save the current strategy."""
        try:
            self.strategy_data.save_strategy_to_file("modern_strategy.json")
            messagebox.showinfo("Success", "Strategy saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save strategy: {e}")

    def _save_strategy_as(self):
        """Save the strategy with a new filename."""
        filename = filedialog.asksaveasfilename(
            title="Save Strategy As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.strategy_data.save_strategy_to_file(filename)
                messagebox.showinfo("Success", f"Strategy saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save strategy: {e}")

    def _generate_default_strategy(self):
        """Generate a default strategy with complete decision tables."""
        try:
            self.strategy_data.load_default_tiers()
            self.strategy_data.strategy_dict = self.strategy_data._create_strategy_from_tiers()
            self._refresh_all_panels()
            messagebox.showinfo("Success", "Default strategy generated with complete decision tables!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate default strategy: {e}")

    def _show_about(self):
        """Show about dialog."""
        about_text = """
Enhanced Poker Strategy Development System V2

Features:
• Advanced poker state machine integration
• Enhanced strategy analysis and optimization
• Professional poker table simulation
• Complete decision table management
• PDF export capabilities
• Memory-efficient components

Version: 2.0
        """
        messagebox.showinfo("About", about_text)

    def _reset_to_default(self):
        """Reset to default strategy."""
        if messagebox.askyesno("Reset", "Reset to default strategy? This will clear all changes."):
            try:
                self.strategy_data.load_default_tiers()
                self.strategy_data.strategy_dict = self.strategy_data._create_strategy_from_tiers()
                self._refresh_all_panels()
                messagebox.showinfo("Success", "Reset to default strategy!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset: {e}")

    def _clear_all_changes(self):
        """Clear all unsaved changes."""
        if messagebox.askyesno("Clear Changes", "Clear all unsaved changes?"):
            try:
                # Reload the current strategy file
                if os.path.exists("modern_strategy_enhanced.json"):
                    self.strategy_data.load_strategy_from_file("modern_strategy_enhanced.json")
                elif os.path.exists("modern_strategy.json"):
                    self.strategy_data.load_strategy_from_file("modern_strategy.json")
                else:
                    self.strategy_data.load_default_tiers()
                    self.strategy_data.strategy_dict = self.strategy_data._create_strategy_from_tiers()
                
                self._refresh_all_panels()
                messagebox.showinfo("Success", "All changes cleared!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear changes: {e}")

    def _reload_current_strategy(self):
        """Reload the current strategy from file."""
        try:
            if os.path.exists("modern_strategy_enhanced.json"):
                self.strategy_data.load_strategy_from_file("modern_strategy_enhanced.json")
            elif os.path.exists("modern_strategy.json"):
                self.strategy_data.load_strategy_from_file("modern_strategy.json")
            else:
                messagebox.showwarning("Warning", "No strategy file found to reload.")
                return
            
            self._refresh_all_panels()
            messagebox.showinfo("Success", "Strategy reloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload strategy: {e}")

    def _refresh_all_panels(self):
        """Refresh all panels with current data."""
        try:
            if hasattr(self, 'hand_grid'):
                self.hand_grid.refresh_grid()
            if hasattr(self, 'tier_panel'):
                self.tier_panel.refresh_panel()
            if hasattr(self, 'decision_table_panel'):
                self.decision_table_panel.refresh_panel()
            if hasattr(self, 'postflop_editor'):
                self.postflop_editor.refresh_editor()
            if hasattr(self, 'strategy_optimization_panel'):
                self.strategy_optimization_panel.refresh_panel()
            
            self._update_overview()
            print("SUCCESS: All panels refreshed")
        except Exception as e:
            print(f"ERROR: Failed to refresh panels: {e}")

    def _create_widgets(self):
        """Create the main widgets."""
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Strategy Overview Tab
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Strategy Overview")
        self._create_overview_tab(overview_frame)

        # Hand Grid Tab
        hand_grid_frame = ttk.Frame(self.notebook)
        self.notebook.add(hand_grid_frame, text="Hand Grid")
        self._create_hand_grid_tab(hand_grid_frame)

        # Tier Panel Tab
        tier_frame = ttk.Frame(self.notebook)
        self.notebook.add(tier_frame, text="Tier Management")
        self._create_tier_panel_tab(tier_frame)

        # Decision Tables Tab
        decision_frame = ttk.Frame(self.notebook)
        self.notebook.add(decision_frame, text="Decision Tables")
        self._create_decision_table_tab(decision_frame)

        # Postflop Editor Tab
        postflop_frame = ttk.Frame(self.notebook)
        self.notebook.add(postflop_frame, text="Postflop Editor")
        self._create_postflop_editor_tab(postflop_frame)

        # Strategy Optimization Tab
        optimization_frame = ttk.Frame(self.notebook)
        self.notebook.add(optimization_frame, text="Strategy Optimization")
        self._create_optimization_tab(optimization_frame)

        # Enhanced Game Tab
        game_frame = ttk.Frame(self.notebook)
        self.notebook.add(game_frame, text="Enhanced Game")
        self._create_enhanced_game_tab(game_frame)

    def _create_overview_tab(self, parent_frame):
        """Create the strategy overview tab."""
        # Overview content
        overview_label = ttk.Label(
            parent_frame, 
            text="Enhanced Poker Strategy Development System V2",
            font=("Arial", 16, "bold")
        )
        overview_label.pack(pady=20)

        # Strategy info frame
        info_frame = ttk.LabelFrame(parent_frame, text="Strategy Information", style="Enhanced.TLabelframe")
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        self.strategy_info_text = tk.Text(info_frame, height=15, width=80)
        self.strategy_info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Update overview
        self._update_overview()

    def _create_hand_grid_tab(self, parent_frame):
        """Create the hand grid tab."""
        # Control frame
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Font size control
        ttk.Label(control_frame, text="Font Size:").pack(side=tk.LEFT, padx=5)
        self.font_size_var = tk.StringVar(value="3")
        font_size_combo = ttk.Combobox(
            control_frame, 
            textvariable=self.font_size_var,
            values=["1", "2", "3", "4", "5"],
            state="readonly",
            width=5
        )
        font_size_combo.pack(side=tk.LEFT, padx=5)
        font_size_combo.bind("<<ComboboxSelected>>", self._on_font_size_change)

        # Grid size control
        ttk.Label(control_frame, text="Grid Size:").pack(side=tk.LEFT, padx=5)
        self.grid_size_var = tk.StringVar(value="7")
        grid_size_combo = ttk.Combobox(
            control_frame,
            textvariable=self.grid_size_var,
            values=["5", "6", "7", "8", "9"],
            state="readonly",
            width=5
        )
        grid_size_combo.pack(side=tk.LEFT, padx=5)
        grid_size_combo.bind("<<ComboboxSelected>>", self._on_grid_size_change)

        # Hand grid widget
        self.hand_grid = HandGridWidget(parent_frame, self.strategy_data)

    def _create_tier_panel_tab(self, parent_frame):
        """Create the tier panel tab."""
        self.tier_panel = TierPanel(parent_frame, self.strategy_data)

    def _create_decision_table_tab(self, parent_frame):
        """Create the decision table panel tab."""
        self.decision_table_panel = DecisionTablePanel(parent_frame, self.strategy_data)

    def _create_postflop_editor_tab(self, parent_frame):
        """Create the postflop editor tab."""
        self.postflop_editor = PostflopHSEditor(parent_frame, self.strategy_data)

    def _create_optimization_tab(self, parent_frame):
        """Create the strategy optimization tab."""
        self.strategy_optimization_panel = StrategyOptimizationPanel(parent_frame, self.strategy_data)

    def _create_enhanced_game_tab(self, parent_frame):
        """Create the enhanced game tab with poker state machine integration."""
        # Game controls frame
        controls_frame = ttk.LabelFrame(parent_frame, text="Enhanced Game Controls", style="Enhanced.TLabelframe")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)

        # Start game button
        self.start_game_btn = ttk.Button(
            controls_frame, 
            text="Start Enhanced Poker Game", 
            command=self._start_enhanced_game
        )
        self.start_game_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # State machine info
        self.state_machine_info = ttk.Label(
            controls_frame,
            text="Enhanced Poker State Machine Ready",
            font=("Arial", 10, "bold")
        )
        self.state_machine_info.pack(side=tk.RIGHT, padx=10, pady=10)

        # Game status frame
        status_frame = ttk.LabelFrame(parent_frame, text="Game Status", style="Enhanced.TLabelframe")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.game_status_text = tk.Text(status_frame, height=20, width=80)
        self.game_status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Initialize game status
        self._update_game_status()

    def _start_enhanced_game(self):
        """Start the enhanced poker game with state machine."""
        try:
            # Initialize the state machine
            self.poker_state_machine = ImprovedPokerStateMachine(num_players=6)
            
            # Start a new hand
            self.poker_state_machine.start_hand()
            
            # Update game status
            self._update_game_status()
            
            # Show success message
            messagebox.showinfo("Success", "Enhanced poker game started! Check the Game Status tab for details.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start enhanced game: {e}")

    def _update_game_status(self):
        """Update the game status display."""
        try:
            status_text = "Enhanced Poker Game Status:\n\n"
            
            if hasattr(self, 'poker_state_machine'):
                game_state = self.poker_state_machine.game_state
                status_text += f"Current State: {game_state.current_state}\n"
                status_text += f"Current Street: {game_state.current_street}\n"
                status_text += f"Pot Size: ${game_state.pot:.2f}\n"
                status_text += f"Current Bet: ${game_state.current_bet:.2f}\n"
                status_text += f"Active Players: {len([p for p in game_state.players if p.is_active])}\n\n"
                
                status_text += "Players:\n"
                for i, player in enumerate(game_state.players):
                    status_text += f"  {i+1}. {player.name}: ${player.stack:.2f} (Active: {player.is_active})\n"
                
                if game_state.community_cards:
                    status_text += f"\nCommunity Cards: {', '.join(game_state.community_cards)}\n"
                
                if game_state.current_player is not None:
                    status_text += f"\nCurrent Player: {game_state.current_player.name}\n"
            else:
                status_text += "State machine not initialized.\n"
            
            self.game_status_text.delete(1.0, tk.END)
            self.game_status_text.insert(1.0, status_text)
            
        except Exception as e:
            self.game_status_text.delete(1.0, tk.END)
            self.game_status_text.insert(1.0, f"Error updating game status: {e}")

    def _start_practice_session(self):
        """Start a practice session."""
        messagebox.showinfo("Practice Session", "Practice session feature coming soon!")

    def _launch_enhanced_poker_table(self):
        """Launch the enhanced poker table."""
        try:
            # Import and launch the enhanced visual poker table
            from enhanced_visual_poker_table import ProfessionalPokerTableGUI
            
            # Create and run the poker table GUI
            poker_table = ProfessionalPokerTableGUI(self.strategy_data)
            poker_table.run()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch enhanced poker table: {e}")

    def _export_strategy_to_pdf(self):
        """Export strategy to PDF."""
        try:
            from pdf_export import export_strategy_to_pdf
            filename = filedialog.asksaveasfilename(
                title="Export Strategy to PDF",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if filename:
                export_strategy_to_pdf(self.strategy_data, filename)
                messagebox.showinfo("Success", f"Strategy exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export strategy: {e}")

    def _on_font_size_change(self, event=None):
        """Handle font size change."""
        try:
            font_size = int(self.font_size_var.get())
            self._update_font_size()
        except ValueError:
            pass

    def _on_grid_size_change(self, event=None):
        """Handle grid size change."""
        try:
            grid_size = int(self.grid_size_var.get())
            if hasattr(self, 'hand_grid'):
                self.hand_grid.update_grid_size(grid_size)
        except ValueError:
            pass

    def _update_font_size(self):
        """Update font size across all components."""
        try:
            font_size = int(self.font_size_var.get())
            
            # Update tier panel
            if hasattr(self, 'tier_panel'):
                self.tier_panel.update_font_size(font_size)
            
            # Update postflop editor
            if hasattr(self, 'postflop_editor'):
                self.postflop_editor.update_font_size(font_size)
                
            print(f"Font size updated to {font_size}")
            
        except Exception as e:
            print(f"Error updating font size: {e}")

    def _apply_initial_font_size(self):
        """Apply initial font size settings."""
        self._update_font_size()

    def _update_overview(self):
        """Update the strategy overview."""
        try:
            overview_text = "Enhanced Poker Strategy Development System V2\n"
            overview_text += "=" * 50 + "\n\n"
            
            # Strategy information
            if hasattr(self.strategy_data, 'tiers'):
                total_hands = sum(len(tier.hands) for tier in self.strategy_data.tiers)
                overview_text += f"Strategy Overview:\n"
                overview_text += f"  • Total Hands: {total_hands}\n"
                overview_text += f"  • Number of Tiers: {len(self.strategy_data.tiers)}\n"
                
                for i, tier in enumerate(self.strategy_data.tiers):
                    overview_text += f"  • Tier {i+1}: {len(tier.hands)} hands\n"
                
                overview_text += "\n"
            
            # Decision tables information
            if hasattr(self.strategy_data, 'strategy_dict'):
                strategy = self.strategy_data.strategy_dict
                overview_text += "Decision Tables:\n"
                
                if 'preflop' in strategy:
                    overview_text += f"  • Preflop: {len(strategy['preflop'])} entries\n"
                if 'flop' in strategy:
                    overview_text += f"  • Flop: {len(strategy['flop'])} entries\n"
                if 'turn' in strategy:
                    overview_text += f"  • Turn: {len(strategy['turn'])} entries\n"
                if 'river' in strategy:
                    overview_text += f"  • River: {len(strategy['river'])} entries\n"
                
                overview_text += "\n"
            
            # Enhanced features
            overview_text += "Enhanced Features:\n"
            overview_text += "  • Advanced Poker State Machine\n"
            overview_text += "  • Enhanced Strategy Analysis\n"
            overview_text += "  • Professional Poker Table\n"
            overview_text += "  • Complete Decision Tables\n"
            overview_text += "  • PDF Export Capabilities\n"
            overview_text += "  • Memory-Efficient Components\n"
            
            self.strategy_info_text.delete(1.0, tk.END)
            self.strategy_info_text.insert(1.0, overview_text)
            
        except Exception as e:
            self.strategy_info_text.delete(1.0, tk.END)
            self.strategy_info_text.insert(1.0, f"Error updating overview: {e}")

    def run(self):
        """Run the enhanced main GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    app = EnhancedMainGUIV2()
    app.run() 
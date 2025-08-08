#!/usr/bin/env python3
"""
FPSM Hands Review Panel

A hands review panel that uses the Flexible Poker State Machine (FPSM) directly
for hand simulation and review. This provides a modern, event-driven approach
to hands review while maintaining compatibility with existing hand data.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Import core components
from core.hands_database import ComprehensiveHandsDatabase, HandCategory
from core.types import ActionType
from core.phh_converter import PracticeHandsPHHManager
from core.flexible_poker_state_machine import (
    FlexiblePokerStateMachine, GameConfig, GameEvent, EventListener, Player
)

# Import UI components
from .reusable_poker_game_widget import ReusablePokerGameWidget
from core.gui_models import THEME


class FPSMHandsReviewPanel(ttk.Frame, EventListener):
    """
    Hands review panel using the Flexible Poker State Machine (FPSM).
    
    This panel provides:
    - Hand selection and categorization
    - Interactive step-by-step simulation using FPSM
    - Study mode with hand analysis
    - Event-driven updates
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Initialize hands database
        self.hands_database = ComprehensiveHandsDatabase()
        self.phh_manager = PracticeHandsPHHManager()
        
        # Hand data
        self.legendary_hands = []
        self.practice_hands = []
        self.current_hand = None
        self.current_hand_index = -1
        
        # Simulation state
        self.simulation_active = False
        self.fpsm = None
        self.poker_game_widget = None
        self.action_history = []  # Track actions for historical replay
        
        # UI state
        self.font_size = 12
        self.mode = "legendary"
        
        # Setup UI
        self.setup_ui()
        
        # Load data
        self.load_data()
    
    def setup_ui(self):
        """Setup the redesigned two-pane interface."""
        # Main container with horizontal split
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane: Hand selection
        self.setup_left_pane(main_paned)
        
        # Right pane: Study/Simulation
        self.setup_right_pane(main_paned)
    
    def setup_left_pane(self, parent):
        """Setup the left pane for hand selection."""
        left_frame = ttk.Frame(parent)
        parent.add(left_frame, weight=30)
        
        # Title
        self.title_label = ttk.Label(left_frame, text="🎯 FPSM Hands Review")
        self.title_label.pack(pady=(0, 10))
        
        # Category selection
        category_frame = ttk.Frame(left_frame)
        category_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="Legendary Hands")
        self.category_combo = ttk.Combobox(
            category_frame, 
            textvariable=self.category_var,
            values=["Legendary Hands", "Practice Hands"],
            state="readonly",
            width=15
        )
        self.category_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        # Subcategory selection (for legendary hands)
        subcategory_frame = ttk.Frame(left_frame)
        subcategory_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(subcategory_frame, text="Filter:").pack(side=tk.LEFT)
        self.subcategory_var = tk.StringVar(value="All")
        self.subcategory_combo = ttk.Combobox(
            subcategory_frame,
            textvariable=self.subcategory_var,
            state="readonly",
            width=15
        )
        self.subcategory_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        self.subcategory_combo.bind('<<ComboboxSelected>>', self.on_subcategory_change)
        
        # Hands list
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(list_frame, text="Select Hand to Review:").pack(anchor=tk.W)
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.hands_listbox = tk.Listbox(list_container)
        hands_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.hands_listbox.yview)
        self.hands_listbox.configure(yscrollcommand=hands_scrollbar.set)
        
        self.hands_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hands_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.hands_listbox.bind('<<ListboxSelect>>', self.on_hand_select)
        
        # Hand info display
        info_frame = ttk.LabelFrame(left_frame, text="Hand Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.hand_info_text = tk.Text(
            info_frame,
            height=8,
            width=40,
            font=("Consolas", 10),
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            state=tk.DISABLED
        )
        self.hand_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_right_pane(self, parent):
        """Setup the right pane for study and simulation."""
        right_frame = ttk.Frame(parent)
        parent.add(right_frame, weight=70)
        
        # Create notebook for tabs
        self.right_notebook = ttk.Notebook(right_frame)
        self.right_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Simulation tab
        self.setup_simulation_tab()
        
        # Study tab
        self.setup_study_tab()
        
        # Logging tab
        self.setup_logging_tab()
    
    def setup_simulation_tab(self):
        """Setup the simulation tab."""
        simulation_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(simulation_frame, text="🎮 Simulation")
        
        # Controls frame
        controls_frame = ttk.Frame(simulation_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start simulation button
        self.start_simulation_btn = ttk.Button(
            controls_frame, 
            text="Start Simulation", 
            command=self.start_hand_simulation
        )
        self.start_simulation_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Next action button
        self.next_action_btn = ttk.Button(
            controls_frame, 
            text="Next Action", 
            command=self.next_action,
            state="disabled"
        )
        self.next_action_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Auto play button
        self.auto_play_btn = ttk.Button(
            controls_frame, 
            text="Auto Play", 
            command=self.toggle_auto_play,
            state="disabled"
        )
        self.auto_play_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Reset button
        self.reset_simulation_btn = ttk.Button(
            controls_frame, 
            text="Reset", 
            command=self.reset_hand_simulation,
            state="disabled"
        )
        self.reset_simulation_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Quit button
        self.quit_simulation_btn = ttk.Button(
            controls_frame, 
            text="Quit", 
            command=self.quit_simulation,
            state="disabled"
        )
        self.quit_simulation_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        self.simulation_status_label = ttk.Label(
            controls_frame, 
            text="No simulation active"
        )
        self.simulation_status_label.pack(side=tk.RIGHT)
        
        # Game container
        self.game_container = ttk.Frame(simulation_frame)
        self.game_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Placeholder label
        self.placeholder_label = ttk.Label(
            self.game_container, 
            text="Select a hand and click 'Start Simulation' to begin",
            font=("Arial", 14)
        )
        self.placeholder_label.pack(expand=True)
    
    def setup_study_tab(self):
        """Setup the study tab."""
        study_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(study_frame, text="📚 Study")
        
        # Study content
        study_label = ttk.Label(
            study_frame, 
            text="Study mode - Hand analysis and strategy insights",
            font=("Arial", 12)
        )
        study_label.pack(expand=True)
    
    def setup_logging_tab(self):
        """Setup the logging tab to display real-time logged events."""
        logging_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(logging_frame, text="📊 Logging")
        
        # Logging controls
        logging_controls_frame = ttk.Frame(logging_frame)
        logging_controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Clear logs button
        self.clear_logs_btn = ttk.Button(
            logging_controls_frame,
            text="Clear Logs",
            command=self.clear_logs
        )
        self.clear_logs_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Export logs button
        self.export_logs_btn = ttk.Button(
            logging_controls_frame,
            text="Export Logs",
            command=self.export_logs
        )
        self.export_logs_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Log level filter
        ttk.Label(logging_controls_frame, text="Log Level:").pack(
            side=tk.LEFT, padx=(10, 5)
        )
        self.log_level_var = tk.StringVar(value="ALL")
        self.log_level_combo = ttk.Combobox(
            logging_controls_frame,
            textvariable=self.log_level_var,
            values=["ALL", "INFO", "WARNING", "ERROR", "GUI_EVENT", 
                   "ACTION", "STATE_CHANGE"],
            state="readonly",
            width=15
        )
        self.log_level_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.log_level_combo.bind('<<ComboboxSelected>>', self.on_log_level_change)
        
        # Logging display
        log_display_frame = ttk.Frame(logging_frame)
        log_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create text widget with scrollbar for logs
        self.log_text = tk.Text(
            log_display_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#1a1a1a",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        
        # Scrollbar for log text
        log_scrollbar = ttk.Scrollbar(
            log_display_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Pack the text widget and scrollbar
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize log display
        self.log_entries = []
        self.update_log_display()
    
    def clear_logs(self):
        """Clear the log display."""
        self.log_entries = []
        self.log_text.delete(1.0, tk.END)
        self.add_log_entry("INFO", "LOGGING", "Logs cleared")
    
    def export_logs(self):
        """Export logs to a file."""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Logs"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    for entry in self.log_entries:
                        f.write(f"{entry}\n")
                
                self.add_log_entry("INFO", "LOGGING", 
                                 f"Logs exported to {filename}")
        except Exception as e:
            self.add_log_entry("ERROR", "LOGGING", f"Error exporting logs: {e}")
    
    def on_log_level_change(self, event=None):
        """Handle log level filter change."""
        self.update_log_display()
    
    def add_log_entry(self, level: str, category: str, message: str, 
                     data: dict = None):
        """Add a log entry to the display."""
        import time
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        
        # Format the log entry
        if data:
            data_str = f" | Data: {data}"
        else:
            data_str = ""
        
        log_entry = f"[{timestamp}] {level}/{category}: {message}{data_str}"
        self.log_entries.append(log_entry)
        
        # Apply color coding based on level
        self.log_text.insert(tk.END, log_entry + "\n")
        
        # Color coding
        last_line_start = self.log_text.index("end-2c linestart")
        last_line_end = self.log_text.index("end-1c")
        
        if level == "ERROR":
            self.log_text.tag_add("error", last_line_start, last_line_end)
        elif level == "WARNING":
            self.log_text.tag_add("warning", last_line_start, last_line_end)
        elif level == "INFO":
            self.log_text.tag_add("info", last_line_start, last_line_end)
        
        # Configure tags
        self.log_text.tag_config("error", foreground="#ff6b6b")
        self.log_text.tag_config("warning", foreground="#ffd93d")
        self.log_text.tag_config("info", foreground="#6bcf7f")
        
        # Auto-scroll to bottom
        self.log_text.see(tk.END)
    
    def update_log_display(self):
        """Update the log display based on current filter."""
        self.log_text.delete(1.0, tk.END)
        
        selected_level = self.log_level_var.get()
        
        for entry in self.log_entries:
            if selected_level == "ALL" or selected_level in entry:
                self.log_text.insert(tk.END, entry + "\n")
        
        self.log_text.see(tk.END)
    
    def load_data(self):
        """Load hands data."""
        self.load_legendary_hands()
        self.load_practice_hands()
        self.update_hands_list()
    
    def load_legendary_hands(self):
        """Load legendary hands from database."""
        try:
            # Load all hands and get legendary hands
            all_hands = self.hands_database.load_all_hands()
            self.legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
            print(f"✅ Loaded {len(self.legendary_hands)} legendary hands")
        except Exception as e:
            print(f"❌ Error loading legendary hands: {e}")
            self.legendary_hands = []
    
    def load_practice_hands(self):
        """Load practice hands from PHH files."""
        try:
            # Load all hands and get practice hands
            all_hands = self.hands_database.load_all_hands()
            self.practice_hands = all_hands.get(HandCategory.PRACTICE, [])
            print(f"✅ Loaded {len(self.practice_hands)} practice hands")
        except Exception as e:
            print(f"❌ Error loading practice hands: {e}")
            self.practice_hands = []
    
    def update_hands_list(self):
        """Update the hands listbox."""
        self.hands_listbox.delete(0, tk.END)
        
        if self.category_var.get() == "Legendary Hands":
            hands = self.legendary_hands
        else:
            hands = self.practice_hands
        
        for hand in hands:
            if hasattr(hand, 'metadata') and hand.metadata:
                name = hand.metadata.name
            else:
                name = f"Hand {getattr(hand, 'id', 'Unknown')}"
            self.hands_listbox.insert(tk.END, name)
    
    def on_category_change(self, event=None):
        """Handle category change."""
        self.update_hands_list()
        self.current_hand = None
        self.update_hand_info()
    
    def on_subcategory_change(self, event=None):
        """Handle subcategory change."""
        # TODO: Implement filtering
        pass
    
    def on_hand_select(self, event=None):
        """Handle hand selection."""
        selection = self.hands_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if self.category_var.get() == "Legendary Hands":
            self.current_hand = self.legendary_hands[index]
        else:
            self.current_hand = self.practice_hands[index]
        
        self.update_hand_info()
    
    def on_mode_change(self, event=None):
        """Handle mode change."""
        self.set_mode(self.mode_var.get())
    
    def update_hand_info(self):
        """Update hand information display."""
        if not self.current_hand:
            self.hand_info_text.config(state=tk.NORMAL)
            self.hand_info_text.delete(1.0, tk.END)
            self.hand_info_text.insert(1.0, "No hand selected")
            self.hand_info_text.config(state=tk.DISABLED)
            return
        
        # Display hand information
        if hasattr(self.current_hand, 'metadata') and self.current_hand.metadata:
            hand_name = getattr(self.current_hand.metadata, 'name', 'Unknown')
        else:
            hand_name = 'Unknown'
        
        info_text = f"Hand: {hand_name}\n\n"
        
        if hasattr(self.current_hand, 'players') and self.current_hand.players:
            info_text += f"Players: {len(self.current_hand.players)}\n"
            for i, player in enumerate(self.current_hand.players):
                name = player.get('name', f'Player {i+1}')
                cards = player.get('cards', [])
                stack = player.get('starting_stack_chips', 0)
                info_text += f"  {name}: {cards} (${stack})\n"
        
        if hasattr(self.current_hand, 'game_info') and self.current_hand.game_info:
            game_info = self.current_hand.game_info
            info_text += f"\nGame Info:\n"
            info_text += f"  Pot: ${game_info.get('pot', 0)}\n"
            info_text += f"  Board: {game_info.get('board', [])}\n"
        
        self.hand_info_text.config(state=tk.NORMAL)
        self.hand_info_text.delete(1.0, tk.END)
        self.hand_info_text.insert(1.0, info_text)
        self.hand_info_text.config(state=tk.DISABLED)
    
    def set_mode(self, mode):
        """Set the current mode."""
        self.current_mode = mode
        if mode == "simulation":
            self.simulation_controls_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.simulation_controls_frame.pack_forget()
    
    def start_hand_simulation(self):
        """Start the hand simulation."""
        if not self.current_hand:
            messagebox.showwarning("No Hand Selected", "Please select a hand first.")
            return
        
        try:
            print(f"🎯 Starting simulation for hand: {self.current_hand.metadata.name}")
            self.add_log_entry("INFO", "SIMULATION", 
                             f"Starting simulation for: {self.current_hand.metadata.name}")
            
            # Setup the hand for simulation
            self.setup_hand_for_simulation()
            
            if self.fpsm:
                self.simulation_active = True
                
                # Update UI state
                self.start_simulation_btn.configure(state="disabled")
                self.next_action_btn.configure(state="normal")
                self.auto_play_btn.configure(state="normal")
                self.reset_simulation_btn.configure(state="normal")
                self.quit_simulation_btn.configure(state="normal")
                self.simulation_status_label.configure(text="Simulation active")
                
                # Hide placeholder
                if hasattr(self, 'placeholder_label'):
                    self.placeholder_label.pack_forget()
                
                print("✅ Simulation started successfully")
                self.add_log_entry("INFO", "SIMULATION", "Simulation started successfully")
            
        except Exception as e:
            print(f"❌ Error starting simulation: {e}")
            self.add_log_entry("ERROR", "SIMULATION", f"Error starting simulation: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_hand_for_simulation(self):
        """Setup the hand for simulation using FPSM."""
        if hasattr(self, '_setup_complete') and self._setup_complete:
            print("⚠️ Hand setup already complete, skipping duplicate setup")
            return
        
        if not self.current_hand:
            print("❌ No hand selected for simulation")
            return
        
        try:
            print(f"🎯 Setting up hand: {self.current_hand.metadata.name}")
            
            # Parse hand data
            hand_data = self.current_hand.raw_data
            print(f"📊 Players: {len(hand_data.get('players', []))}, Board: {hand_data.get('board', {})}, Actions: {len(hand_data.get('actions', []))}")
            
            # Create FPSM with simulation configuration - ensure at least 6 players
            num_players = max(6, len(hand_data.get('players', [])))
            config = GameConfig(
                num_players=num_players,
                big_blind=1.0,
                small_blind=0.5,
                starting_stack=1000.0,
                test_mode=False,  # Disable test mode to allow real card dealing
                show_all_cards=True,  # Show all cards in simulation mode
                auto_advance=False
            )
            
            self.fpsm = FlexiblePokerStateMachine(config)
            
            # Add this panel as an event listener
            self.fpsm.add_event_listener(self)
            
            # Create players from hand data
            fpsm_players = []
            players_data = hand_data.get('players', [])
            
            # If no players in hand data, create default players
            if not players_data:
                sample_cards = [["Ah", "Ks"], ["Qd", "Jc"], ["Th", "9s"], ["8d", "7c"], ["6h", "5s"], ["4d", "3c"]]
                for i in range(6):
                    player = Player(
                        name=f"Player {i+1}", 
                        stack=1000.0, 
                        position="", 
                        is_human=False, 
                        is_active=True, 
                        cards=sample_cards[i] if i < len(sample_cards) else ["**", "**"]
                    )
                    fpsm_players.append(player)
                    print(f"👤 Created default player {i}: {player.name} with cards: {player.cards}")
            else:
                # Process existing players from hand data
                for i, player_info in enumerate(players_data):
                    # Extract cards from player info - try multiple possible formats
                    cards = []
                    if isinstance(player_info, dict):
                        for card_field in ['cards', 'hole_cards', 'hand']:
                            if card_field in player_info:
                                potential_cards = player_info[card_field]
                                if isinstance(potential_cards, list) and len(potential_cards) >= 2:
                                    cards = potential_cards[:2]
                                    break
                                elif isinstance(potential_cards, str):
                                    if len(potential_cards) >= 4:
                                        cards = [potential_cards[:2], potential_cards[2:4]]
                                        break
                    
                    if not cards and 'raw_data' in player_info:
                        raw_data = player_info['raw_data']
                        for key, value in raw_data.items():
                            if 'card' in key.lower() and isinstance(value, list):
                                cards = value[:2]
                                break
                    
                    # If still no cards, use sample cards
                    if not cards:
                        sample_cards = [["Ah", "Ks"], ["Qd", "Jc"], ["Th", "9s"], ["8d", "7c"], ["6h", "5s"], ["4d", "3c"]]
                        cards = sample_cards[i] if i < len(sample_cards) else ["**", "**"]
                    
                    # Create player
                    player = Player(
                        name=player_info.get('name', f'Player {i+1}'),
                        stack=player_info.get('stack', 1000.0),
                        position=player_info.get('position', ''),
                        is_human=player_info.get('is_human', False),
                        is_active=player_info.get('is_active', True),
                        cards=cards
                    )
                    fpsm_players.append(player)
                    print(f"👤 Created player {i}: {player.name} with cards: {cards}")
            
            # Ensure we have exactly 6 players (pad with default players if needed)
            while len(fpsm_players) < 6:
                i = len(fpsm_players)
                sample_cards = [["Ah", "Ks"], ["Qd", "Jc"], ["Th", "9s"], ["8d", "7c"], ["6h", "5s"], ["4d", "3c"]]
                player = Player(
                    name=f"Player {i+1}", 
                    stack=1000.0, 
                    position="", 
                    is_human=False, 
                    is_active=True, 
                    cards=sample_cards[i] if i < len(sample_cards) else ["**", "**"]
                )
                fpsm_players.append(player)
                print(f"👤 Added default player {i}: {player.name} with cards: {player.cards}")
            
            # Extract board cards from hand data
            board_cards = []
            board_data = hand_data.get('board', {})
            if isinstance(board_data, dict):
                # Try to get cards from different board fields
                for field in ['flop', 'turn', 'river', 'cards']:
                    if field in board_data:
                        field_cards = board_data[field]
                        if isinstance(field_cards, list):
                            board_cards.extend(field_cards)
                        elif isinstance(field_cards, str):
                            # Parse string format like "AhKsQd"
                            if len(field_cards) >= 2:
                                for i in range(0, len(field_cards), 2):
                                    if i + 1 < len(field_cards):
                                        board_cards.append(field_cards[i:i+2])
            elif isinstance(board_data, list):
                board_cards = board_data
            
            print(f"🎯 Board cards extracted: {board_cards}")
            
            # Start the hand with existing players
            self.fpsm.start_hand(existing_players=fpsm_players)
            
            # Set board cards if available (this will override the placeholder cards)
            if board_cards:
                self.fpsm.set_board_cards(board_cards)
                print(f"✅ Set board cards: {board_cards}")
            
            # Create the poker game widget (RPGW will automatically listen for FPSM events)
            if self.poker_game_widget:
                self.poker_game_widget.destroy()
                self.poker_game_widget = None
            
            self.poker_game_widget = ReusablePokerGameWidget(
                self.game_container,
                state_machine=self.fpsm
            )
            self.poker_game_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Connect RPGW logging to our display
            self._connect_rpgw_logging()
            
            print("✅ Hand setup complete")
            self.add_log_entry("INFO", "SETUP", "Hand setup complete")
            self._setup_complete = True
            
        except Exception as e:
            print(f"❌ Error setting up hand for simulation: {e}")
            self.add_log_entry("ERROR", "SETUP", f"Error setting up hand: {e}")
            import traceback
            traceback.print_exc()
            self.simulation_active = False
    
    def _connect_rpgw_logging(self):
        """Connect the RPGW logging to our display panel."""
        if not self.poker_game_widget:
            return
        
        # Override the RPGW's session logger to also log to our display
        original_log_system = self.poker_game_widget.session_logger.log_system
        
        def enhanced_log_system(level, category, message, data=None):
            # Call the original method
            original_log_system(level, category, message, data)
            
            # Also log to our display
            self.add_log_entry(level, category, message, data)
        
        # Replace the method
        self.poker_game_widget.session_logger.log_system = enhanced_log_system
        
        # Also enhance the action logging
        original_log_action = self.poker_game_widget.session_logger.log_action
        
        def enhanced_log_action(**kwargs):
            # Call the original method
            original_log_action(**kwargs)
            
            # Create a formatted message for display
            player_name = kwargs.get('player_name', 'Unknown')
            action = kwargs.get('action', 'unknown')
            amount = kwargs.get('amount', 0.0)
            street = kwargs.get('street', 'unknown')
            
            action_msg = f"{player_name} {action} ${amount:.2f} on {street}"
            self.add_log_entry("INFO", "PLAYER_ACTION", action_msg, kwargs)
        
        # Replace the method
        self.poker_game_widget.session_logger.log_action = enhanced_log_action
        
        self.add_log_entry("INFO", "LOGGING", "RPGW logging connected to display")
    
    def next_action(self):
        """Execute the next action in the simulation."""
        if not self.fpsm or not self.simulation_active:
            return
        
        try:
            # Get the current action player
            action_player = self.fpsm.get_action_player()
            if not action_player:
                print("No action player available")
                self.add_log_entry("WARNING", "SIMULATION", "No action player available")
                return
            
            # Get valid actions for the player
            valid_actions = self.fpsm.get_valid_actions_for_player(action_player)
            
            # Determine the action to take (for now, use a simple strategy)
            action = self.determine_action_from_history(action_player, valid_actions)
            
            if action:
                # Log the action before execution
                action_msg = (f"Executing action: {action_player.name} "
                            f"{action['type'].value} ${action['amount']}")
                self.add_log_entry("INFO", "ACTION_EXECUTION", action_msg)
                
                # Execute the action
                self.fpsm.execute_action(action_player, action['type'], action['amount'])
                print(f"✅ {action_msg}")
                
                # Track the action in history
                self.action_history.append({
                    'player': action_player.name,
                    'action': action['type'].value,
                    'amount': action['amount'],
                    'valid_actions': valid_actions
                })
            else:
                self.add_log_entry("WARNING", "SIMULATION", 
                                 f"No action determined for {action_player.name}")
            
        except Exception as e:
            print(f"❌ Error executing action: {e}")
            self.add_log_entry("ERROR", "SIMULATION", f"Error executing action: {e}")
            import traceback
            traceback.print_exc()
    
    def determine_action_from_history(self, player, valid_actions):
        """Determine action based on actual hand history."""
        if not self.current_hand:
            return self.determine_action_simple(player, valid_actions)
        
        try:
            # Get hand history from ParsedHand structure
            actions = self.current_hand.actions if hasattr(self.current_hand, 'actions') else {}
            
            # Flatten actions from all streets
            all_actions = []
            for street, street_actions in actions.items():
                if isinstance(street_actions, list):
                    all_actions.extend(street_actions)
            
            print(f"🎯 Found {len(all_actions)} historical actions")
            
            # Find the next action for this player
            current_action_index = len(self.action_history)
            if current_action_index < len(all_actions):
                next_action = all_actions[current_action_index]
                if next_action.get('player') == player.name:
                    action_type_str = next_action.get('action', '').upper()
                    amount = next_action.get('amount', 0)
                    
                    # Map action string to ActionType
                    action_type_map = {
                        'FOLD': ActionType.FOLD,
                        'CHECK': ActionType.CHECK,
                        'CALL': ActionType.CALL,
                        'BET': ActionType.BET,
                        'RAISE': ActionType.RAISE,
                        'ALL_IN': ActionType.ALL_IN
                    }
                    
                    if action_type_str in action_type_map:
                        print(f"🎯 Using historical action: {action_type_str} ${amount}")
                        return {
                            'type': action_type_map[action_type_str],
                            'amount': amount
                        }
            
            # Fallback to simple action determination
            return self.determine_action_simple(player, valid_actions)
            
        except Exception as e:
            print(f"❌ Error determining action from history: {e}")
            return self.determine_action_simple(player, valid_actions)
    
    def determine_action_simple(self, player, valid_actions):
        """Simple action determination logic (fallback)."""
        # Prioritize actions in a more reasonable order - NOT always FOLD first!
        if valid_actions.get('check', False):
            return {'type': ActionType.CHECK, 'amount': 0}
        elif valid_actions.get('call', False):
            call_amount = valid_actions.get('call_amount', 0)
            return {'type': ActionType.CALL, 'amount': call_amount}
        elif valid_actions.get('bet', False):
            return {'type': ActionType.BET, 'amount': 10}
        elif valid_actions.get('raise', False):
            min_bet = valid_actions.get('min_bet', 10)
            return {'type': ActionType.RAISE, 'amount': min_bet}
        elif valid_actions.get('fold', False):
            return {'type': ActionType.FOLD, 'amount': 0}
        
        return None
    
    def toggle_auto_play(self):
        """Toggle auto-play mode."""
        # TODO: Implement auto-play functionality
        pass
    
    def reset_hand_simulation(self):
        """Reset the hand simulation."""
        if self.fpsm:
            self.fpsm.start_hand()
            if self.poker_game_widget:
                self.poker_game_widget.update_display("full_update")
            print("✅ Reset hand simulation")
            self.add_log_entry("INFO", "SIMULATION", "Hand simulation reset")
    
    def quit_simulation(self):
        """Quit the current simulation."""
        self.simulation_active = False
        
        # Reset setup flag
        self._setup_complete = False
        
        # Clear simulation
        if self.poker_game_widget:
            self.poker_game_widget.destroy()
            self.poker_game_widget = None
        
        # Show placeholder
        self.placeholder_label.pack(expand=True)
        
        # Reset controls
        self.start_simulation_btn.configure(state="normal")
        self.next_action_btn.configure(state="disabled")
        self.auto_play_btn.configure(state="disabled")
        self.reset_simulation_btn.configure(state="disabled")
        self.quit_simulation_btn.configure(state="disabled")
        self.simulation_status_label.configure(text="No simulation active")
        
        print("✅ Quit simulation")
        self.add_log_entry("INFO", "SIMULATION", "Simulation quit")
    
    def update_font_size(self, new_size):
        """Update font size throughout the panel."""
        self.font_size = new_size
        if self.poker_game_widget:
            self.poker_game_widget.update_font_size(new_size)
    
    # EventListener methods
    def on_event(self, event: GameEvent):
        """Handle events from the FPSM."""
        print(f"🎯 FPSM Event: {event.event_type}")
        
        # Add event to logging display
        self.add_log_entry("INFO", "FPSM_EVENT", f"Event: {event.event_type}")
        
        # Handle display state events (new architecture)
        if event.event_type == "display_state_update":
            # The RPGW will automatically handle display state updates
            # since it's listening to the same FPSM events
            print("🎯 Display state update received from FPSM")
            self.add_log_entry("INFO", "DISPLAY", "Display state updated")
            return
        
        # Handle other events for UI updates
        if event.event_type == "action_executed":
            action_msg = (f"Action executed: {event.player_name} "
                        f"{event.action.value if event.action else 'unknown'} "
                        f"${event.amount}")
            print(f"🎯 {action_msg}")
            self.add_log_entry("INFO", "ACTION", action_msg)
            
            # Update simulation status
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.configure(
                    text=f"Last action: {event.player_name} "
                         f"{event.action.value if event.action else 'unknown'} "
                         f"${event.amount}"
                )
        
        elif event.event_type == "state_change":
            state_msg = f"State changed to: {event.data.get('new_state', str(self.fpsm.current_state))}"
            print(f"🎯 {state_msg}")
            self.add_log_entry("INFO", "STATE_CHANGE", state_msg)
            
            # Update simulation status
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.configure(
                    text=f"State: {event.data.get('new_state', str(self.fpsm.current_state))}"
                )
        
        elif event.event_type == "hand_complete":
            winners = event.data.get('winners', [])
            winner_names = [w.name for w in winners] if winners else ["No winners"]
            hand_msg = f"Hand complete - Winners: {', '.join(winner_names)}"
            print(f"🎯 {hand_msg}")
            self.add_log_entry("INFO", "HAND_COMPLETE", hand_msg)
            
            # Update simulation status
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.configure(text=hand_msg)
        
        elif event.event_type == "action_required":
            action_req_msg = f"Action required from: {event.player_name}"
            print(f"🎯 {action_req_msg}")
            self.add_log_entry("INFO", "ACTION_REQUIRED", action_req_msg)
            
            # Update simulation status
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.configure(text=action_req_msg)
        
        # For any other event, just log it
        else:
            print(f"🎯 Unhandled event type: {event.event_type}")
            self.add_log_entry("INFO", "UNHANDLED_EVENT", 
                             f"Unhandled event: {event.event_type}")

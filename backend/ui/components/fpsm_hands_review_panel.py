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
    
    def __init__(self, parent, hands_db=None, debug_mode=False, test_mode=False, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Initialize hands database
        self.hands_database = hands_db if hands_db else ComprehensiveHandsDatabase()
        self.phh_manager = PracticeHandsPHHManager()
        
        # Mock UI testing support
        self.debug_mode = debug_mode
        self.test_mode = test_mode
        
        # Testing properties
        self.rpgw = None  # Reference to poker game widget for testing
        
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
        
        # Historical action management (for legendary hands only - does not affect FPSM core)
        self.historical_actions = []  # All actions from legendary hand
        self.historical_action_index = 0  # Current position in historical sequence
        self.use_historical_actions = False  # Only true for legendary hands
        self.hand_completed = False  # Track if hand is finished to prevent extra actions
        
        # UI state
        self.font_size = 12
        self.mode = "legendary"
        
        # Setup UI
        if not self.test_mode:
            self.setup_ui()
            # Load data
            self.load_data()
        else:
            # For test mode, just load hands data without UI
            self._load_hands_data_only()
    
    def load_hand_data(self, hand_data):
        """Load specific hand data for testing."""
        self.current_hand = hand_data
        self.current_hand_index = 0
        print(f"📖 Loaded hand data: {hand_data.metadata.name if hand_data and hasattr(hand_data, 'metadata') else 'Unknown'}")
    
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
    
    def _load_hands_data_only(self):
        """Load hands data without updating UI (for test mode)."""
        self.load_legendary_hands()
        self.load_practice_hands()
        # Skip update_hands_list() in test mode since UI components don't exist
    
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
        # Clear cache for new hand
        if hasattr(self, '_cached_actor_mapping'):
            del self._cached_actor_mapping
            
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
    
    def prepare_historical_actions(self):
        """Prepare historical action sequence for legendary hands (FPSM-independent)."""
        self.historical_actions = []
        self.historical_action_index = 0
        self.use_historical_actions = False
        
        if not self.current_hand or not hasattr(self.current_hand, 'actions'):
            return
        
        # Only use historical actions for legendary hands  
        is_legendary = False
        if hasattr(self.current_hand, 'metadata') and self.current_hand.metadata:
            from core.hands_database import HandCategory
            category = getattr(self.current_hand.metadata, 'category', None)
            is_legendary = category == HandCategory.LEGENDARY
            print(f"🎯 Hand category: {category}, is_legendary: {is_legendary}")
        
        if not is_legendary:
            print("🎯 Not a legendary hand - using normal FPSM flow")
            return
        
        # Flatten all actions from all streets into chronological order
        for street, street_actions in self.current_hand.actions.items():
            if isinstance(street_actions, list):
                for action in street_actions:
                    # Handle both 'amount' and 'to' fields correctly
                    action_type = action.get('type', '').upper()
                    amount = 0
                    
                    if action_type in ['RAISE', 'RERAISE'] and 'to' in action:
                        # For raises/reraises, use the 'to' field (total amount to raise to)
                        amount = action['to']
                    elif action_type in ['CALL', 'BET'] and 'amount' in action:
                        # For calls/bets, use the 'amount' field
                        amount = action['amount']
                    elif action_type == 'ALL-IN' and 'amount' in action:
                        # For all-ins, use the 'amount' field
                        amount = action['amount']
                    # FOLD and CHECK actions typically have amount = 0, which is correct
                    
                    self.historical_actions.append({
                        'street': street,
                        'actor': action.get('actor'),
                        'type': action_type,
                        'amount': amount
                    })
        
        self.use_historical_actions = True
        print(f"🎯 Prepared {len(self.historical_actions)} historical actions for legendary hand")
        for i, action in enumerate(self.historical_actions):
            print(f"  [{i}] {action['street']}: Actor {action['actor']} {action['type']} ${action['amount']}")
    
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
            
            # Parse hand data from legendary hand attributes
            print(f"📊 Players: {len(self.current_hand.players)}, Game: {self.current_hand.game_info}, Actions: {len(self.current_hand.actions) if self.current_hand.actions else 0}")
            
            # Extract stakes from game info
            big_blind = 40000.0  # Default for high stakes
            small_blind = 20000.0  # Default for high stakes
            starting_stack = 5000000.0  # Default high stakes stack
            
            if hasattr(self.current_hand, 'game_info') and self.current_hand.game_info:
                stakes_str = self.current_hand.game_info.get('stakes', '20000/40000/0')
                try:
                    # Parse stakes format: "sb/bb/ante"
                    parts = stakes_str.split('/')
                    if len(parts) >= 2:
                        small_blind = float(parts[0])
                        big_blind = float(parts[1])
                        print(f"💰 Using real stakes: SB=${small_blind:,.0f}, BB=${big_blind:,.0f}")
                except Exception as e:
                    print(f"⚠️ Error parsing stakes '{stakes_str}': {e}")
            
            # Create FPSM with simulation configuration using real stakes
            # Use EXACT player count from historical hand - no padding!
            num_players = len(self.current_hand.players)
            config = GameConfig(
                num_players=num_players,
                big_blind=big_blind,
                small_blind=small_blind,
                starting_stack=starting_stack,
                test_mode=False,  # Disable test mode for normal GUI operation
                show_all_cards=True,  # Show all cards in simulation mode
                auto_advance=False  # Disable auto-advance for manual GUI control
            )
            
            self.fpsm = FlexiblePokerStateMachine(config)
            
            # Add this panel as an event listener
            self.fpsm.add_event_listener(self)
            
            # Create players from legendary hand data
            fpsm_players = []
            players_data = self.current_hand.players if hasattr(self.current_hand, 'players') else []
            
            # Use actual legendary hand players
            for i, player_info in enumerate(players_data):
                # Extract cards - they should be in 'cards' field
                cards = player_info.get('cards', [])
                if len(cards) < 2:
                    # Fallback to sample cards if insufficient data
                    sample_cards = [["Ah", "Ks"], ["Qd", "Jc"], ["Th", "9s"], ["8d", "7c"], ["6h", "5s"], ["4d", "3c"]]
                    cards = sample_cards[i] if i < len(sample_cards) else ["**", "**"]
                elif len(cards) > 2:
                    # Only take first 2 cards (hole cards)
                    cards = cards[:2]
                
                # Use actual starting stack from PHH data if available
                phh_stack = player_info.get('starting_stack_chips', 0)
                if phh_stack > 0:
                    estimated_stack = phh_stack
                else:
                    # Fallback to default high stakes stack
                    estimated_stack = starting_stack
                
                # Create player with real name and cards from legendary hand
                player = Player(
                    name=player_info.get('name', f'Player {i+1}'),
                    stack=estimated_stack,
                    position=player_info.get('position', ''),
                    is_human=player_info.get('name') == 'Chris Moneymaker',  # Moneymaker is human
                    is_active=True,
                    cards=cards
                )
                fpsm_players.append(player)
                print(f"👤 Created legendary player {i}: {player.name} with cards: {cards} stack: ${player.stack:,.0f}")
            
            # No padding! Use exact historical player count for accurate simulation
            
            # Extract board cards from legendary hand data
            board_cards = []
            if hasattr(self.current_hand, 'board') and self.current_hand.board:
                # Handle both dict and list formats for board
                if isinstance(self.current_hand.board, dict):
                    # Convert dict format to list
                    for street in ['flop', 'turn', 'river']:
                        if street in self.current_hand.board:
                            street_data = self.current_hand.board[street]
                            if isinstance(street_data, dict):
                                if 'cards' in street_data:
                                    board_cards.extend(street_data['cards'])
                                elif 'card' in street_data:
                                    board_cards.append(street_data['card'])
                            elif isinstance(street_data, list):
                                board_cards.extend(street_data)
                            elif isinstance(street_data, str):
                                board_cards.append(street_data)
                    print(f"🎯 Converted board dict to list: {board_cards}")
                elif isinstance(self.current_hand.board, list):
                    board_cards = self.current_hand.board.copy()
            elif hasattr(self.current_hand, 'actions') and self.current_hand.actions:
                # For legendary hands, board cards may need to be inferred from actions
                # For now, use a sample board that works with the betting pattern
                if 'flop' in self.current_hand.actions:
                    board_cards.extend(['Ah', '8c', '7h'])  # Sample flop
                if 'turn' in self.current_hand.actions:
                    board_cards.append('3s')  # Sample turn
                if 'river' in self.current_hand.actions:
                    board_cards.append('9d')  # Sample river
                print(f"🎯 Using sample board cards for legendary hand: {board_cards}")
            
            print(f"🎯 Board cards extracted: {board_cards}")
            
            # Start the hand with existing players
            self.fpsm.start_hand(existing_players=fpsm_players)
            
            # Set board cards if available (this will override the placeholder cards)
            if board_cards:
                self.fpsm.set_board_cards(board_cards)
                print(f"✅ Set board cards: {board_cards}")
            
            # Prepare historical action sequence (for legendary hands only)
            self.prepare_historical_actions()
            
            # Reset hand completion flag for new simulation
            self.hand_completed = False
            self.last_pot_amount = 0  # Track pot for winner animation
            
            # Create the poker game widget (RPGW will automatically listen for FPSM events)
            if self.poker_game_widget:
                self.poker_game_widget.destroy()
                self.poker_game_widget = None
            
            self.poker_game_widget = ReusablePokerGameWidget(
                self.game_container,
                state_machine=self.fpsm,
                debug_mode=self.debug_mode or self.test_mode  # Use debug mode for testing
            )
            
            # Enable UI rendering for GUI display (unless in test mode)
            if not self.test_mode:
                self.poker_game_widget.headless_mode = False
                self.poker_game_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Store reference for testing
            self.rpgw = self.poker_game_widget
            
            # Set poker game config for dynamic positioning
            if self.fpsm and hasattr(self.fpsm, 'config'):
                self.poker_game_widget.set_poker_game_config(self.fpsm.config)
            
            # Reset change tracking for flicker-free updates
            self.poker_game_widget.reset_change_tracking()
            
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
        """Execute the next action in the simulation with enhanced completion handling."""
        if not self.fpsm or not self.simulation_active:
            return
        
        # Prevent actions after hand completion
        if self.hand_completed:
            print("🚫 Hand completed - ignoring next_action request")
            self._disable_action_buttons()
            return
        
        # CRITICAL: Prevent multiple concurrent action executions
        if hasattr(self, '_executing_action') and self._executing_action:
            print("⚠️ Action execution already in progress - ignoring duplicate call")
            return
        
        self._executing_action = True
        
        # Check if we're already at end state
        if self.fpsm.current_state.name in ['END_HAND', 'SHOWDOWN']:
            print(f"🏁 Hand at final state: {self.fpsm.current_state.name}")
            self._executing_action = False  # Clear the flag
            self._handle_simulation_completion()
            return
        
        try:
            # Get the current action player
            action_player = self.fpsm.get_action_player()
            if not action_player:
                print("No action player available - checking if hand should end")
                self.add_log_entry("WARNING", "SIMULATION", "No action player available")
                self._executing_action = False  # Clear the flag
                self._check_for_hand_completion()
                return
            
            # Get valid actions for the player
            valid_actions = self.fpsm.get_valid_actions_for_player(action_player)
            
            # Determine the action to take using historical data
            action = self.determine_action_from_history(action_player, valid_actions)
            
            if action:
                # Log action with enhanced detail including stack/pot info
                action_msg = (f"Executing action: {action_player.name} "
                            f"{action['type'].value} ${action['amount']}")
                
                # Log stack and pot before action
                current_pot = self.fpsm.game_state.pot
                current_stack = action_player.stack
                
                self.add_log_entry("INFO", "ACTION_EXECUTION", 
                                 f"{action_msg} (Stack: ${current_stack}, Pot: ${current_pot})")
                
                # Execute the action
                success = self.fpsm.execute_action(action_player, action['type'], action['amount'])
                
                if success:
                    print(f"✅ {action_msg}")
                    
                    # Log stack and pot after action for accuracy validation
                    new_pot = self.fpsm.game_state.pot
                    new_stack = action_player.stack
                    
                    # Track the action in history
                    self.action_history.append({
                        'player': action_player.name,
                        'action': action['type'].value,
                        'amount': action['amount'],
                        'valid_actions': valid_actions,
                        'action_index': len(self.action_history),
                        'stack_before': current_stack,
                        'stack_after': new_stack,
                        'pot_before': current_pot,
                        'pot_after': new_pot
                    })
                    
                    print(f"🎯 Action executed: Stack {current_stack} → {new_stack}, Pot {current_pot} → {new_pot}")
                    print(f"📊 Action history updated! Now {len(self.action_history)} actions executed")
                    
                    # Check if this action caused hand completion
                    self._check_for_hand_completion()
                    
                else:
                    print(f"❌ Failed to execute action: {action_msg}")
                    self.add_log_entry("ERROR", "ACTION_EXECUTION", f"Failed to execute: {action_msg}")
                    
                    # CRITICAL: Stop simulation on action failure to prevent infinite loops
                    print("🛑 Stopping simulation due to action execution failure")
                    self._executing_action = False  # Clear the flag
                    self._handle_simulation_completion()
                    return
                    
            else:
                self.add_log_entry("WARNING", "SIMULATION", 
                                 f"No action determined for {action_player.name}")
                # If no action can be determined, the hand might be complete
                self._check_for_hand_completion()
            
        except Exception as e:
            print(f"❌ Error executing action: {e}")
            self.add_log_entry("ERROR", "SIMULATION", f"Error executing action: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Always clear the execution flag
            self._executing_action = False
    
    def _check_for_hand_completion(self):
        """Check if the hand should be completed and handle accordingly."""
        if not self.fpsm:
            return
        
        current_state = self.fpsm.current_state.name
        
        # Check for completion states
        if current_state in ['END_HAND', 'SHOWDOWN']:
            print(f"🏁 Hand completion detected: {current_state}")
            self._handle_simulation_completion()
            return
        
        # Check if only one or fewer active players remain
        active_players = [p for p in self.fpsm.game_state.players 
                         if not p.has_folded and p.is_active]
        
        if len(active_players) <= 1:
            print(f"🏁 Only {len(active_players)} active players remaining - hand should end")
            self._handle_simulation_completion()
            return
    
    def _handle_simulation_completion(self):
        """Handle simulation completion with enhanced animations and logging."""
        if self.hand_completed:
            return  # Already handled
            
        print("🎉 Handling simulation completion")
        self.hand_completed = True
        
        # Disable action buttons
        self._disable_action_buttons()
        
        # Log final state
        if self.fpsm:
            final_pot = self.fpsm.game_state.pot
            active_players = [p for p in self.fpsm.game_state.players 
                             if not p.has_folded and p.is_active]
            
            completion_msg = f"Hand completed - Final pot: ${final_pot:,.0f}, Active players: {len(active_players)}"
            self.add_log_entry("INFO", "COMPLETION", completion_msg)
            
            # Log final stacks for all players
            for i, player in enumerate(self.fpsm.game_state.players):
                stack_msg = f"{player.name}: ${player.stack:,.0f} (Folded: {player.has_folded})"
                self.add_log_entry("INFO", "FINAL_STACKS", stack_msg)
        
        # Trigger showdown animations if we have RPGW
        if hasattr(self, 'poker_game_widget') and self.poker_game_widget:
            self._trigger_showdown_animations()
        
        # Enable reset button for new simulation
        if hasattr(self, 'reset_simulation_btn'):
            self.reset_simulation_btn.configure(state="normal")
        
        print("✅ Simulation completion handled successfully")
    
    def _disable_action_buttons(self):
        """Disable action control buttons when simulation is complete."""
        if hasattr(self, 'next_action_btn'):
            self.next_action_btn.configure(state="disabled")
        if hasattr(self, 'auto_play_btn'):
            self.auto_play_btn.configure(state="disabled")
        
        print("🚫 Action buttons disabled - simulation complete")
    
    def _trigger_showdown_animations(self):
        """Trigger showdown and winner animations."""
        if not self.fpsm or not hasattr(self, 'poker_game_widget'):
            return
        
        try:
            # Force showdown state for card reveals
            current_state = self.fpsm.current_state.name
            
            if current_state not in ['SHOWDOWN', 'END_HAND']:
                print("🎭 Forcing transition to showdown for animations")
                # Manually trigger showdown transition
                from core.flexible_poker_state_machine import PokerState
                if hasattr(self.fpsm, 'transition_to'):
                    self.fpsm.transition_to(PokerState.SHOWDOWN)
            
            # Trigger final display state update to show all cards
            self.fpsm._emit_display_state_event()
            
            # Get winners for animation
            active_players = [p for p in self.fpsm.game_state.players 
                             if not p.has_folded and p.is_active]
            
            if active_players:
                # For now, treat first active player as winner (can be enhanced with actual evaluation)
                winner = active_players[0]
                
                # Get pot amount before it's reset to 0 by FPSM
                pot_amount = self.fpsm.game_state.pot
                if pot_amount == 0 and hasattr(self, 'last_pot_amount'):
                    pot_amount = getattr(self, 'last_pot_amount', 0)
                    print(f"🏆 Using last known pot amount: ${pot_amount:,.0f}")
                
                # Store current pot for future reference
                if pot_amount > 0:
                    self.last_pot_amount = pot_amount
                
                print(f"🏆 Triggering winner animation: {winner.name} wins ${pot_amount:,.0f}")
                
                # Find winner seat index for proper animation
                winner_seat = 0
                if hasattr(self.poker_game_widget, 'player_seats'):
                    for i, seat in enumerate(self.poker_game_widget.player_seats):
                        if hasattr(seat, 'name_label') and seat.name_label:
                            seat_text = seat.name_label.cget('text')
                            if winner.name in seat_text:
                                winner_seat = i
                                break
                
                # Use RPGW's winner animation with proper seat info
                if hasattr(self.poker_game_widget, 'animate_pot_to_winner') and pot_amount > 0:
                    winner_info = {'name': winner.name, 'seat': winner_seat}
                    self.poker_game_widget.animate_pot_to_winner(winner_info, pot_amount)
                else:
                    print(f"🏆 {winner.name} wins ${pot_amount:,.0f} (no animation - pot: {pot_amount})")
            else:
                print("🏆 No active players found for winner animation")
                
        except Exception as e:
            print(f"⚠️ Error triggering showdown animations: {e}")
    
    def build_actor_mapping(self):
        """Build mapping from FPSM player index to legendary hand actor ID (DYNAMIC)."""
        # Cache the mapping to avoid rebuilding repeatedly during the same hand
        if hasattr(self, '_cached_actor_mapping') and self._cached_actor_mapping:
            return self._cached_actor_mapping
            
        fpsm_to_actor = {}
        
        if not hasattr(self.current_hand, 'players'):
            return fpsm_to_actor
        
        # Create dynamic mapping based on actual hand players
        hand_players = self.current_hand.players
        fpsm_players = self.fpsm.game_state.players if self.fpsm else []
        
        print(f"🎯 Building dynamic actor mapping for {len(hand_players)} hand players, {len(fpsm_players)} FPSM players")
        
        # Create mapping between hand seats and FPSM player indices based on name matching
        for fpsm_index, fpsm_player in enumerate(fpsm_players):
            matched = False
            
            # First, try exact name matching
            for hand_player in hand_players:
                hand_name = hand_player.get('name', '')
                hand_seat = hand_player.get('seat', 0)
                
                if (fpsm_player.name == hand_name or 
                    self._names_match(fpsm_player.name, hand_name)):
                    fpsm_to_actor[fpsm_index] = hand_seat
                    print(f"🎯 Mapped FPSM player {fpsm_index} ({fpsm_player.name}) → Actor {hand_seat} ({hand_name}) [NAME MATCH]")
                    matched = True
                    break
            
            # If no name match, map by order (for folded players or when names don't match)
            if not matched:
                # Map to the next available seat in the hand data
                hand_seats = [p.get('seat', i+1) for i, p in enumerate(hand_players)]
                if fpsm_index < len(hand_seats):
                    mapped_seat = hand_seats[fpsm_index]
                    fpsm_to_actor[fpsm_index] = mapped_seat
                    print(f"🎯 Mapped FPSM player {fpsm_index} ({fpsm_player.name}) → Actor {mapped_seat} [POSITIONAL MATCH]")
                else:
                    # Fallback for extra players
                    fallback_actor = fpsm_index + 1
                    fpsm_to_actor[fpsm_index] = fallback_actor
                    print(f"🎯 Fallback mapping: FPSM player {fpsm_index} → Actor {fallback_actor}")
        
        # Cache the mapping for this hand
        self._cached_actor_mapping = fpsm_to_actor
        return fpsm_to_actor
    
    def _names_match(self, fpsm_name: str, hand_name: str) -> bool:
        """Check if FPSM player name matches hand player name."""
        # Handle common name variations
        fpsm_clean = fpsm_name.lower().replace(' ', '')
        hand_clean = hand_name.lower().replace(' ', '')
        
        # Check for partial matches (first/last name)
        if fpsm_clean in hand_clean or hand_clean in fpsm_clean:
            return True
        
        # Check for specific known mappings
        name_mappings = {
            'nicolasmanion': ['manion', 'nicolas'],
            'yueqizhu': ['zhu', 'yueqi', 'yang'],  # Handle Yang Zhu → Yueqi Zhu
            'antoinelabat': ['labat', 'antoine']
        }
        
        for canonical, variants in name_mappings.items():
            if fpsm_clean == canonical or any(v in fpsm_clean for v in variants):
                if hand_clean == canonical or any(v in hand_clean for v in variants):
                    return True
        
        return False
    
    def get_player_fpsm_index(self, player):
        """Get the FPSM index for a player."""
        if hasattr(self, 'fpsm') and self.fpsm:
            for i, fpsm_player in enumerate(self.fpsm.game_state.players):
                if fpsm_player.name == player.name:
                    return i
        return -1
    
    def determine_action_from_history(self, player, valid_actions):
        """
        NEW APPROACH: Natural turn order with historical action lookup.
        
        Instead of forcing PHH action sequence, let FPSM control turn order naturally
        and look up what each player should do when it's their turn.
        """
        if not self.current_hand:
            return self.determine_action_simple(player, valid_actions)
        
        # Special case: Players named "Folded Player X" should always fold immediately
        if "Folded Player" in player.name:
            print(f"🎯 Auto-folding {player.name} (marked as folder in PHH)")
            return {'type': ActionType.FOLD, 'amount': 0}
        
        # For legendary hands, use historical action lookup
        if self.use_historical_actions:
            return self._lookup_historical_action_for_player(player, valid_actions)
        
        # Fallback for non-legendary hands
        return self.determine_action_simple(player, valid_actions)
    
    def _lookup_historical_action_for_player(self, player, valid_actions):
        """
        Look up what action this specific player should take based on PHH history.
        
        This respects FPSM's natural turn order while achieving historical accuracy.
        """
        try:
            # Build actor mapping to connect FPSM players to PHH actors
            fpsm_to_actor = self.build_actor_mapping()
            fpsm_player_index = self.get_player_fpsm_index(player)
            player_actor_id = fpsm_to_actor.get(fpsm_player_index)
            
            print(f"🎯 Looking up action for {player.name} (FPSM index {fpsm_player_index}) → Actor {player_actor_id}")
            
            if player_actor_id is None:
                print(f"⚠️  No actor mapping for {player.name} - using fallback")
                return self.determine_action_simple(player, valid_actions)
            
            # Get current game context
            current_street = self._get_current_street()
            current_bet = self.fpsm.game_state.current_bet
            player_current_bet = player.current_bet
            
            print(f"🎯 Game context: {current_street}, Current bet: ${current_bet:,}, Player bet: ${player_current_bet:,}")
            
            # Find the appropriate action for this player in this context
            historical_action = self._find_historical_action_for_player_context(
                player_actor_id, current_street, current_bet, player_current_bet)
            
            if historical_action:
                action_type_str = historical_action.get('type', '').upper()
                amount = historical_action.get('amount', historical_action.get('to', 0))
                
                # Handle different action amount types
                if action_type_str in ['RAISE', 'RERAISE'] and 'to' in historical_action:
                    amount = historical_action['to']  # Total amount to raise to
                elif action_type_str in ['CALL', 'BET'] and 'amount' in historical_action:
                    amount = historical_action['amount']  # Call/bet amount
                elif action_type_str == 'ALL-IN' and 'amount' in historical_action:
                    amount = historical_action['amount']  # All-in amount
                
                # Map action string to ActionType
                action_type_map = {
                    'FOLD': ActionType.FOLD,
                    'CHECK': ActionType.CHECK,
                    'CALL': ActionType.CALL,
                    'BET': ActionType.BET,
                    'RAISE': ActionType.RAISE,
                    'RERAISE': ActionType.RAISE,  # Map reraise to raise
                    'ALL-IN': ActionType.RAISE,  # Map all-in to raise (for large raise amounts)
                    'ALL_IN': ActionType.RAISE
                }
                
                if action_type_str in action_type_map:
                    action_type = action_type_map[action_type_str]
                    print(f"✅ HISTORICAL ACTION FOUND: {player.name} (actor {player_actor_id}) {action_type_str} ${amount:,.0f}")
                    
                    # Validate action is actually possible in current game state
                    if self._validate_action_feasible(player, action_type, amount, valid_actions):
                        return {'type': action_type, 'amount': amount}
                    else:
                        print(f"⚠️  Historical action not feasible in current state - using fallback")
                        return self.determine_action_simple(player, valid_actions)
                else:
                    print(f"❌ Unknown action type: {action_type_str}")
                    return self.determine_action_simple(player, valid_actions)
            
            # No historical action found for this player in this context
            print(f"🎯 No historical action found for {player.name} in current context - using fallback")
            return self.determine_action_simple(player, valid_actions)
            
        except Exception as e:
            print(f"❌ Error in historical action lookup: {e}")
            import traceback
            traceback.print_exc()
            return self.determine_action_simple(player, valid_actions)
    
    def _get_current_street(self):
        """Get the current street name."""
        if not self.fpsm:
            return "unknown"
        
        state_name = self.fpsm.current_state.name
        if 'PREFLOP' in state_name:
            return "preflop"
        elif 'FLOP' in state_name:
            return "flop"
        elif 'TURN' in state_name:
            return "turn"
        elif 'RIVER' in state_name:
            return "river"
        else:
            return "unknown"
    
    def _find_historical_action_for_player_context(self, actor_id, street, current_bet, player_bet):
        """
        Find the historical action for a specific actor in the current game context.
        
        This looks through all actions for this actor and finds the one that matches
        the current street and betting situation.
        """
        if not self.current_hand or not hasattr(self.current_hand, 'actions'):
            return None
        
        actions = self.current_hand.actions
        street_actions = actions.get(street, [])
        
        if not isinstance(street_actions, list):
            return None
        
        # Look for actions by this actor on this street
        actor_actions = [action for action in street_actions if action.get('actor') == actor_id]
        
        print(f"🔍 Found {len(actor_actions)} actions for actor {actor_id} on {street}")
        
        if not actor_actions:
            return None
        
        # For now, return the first action for this actor on this street
        # This can be enhanced to consider betting context for multiple actions
        action = actor_actions[0]
        print(f"🎯 Selected action: Actor {actor_id} {action.get('type')} ${action.get('amount', action.get('to', 0))}")
        
        return action
    
    def _validate_action_feasible(self, player, action_type, amount, valid_actions):
        """
        Validate that the historical action is actually feasible in the current game state.
        
        This prevents trying impossible actions like calling more than stack, etc.
        """
        # Basic validation - can be enhanced
        if action_type == ActionType.FOLD:
            return True  # Fold is always possible
        
        if action_type == ActionType.CHECK:
            return valid_actions.get('check', False)
        
        if action_type == ActionType.CALL:
            if not valid_actions.get('call', False):
                return False
            # Check if player can afford the call
            call_amount = self.fpsm.game_state.current_bet - player.current_bet
            return call_amount <= player.stack
        
        if action_type in [ActionType.BET, ActionType.RAISE]:
            if action_type == ActionType.BET and not valid_actions.get('bet', False):
                return False
            if action_type == ActionType.RAISE and not valid_actions.get('raise', False):
                return False
            # Check if player can afford the bet/raise
            return amount <= player.stack
        
        # Note: ALL_IN is handled as RAISE with large amount
        
        return True
    
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
            # Safe winner name extraction - handle both objects and strings
            winner_names = []
            for w in winners:
                if hasattr(w, 'name'):
                    winner_names.append(w.name)
                elif isinstance(w, str):
                    winner_names.append(w)
                else:
                    winner_names.append(str(w))
            
            if not winner_names:
                winner_names = ["No winners"]
                
            pot_amount = event.data.get('pot_amount', 0.0)
            hand_msg = f"Hand complete - Winners: {', '.join(winner_names)}, Pot: ${pot_amount:,.0f}"
            print(f"🏆 {hand_msg}")
            self.add_log_entry("INFO", "HAND_COMPLETE", hand_msg)
            
            # Enhanced completion handling
            self._handle_simulation_completion()
            
            # Update simulation status
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.configure(text=hand_msg + " - COMPLETED")
        
        elif event.event_type == "round_complete":
            street = event.data.get('street', 'unknown')
            print(f"🎯 Round complete on {street} - triggering street animation")
            self.add_log_entry("INFO", "ROUND_COMPLETE", f"Round complete on {street}")
            
            # Street transition animations are handled automatically by RPGW
            # Log the transition for debugging
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.configure(text=f"Moving to next street after {street}")
        
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

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
from core.json_hands_database import JSONHandsDatabase, HandCategory
from core.types import ActionType
from core.flexible_poker_state_machine import GameConfig, GameEvent, EventListener, Player
from core.hands_review_poker_state_machine import HandsReviewPokerStateMachine

# Import UI components
from .hands_review_poker_widget import HandsReviewPokerWidget
from core.gui_models import THEME, FONTS


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
        
        # Initialize JSON hands database
        self.hands_database = JSONHandsDatabase("data/legendary_hands_complete_130_fixed.json")
        
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
        self.title_label = ttk.Label(
            left_frame, 
            text="🎯 FPSM Hands Review",
            font=FONTS["header"]
        )
        self.title_label.pack(pady=(0, 10))
        
        # Category selection
        category_frame = ttk.Frame(left_frame)
        category_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(category_frame, text="Category:", font=FONTS["main"]).pack(side=tk.LEFT)
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
        
        ttk.Label(subcategory_frame, text="Filter:", font=FONTS["main"]).pack(side=tk.LEFT)
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
        
        ttk.Label(list_frame, text="Select Hand to Review:", font=FONTS["main"]).pack(anchor=tk.W)
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.hands_listbox = tk.Listbox(
            list_container,
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            font=FONTS["small"],
            selectbackground=THEME["accent_primary"],
            selectforeground=THEME["text"],
            highlightbackground=THEME["border"],
            relief="flat"
        )
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
            font=FONTS["small"],
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            wrap=tk.WORD,
            relief="flat",
            highlightbackground=THEME["border"],
            insertbackground=THEME["text"],
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
            text="🎮 Start Simulation", 
            command=self.start_hand_simulation,
            style="Primary.TButton"
        )
        self.start_simulation_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Next action button
        self.next_action_btn = ttk.Button(
            controls_frame, 
            text="▶️ Next Action", 
            command=self.next_action,
            state="disabled"
        )
        self.next_action_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Auto play button
        self.auto_play_btn = ttk.Button(
            controls_frame, 
            text="⚡ Auto Play", 
            command=self.toggle_auto_play,
            state="disabled"
        )
        self.auto_play_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Reset button
        self.reset_simulation_btn = ttk.Button(
            controls_frame, 
            text="🔄 Reset", 
            command=self.reset_hand_simulation,
            state="disabled"
        )
        self.reset_simulation_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Quit button
        self.quit_simulation_btn = ttk.Button(
            controls_frame, 
            text="❌ Quit", 
            command=self.quit_simulation,
            state="disabled",
            style="Danger.TButton"
        )
        self.quit_simulation_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        self.simulation_status_label = ttk.Label(
            controls_frame, 
            text="No simulation active",
            font=FONTS["main"]
        )
        self.simulation_status_label.pack(side=tk.RIGHT)
        
        # Game container
        self.game_container = ttk.Frame(simulation_frame)
        self.game_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Placeholder label
        self.placeholder_label = ttk.Label(
            self.game_container, 
            text="Select a hand and click 'Start Simulation' to begin",
            font=FONTS["large"]
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
            font=FONTS["main"]
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
            text="🗑️ Clear Logs",
            command=self.clear_logs,
            style="Danger.TButton"
        )
        self.clear_logs_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Export logs button
        self.export_logs_btn = ttk.Button(
            logging_controls_frame,
            text="📤 Export Logs",
            command=self.export_logs
        )
        self.export_logs_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Log level filter
        ttk.Label(logging_controls_frame, text="Log Level:", font=FONTS["main"]).pack(
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
            font=FONTS["small"],
            bg=THEME["primary_bg"],
            fg=THEME["text"],
            insertbackground=THEME["text"],
            relief="flat",
            highlightbackground=THEME["border"]
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
        """Load legendary hands from JSON database."""
        try:
            # Load all hands and get legendary hands
            all_hands = self.hands_database.load_all_hands()
            self.legendary_hands = all_hands.get(HandCategory.LEGENDARY, [])
            print(f"✅ Loaded {len(self.legendary_hands)} legendary hands")
        except Exception as e:
            print(f"❌ Error loading legendary hands: {e}")
            self.legendary_hands = []
    
    def load_practice_hands(self):
        """Load practice hands from JSON database (practice hands not available in current DB)."""
        try:
            # For now, practice hands are not available in the JSON database
            self.practice_hands = []
            print(f"✅ Practice hands not available in current JSON database")
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
            from core.json_hands_database import HandCategory
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
                    self.historical_actions.append({
                        'street': street,
                        'actor': action.get('actor'),
                        'action_type': action.get('action_type', action.get('type', '')),
                        'amount': action.get('amount', 0),
                        'to_amount': action.get('to_amount', action.get('amount', 0))
                    })
        
        self.use_historical_actions = True
        print(f"🎯 Prepared {len(self.historical_actions)} historical actions for legendary hand")
        for i, action in enumerate(self.historical_actions):
            print(f"  [{i}] {action['street']}: Actor {action['actor']} {action.get('action_type', action.get('type', 'UNKNOWN'))} ${action['amount']}")
    
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
            
            # Create specialized hands review state machine using inheritance
            num_players = len(self.current_hand.players)
            config = GameConfig(
                num_players=num_players,
                big_blind=big_blind,
                small_blind=small_blind,
                starting_stack=starting_stack
            )
            
            self.fpsm = HandsReviewPokerStateMachine(config)
            
            # Add this panel as an event listener
            self.fpsm.add_event_listener(self)
            
            # Create players from legendary hand data
            fpsm_players = []
            players_data = self.current_hand.players if hasattr(self.current_hand, 'players') else []
            
            # Use actual legendary hand players
            for i, player_info in enumerate(players_data):
                # Extract cards - try both 'hole_cards' and 'cards' fields
                cards = player_info.get('hole_cards', player_info.get('cards', []))
                if len(cards) < 2:
                    # In hands review mode, we need to see everyone's cards
                    # If player has no cards in legendary hand data, generate random cards for visualization
                    # This ensures all players have visible cards in hands review
                    sample_hole_cards = [
                        ["As", "Ks"], ["Qd", "Jc"], ["Tc", "9h"], ["8s", "7d"], 
                        ["6h", "5c"], ["4s", "3d"], ["2h", "Ac"], ["Kd", "Qh"]
                    ]
                    cards = sample_hole_cards[i % len(sample_hole_cards)]
                    print(f"🎯 Player {i} had no cards in legendary hand data - assigned sample cards: {cards} for visualization")
                elif len(cards) > 2:
                    # Only take first 2 cards (hole cards)
                    cards = cards[:2]
                
                # Use actual starting stack from hand data if available
                estimated_stack = player_info.get('starting_stack', starting_stack)
                print(f"👤 Created legendary player {i}: {player_info.get('name', f'Player {i+1}')} with cards: {cards} stack: ${estimated_stack:,.0f}")
                
                # Create player with real name and cards from legendary hand
                player = Player(
                    name=player_info.get('name', f'Player {i+1}'),
                    stack=estimated_stack,
                    position=player_info.get('position', ''),
                    is_human=False,  # In hands review, ALL players are automated
                    is_active=True,
                    cards=cards
                )
                fpsm_players.append(player)
            
            # Use actual number of players from the hand (no padding for heads-up)
            actual_player_count = len(self.current_hand.players)
            print(f"🎯 Using actual player count: {actual_player_count} (no dummy padding)")
            
            # Only pad if we have fewer than 2 players (minimum for poker)
            if len(fpsm_players) < 2:
                print(f"⚠️ Only {len(fpsm_players)} players found, padding to minimum of 2")
                while len(fpsm_players) < 2:
                    i = len(fpsm_players)
                    sample_cards = [["Ah", "Ks"], ["Qd", "Jc"]]
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
            
            # Extract board cards from legendary hand data
            board_cards = []
            if hasattr(self.current_hand, 'board') and self.current_hand.board:
                # Handle both dict and list formats for board
                if isinstance(self.current_hand.board, dict):
                    # Try to use all_cards first if available and complete
                    if 'all_cards' in self.current_hand.board:
                        all_cards = self.current_hand.board['all_cards']
                        if len(all_cards) >= 5:
                            board_cards = all_cards[:5]  # Use first 5 cards
                            print(f"🎯 Using complete all_cards: {board_cards}")
                        else:
                            print(f"🎯 Incomplete all_cards ({len(all_cards)} cards), generating full board")
                            board_cards = []
                    
                    # If all_cards is incomplete or missing, try street-by-street
                    if not board_cards:
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
            
            # If we don't have 5 board cards, generate the missing ones for a complete simulation
            if len(board_cards) < 5:
                print(f"🎯 Incomplete board data ({len(board_cards)} cards), generating missing community cards")
                
                # Always generate 5 cards for complete simulation (needed for showdown)
                needed_cards = 5
                
                # Use existing cards as base and generate missing ones that don't conflict with player hole cards
                all_player_cards = []
                if hasattr(self.current_hand, 'players'):
                    for player in self.current_hand.players:
                        hole_cards = player.get('hole_cards', player.get('cards', []))
                        all_player_cards.extend(hole_cards)
                
                sample_cards = ['As', 'Kh', 'Qc', 'Jd', '9d', '7s', '5h', '3c', '2d']
                while len(board_cards) < needed_cards:
                    # Add cards that don't conflict with existing board cards or player hole cards
                    for card in sample_cards:
                        if (card not in board_cards and 
                            card not in all_player_cards and 
                            len(board_cards) < needed_cards):
                            board_cards.append(card)
                            break
                    # Fallback if we run out of sample cards
                    if len(board_cards) < needed_cards and len([c for c in sample_cards if c not in board_cards and c not in all_player_cards]) == 0:
                        # Use more sample cards
                        extra_cards = ['4h', '6c', '8s', 'Tc', 'Jh', 'Qs', 'Kd', 'Ad']
                        for card in extra_cards:
                            if (card not in board_cards and 
                                card not in all_player_cards and 
                                len(board_cards) < needed_cards):
                                board_cards.append(card)
                                break
                
                print(f"🎯 Generated complete board with {len(board_cards)} cards: {board_cards}")
            
            print(f"🎯 Final board cards: {board_cards}")
            
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
            
            # Create the specialized hands review poker widget
            if self.poker_game_widget:
                self.poker_game_widget.destroy()
                self.poker_game_widget = None
            
            self.poker_game_widget = HandsReviewPokerWidget(
                self.game_container,
                state_machine=self.fpsm
            )
            self.poker_game_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
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
        
        # Check if we're already at end state
        if self.fpsm.current_state.name in ['END_HAND', 'SHOWDOWN']:
            print(f"🏁 Hand at final state: {self.fpsm.current_state.name}")
            self._handle_simulation_completion()
            return
        
        try:
            # Get the current action player
            action_player = self.fpsm.get_action_player()
            if not action_player:
                print("No action player available - checking if hand should end")
                self.add_log_entry("WARNING", "SIMULATION", "No action player available")
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
                    # Action success logged to session via add_log_entry above
                    
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
                    
                    # Action execution tracking (logged to session for analysis)
                    
                    # Check if this action caused hand completion
                    self._check_for_hand_completion()
                    
                else:
                    # Failed action execution already logged via add_log_entry below
                    self.add_log_entry("ERROR", "ACTION_EXECUTION", f"Failed to execute: {action_msg}")
                    
            else:
                self.add_log_entry("WARNING", "SIMULATION", 
                                 f"No action determined for {action_player.name}")
                # If no action can be determined, the hand might be complete
                self._check_for_hand_completion()
            
        except Exception as e:
            # Error already logged via add_log_entry below
            self.add_log_entry("ERROR", "SIMULATION", f"Error executing action: {e}")
            import traceback
            traceback.print_exc()
    
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
                pot_amount = self.fpsm.game_state.pot
                
                print(f"🏆 Triggering winner animation: {winner.name} wins ${pot_amount:,.0f}")
                
                # Use RPGW's winner animation
                if hasattr(self.poker_game_widget, 'animate_pot_to_winner'):
                    winner_info = {'name': winner.name, 'seat': 0}  # Simplified
                    self.poker_game_widget.animate_pot_to_winner(winner_info, pot_amount)
                
        except Exception as e:
            print(f"⚠️ Error triggering showdown animations: {e}")
    
    def get_next_historical_action(self, player):
        """Get the next historical action for legendary hands (FPSM-independent)."""
        if not self.use_historical_actions or self.historical_action_index >= len(self.historical_actions):
            return None
        
        # Map FPSM player to legendary hand actor
        fpsm_to_actor = self.build_actor_mapping()
        fpsm_player_index = self.get_player_fpsm_index(player)
        player_actor_id = fpsm_to_actor.get(fpsm_player_index)
        
        # Look ahead in historical actions to find an action for this player
        # (This handles the case where FPSM action order doesn't match historical order)
        max_lookahead = 10  # Prevent infinite loops
        original_index = self.historical_action_index
        
        for lookahead in range(max_lookahead):
            check_index = self.historical_action_index + lookahead
            if check_index >= len(self.historical_actions):
                break
                
            next_action = self.historical_actions[check_index]
            # Check if this action belongs to the current player (ensure same type comparison)
            if str(next_action['actor']) == str(player_actor_id):
                # Map action string to ActionType (support both uppercase and lowercase)
                action_type_map = {
                    'FOLD': ActionType.FOLD,
                    'fold': ActionType.FOLD,
                    'CHECK': ActionType.CHECK,
                    'check': ActionType.CHECK,
                    'CALL': ActionType.CALL,
                    'call': ActionType.CALL,
                    'BET': ActionType.BET,
                    'bet': ActionType.BET,
                    'RAISE': ActionType.RAISE,
                    'raise': ActionType.RAISE,
                    'ALL-IN': ActionType.ALL_IN if hasattr(ActionType, 'ALL_IN') else ActionType.BET,
                    'ALL_IN': ActionType.ALL_IN if hasattr(ActionType, 'ALL_IN') else ActionType.BET,
                    'all-in': ActionType.ALL_IN if hasattr(ActionType, 'ALL_IN') else ActionType.BET,
                    'all_in': ActionType.ALL_IN if hasattr(ActionType, 'ALL_IN') else ActionType.BET
                }
                
                action_type_str = next_action.get('action_type', next_action.get('type', 'UNKNOWN'))
                if action_type_str in action_type_map:
                    # Use to_amount for raises if available, otherwise use amount
                    action_amount = next_action.get('to_amount', next_action['amount'])
                    # Log successful match to session logger
                    self.add_log_entry("DEBUG", "HANDS_REVIEW_HISTORICAL_ACTION", 
                                     f"[HANDS_REVIEW_PANEL] Found historical action: {player.name} {action_type_str} ${action_amount:,.0f}")
                    # Advance the historical index to this action + 1
                    self.historical_action_index = check_index + 1
                    return {
                        'type': action_type_map[action_type_str],
                        'amount': action_amount
                    }
                else:
                    # Log unknown action type (could be important for debugging)
                    self.add_log_entry("WARNING", "HANDS_REVIEW_HISTORICAL_ACTION", f"[HANDS_REVIEW_PANEL] Unknown action type: {action_type_str}")
        
        # Log fallback usage (could indicate data issues)
        self.add_log_entry("DEBUG", "HANDS_REVIEW_HISTORICAL_ACTION", 
                         f"[HANDS_REVIEW_PANEL] No historical action found for {player.name}, using fallback")
        return None
    
    def build_actor_mapping(self):
        """Build mapping from FPSM player index to legendary hand actor ID (DYNAMIC)."""
        fpsm_to_actor = {}
        
        if not hasattr(self.current_hand, 'players'):
            return fpsm_to_actor
        
        # Create dynamic mapping based on actual hand players
        hand_players = self.current_hand.players
        fpsm_players = self.fpsm.game_state.players if self.fpsm else []
        
        # Building dynamic actor mapping (logged to session only)
        
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
                    matched = True
                    break
            
            # If no name match, map by order (for folded players or when names don't match)
            if not matched:
                # Map to the next available seat in the hand data
                hand_seats = [p.get('seat', i+1) for i, p in enumerate(hand_players)]
                if fpsm_index < len(hand_seats):
                    mapped_seat = hand_seats[fpsm_index]
                    fpsm_to_actor[fpsm_index] = mapped_seat
                else:
                    # Fallback for extra players
                    fallback_actor = fpsm_index + 1
                    fpsm_to_actor[fpsm_index] = fallback_actor
                    # Fallback mapping (log only if needed for debugging data issues)
        
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
        """Determine action based on actual hand history."""
        if not self.current_hand:
            return self.determine_action_simple(player, valid_actions)
        
        # For legendary hands, try to get historical action first
        if self.use_historical_actions:
            historical_action = self.get_next_historical_action(player)
            if historical_action:
                return historical_action
            else:
                print(f"🎯 No historical action for {player.name}, using fallback")
        
        # For legendary hands that didn't match, force fold if they should have folded
        if self.use_historical_actions:
            # Check if this player should have folded in preflop based on actor mapping
            fpsm_to_actor = self.build_actor_mapping()
            fpsm_player_index = self.get_player_fpsm_index(player)
            player_actor_id = fpsm_to_actor.get(fpsm_player_index)
            
            # Only force fold if this actor has NO historical actions in the entire hand
            # This prevents dummy players from participating, but allows real players to play
            if player_actor_id is None:
                # Player not in original hand - force fold (logged to session)
                self.add_log_entry("DEBUG", "HISTORICAL_ACTION", 
                                 f"Forcing fold for {player.name} - not in original hand")
                return {'type': ActionType.FOLD, 'amount': 0}
            
            # Check if this actor has ANY historical actions in the hand
            has_historical_actions = False
            for action in self.historical_actions:
                if action.get('actor_id') == player_actor_id:
                    has_historical_actions = True
                    break
            
            if not has_historical_actions:
                # Player has no actions in historical data - force fold (logged to session)
                self.add_log_entry("DEBUG", "HISTORICAL_ACTION", 
                                 f"Forcing fold for {player.name} - no historical actions found")
                return {'type': ActionType.FOLD, 'amount': 0}
        
        # Fallback to original logic for non-legendary hands or when no historical action matches
        try:
            # Get hand history from ParsedHand structure
            actions = self.current_hand.actions if hasattr(self.current_hand, 'actions') else {}
            
            # Flatten actions from all streets
            all_actions = []
            for street, street_actions in actions.items():
                if isinstance(street_actions, list):
                    all_actions.extend(street_actions)
            
            print(f"🎯 Found {len(all_actions)} historical actions")
            print(f"🎯 Action history so far: {len(self.action_history)} actions executed")
            
            # The next action index should be the length of our action history
            current_action_index = len(self.action_history)
            
            # Map FPSM player positions to legendary hand actor IDs
            # FPSM creates players in order [0,1,2,3,4,5] but legendary hand uses actor IDs [1,2,3,4,5,6]
            fpsm_to_actor = {}
            if hasattr(self.current_hand, 'players'):
                for i, p in enumerate(self.current_hand.players):
                    seat = p.get('seat', i+1)
                    # Map FPSM player index to legendary hand actor ID based on seat
                    if seat == 2:  # Chris Moneymaker
                        fpsm_to_actor[0] = 1  # FPSM player 0 → Actor 1 
                    elif seat == 3:  # Sammy Farha  
                        fpsm_to_actor[1] = 2  # FPSM player 1 → Actor 2
                    elif seat == 4:  # Folded Player 1
                        fpsm_to_actor[2] = 3  # FPSM player 2 → Actor 3
                    elif seat == 5:  # Folded Player 2
                        fpsm_to_actor[3] = 4  # FPSM player 3 → Actor 4
                    elif seat == 6:  # Folded Player 3
                        fpsm_to_actor[4] = 5  # FPSM player 4 → Actor 5
                    else:  # Folded Player 4 (no seat specified)
                        fpsm_to_actor[5] = 6  # FPSM player 5 → Actor 6
            
            # Find current player's actor ID based on FPSM position
            fpsm_player_index = -1
            if hasattr(self, 'fpsm') and self.fpsm:
                for i, fpsm_player in enumerate(self.fpsm.game_state.players):
                    if fpsm_player.name == player.name:
                        fpsm_player_index = i
                        break
            
            player_actor_id = fpsm_to_actor.get(fpsm_player_index)
            print(f"🎯 Player {player.name} (FPSM index {fpsm_player_index}) → Actor {player_actor_id}")
            
            if current_action_index < len(all_actions):
                next_action = all_actions[current_action_index]
                action_actor = next_action.get('actor')
                action_type_str = next_action.get('type', '').upper()
                amount = next_action.get('amount', 0)
                
                print(f"🎯 Next historical action [{current_action_index}]: Actor {action_actor} {action_type_str} ${amount}")
                print(f"🎯 Current player: {player.name} (Actor {player_actor_id})")
                
                # Check if this action belongs to the current player
                if action_actor == player_actor_id:
                    # Map action string to ActionType
                    action_type_map = {
                        'FOLD': ActionType.FOLD,
                        'CHECK': ActionType.CHECK,
                        'CALL': ActionType.CALL,
                        'BET': ActionType.BET,
                        'RAISE': ActionType.RAISE,
                        'ALL-IN': ActionType.ALL_IN if hasattr(ActionType, 'ALL_IN') else ActionType.BET,
                        'ALL_IN': ActionType.ALL_IN if hasattr(ActionType, 'ALL_IN') else ActionType.BET
                    }
                    
                    if action_type_str in action_type_map:
                        # Historical action match (logged to session for analysis)
                        return {
                            'type': action_type_map[action_type_str],
                            'amount': amount
                        }
                else:
                    print(f"❌ NO MATCH: Expected actor {player_actor_id}, but next action is for actor {action_actor}")
                    print(f"🎯 This means {player.name} should wait or use fallback action")
            
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
        
        # Create new font tuples based on the new size
        header_font = (FONTS["header"][0], int(new_size * 1.3), FONTS["header"][2] if len(FONTS["header"]) > 2 else "bold")
        main_font = (FONTS["main"][0], new_size, FONTS["main"][2] if len(FONTS["main"]) > 2 else "normal")
        small_font = (FONTS["small"][0], int(new_size * 0.9), FONTS["small"][2] if len(FONTS["small"]) > 2 else "normal")
        large_font = (FONTS["large"][0], int(new_size * 1.2), FONTS["large"][2] if len(FONTS["large"]) > 2 else "normal")
        
        # Update title
        if hasattr(self, 'title_label'):
            self.title_label.config(font=header_font)
        
        # Update hand info text
        if hasattr(self, 'hand_info_text'):
            self.hand_info_text.config(font=small_font)
        
        # Update hands listbox
        if hasattr(self, 'hands_listbox'):
            self.hands_listbox.config(font=small_font)
        
        # Update placeholder label
        if hasattr(self, 'placeholder_label'):
            self.placeholder_label.config(font=large_font)
        
        # Update log text
        if hasattr(self, 'log_text'):
            self.log_text.config(font=small_font)
        
        # Update poker game widget
        if self.poker_game_widget:
            self.poker_game_widget.update_font_size(new_size)
    
    # EventListener methods
    def on_event(self, event: GameEvent):
        """Handle events from the FPSM."""
        # FPSM Event received (kept silent for clean console)
        
        # Add event to logging display
        self.add_log_entry("INFO", "HANDS_REVIEW_FPSM_EVENT", f"[HANDS_REVIEW_PANEL] Event: {event.event_type}")
        
        # Handle display state events (new architecture)
        if event.event_type == "display_state_update":
            # The RPGW will automatically handle display state updates
            # since it's listening to the same FPSM events
            # Display state update (keep silent for clean console)
            self.add_log_entry("INFO", "DISPLAY", "Display state updated")
            return
        
        # Handle other events for UI updates
        if event.event_type == "action_executed":
            action_msg = (f"Action executed: {event.player_name} "
                        f"{event.action.value if event.action else 'unknown'} "
                        f"${event.amount}")
            # Action execution already logged to session via add_log_entry below
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
            # State change already logged to session via add_log_entry below
            self.add_log_entry("INFO", "STATE_CHANGE", state_msg)
            
            # Update simulation status
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.configure(
                    text=f"State: {event.data.get('new_state', str(self.fpsm.current_state))}"
                )
        
        elif event.event_type == "hand_complete":
            winners = event.data.get('winners', [])
            # Handle both string and object winner formats
            winner_names = []
            for w in winners:
                if isinstance(w, str):
                    winner_names.append(w)
                elif hasattr(w, 'name'):
                    winner_names.append(w.name)
                else:
                    winner_names.append(str(w))
            
            if not winner_names:
                winner_names = ["No winners"]
                
            pot_amount = event.data.get('pot_amount', 0.0)
            hand_msg = f"Hand complete - Winners: {', '.join(winner_names)}, Pot: ${pot_amount:,.0f}"
            print(f"🎯 {hand_msg}")
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
            # Action required already logged to session via add_log_entry below
            self.add_log_entry("INFO", "ACTION_REQUIRED", action_req_msg)
            
            # Update simulation status
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.configure(text=action_req_msg)
        
        elif event.event_type == "round_complete":
            street = event.data.get("street", "")
            round_msg = f"Round complete: {street}"
            print(f"🎯 {round_msg}")
            self.add_log_entry("INFO", "ROUND_COMPLETE", round_msg)
            
            # Update simulation status
            if hasattr(self, 'simulation_status_label'):
                self.simulation_status_label.configure(text=f"Round complete: {street}")
        
        # For any other event, just log it
        else:
            print(f"🎯 Unhandled event type: {event.event_type}")
            self.add_log_entry("INFO", "UNHANDLED_EVENT", 
                             f"Unhandled event: {event.event_type}")

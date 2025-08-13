#!/usr/bin/env python3
"""
Modern Hands Review Panel

A clean, event-driven hands review panel that follows our established architecture.

Key principles:
- UI layer is a dumb renderer - NO game logic
- All game logic in specialized state machine
- Event-driven communication
- Clean separation of concerns
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Core components
from core.json_hands_database import JSONHandsDatabase, HandCategory
from core.flexible_poker_state_machine import GameConfig, GameEvent, EventListener
from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
from core.session_manager import SessionManager
from core.multi_session_game_director import MultiSessionGameDirector
from core.gui_models import THEME, FONTS
# Session logger imported locally where needed

# UI components
from .hands_review_poker_widget_modern import HandsReviewPokerWidget


class ModernHandsReviewPanel(ttk.Frame, EventListener):
    """
    Modern hands review panel using clean architecture patterns.
    
    This panel provides:
    - Hand selection and categorization (UI only)
    - Step-by-step navigation controls (UI only)
    - Educational features and annotations (UI only)
    - Clean event-driven communication with state machine
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Get session logger
        try:
            from core.session_logger import get_session_logger
            self.logger = get_session_logger()
            # Test log to ensure logger is working
            if self.logger:
                self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "🔧 LOGGER TEST: ModernHandsReviewPanel __init__ started", {})
        except Exception as e:
            self.logger = None
            print(f"🚨 HANDS REVIEW PANEL: Logger initialization failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Console fallback logging
        print("🔧 CONSOLE: ModernHandsReviewPanel __init__ started")
        
        # Initialize hands database
        self.hands_database = JSONHandsDatabase("data/clean_poker_hands_flat.json")
        
        # UI state (NO game logic)
        self.legendary_hands = []
        self.practice_hands = []
        self.current_hand_index = -1
        self.font_size = 12
        self.mode = "legendary"  # or "practice"
        
        # Components (initialized later)
        self.state_machine: Optional[HandsReviewPokerStateMachine] = None
        self.poker_widget: Optional[HandsReviewPokerWidget] = None
        self.game_director = None
        self.sound_manager = None
        
        # UI elements
        self.hand_listbox = None
        self.progress_var = None
        self.action_label_var = None
        self.step_buttons = {}
        
        # Setup
        if self.logger:
            self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "🔧 About to setup UI", {})
        self._setup_ui()
        
        if self.logger:
            self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "🔧 About to load hands data", {})
        self._load_hands_data()
        
        if self.logger:
            self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "🔧 About to initialize state machine", {})
        self._initialize_state_machine()
        
        if self.logger:
            self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "ModernHandsReviewPanel initialized", {
                "legendary_hands": len(self.legendary_hands),
                "practice_hands": len(self.practice_hands),
                "current_mode": self.mode,
                "has_state_machine": hasattr(self, 'state_machine') and self.state_machine is not None,
                "has_poker_widget": hasattr(self, 'poker_widget') and self.poker_widget is not None,
                "has_game_director": hasattr(self, 'game_director') and self.game_director is not None
            })
    
    def _setup_ui(self):
        """Setup the modern two-pane interface."""
        # Main horizontal split
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane: Hand selection and controls
        self._setup_left_pane(main_paned)
        
        # Right pane: Poker table and analysis
        self._setup_right_pane(main_paned)
        
        # Configure pane weights - ttk.PanedWindow doesn't support sashrelief
        # main_paned.configure(relief=tk.RAISED)  # Alternative if needed
    
    def _load_hands_data(self):
        """Load hands data from the database."""
        try:
            if self.logger:
                self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Loading hands data from database")
            
            # Load legendary hands
            self.legendary_hands = self.hands_database.get_hands_by_category(HandCategory.LEGENDARY)
            
            # Load practice hands
            self.practice_hands = self.hands_database.get_hands_by_category(HandCategory.PRACTICE)
            
            if self.logger:
                self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Hands data loaded successfully", {
                    "legendary_count": len(self.legendary_hands),
                    "practice_count": len(self.practice_hands)
                })
            
            # Populate the hand list for the current mode
            self._populate_hand_list()
            
        except Exception as e:
            if self.logger:
                self.logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Failed to load hands data: {e}")
            # Set empty lists as fallback
            self.legendary_hands = []
            self.practice_hands = []
    
    def _populate_hand_list(self):
        """Populate the hand list based on current mode."""
        try:
            if not hasattr(self, 'hand_listbox') or not self.hand_listbox:
                # Hand listbox not created yet, will be populated when UI is ready
                return
            
            # Clear existing items
            self.hand_listbox.delete(0, tk.END)
            
            # Get hands for current mode
            hands = self.legendary_hands if self.mode == "legendary" else self.practice_hands
            
            # Populate listbox
            for i, hand in enumerate(hands):
                if hasattr(hand, 'metadata'):
                    display_name = f"{hand.metadata.id}: {hand.metadata.name}"
                else:
                    # Fallback for dictionary format
                    name = hand.get('name', 'Unknown') if isinstance(hand, dict) else 'Unknown'
                    display_name = f"Hand {i+1}: {name}"
                self.hand_listbox.insert(tk.END, display_name)
            
            if self.logger:
                self.logger.log_system("DEBUG", "HANDS_REVIEW_PANEL", f"Populated hand list with {len(hands)} hands in {self.mode} mode")
                
        except Exception as e:
            if self.logger:
                self.logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Failed to populate hand list: {e}")
    
    def _initialize_state_machine(self):
        """Initialize the hands review state machine with GameDirector integration."""
        try:
            if self.logger:
                self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Initializing hands review state machine")
            
            # Create game config for hands review
            from core.flexible_poker_state_machine import GameConfig
            config = GameConfig(
                num_players=6,
                small_blind=1.0,
                big_blind=2.0,
                starting_stack=200.0
            )
            
            # Create hands review state machine
            from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
            self.state_machine = HandsReviewPokerStateMachine(config, session_logger=self.logger)
            
            # Initialize sound manager for hands review
            from utils.sound_manager import SoundManager
            self.sound_manager = SoundManager(test_mode=False)
            
            # Create poker widget for hands review
            self._create_poker_widget()
            
            # Create GameDirector to coordinate timing and events
            self._initialize_game_director()
            
            if self.logger:
                self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Hands review system initialized successfully with GameDirector")
                
        except Exception as e:
            if self.logger:
                self.logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Failed to initialize hands review system: {e}")
            else:
                print(f"❌ Hands review init error (no logger): {e}")
                import traceback
                traceback.print_exc()
            self.state_machine = None
            self.sound_manager = None
            self.poker_widget = None
    
    def _create_poker_widget(self):
        """Create the hands review poker widget."""
        if not hasattr(self, 'poker_container') or not self.state_machine:
            if self.logger:
                self.logger.log_system("WARNING", "HANDS_REVIEW_PANEL", "Cannot create poker widget - missing container or state machine")
            return
        
        try:
            # Create hands review poker widget
            self.poker_widget = HandsReviewPokerWidget(
                parent=self.poker_container,
                state_machine=self.state_machine
            )
            self.poker_widget.pack(fill=tk.BOTH, expand=True)
            
            if self.logger:
                self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "Poker widget created successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Failed to create poker widget: {e}")
            self.poker_widget = None
    
    def _initialize_game_director(self):
        """Initialize GameDirector for hands review coordination."""
        if not self.state_machine or not self.poker_widget or not self.sound_manager:
            if self.logger:
                self.logger.log_system("WARNING", "HANDS_REVIEW_PANEL", "Cannot initialize GameDirector - missing components")
            return
        
        try:
            from core.game_director import GameDirector
            
            # Create GameDirector with all components
            self.game_director = GameDirector(
                state_machine=self.state_machine,
                ui_renderer=self.poker_widget,
                audio_manager=self.sound_manager,
                session_logger=self.logger
            )
            
            # Set GameDirector reference in state machine for auto-advance
            if hasattr(self.state_machine, 'set_game_director'):
                self.state_machine.set_game_director(self.game_director)
            
            # Start the GameDirector
            self.game_director.start()
            
            if self.logger:
                self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", "GameDirector initialized and started successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Failed to initialize GameDirector: {e}")
            self.game_director = None
    
    def _setup_left_pane(self, parent):
        """Setup the left pane for hand selection and controls."""
        left_frame = ttk.Frame(parent)
        parent.add(left_frame, weight=1)
        
        # Hand selection section
        self._create_hand_selection_section(left_frame)
        
        # Navigation controls section
        self._create_navigation_controls(left_frame)
        
        # Street progression controls section
        self._create_street_progression_controls(left_frame)
        
        # Progress display section
        self._create_progress_section(left_frame)
    
    def _setup_right_pane(self, parent):
        """Setup the right pane for poker table display."""
        right_frame = ttk.Frame(parent)
        parent.add(right_frame, weight=3)
        
        # Create poker widget container
        poker_container = ttk.LabelFrame(right_frame, text="Hand Review Table", padding=10)
        poker_container.pack(fill=tk.BOTH, expand=True)
        
        # Poker widget will be created when state machine is ready
        self.poker_container = poker_container
    
    def _create_hand_selection_section(self, parent):
        """Create hand selection UI."""
        selection_frame = ttk.LabelFrame(parent, text="Hand Selection", padding=10)
        selection_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Mode selection
        mode_frame = ttk.Frame(selection_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        
        self.mode_var = tk.StringVar(value="legendary")
        legendary_radio = ttk.Radiobutton(mode_frame, text="Legendary Hands", 
                                        variable=self.mode_var, value="legendary",
                                        command=self._on_mode_change)
        legendary_radio.pack(side=tk.LEFT, padx=5)
        
        practice_radio = ttk.Radiobutton(mode_frame, text="Practice Hands", 
                                       variable=self.mode_var, value="practice",
                                       command=self._on_mode_change)
        practice_radio.pack(side=tk.LEFT, padx=5)
        
        # Hand list
        list_frame = ttk.Frame(selection_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollable listbox
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.hand_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set,
                                     font=("Consolas", 10))
        self.hand_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.hand_listbox.yview)
        
        # Bind selection event
        self.hand_listbox.bind('<<ListboxSelect>>', self._on_hand_select)
        
        # Add comprehensive click logging
        self.hand_listbox.bind('<Button-1>', self._on_listbox_click)
        self.hand_listbox.bind('<Double-Button-1>', self._on_listbox_double_click)
        
        # Load hand button
        load_button = ttk.Button(selection_frame, text="Load Selected Hand",
                               command=self._on_load_button_clicked)
        load_button.pack(pady=5)
    
    def _create_street_progression_controls(self, parent):
        """Create street progression controls for hands review."""
        street_frame = ttk.LabelFrame(parent, text="Street Progression", padding=10)
        street_frame.pack(fill=tk.X, pady=5)
        
        # Deal Flop button
        self.deal_flop_button = ttk.Button(street_frame, text="Deal Flop",
                                          command=self._on_deal_flop_clicked)
        self.deal_flop_button.pack(fill=tk.X, pady=2)
        
        # Deal Turn button
        self.deal_turn_button = ttk.Button(street_frame, text="Deal Turn",
                                          command=self._on_deal_turn_clicked)
        self.deal_turn_button.pack(fill=tk.X, pady=2)
        
        # Deal River button
        self.deal_river_button = ttk.Button(street_frame, text="Deal River",
                                           command=self._on_deal_river_clicked)
        self.deal_river_button.pack(fill=tk.X, pady=2)
        
        # Initially disable all street buttons
        self.deal_flop_button.config(state='disabled')
        self.deal_turn_button.config(state='disabled')
        self.deal_river_button.config(state='disabled')
    
    def _create_navigation_controls(self, parent):
        """Create step navigation controls."""
        nav_frame = ttk.LabelFrame(parent, text="Navigation Controls", padding=10)
        nav_frame.pack(fill=tk.X, pady=5)
        
        # Step controls
        step_frame = ttk.Frame(nav_frame)
        step_frame.pack(fill=tk.X, pady=5)
        
        # Step backward button
        self.step_buttons['backward'] = ttk.Button(step_frame, text="◀ Step Back",
                                                 command=self._on_step_backward_clicked,
                                                 state='disabled')
        self.step_buttons['backward'].pack(side=tk.LEFT, padx=2)
        
        # Step forward button
        self.step_buttons['forward'] = ttk.Button(step_frame, text="Step Forward ▶",
                                                command=self._on_step_forward_clicked,
                                                state='disabled')
        self.step_buttons['forward'].pack(side=tk.LEFT, padx=2)
        
        # Auto-play controls
        auto_frame = ttk.Frame(nav_frame)
        auto_frame.pack(fill=tk.X, pady=5)
        
        self.auto_play_var = tk.BooleanVar()
        auto_check = ttk.Checkbutton(auto_frame, text="Auto-play", 
                                   variable=self.auto_play_var,
                                   command=self._toggle_auto_play)
        auto_check.pack(side=tk.LEFT)
        
        # Speed control
        ttk.Label(auto_frame, text="Speed:").pack(side=tk.LEFT, padx=(10, 5))
        self.speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(auto_frame, textvariable=self.speed_var,
                                 values=["Slow", "Normal", "Fast"],
                                 state="readonly", width=8)
        speed_combo.pack(side=tk.LEFT)
        
        # Reset button
        reset_button = ttk.Button(nav_frame, text="Reset to Start",
                                command=self._reset_hand,
                                state='disabled')
        reset_button.pack(pady=5)
        self.step_buttons['reset'] = reset_button
    
    def _create_progress_section(self, parent):
        """Create progress display section."""
        progress_frame = ttk.LabelFrame(parent, text="Hand Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                     maximum=100)
        progress_bar.pack(fill=tk.X, pady=5)
        
        # Action counter
        self.action_label_var = tk.StringVar(value="No hand loaded")
        action_label = ttk.Label(progress_frame, textvariable=self.action_label_var)
        action_label.pack(pady=2)
        
        # Hand info
        self.hand_info_var = tk.StringVar(value="")
        info_label = ttk.Label(progress_frame, textvariable=self.hand_info_var,
                             wraplength=200)
        info_label.pack(pady=2)
    
    def _update_hand_list(self):
        """Update the hand list display."""
        if not self.hand_listbox:
            return
        
        # Clear current list
        self.hand_listbox.delete(0, tk.END)
        
        # Get hands based on current mode
        hands = self.legendary_hands if self.mode == "legendary" else self.practice_hands
        
        # Populate list
        for i, hand in enumerate(hands):
            # Format hand display - handle both ParsedHand and dict formats
            if hasattr(hand, 'metadata'):
                # ParsedHand format
                hand_id = hand.metadata.id
                players = hand.players if hasattr(hand, 'players') else []
                num_players = len(players)
                num_actions = len(hand.actions) if hasattr(hand, 'actions') and hand.actions else 0
            else:
                # Dictionary format fallback
                hand_id = hand.get('hand_id', f'Hand {i+1}') if isinstance(hand, dict) else f'Hand {i+1}'
                players = hand.get('players', []) if isinstance(hand, dict) else []
                num_players = len(players)
                num_actions = len(hand.get('actions', [])) if isinstance(hand, dict) else 0
            
            display_text = f"{hand_id} ({num_players}P, {num_actions} actions)"
            self.hand_listbox.insert(tk.END, display_text)
    
    # ==============================
    # EVENT HANDLERS (UI ONLY)
    # ==============================
    
    def _on_mode_change(self):
        """Handle mode change (legendary vs practice)."""
        old_mode = self.mode
        self.mode = self.mode_var.get()
        self._update_hand_list()
        
        if self.logger:
            self.logger.log_system("INFO", "UI_INTERACTION", "Mode changed", {
                "old_mode": old_mode,
                "new_mode": self.mode,
                "event_type": "mode_change",
                "legendary_hands_count": len(self.legendary_hands),
                "practice_hands_count": len(self.practice_hands)
            })
    
    def _on_hand_select(self, event):
        """Handle hand selection from list."""
        if self.logger:
            self.logger.log_system("DEBUG", "HANDS_REVIEW_UI", "Hand selection event triggered", {
                "event_type": str(type(event)),
                "event_widget": str(event.widget) if hasattr(event, 'widget') else "unknown"
            })
            
        # Just update UI state - actual loading happens on button click
        selection = self.hand_listbox.curselection()
        if selection:
            old_index = self.current_hand_index
            self.current_hand_index = selection[0]
            if self.logger:
                self.logger.log_system("DEBUG", "HANDS_REVIEW_UI", "Hand selection changed", {
                    "old_index": old_index,
                    "new_index": self.current_hand_index,
                    "selection": list(selection)
                })
            
            # Check if this somehow triggers auto-loading
            if hasattr(self, 'state_machine') and self.state_machine:
                if self.logger:
                    self.logger.log_system("DEBUG", "HANDS_REVIEW_UI", "State machine exists during selection", {
                        "current_hand_index": self.current_hand_index
                    })
    
    def _on_listbox_click(self, event):
        """Log single clicks on the listbox."""
        if self.logger:
            self.logger.log_system("INFO", "UI_INTERACTION", "Listbox single click", {
                "event_type": "listbox_single_click",
                "x": event.x,
                "y": event.y,
                "widget": str(event.widget),
                "current_selection": list(self.hand_listbox.curselection()) if self.hand_listbox else []
            })
    
    def _on_listbox_double_click(self, event):
        """Log double clicks on the listbox."""
        if self.logger:
            self.logger.log_system("INFO", "UI_INTERACTION", "Listbox double click", {
                "event_type": "listbox_double_click",
                "x": event.x,
                "y": event.y,
                "widget": str(event.widget),
                "current_selection": list(self.hand_listbox.curselection()) if self.hand_listbox else []
            })
    
    def _on_load_button_clicked(self):
        """Handle load button click with comprehensive logging."""
        print("🔥 CONSOLE: Load Selected Hand button clicked!")
        
        if self.logger:
            self.logger.log_system("INFO", "UI_INTERACTION", "Load Selected Hand button clicked", {
                "current_hand_index": self.current_hand_index,
                "event_type": "button_click",
                "button_name": "load_selected_hand",
                "listbox_selection": list(self.hand_listbox.curselection()) if self.hand_listbox else [],
                "total_hands": len(self.legendary_hands) + len(self.practice_hands)
            })
        self._load_selected_hand()
    
    def _on_step_forward_clicked(self):
        """Handle step forward button click with comprehensive logging."""
        print("🔥 CONSOLE: Step Forward button clicked!")
        
        if self.logger:
            self.logger.log_system("INFO", "UI_INTERACTION", "Step Forward button clicked", {
                "current_hand_index": self.current_hand_index,
                "event_type": "button_click",
                "button_name": "step_forward",
                "button_state": self.step_buttons['forward']['state'] if 'forward' in self.step_buttons else 'unknown'
            })
        self._step_forward()
    
    def _on_step_backward_clicked(self):
        """Handle step backward button click with comprehensive logging."""
        if self.logger:
            self.logger.log_system("INFO", "UI_INTERACTION", "Step Backward button clicked", {
                "current_hand_index": self.current_hand_index,
                "event_type": "button_click",
                "button_name": "step_backward",
                "button_state": self.step_buttons['backward']['state'] if 'backward' in self.step_buttons else 'unknown'
            })
        self._step_backward()
    
    def _load_selected_hand(self):
        """Load the currently selected hand."""
        if self.logger:
            self.logger.log_system("DEBUG", "HANDS_REVIEW_UI", "Load Selected Hand button clicked", {
                "current_hand_index": self.current_hand_index
            })
            
        if self.current_hand_index < 0:
            messagebox.showwarning("No Selection", "Please select a hand to load.")
            return
        
        try:
            # Get selected hand
            hands = self.legendary_hands if self.mode == "legendary" else self.practice_hands
            if self.current_hand_index >= len(hands):
                messagebox.showerror("Error", "Invalid hand selection.")
                return
            
            hand_data = hands[self.current_hand_index]
            
            # Load hand in state machine (this is where game logic happens)
            if self.logger:
                self.logger.log_system("DEBUG", "HANDS_REVIEW_UI", "Attempting to load hand in state machine", {
                    "has_state_machine": self.state_machine is not None,
                    "hand_index": self.current_hand_index,
                    "hand_id": hand_data.metadata.id if hasattr(hand_data, 'metadata') else "unknown"
                })
                
            if self.state_machine:
                # State machine expects raw dictionary data, not ParsedHand objects
                hand_dict = hand_data.raw_data if hasattr(hand_data, 'raw_data') else hand_data
                
                if self.logger:
                    self.logger.log_system("DEBUG", "HANDS_REVIEW_UI", "Calling state_machine.load_hand_for_review", {
                        "hand_dict_keys": list(hand_dict.keys()) if hand_dict else None,
                        "has_actions": 'actions' in hand_dict if hand_dict else False,
                        "has_players": 'players' in hand_dict if hand_dict else False
                    })
                
                success = self.state_machine.load_hand_for_review(hand_dict)
                
                if self.logger:
                    self.logger.log_system("DEBUG", "HANDS_REVIEW_UI", f"load_hand_for_review returned: {success}", {})
                if success:
                    # Enable navigation controls
                    self._enable_navigation_controls(True)
                    
                    # Update hand info display using correct ParsedHand access
                    hand_id = hand_data.metadata.id if hasattr(hand_data, 'metadata') else hand_dict.get('id', 'Unknown')
                    num_actions = len(hand_data.actions) if hasattr(hand_data, 'actions') and hand_data.actions else len(hand_dict.get('actions', {}))
                    self.hand_info_var.set(f"Loaded: {hand_id}\n{num_actions} action streets total")
                    
                    if self.logger:
                        self.logger.log_system("INFO", "HANDS_REVIEW_PANEL", f"Hand loaded successfully: {hand_id}")
                else:
                    messagebox.showerror("Error", "Failed to load hand.")
            
        except Exception as e:
            if self.logger:
                self.logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Error loading hand: {e}")
            messagebox.showerror("Error", f"Failed to load hand: {e}")
    
    def _step_forward(self):
        """Step forward one action."""
        print(f"🔥 CONSOLE: _step_forward called - state_machine exists: {self.state_machine is not None}")
        
        if self.logger:
            self.logger.log_system("DEBUG", "HANDS_REVIEW_UI", "Step forward button clicked", {
                "has_state_machine": self.state_machine is not None,
                "action_index": getattr(self.state_machine, 'action_index', 'unknown') if self.state_machine else None,
                "total_actions": len(getattr(self.state_machine, 'historical_actions', [])) if self.state_machine else 0
            })
        
        if self.state_machine:
            action_index_before = getattr(self.state_machine, 'action_index', 'unknown')
            historical_actions_length = len(getattr(self.state_machine, 'historical_actions', []))
            
            print(f"🔥 CONSOLE: Before step_forward - action_index: {action_index_before}, total_actions: {historical_actions_length}")
            
            if self.logger:
                self.logger.log_system("DEBUG", "HANDS_REVIEW_UI", "Calling state_machine.step_forward()", {
                    "action_index_before": action_index_before,
                    "historical_actions_length": historical_actions_length
                })
            
            result = self.state_machine.step_forward()
            
            action_index_after = getattr(self.state_machine, 'action_index', 'unknown')
            print(f"🔥 CONSOLE: After step_forward - result: {result}, action_index: {action_index_after}")
            
            if self.logger:
                self.logger.log_system("DEBUG", "HANDS_REVIEW_UI", f"Step forward result: {result}", {
                    "action_index_after": action_index_after,
                    "state_machine_type": type(self.state_machine).__name__
                })
        else:
            print("🔥 CONSOLE: No state machine available!")
    
    def _step_backward(self):
        """Step backward one action."""
        if self.state_machine:
            self.state_machine.step_backward()
    
    def _reset_hand(self):
        """Reset hand to beginning."""
        if self.state_machine and hasattr(self.state_machine, '_reset_to_hand_start'):
            self.state_machine._reset_to_hand_start()
            self.state_machine._emit_display_state_event()
    
    def _toggle_auto_play(self):
        """Toggle auto-play mode."""
        enabled = self.auto_play_var.get()
        
        if self.state_machine:
            # Map speed to delay
            speed_delays = {"Slow": 3000, "Normal": 2000, "Fast": 1000}
            delay = speed_delays.get(self.speed_var.get(), 2000)
            
            self.state_machine.set_auto_advance(enabled, delay)
    
    def _enable_navigation_controls(self, enabled: bool):
        """Enable/disable navigation controls."""
        state = 'normal' if enabled else 'disabled'
        for button in self.step_buttons.values():
            button.configure(state=state)
    
    # ==============================
    # EVENT LISTENER IMPLEMENTATION
    # ==============================
    
    def on_event(self, event: GameEvent):
        """Handle events from the state machine."""
        try:
            if event.event_type == "step_forward":
                self._handle_step_forward_event(event)
            elif event.event_type == "step_backward":
                self._handle_step_backward_event(event)
            elif event.event_type == "hand_loaded":
                self._handle_hand_loaded_event(event)
            elif event.event_type == "annotation_added":
                self._handle_annotation_added_event(event)
                
        except Exception as e:
            if self.logger:
                self.logger.log_system("ERROR", "HANDS_REVIEW_PANEL", f"Error handling event {event.event_type}: {e}")
    
    def _handle_step_forward_event(self, event: GameEvent):
        """Handle step forward event."""
        data = event.data
        current_action = data.get('action_index', 0)
        total_actions = data.get('total_actions', 0)
        progress = data.get('progress', 0.0)
        
        # Update progress display
        self.progress_var.set(progress * 100)
        self.action_label_var.set(f"Action {current_action} of {total_actions}")
        
        # Update button states
        self.step_buttons['backward'].configure(state='normal' if current_action > 0 else 'disabled')
        self.step_buttons['forward'].configure(state='normal' if current_action < total_actions else 'disabled')
    
    def _handle_step_backward_event(self, event: GameEvent):
        """Handle step backward event."""
        data = event.data
        current_action = data.get('action_index', 0)
        total_actions = data.get('total_actions', 0)
        progress = data.get('progress', 0.0)
        
        # Update progress display
        self.progress_var.set(progress * 100)
        self.action_label_var.set(f"Action {current_action} of {total_actions}")
        
        # Update button states
        self.step_buttons['backward'].configure(state='normal' if current_action > 0 else 'disabled')
        self.step_buttons['forward'].configure(state='normal' if current_action < total_actions else 'disabled')
    
    def _handle_hand_loaded_event(self, event: GameEvent):
        """Handle hand loaded event."""
        data = event.data
        total_actions = data.get('num_actions', 0)
        
        print(f"🔥 CONSOLE: Hand loaded event - {total_actions} actions")
        
        # Reset progress
        self.progress_var.set(0)
        self.action_label_var.set(f"Action 0 of {total_actions}")
        
        # Update button states
        self.step_buttons['backward'].configure(state='disabled')
        self.step_buttons['forward'].configure(state='normal' if total_actions > 0 else 'disabled')
        self.step_buttons['reset'].configure(state='normal')
        
        # Enable Deal Flop button when hand is loaded
        self.deal_flop_button.config(state='normal')
        
        print(f"🔥 CONSOLE: Step Forward button state: {self.step_buttons['forward']['state']}")
        print(f"🔥 CONSOLE: Deal Flop button enabled")
    
    def _handle_annotation_added_event(self, event: GameEvent):
        """Handle annotation added event."""
        # Could add UI feedback for annotations
        pass
    
    # ==============================
    # PUBLIC INTERFACE
    # ==============================
    
    def update_font_size(self, new_size: int):
        """Update font size for the panel."""
        self.font_size = new_size
        
        # Update listbox font
        if self.hand_listbox:
            self.hand_listbox.configure(font=("Consolas", new_size))
    
    def get_current_hand_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently loaded hand."""
        if self.state_machine and hasattr(self.state_machine, 'current_hand_data'):
            return self.state_machine.current_hand_data.copy()
        return None
    
    def _on_deal_flop_clicked(self):
        """Handle Deal Flop button click."""
        print(f"🔥 CONSOLE: Deal Flop button clicked!")
        if self.state_machine and hasattr(self.state_machine, '_deal_historical_flop'):
            self.state_machine._deal_historical_flop()
            self.state_machine.current_state = PokerState.FLOP_BETTING
            self.state_machine._reset_bets_for_new_round()
            print(f"🔥 CONSOLE: Flop dealt, advanced to FLOP_BETTING")
            
            # Update button states
            self.deal_flop_button.config(state='disabled')
            self.deal_turn_button.config(state='normal')
            
            # Update progress display
            self.action_label_var.set("Flop dealt - FLOP_BETTING")
    
    def _on_deal_turn_clicked(self):
        """Handle Deal Turn button click."""
        print(f"🔥 CONSOLE: Deal Turn button clicked!")
        if self.state_machine and hasattr(self.state_machine, '_deal_historical_turn'):
            self.state_machine._deal_historical_turn()
            self.state_machine.current_state = PokerState.TURN_BETTING
            self.state_machine._reset_bets_for_new_round()
            print(f"🔥 CONSOLE: Turn dealt, advanced to TURN_BETTING")
            
            # Update button states
            self.deal_turn_button.config(state='disabled')
            self.deal_river_button.config(state='normal')
            
            # Update progress display
            self.action_label_var.set("Turn dealt - TURN_BETTING")
    
    def _on_deal_river_clicked(self):
        """Handle Deal River button click."""
        print(f"🔥 CONSOLE: Deal River button clicked!")
        if self.state_machine and hasattr(self.state_machine, '_deal_historical_river'):
            self.state_machine._deal_historical_river()
            self.state_machine.current_state = PokerState.RIVER_BETTING
            self.state_machine._reset_bets_for_new_round()
            print(f"🔥 CONSOLE: River dealt, advanced to RIVER_BETTING")
            
            # Update button states
            self.deal_river_button.config(state='disabled')
            
            # Update progress display
            self.action_label_var.set("River dealt - RIVER_BETTING")

#!/usr/bin/env python3
"""
Refactored Practice Session UI - Clean Architecture

This version properly utilizes the specialized PracticeSessionPokerWidget
and PracticeSessionPokerStateMachine, following clean inheritance patterns.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from datetime import datetime

# Import core components
from core.practice_session_poker_state_machine import PracticeSessionPokerStateMachine
from core.flexible_poker_state_machine import GameConfig, EventListener, GameEvent
from core.gui_models import StrategyData, THEME, FONTS
from core.types import Player, ActionType

# Import specialized components
from ui.components.practice_session_poker_widget import PracticeSessionPokerWidget


class PracticeSessionUI(ttk.Frame, EventListener):
    """
    A clean practice session UI that properly leverages specialized components:
    - Uses PracticeSessionPokerWidget for table display
    - Uses PracticeSessionPokerStateMachine for game logic
    - Focuses on session management and educational features
    """
    
    def __init__(self, parent, strategy_data: StrategyData, poker_config=None, **kwargs):
        from core.session_logger import get_session_logger
        
        super().__init__(parent, **kwargs)
        
        # Get logger instance
        try:
            self.logger = get_session_logger()
            self.logger.log_system("INFO", "PRACTICE_UI_INIT", "PracticeSessionUI initialization started", {
                "strategy_data": bool(strategy_data)
            })
        except Exception as e:
            print(f"⚠️ Could not get logger in PracticeSessionUI init: {e}")
            self.logger = None
        
        self.strategy_data = strategy_data
        self.session_start_time = datetime.now()
        
        # Initialize specialized state machine with GUI config or defaults
        if poker_config:
            config = poker_config
            if self.logger:
                self.logger.log_system("INFO", "PRACTICE_UI_INIT", "Using provided poker configuration", {
                    "num_players": config.num_players,
                    "big_blind": config.big_blind,
                    "small_blind": config.small_blind,
                    "starting_stack": config.starting_stack
                })
        else:
            # Fallback to defaults if no config provided (use standard GameConfig defaults)
            config = GameConfig(
                num_players=6,
                big_blind=2.0,  # Standard $2 big blind (no floating point)
                small_blind=1.0,  # Standard $1 small blind (no floating point)
                starting_stack=200.0
            )
            if self.logger:
                self.logger.log_system("DEBUG", "PRACTICE_UI_CONFIG", f"Using default config: starting_stack={config.starting_stack}", {})
            if self.logger:
                self.logger.log_system("INFO", "PRACTICE_UI_INIT", "Using default poker configuration", {
                    "num_players": config.num_players,
                    "big_blind": config.big_blind,
                    "small_blind": config.small_blind,
                    "starting_stack": config.starting_stack
                })
        
        if self.logger:
            self.logger.log_system("INFO", "PRACTICE_UI_INIT", "Creating PracticeSessionPokerStateMachine", {
                "num_players": config.num_players,
                "big_blind": config.big_blind,
                "small_blind": config.small_blind,
                "starting_stack": config.starting_stack
            })
        
        try:
            if self.logger:
                self.logger.log_system("DEBUG", "PRACTICE_UI_CONFIG", f"Creating state machine with config starting_stack={config.starting_stack}", {})
            self.state_machine = PracticeSessionPokerStateMachine(config, strategy_data)
            if self.logger:
                self.logger.log_system("DEBUG", "PRACTICE_UI_CONFIG", "State machine created, checking player stacks", {})
                for i, p in enumerate(self.state_machine.game_state.players):
                    self.logger.log_system("DEBUG", "PRACTICE_UI_CONFIG", f"Player {i+1}: ${p.stack}, is_human={p.is_human}", {})
            if self.logger:
                self.logger.log_system("INFO", "PRACTICE_UI_INIT", "PracticeSessionPokerStateMachine created successfully", {})
        except Exception as e:
            if self.logger:
                self.logger.log_system("ERROR", "PRACTICE_UI_INIT", f"Failed to create PracticeSessionPokerStateMachine: {e}", {
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })
            raise
        
        # Add this UI as an event listener
        if self.logger:
            self.logger.log_system("INFO", "PRACTICE_UI_INIT", "Adding UI as event listener", {})
        self.state_machine.add_event_listener(self)
        
        # Setup UI
        if self.logger:
            self.logger.log_system("INFO", "PRACTICE_UI_INIT", "Setting up UI components", {})
        self._setup_ui()
        
        if self.logger:
            self.logger.log_system("INFO", "PRACTICE_UI_INIT", "PracticeSessionUI initialization completed successfully", {})
        print("🎓 Practice Session UI ready")
        
        # Initialize table felt style after UI setup
        self._initialize_table_felt()
    
    def on_event(self, event: GameEvent):
        """Handle events from the specialized state machine."""
        try:
            # Handle practice-specific events
            if event.event_type == "practice_hand_started":
                self._handle_hand_started(event)
                # Start new hand with buttons disabled
                self._disable_action_buttons()
                # Update action buttons for new hand
                self._update_action_buttons_for_game_state()
                # Check if human should have action
                self._check_and_enable_human_turn()
            elif event.event_type == "practice_feedback":
                self._handle_practice_feedback(event)
            elif event.event_type == "practice_analysis":
                self._handle_practice_analysis(event)
            elif event.event_type == "practice_showdown_analysis":
                self._handle_showdown_analysis(event)
            elif event.event_type == "practice_stats_reset":
                pass  # Statistics panel removed
            elif event.event_type == "action_executed":
                # Add user-friendly action messages
                self._handle_action_message(event)
                # Disable buttons immediately after human action
                self._disable_action_buttons()
                # Update action buttons when game state changes
                self._update_action_buttons_for_game_state()
                # Check if it's now human's turn and enable buttons
                self._check_and_enable_human_turn()
                # Forward events to poker widget so it can handle button states
                if hasattr(self, 'poker_widget') and hasattr(self.poker_widget, 'on_event'):
                    self.poker_widget.on_event(event)
            elif event.event_type == "state_change":
                # Handle street transitions (flop, turn, river)
                self._handle_street_change_message(event)
                # Check button state on state changes
                self._check_and_enable_human_turn()
                # Forward to poker widget
                if hasattr(self, 'poker_widget') and hasattr(self.poker_widget, 'on_event'):
                    self.poker_widget.on_event(event)
            elif event.event_type == "hand_complete":
                # Handle showdown results
                self._handle_hand_complete_message(event)
                # Forward to poker widget
                if hasattr(self, 'poker_widget') and hasattr(self.poker_widget, 'on_event'):
                    self.poker_widget.on_event(event)
                # Make Start New Hand clickable immediately after hand ends
                self._enable_start_button()
                # Toast message to guide the user
                self._add_action_message("✅ Hand complete. Click START NEW HAND to continue.")
            elif event.event_type in ["action_required", "display_state_update"]:
                # Update action buttons when game state changes
                self._update_action_buttons_for_game_state()
                # Forward events to poker widget so it can handle button states
                if hasattr(self, 'poker_widget') and hasattr(self.poker_widget, 'on_event'):
                    self.poker_widget.on_event(event)
            else:
                # Forward all other events to the poker widget
                if hasattr(self, 'poker_widget') and hasattr(self.poker_widget, 'on_event'):
                    self.poker_widget.on_event(event)
                
        except Exception as e:
            print(f"⚠️ Error handling event {event.event_type}: {e}")
    
    def _setup_ui(self):
        """Setup the full-width layout with bottom control strip."""
        # Configure main layout - poker table takes full width, bottom strip for controls
        self.grid_rowconfigure(0, weight=1)  # Poker table area (expandable)
        self.grid_rowconfigure(1, weight=0)  # Bottom control strip (fixed height)
        self.grid_columnconfigure(0, weight=1)  # Full width
        
        # === TOP: Full-width Practice Poker Widget (Table Display) ===
        table_frame = ttk.Frame(self)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 0))
        
        # Use specialized practice session poker widget with session controls
        self.poker_widget = PracticeSessionPokerWidget(
            table_frame,
            state_machine=self.state_machine,
            strategy_data=self.strategy_data
        )
        
        # Pass session control callbacks to the poker widget
        self.poker_widget.set_session_callbacks(
            start_new_hand=self._start_new_hand
        )
        self.poker_widget.pack(fill=tk.BOTH, expand=True)
        
        # === BOTTOM: Control Strip (Session | Action Buttons | Statistics) ===
        self._setup_bottom_control_strip()
    
    def _setup_bottom_control_strip(self):
        """Setup the professional bottom control panel."""
        # Professional bottom panel with theme colors
        bottom_frame = tk.Frame(
            self,
            bg="#1E232A",  # Dark Slate background
            relief='flat',
            bd=0
        )
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        
        # Add top border for separation
        separator = tk.Frame(
            bottom_frame,
            bg="#2E4F76",  # Dark Steel Blue border
            height=2
        )
        separator.pack(fill="x", side="top")
        
        # Main panel content with proper padding
        content_frame = tk.Frame(
            bottom_frame,
            bg="#1E232A",  # Match panel background
            relief='flat',
            bd=0
        )
        content_frame.pack(fill="both", expand=True, padx=16, pady=8)
        
        # Configure four columns in content frame with professional spacing
        content_frame.grid_columnconfigure(0, weight=0, minsize=140)  # Left: Session controls (fixed)
        content_frame.grid_columnconfigure(1, weight=1, minsize=280)  # Center: Message area (expandable)
        content_frame.grid_columnconfigure(2, weight=0, minsize=220)  # Center-Right: Action buttons (fixed)
        content_frame.grid_columnconfigure(3, weight=0, minsize=160)  # Right: Bet buttons (fixed)
        content_frame.grid_rowconfigure(0, weight=1, minsize=80)  # Ensure consistent height
        
        # === LEFT: Session Controls ===
        session_frame = tk.Frame(
            content_frame,
            bg="#1E232A"  # Match panel background
        )
        session_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)
        self._setup_session_controls_bottom(session_frame)
        
        # === CENTER: Game Message Area ===
        message_frame = tk.Frame(
            content_frame,
            bg="#1E232A"  # Match panel background
        )
        message_frame.grid(row=0, column=1, sticky="nsew", padx=12, pady=0)
        self._setup_action_message_area(message_frame)
        
        # === CENTER-RIGHT: Action Buttons ===
        action_frame = tk.Frame(
            content_frame,
            bg="#1E232A"  # Match panel background
        )
        action_frame.grid(row=0, column=2, sticky="nsew", padx=12, pady=0)
        self._setup_action_buttons(action_frame)
        
        # === RIGHT: Quick Bet Buttons ===
        bet_buttons_frame = tk.Frame(
            content_frame,
            bg="#1E232A"  # Match panel background
        )
        bet_buttons_frame.grid(row=0, column=3, sticky="nsew", padx=(12, 0), pady=0)
        self._setup_quick_bet_buttons(bet_buttons_frame)
    
    def _setup_session_controls_bottom(self, parent):
        """Setup session controls with professional styling."""
        # Professional START NEW HAND button
        start_button = tk.Button(
            parent,
            text="START NEW HAND",
            bg='#4CAF50',  # Medium Green (professional)
            fg='#FFFFFF',  # White text
            font=('Segoe UI', 12, 'bold'),
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=20,
            pady=12,
            command=self._start_new_hand
        )
        start_button.pack(expand=True, fill='both', padx=4, pady=6)
        
        # Add hover effects
        def on_enter(e):
            start_button.config(bg='#5CCF63')  # Lighter green on hover
        
        def on_leave(e):
            start_button.config(bg='#4CAF50')  # Back to normal
        
        def on_click(e):
            start_button.config(relief='sunken')
            parent.after(100, lambda: start_button.config(relief='flat'))
        
        start_button.bind('<Enter>', on_enter)
        start_button.bind('<Leave>', on_leave)
        start_button.bind('<Button-1>', on_click)
        
        # Store reference for state management
        self.start_btn = start_button
    
    def _initialize_table_felt(self):
        """Initialize the table felt to the default casino-grade style."""
        try:
            from core.table_felt_styles import get_scheme_manager
            scheme_manager = get_scheme_manager()
            
            # Set the default table felt when poker widget is created
            if hasattr(self, 'poker_widget') and self.poker_widget:
                if hasattr(self.poker_widget, 'change_table_scheme'):
                    default_scheme = scheme_manager.get_current_scheme()
                    self.poker_widget.change_table_scheme(scheme=default_scheme)
                    print(f"🎨 Table felt initialized to {default_scheme.name}")
        except Exception as e:
            print(f"Warning: Could not initialize table felt: {e}")
        

    
    def _setup_action_message_area(self, parent):
        """Setup professional game message area."""
        # Create container with rounded appearance
        message_container = tk.Frame(
            parent,
            bg="#2B3845",  # Muted Navy Gray background
            relief='flat',
            bd=1,
            highlightbackground="#3A4B5C",  # Subtle border
            highlightthickness=1
        )
        message_container.pack(fill='both', expand=True, padx=6, pady=6)
        
        # Message text widget with professional styling
        self.action_message_text = tk.Text(
            message_container,
            height=2,
            bg="#2B3845",  # Muted Navy Gray
            fg="#EAECEE",  # Off-white text
            font=('Segoe UI', 11, 'normal'),  # Medium weight
            wrap=tk.WORD,
            state='disabled',
            relief='flat',
            borderwidth=0,
            insertbackground="#EAECEE",  # Cursor color
            selectbackground="#3980A6",  # Selection color (teal)
            padx=10,
            pady=6
        )
        self.action_message_text.pack(fill='both', expand=True)
        
        # Configure text alignment and spacing
        self.action_message_text.tag_configure("center", justify='center')
        self.action_message_text.tag_configure("vpad", spacing1=4, spacing3=4)
        
        # Initialize with welcome message
        self._add_action_message("Welcome! Start a new hand to begin playing.")
        
        # Store container reference for animations
        self.message_container = message_container
    
    def _add_action_message(self, message: str):
        """Add a message to the action message area (exactly 2 lines, well-centered)."""
        if hasattr(self, 'action_message_text'):
            self.action_message_text.config(state='normal')
            
            # Get current content and split into lines
            current_content = self.action_message_text.get("1.0", tk.END).strip()
            lines = current_content.split('\n') if current_content else []
            
            # Add new message
            lines.append(message)
            
            # Keep only the last 2 lines
            lines = lines[-2:]
            
            # Ensure we always have exactly 2 lines (pad with empty line if needed)
            while len(lines) < 2:
                lines.insert(0, "")  # Pad at the beginning for better centering
            
            # Clear and set new content
            self.action_message_text.delete("1.0", tk.END)
            content = '\n'.join(lines)
            self.action_message_text.insert("1.0", content)
            # Apply centering and vertical padding
            self.action_message_text.tag_add("center", "1.0", tk.END)
            self.action_message_text.tag_add("vpad", "1.0", tk.END)
            
            self.action_message_text.config(state='disabled')

    def _handle_action_message(self, event):
        """Convert action_executed events to user-friendly messages."""
        # Handle both data dict format and direct attribute format
        if hasattr(event, 'data') and event.data:
            player_name = event.data.get('player_name', 'Unknown')
            action = event.data.get('action', 'unknown')
            amount = event.data.get('amount', 0)
        else:
            # Direct attribute format (FPSM style)
            player_name = getattr(event, 'player_name', 'Unknown')
            action = getattr(event, 'action', 'unknown')
            amount = getattr(event, 'amount', 0)
            
            # Convert ActionType enum to string if needed
            if hasattr(action, 'value'):
                action = action.value
            
            # Enhanced action messages with emojis and amounts
            if action == 'fold':
                self._add_action_message(f"💤 {player_name} folds")
            elif action == 'check':
                self._add_action_message(f"✋ {player_name} checks")
            elif action == 'call':
                if amount > 0:
                    self._add_action_message(f"📞 {player_name} calls ${amount:.0f}")
                else:
                    self._add_action_message(f"📞 {player_name} calls")
            elif action == 'bet':
                self._add_action_message(f"💰 {player_name} bets ${amount:.0f}")
            elif action == 'raise':
                self._add_action_message(f"🚀 {player_name} raises to ${amount:.0f}")
            elif action == 'all_in':
                self._add_action_message(f"🔥 {player_name} goes ALL IN (${amount:.0f})")
            else:
                self._add_action_message(f"🎯 {player_name} {action}")

    def _handle_street_change_message(self, event):
        """Convert state_change events to street transition messages."""
        if hasattr(event, 'data') and event.data:
            new_state = event.data.get('new_state', '')
            if 'DEAL_FLOP' in new_state:
                # Get board cards from state machine
                if hasattr(self, 'state_machine'):
                    board = getattr(self.state_machine.game_state, 'board', [])
                    if len(board) >= 3:
                        flop = ' '.join(board[:3])
                        self._add_action_message(f"🃏 Flop: {flop}")
            elif 'DEAL_TURN' in new_state:
                if hasattr(self, 'state_machine'):
                    board = getattr(self.state_machine.game_state, 'board', [])
                    if len(board) >= 4:
                        turn = board[3]
                        self._add_action_message(f"🃏 Turn: {turn}")
            elif 'DEAL_RIVER' in new_state:
                if hasattr(self, 'state_machine'):
                    board = getattr(self.state_machine.game_state, 'board', [])
                    if len(board) >= 5:
                        river = board[4]
                        self._add_action_message(f"🃏 River: {river}")

    def _handle_hand_complete_message(self, event):
        """Convert hand_complete events to showdown result messages with best 5 cards."""
        if hasattr(event, 'data') and event.data:
            winner_info = event.data.get('winner_info', {})
            winner = winner_info.get('name') or event.data.get('winner', 'Unknown')
            pot_amount = event.data.get('pot_amount', 0)
            hand_desc = winner_info.get('hand_description') or event.data.get('winning_hand', '')
            best_five = winner_info.get('best_five', [])
            if best_five:
                best_five_str = ' '.join(best_five)
                self._add_action_message(f"🏆 {winner} wins ${pot_amount:.2f} with {hand_desc} ({best_five_str})")
            else:
                self._add_action_message(f"🏆 {winner} wins ${pot_amount:.2f} with {hand_desc}")
    
    def _setup_quick_bet_buttons(self, parent):
        """Setup quick bet buttons for faster gameplay."""
        # Add padding frame for consistent spacing
        padding_frame = tk.Frame(parent, bg=THEME["secondary_bg"])
        padding_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Quick bet buttons panel
        bet_panel = tk.Frame(padding_frame, bg=THEME["secondary_bg"])
        bet_panel.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid for quick bet buttons (2x4 layout - 8 buttons total)
        for c in range(4):
            bet_panel.grid_columnconfigure(c, weight=1)
        for r in range(2):
            bet_panel.grid_rowconfigure(r, weight=1)
        
        # Quick bet buttons using Frame+Label pattern
        bet_buttons_data = [
            ("1/4 POT", "quarter", 0, 0),
            ("1/3 POT", "one_third", 0, 1),
            ("1/2 POT", "half", 0, 2),
            ("3/4 POT", "three_quarters", 0, 3),
            ("2/3 POT", "two_thirds", 1, 0),
            ("POT", "pot", 1, 1),
            ("2x POT", "two_x_pot", 1, 2),
            ("ALL IN", "all_in", 1, 3)
        ]
        
        self.quick_bet_buttons = {}
        
        for text, key, row, col in bet_buttons_data:
            # Warm orange-brown for bet chips by spec
            base_color = "#BF682D"
            
            # Create frame
            bet_frame = tk.Frame(
                bet_panel,
                bg=base_color,
                relief='flat',
                bd=0,
                cursor='hand2'
            )
            bet_frame.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            
            # Create label
            bet_label = tk.Label(
                bet_frame,
                text=text,
                bg=base_color,
                fg='white',
                font=('Segoe UI', 11, 'bold'),
                cursor='hand2'
            )
            bet_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

            # Hover and selection effects
            hover_color = "#D97B3A"  # lighten on hover
            selected_outline = "#FFD700"

            def make_hover_handlers(frame=bet_frame, label=bet_label, normal=base_color, hover=hover_color):
                def on_enter(_):
                    frame.config(bg=hover)
                    label.config(bg=hover)
                def on_leave(_):
                    # restore unless selected
                    if getattr(frame, 'is_selected', False):
                        return
                    frame.config(bg=normal)
                    label.config(bg=normal)
                return on_enter, on_leave

            on_enter, on_leave = make_hover_handlers()
            bet_frame.bind('<Enter>', on_enter)
            bet_frame.bind('<Leave>', on_leave)
            bet_label.bind('<Enter>', on_enter)
            bet_label.bind('<Leave>', on_leave)
            
            # Bind click events
            def on_click_factory(bet_type, frame=bet_frame):
                def _on_click(_):
                    # clear selection visuals
                    for k, f in getattr(self, 'quick_bet_buttons', {}).items():
                        f.is_selected = False
                        f.config(highlightthickness=0)
                    # select this
                    frame.is_selected = True
                    frame.config(highlightthickness=2, highlightbackground=selected_outline)
                    self._handle_quick_bet(bet_type)
                return _on_click

            bet_frame.bind("<Button-1>", on_click_factory(key))
            bet_label.bind("<Button-1>", on_click_factory(key))
            
            # Store reference
            self.quick_bet_buttons[key] = bet_frame
    
    def _setup_action_buttons(self, parent):
        """Setup professional action buttons."""
        # Professional button container
        button_container = tk.Frame(parent, bg="#1E232A")
        button_container.pack(fill='both', expand=True, padx=6, pady=6)
        
        # Action buttons panel
        action_panel = tk.Frame(button_container, bg="#1E232A")
        action_panel.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid for equal button distribution
        for i in range(3):  # 3 action buttons only (CHECK, FOLD, BET/RAISE)
            action_panel.grid_columnconfigure(i, weight=1)
        
        # CHECK/CALL button with professional styling
        check_frame = tk.Frame(
            action_panel,
            bg='#3980A6',  # Teal Blue
            relief='flat',
            bd=0,
            cursor='hand2'
        )
        check_frame.grid(row=0, column=0, padx=3, pady=3, sticky="ew", ipadx=10, ipady=8)
        
        check_label = tk.Label(
            check_frame,
            text="CHECK",
            bg='#3980A6',  # Teal Blue
            fg='#FFFFFF',  # White text
            font=('Segoe UI', 11, 'bold'),
            cursor='hand2'
        )
        check_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=8)
        
        # Bind click events to both frame and label with focus protection
        check_frame.bind("<Button-1>", lambda e: self._handle_action_click('check_call'))
        check_label.bind("<Button-1>", lambda e: self._handle_action_click('check_call'))
        
        # DISABLE KEYBOARD TRIGGERS to prevent accidental activation
        check_frame.bind("<Key>", lambda e: "break")  # Block all keyboard events
        check_label.bind("<Key>", lambda e: "break")  # Block all keyboard events
        check_frame.focus_set = lambda: None  # Disable focus
        check_label.focus_set = lambda: None  # Disable focus
        
        check_button = check_frame  # Reference for enable/disable
        
        # FOLD button with professional styling
        fold_frame = tk.Frame(
            action_panel,
            bg='#757575',  # Gray
            relief='flat',
            bd=0,
            cursor='hand2'
        )
        fold_frame.grid(row=0, column=1, padx=3, pady=3, sticky="ew", ipadx=10, ipady=8)
        
        fold_label = tk.Label(
            fold_frame,
            text="FOLD",
            bg='#757575',  # Gray
            fg='#FFFFFF',  # White text
            font=('Segoe UI', 11, 'bold'),
            cursor='hand2'
        )
        fold_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=8)
        
        # Bind click events to both frame and label with focus protection
        fold_frame.bind("<Button-1>", lambda e: self._handle_action_click('fold'))
        fold_label.bind("<Button-1>", lambda e: self._handle_action_click('fold'))
        
        # DISABLE KEYBOARD TRIGGERS to prevent accidental activation
        fold_frame.bind("<Key>", lambda e: "break")  # Block all keyboard events
        fold_label.bind("<Key>", lambda e: "break")  # Block all keyboard events
        fold_frame.focus_set = lambda: None  # Disable focus
        fold_label.focus_set = lambda: None  # Disable focus
        
        fold_button = fold_frame  # Reference for enable/disable
        
        # BET/RAISE button with professional styling
        bet_frame = tk.Frame(
            action_panel,
            bg='#E53935',  # Bright Red
            relief='flat',
            bd=0,
            cursor='hand2'
        )
        bet_frame.grid(row=0, column=2, padx=3, pady=3, sticky="ew", ipadx=10, ipady=8)
        
        bet_label = tk.Label(
            bet_frame,
            text="RAISE",
            bg='#E53935',  # Bright Red
            fg='#FFFFFF',  # White text
            font=('Segoe UI', 11, 'bold'),
            cursor='hand2'
        )
        bet_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=8)
        
        # Bind click events to both frame and label with focus protection
        bet_frame.bind("<Button-1>", lambda e: self._handle_action_click('bet_raise'))
        bet_label.bind("<Button-1>", lambda e: self._handle_action_click('bet_raise'))
        
        # DISABLE KEYBOARD TRIGGERS to prevent accidental activation
        bet_frame.bind("<Key>", lambda e: "break")  # Block all keyboard events
        bet_label.bind("<Key>", lambda e: "break")  # Block all keyboard events
        bet_frame.focus_set = lambda: None  # Disable focus
        bet_label.focus_set = lambda: None  # Disable focus
        
        bet_button = bet_frame  # Reference for enable/disable
        
        # Store button references and original colors for enabling/disabling
        self.action_buttons = {
            'check_call': check_button,
            'fold': fold_button,
            'bet_raise': bet_button
        }
        
        # Store original colors for restoring when enabling
        self.original_button_colors = {
            'check_call': THEME['button_check'],
            'fold': THEME['button_fold'], 
            'bet_raise': THEME['button_raise']
        }
        
        # Store labels for color updates
        self.action_button_labels = {
            'check_call': check_label,
            'fold': fold_label,
            'bet_raise': bet_label
        }
        
        # Store label references and original colors for restoration
        self.action_labels = {
            'check_call': check_label,
            'fold': fold_label,
            'bet_raise': bet_label
        }
        
        self.button_colors = {
            'check_call': THEME['button_check'],
            'fold': THEME['button_fold'],
            'bet_raise': THEME['button_raise']
        }
        
        # Store original button configurations for dynamic updates
        self.button_configs = {
            'check': {'text': 'CHECK', 'color': THEME['button_check']},
            'call': {'text': 'CALL', 'color': THEME.get('button_call', THEME['button_check'])},
            'bet': {'text': 'BET', 'color': THEME['button_raise']},
            'raise': {'text': 'RAISE', 'color': THEME['button_raise']}
        }
        
        # Start with buttons disabled until it's human's turn
        self._disable_action_buttons()
        # Set initial button state (will show CHECK/BET/FOLD by default) 
        self._update_action_buttons_for_game_state()
    
    def _disable_action_buttons(self):
        """Disable all action buttons - only human's turn should enable them."""
        disabled_color = '#2A2A2A'  # Dark gray for disabled state
        disabled_text_color = '#666666'  # Gray text for disabled state
        
        print("🔒 DISABLING all action buttons")
        
        for button_key, button_frame in self.action_buttons.items():
            if hasattr(button_frame, 'config'):
                button_frame.config(bg=disabled_color, cursor='', relief='flat')
                
            # Disable the label inside the frame
            if button_key in self.action_button_labels:
                label = self.action_button_labels[button_key]
                if hasattr(label, 'config'):
                    label.config(bg=disabled_color, fg=disabled_text_color, cursor='')
            
            # Unbind all click events to make truly non-clickable
            button_frame.unbind("<Button-1>")
            if button_key in self.action_button_labels:
                self.action_button_labels[button_key].unbind("<Button-1>")
    
    def _enable_action_buttons(self):
        """Enable action buttons for human player's turn."""
        print("🔓 ENABLING action buttons for human turn")
        
        for button_key, button_frame in self.action_buttons.items():
            # Restore original colors
            original_color = self.original_button_colors.get(button_key, THEME['button_check'])
            
            if hasattr(button_frame, 'config'):
                button_frame.config(bg=original_color, cursor='hand2', relief='raised')
                
            # Enable the label inside the frame
            if button_key in self.action_button_labels:
                label = self.action_button_labels[button_key]
                if hasattr(label, 'config'):
                    label.config(bg=original_color, fg='white', cursor='hand2')
            
            # Re-bind click events with proper closure
            def make_handler(action):
                return lambda e: self._handle_action_click(action)
            
            handler = make_handler(button_key)
            button_frame.bind("<Button-1>", handler)
            if button_key in self.action_button_labels:
                self.action_button_labels[button_key].bind("<Button-1>", handler)

    def _check_and_enable_human_turn(self):
        """Check if it's human's turn and enable buttons accordingly."""
        if not hasattr(self, 'state_machine') or not self.state_machine:
            return
            
        try:
            # Check if game is in a valid state for human actions
            if hasattr(self.state_machine, 'current_state'):
                invalid_states = ['END_HAND', 'SHOWDOWN', 'START_HAND']
                state_name = str(self.state_machine.current_state).split('.')[-1]
                if state_name in invalid_states:
                    print(f"🔒 Keeping buttons disabled - game in {state_name} state")
                    return
            
            # Check if current player is human
            current_player = self.state_machine.get_action_player()
            if current_player and hasattr(current_player, 'is_human') and current_player.is_human:
                print(f"🔓 Human turn detected - enabling buttons for {current_player.name}")
                self._enable_action_buttons()
            else:
                player_name = getattr(current_player, 'name', 'Unknown') if current_player else 'None'
                print(f"🔒 Not human turn - keeping buttons disabled (current: {player_name})")
                
        except Exception as e:
            print(f"⚠️ Error checking human turn: {e}")

    def _handle_action_click(self, action_key: str):
        """Handle action button clicks directly with anti-auto-click protection."""
        import time
        
        # ANTI-AUTO-CLICK PROTECTION: Add small delay and confirmation
        current_time = time.time()
        if hasattr(self, '_last_action_time') and hasattr(self, '_last_action_key'):
            time_since_last = current_time - self._last_action_time
            
            # Block rapid clicks (within 500ms)
            if time_since_last < 0.5:
                print(f"🛡️ AUTO-CLICK PROTECTION: Action blocked (too fast: {time_since_last:.3f}s)")
                if self.logger:
                    self.logger.log_system("WARNING", "PRACTICE_UI_ACTION", f"Action blocked - too fast: {time_since_last:.3f}s", {"action": action_key})
                return
            
            # Block repeated identical actions within 2 seconds (likely accidental/auto-clicks)
            if self._last_action_key == action_key and time_since_last < 2.0:
                print(f"🛡️ REPEAT-CLICK PROTECTION: Identical action blocked (repeated {action_key} within {time_since_last:.3f}s)")
                if self.logger:
                    self.logger.log_system("WARNING", "PRACTICE_UI_ACTION", f"Action blocked - repeated {action_key} within {time_since_last:.3f}s", {"action": action_key})
                return
        
        self._last_action_time = current_time
        self._last_action_key = action_key
        
        if self.logger:
            self.logger.log_system("DEBUG", "PRACTICE_UI_ACTION", f"Action button clicked: {action_key}", {"timestamp": current_time})
        
        print(f"🎯 HUMAN ACTION: {action_key} button clicked at {current_time}")
        
        # ADDITIONAL DEBUGGING: Log call stack to see what triggered this
        import traceback
        stack_trace = ''.join(traceback.format_stack()[-3:-1])  # Get last 2 stack frames
        print(f"📋 ACTION TRIGGERED BY:\\n{stack_trace}")
        
        if not hasattr(self, 'state_machine') or not self.state_machine:
            if self.logger:
                self.logger.log_system("WARNING", "PRACTICE_UI_ACTION", "No state machine available", {})
            return
        
        # Check if game is in a valid state for human actions
        if hasattr(self.state_machine, 'current_state'):
            invalid_states = ['END_HAND', 'SHOWDOWN', 'START_HAND']
            if str(self.state_machine.current_state).split('.')[-1] in invalid_states:
                print(f"🚫 ACTION BLOCKED: Game in {self.state_machine.current_state} state")
                if self.logger:
                    self.logger.log_system("WARNING", "PRACTICE_UI_ACTION", f"Action blocked - invalid state: {self.state_machine.current_state}", {"action": action_key})
                return
        
        # Check if it's the human player's turn
        current_player = self.state_machine.get_action_player()
        if not current_player:
            if self.logger:
                self.logger.log_system("DEBUG", "PRACTICE_UI_ACTION", "No current player", {})
            return
        
        # Robust type checking - ensure we have a Player object
        if not hasattr(current_player, 'is_human') or isinstance(current_player, str):
            if self.logger:
                self.logger.log_system("ERROR", "PRACTICE_UI_ACTION", f"current_player is {type(current_player)}, not Player object: {current_player}", {})
                self.logger.log_system("ERROR", "PRACTICE_UI_ACTION", f"Action player index: {getattr(self.state_machine, 'action_player_index', 'unknown')}, Players count: {len(getattr(self.state_machine.game_state, 'players', []))}", {})
            return
            
        if not current_player.is_human:
            print(f"🚫 ACTION BLOCKED: Not human's turn (current: {getattr(current_player, 'name', 'Unknown')})")
            if self.logger:
                self.logger.log_system("WARNING", "PRACTICE_UI_ACTION", f"Action blocked - not human's turn: {getattr(current_player, 'name', 'Unknown')}", {"action": action_key})
            return
            
        if self.logger:
            self.logger.log_system("DEBUG", "PRACTICE_UI_ACTION", f"Human player's turn, executing action: {action_key}", {})
        
        # Determine the action and amount based on the button clicked
        if action_key == 'check_call':
            # Check if we need to call or check
            current_bet = getattr(self.state_machine.game_state, 'current_bet', 0)
            player_bet = getattr(current_player, 'current_bet', 0)
            call_amount = current_bet - player_bet
            if self.logger:
                self.logger.log_system("DEBUG", "PRACTICE_UI_ACTION", f"Bet calculation: current_bet={current_bet}, player_bet={player_bet}, call_amount={call_amount}", {})
            
            if call_amount > 0:
                action = 'call'
                amount = call_amount
            else:
                action = 'check'
                amount = 0
        elif action_key == 'fold':
            action = 'fold'
            amount = 0
        elif action_key == 'bet_raise':
            # Use the current bet amount set by bet size controls
            amount = getattr(self, 'current_bet_amount', self.state_machine.config.big_blind * 2)
            current_bet = getattr(self.state_machine.game_state, 'current_bet', 0)
            if current_bet > 0:
                action = 'raise'
            else:
                action = 'bet'
        else:
            if self.logger:
                self.logger.log_system("WARNING", "PRACTICE_UI_ACTION", f"Unknown action: {action_key}", {})
            return
        
        # Execute the action through the state machine
        try:
            if self.logger:
                self.logger.log_system("INFO", "PRACTICE_UI_ACTION", f"Executing {action} with amount {amount}", {})
            
            # Convert string action to ActionType enum
            action_type_map = {
                'fold': ActionType.FOLD,
                'check': ActionType.CHECK, 
                'call': ActionType.CALL,
                'bet': ActionType.BET,
                'raise': ActionType.RAISE
            }
            action_type = action_type_map.get(action)
            if not action_type:
                if self.logger:
                    self.logger.log_system("ERROR", "PRACTICE_UI_ACTION", f"Unknown action type: {action}", {})
                return
                
            # Final safety check before executing action
            if not isinstance(current_player, Player):
                if self.logger:
                    self.logger.log_system("ERROR", "PRACTICE_UI_ACTION", f"Final check failed: current_player is {type(current_player)}, expected Player object", {})
                return
            
            # CRITICAL DEBUGGING: Log the actual action execution
            print(f"🚨 EXECUTING ACTION: {current_player.name} ({action_type.value}) ${amount}")
            print(f"   Player is human: {current_player.is_human}")
            print(f"   Action player index: {self.state_machine.action_player_index}")
            
            self.state_machine.execute_action(current_player, action_type, amount)
            
            print(f"✅ ACTION COMPLETED: {action_type.value} executed successfully")
            
            # Immediately disable buttons after human action
            print("🔒 Disabling buttons after human action")
            self._disable_action_buttons()
        except Exception as e:
            if self.logger:
                self.logger.log_system("ERROR", "PRACTICE_UI_ACTION", f"Error executing action: {e}", {})
    
    def _handle_quick_bet(self, bet_type: str):
        """Handle quick bet button clicks and delegate calculation to state machine."""
        try:
            # Delegate bet calculation to the state machine (proper architecture)
            if hasattr(self, 'state_machine') and self.state_machine:
                bet_amount = self.state_machine.calculate_quick_bet_amount(bet_type)
                self.current_bet_amount = bet_amount
                
                # Execute the appropriate action based on bet type
                if bet_type == "all_in":
                    self._handle_action_click('all_in')
                else:
                    self._handle_action_click('bet_raise')
                    
                print(f"🎯 Quick bet executed: {bet_type} = ${bet_amount}")
            else:
                print("⚠️ No state machine available for bet calculation")
                self.current_bet_amount = 10  # Safe fallback
            
        except Exception as e:
            print(f"⚠️ Error handling quick bet: {e}")
            # Set a default bet amount if calculation fails
            self.current_bet_amount = 10
    
    def _enable_action_buttons(self):
        """Enable action buttons for human player interaction."""
        for key, button_frame in self.action_buttons.items():
            # Restore original colors for frames
            original_color = self.button_colors[key]
            button_frame.config(relief='raised', bg=original_color)
            
            # Restore original colors for labels
            if key in self.action_labels:
                self.action_labels[key].config(bg=original_color, fg='white')
    
    def _disable_action_buttons(self):
        """Disable action buttons (not human player's turn)."""
        disabled_color = THEME['button_fold']  # Use theme gray
        disabled_text = THEME['text_muted']    # Use theme muted text
        
        for key, button_frame in self.action_buttons.items():
            # Set disabled appearance for frames
            button_frame.config(relief='sunken', bg=disabled_color)
            
            # Set disabled appearance for labels
            if key in self.action_labels:
                self.action_labels[key].config(bg=disabled_color, fg=disabled_text)

    # Old session controls method removed - using bottom control strip instead
    
    def _setup_educational_panel(self, parent):
        """Setup educational features panel."""
        edu_frame = ttk.LabelFrame(parent, text="Educational Features", padding=10)
        edu_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Educational content display
        self.edu_text = tk.Text(
            edu_frame,
            height=8,
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            font=FONTS["small"],
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.edu_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Educational content scrollbar
        edu_scrollbar = ttk.Scrollbar(edu_frame, orient=tk.VERTICAL, command=self.edu_text.yview)
        edu_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.edu_text.config(yscrollcommand=edu_scrollbar.set)
        
        # Quick analysis buttons
        analysis_frame = ttk.Frame(edu_frame)
        analysis_frame.pack(fill=tk.X)
        
        ttk.Button(
            analysis_frame,
            text="💡 Get Hint",
            command=self._get_strategy_hint,
            width=12
        ).pack(side=tk.LEFT, padx=(0, 2))
        
        ttk.Button(
            analysis_frame,
            text="📊 Hand Analysis",
            command=self._analyze_current_hand,
            width=12
        ).pack(side=tk.LEFT, padx=(2, 0))
    
    def _setup_statistics_panel(self, parent):
        """Setup session statistics panel."""
        stats_frame = ttk.LabelFrame(parent, text="Session Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Statistics display
        self.stats_text = tk.Text(
            stats_frame,
            height=6,
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            font=FONTS["small"],
            state=tk.DISABLED
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Initialize statistics display
        self._update_session_stats()
    
    def _start_new_hand(self):
        """Start a new practice hand using the specialized state machine."""
        try:
            print("🎓 Starting new practice hand...")
            self.state_machine.start_hand()
            
            # Update UI state
            self._disable_start_button()
            self._add_educational_message("🎯 New hand started! Observe the cards and consider your position.")
            
        except Exception as e:
            print(f"❌ Error starting new hand: {e}")
            messagebox.showerror("Error", f"Failed to start new hand: {e}")
    
    def _reset_session(self):
        """Reset the practice session."""
        if messagebox.askyesno("Reset Session", "Are you sure you want to reset the practice session?"):
            try:
                # Reset state machine
                self.state_machine.reset_practice_stats()
                
                # Reset poker widget
                if hasattr(self.poker_widget, 'reset_practice_session'):
                    self.poker_widget.reset_practice_session()
                
                # Reset UI
                self._enable_start_button()
                self._clear_educational_content()
                self._update_session_stats()
                
                print("🔄 Practice session reset")
                
            except Exception as e:
                print(f"❌ Error resetting session: {e}")
                messagebox.showerror("Error", f"Failed to reset session: {e}")
    
    def _toggle_coaching_mode(self):
        """Toggle coaching mode on/off."""
        enabled = self.coaching_var.get()
        
        if hasattr(self.poker_widget, 'enable_coaching_mode'):
            self.poker_widget.enable_coaching_mode(enabled)
        
        mode_text = "enabled" if enabled else "disabled"
        self._add_educational_message(f"🎓 Coaching mode {mode_text}")
    
    def _get_strategy_hint(self):
        """Get a strategy hint for the current situation."""
        try:
            # Delegate to state machine's encapsulated method
            human_player = self.state_machine.get_human_player()
            
            if human_player:
                suggestion = self.state_machine.get_strategy_suggestion(human_player)
                if suggestion:
                    self._add_educational_message(f"💡 Strategy Hint: {suggestion}")
                else:
                    self._add_educational_message("💡 No specific hint available for current situation.")
            else:
                self._add_educational_message("💡 Start a hand first to get strategy hints.")
                
        except Exception as e:
            print(f"⚠️ Error getting strategy hint: {e}")
    
    def _analyze_current_hand(self):
        """Analyze the current hand situation."""
        try:
            # Delegate to state machine's encapsulated analysis method
            analysis = self.state_machine.get_current_analysis()
            self._add_educational_message(analysis)
                
        except Exception as e:
            print(f"⚠️ Error analyzing current hand: {e}")
    
    def _handle_hand_started(self, event: GameEvent):
        """Handle practice hand started event."""
        if event.data:
            hand_num = event.data.get("hand_number", 0)
            position = event.data.get("your_position", "Unknown")
            
            message = f"🎯 Hand #{hand_num} started! You are in {position} position."
            self._add_educational_message(message)
        
        # Re-enable start button when hand is complete
        self._enable_start_button()
    
    def _handle_practice_feedback(self, event: GameEvent):
        """Handle practice feedback events."""
        if hasattr(event, 'data') and event.data and 'feedback' in event.data:
            feedback = event.data['feedback']
            self._add_educational_message(f"🎓 Feedback: {feedback}")
    
    def _handle_practice_analysis(self, event: GameEvent):
        """Handle practice analysis events."""
        if hasattr(event, 'data') and event.data and 'analysis' in event.data:
            analysis = event.data['analysis']
            self._add_educational_message(f"💡 Analysis: {analysis}")
    
    def _handle_showdown_analysis(self, event: GameEvent):
        """Handle showdown analysis events."""
        if hasattr(event, 'data') and event.data:
            result = event.data.get('result', 'unknown')
            lesson = event.data.get('lesson', '')
            
            message = f"🎯 Hand Result: You {result}!\n💡 Lesson: {lesson}"
            self._add_educational_message(message)
        
        # Display showdown analysis in poker widget too
        if hasattr(self.poker_widget, 'display_showdown_analysis'):
            self.poker_widget.display_showdown_analysis(event.data)
    
    def _add_educational_message(self, message: str):
        """Add a message to the educational content area - DISABLED (Educational Features removed)."""
        # Educational features have been removed, this method is now a no-op
        pass
    
    def _clear_educational_content(self):
        """Clear the educational content area - DISABLED (Educational Features removed)."""
        # Educational features have been removed, this method is now a no-op
        pass
    
    def _update_session_stats(self):
        """Update the session statistics display."""
        try:
            stats = self.state_machine.get_practice_stats()
            session_duration = datetime.now() - self.session_start_time
            
            stats_text = f"""Session Duration: {str(session_duration).split('.')[0]}
Hands Played: {stats['hands_played']}
Hands Won: {stats['hands_won']}
Hands Lost: {stats['hands_lost']}
Win Rate: {stats['win_rate']:.1f}%

Total Decisions: {stats['decisions_made']}
Correct Decisions: {stats['correct_decisions']}
Decision Accuracy: {stats['decision_accuracy']:.1f}%

Total Winnings: ${stats['total_winnings']:.2f}
"""
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            self.stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"⚠️ Error updating session stats: {e}")
    
    def update_poker_config(self, new_config):
        """Update the poker configuration for the practice session."""
        try:
            if self.logger:
                self.logger.log_system("INFO", "PRACTICE_UI_CONFIG", "Updating poker configuration", {
                    "old_big_blind": self.state_machine.config.big_blind,
                    "new_big_blind": new_config.big_blind,
                    "old_small_blind": self.state_machine.config.small_blind,
                    "new_small_blind": new_config.small_blind,
                    "old_starting_stack": self.state_machine.config.starting_stack,
                    "new_starting_stack": new_config.starting_stack
                })
            
            # Update the state machine configuration
            self.state_machine.config = new_config
            
            # Reset stacks for all players to the new starting amount
            for player in self.state_machine.game_state.players:
                player.stack = new_config.starting_stack
            
            # Force UI refresh to show new values
            if hasattr(self, 'poker_widget'):
                self.poker_widget.force_display_update()
                
            self._add_educational_message(f"🔧 Updated game settings: ${new_config.small_blind}/${new_config.big_blind} blinds, ${new_config.starting_stack} starting stack")
            
        except Exception as e:
            if self.logger:
                self.logger.log_system("ERROR", "PRACTICE_UI_CONFIG", f"Error updating poker configuration: {e}", {})
            print(f"⚠️ Error updating poker configuration: {e}")

    def update_font_size(self, font_size: int):
        """Update font sizes for all text widgets in the practice session UI."""
        try:
            new_font = (FONTS["main"][0], font_size)
            
            # Update game message area font to sync with app font size
            if hasattr(self, 'action_message_text') and self.action_message_text:
                self.action_message_text.config(font=new_font)
            
            # Update educational panel if it exists
            if hasattr(self, 'edu_text') and self.edu_text:
                self.edu_text.config(font=new_font)
            
            # Update statistics panel if it exists
            if hasattr(self, 'stats_text') and self.stats_text:
                self.stats_text.config(font=new_font)
            
            # Also update poker widget font size
            if hasattr(self, 'poker_widget') and hasattr(self.poker_widget, 'update_font_size'):
                self.poker_widget.update_font_size(font_size)
        except Exception as e:
            print(f"⚠️ Error updating font size: {e}")
    
    def increase_table_size(self):
        """Increase the poker table size."""
        if self.logger:
            self.logger.log_system("DEBUG", "PRACTICE_UI_TABLE_SIZE", "increase_table_size() called", {})
        if hasattr(self, 'poker_widget') and self.poker_widget:
            if hasattr(self.poker_widget, 'increase_table_size'):
                self.poker_widget.increase_table_size()
                if self.logger:
                    self.logger.log_system("DEBUG", "PRACTICE_UI_TABLE_SIZE", "Table size increased", {})
            else:
                if self.logger:
                    self.logger.log_system("WARNING", "PRACTICE_UI_TABLE_SIZE", "poker_widget missing increase_table_size method", {})
        else:
            if self.logger:
                self.logger.log_system("WARNING", "PRACTICE_UI_TABLE_SIZE", "poker_widget does not exist", {})

    def decrease_table_size(self):
        """Decrease the poker table size."""
        if self.logger:
            self.logger.log_system("DEBUG", "PRACTICE_UI_TABLE_SIZE", "decrease_table_size() called", {})
        if hasattr(self, 'poker_widget') and self.poker_widget:
            if hasattr(self.poker_widget, 'decrease_table_size'):
                self.poker_widget.decrease_table_size()
                if self.logger:
                    self.logger.log_system("DEBUG", "PRACTICE_UI_TABLE_SIZE", "Table size decreased", {})
            else:
                if self.logger:
                    self.logger.log_system("WARNING", "PRACTICE_UI_TABLE_SIZE", "poker_widget missing decrease_table_size method", {})
        else:
            if self.logger:
                self.logger.log_system("WARNING", "PRACTICE_UI_TABLE_SIZE", "poker_widget does not exist", {})
    
    def change_table_felt(self, felt_color: str):
        """Change the poker table felt color."""
        if hasattr(self.poker_widget, 'change_table_felt'):
            self.poker_widget.change_table_felt(felt_color)
    
    def _disable_start_button(self):
        """Disable the start button (professional Button implementation)."""
        if hasattr(self, 'start_btn'):
            self.start_btn.config(
                bg='#388E3C',  # Darker green disabled state
                fg='#CCCCCC',  # Light gray dimmed text
                state='disabled',
                cursor=''
            )
    
    def _enable_start_button(self):
        """Enable the start button (professional Button implementation)."""
        if hasattr(self, 'start_btn'):
            self.start_btn.config(
                bg='#4CAF50',  # Medium Green
                fg='#FFFFFF',  # White text
                state='normal',
                cursor='hand2'
            )

    def _update_action_buttons_for_game_state(self):
        """Update action button text and appearance based on current game state."""
        if not hasattr(self, 'state_machine') or not self.state_machine:
            return
            
        try:
            # Get current game state information
            human_player = self.state_machine.get_human_player()
            if not human_player:
                return
                
            current_bet = getattr(self.state_machine.game_state, 'current_bet', 0)
            player_bet = getattr(human_player, 'current_bet', 0)
            call_amount = current_bet - player_bet
            
            # Determine what the first button should be: CHECK or CALL
            if call_amount > 0:
                # There's a bet to call - show CALL button
                self._update_check_call_button('call', call_amount)
                # Third button should be RAISE (since there's a bet to raise)
                self._update_bet_raise_button('raise')
            else:
                # No bet to call - show CHECK button  
                self._update_check_call_button('check')
                # Third button should be BET (since there's no current bet)
                self._update_bet_raise_button('bet')
                
        except Exception as e:
            print(f"⚠️ Error updating action buttons: {e}")
    
    def _update_check_call_button(self, action_type: str, amount: float = 0):
        """Update the check/call button dynamically."""
        if action_type not in ['check', 'call']:
            return
            
        config = self.button_configs[action_type]
        label = self.action_labels['check_call']
        frame = self.action_buttons['check_call']
        
        # Update button text
        if action_type == 'call' and amount > 0:
            button_text = f"CALL ${amount:.0f}"
        else:
            button_text = config['text']
            
        # Update label and frame appearance
        label.config(text=button_text, bg=config['color'])
        frame.config(bg=config['color'])
        
    def _update_bet_raise_button(self, action_type: str):
        """Update the bet/raise button dynamically."""
        if action_type not in ['bet', 'raise']:
            return
            
        config = self.button_configs[action_type]
        label = self.action_labels['bet_raise']
        frame = self.action_buttons['bet_raise']
        
        # Update label and frame appearance
        label.config(text=config['text'], bg=config['color'])
        frame.config(bg=config['color'])


# Clean architecture practice session UI is now the main implementation

#!/usr/bin/env python3
"""
Refactored Practice Session UI - Clean Architecture

This version properly utilizes the specialized PracticeSessionPokerWidget
and PracticeSessionPokerStateMachine, following clean inheritance patterns.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from datetime import datetime

# Import core components
from core.practice_session_poker_state_machine import PracticeSessionPokerStateMachine
from core.flexible_poker_state_machine import GameConfig, EventListener, GameEvent
from core.gui_models import StrategyData, THEME, FONTS

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
            # Fallback to defaults if no config provided
            config = GameConfig(
                num_players=6,
                big_blind=2.0,
                small_blind=1.0,
                starting_stack=200.0
            )
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
            self.state_machine = PracticeSessionPokerStateMachine(config, strategy_data)
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
    
    def on_event(self, event: GameEvent):
        """Handle events from the specialized state machine."""
        try:
            # Handle practice-specific events
            if event.event_type == "practice_hand_started":
                self._handle_hand_started(event)
            elif event.event_type == "practice_feedback":
                self._handle_practice_feedback(event)
            elif event.event_type == "practice_analysis":
                self._handle_practice_analysis(event)
            elif event.event_type == "practice_showdown_analysis":
                self._handle_showdown_analysis(event)
            elif event.event_type == "practice_stats_reset":
                pass  # Statistics panel removed
            else:
                # Let the poker widget handle game events
                pass
                
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
        """Setup the bottom control strip with session controls, action message area, action buttons, and quick bet buttons."""
        # Create bottom control strip frame
        bottom_frame = ttk.Frame(self, style='Dark.TFrame')
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Configure four columns in bottom strip
        bottom_frame.grid_columnconfigure(0, weight=1)  # Left: Session controls
        bottom_frame.grid_columnconfigure(1, weight=2)  # Center-Left: Action message area (wider)
        bottom_frame.grid_columnconfigure(2, weight=2)  # Center-Right: Action buttons (wider)
        bottom_frame.grid_columnconfigure(3, weight=1)  # Right: Quick Bet Buttons
        
        # === LEFT: Session Controls ===
        session_frame = ttk.Frame(bottom_frame, style='Dark.TFrame')
        session_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self._setup_session_controls_bottom(session_frame)
        
        # === CENTER-LEFT: Action Message Area ===
        message_frame = ttk.Frame(bottom_frame, style='Dark.TFrame')
        message_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        self._setup_action_message_area(message_frame)
        
        # === CENTER-RIGHT: Action Buttons ===
        action_frame = ttk.Frame(bottom_frame, style='Dark.TFrame')
        action_frame.grid(row=0, column=2, sticky="nsew", padx=5)
        self._setup_action_buttons(action_frame)
        
        # === RIGHT: Quick Bet Buttons ===
        bet_buttons_frame = ttk.Frame(bottom_frame, style='Dark.TFrame')
        bet_buttons_frame.grid(row=0, column=3, sticky="nsew", padx=(5, 0))
        self._setup_quick_bet_buttons(bet_buttons_frame)
    
    def _setup_session_controls_bottom(self, parent):
        """Setup session controls for bottom strip layout."""
        # Start New Hand button using exact same style and sizing as action buttons
        start_frame = tk.Frame(
            parent,
            bg=THEME['chip_green'],  # Green background like CHECK button style
            relief='raised',
            bd=3,
            cursor='hand2'
        )
        # Use same positioning style as action buttons with exact padding
        start_frame.pack(side=tk.LEFT, padx=(5, 10), pady=10, ipadx=10, ipady=8)
        
        start_label = tk.Label(
            start_frame,
            text="🎯 START NEW HAND",
            bg=THEME['chip_green'],  # Green background
            fg='white',  # White text like other action buttons
            font=('Arial', 14, 'bold'),  # Same font as action buttons
            cursor='hand2'
        )
        start_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=8)  # Exact same as action buttons
        
        # Bind click events to both frame and label
        start_frame.bind("<Button-1>", lambda e: self._start_new_hand())
        start_label.bind("<Button-1>", lambda e: self._start_new_hand())
        
        # Store reference
        self.start_btn = start_frame
    
    def _setup_action_message_area(self, parent):
        """Setup action message area for game notifications."""
        # Message text widget with dark teal blue background
        self.action_message_text = tk.Text(
            parent,
            height=2,  # Reduced height to match button height
            bg="#2E4F76",  # Dark teal blue background
            fg="white",    # White text for contrast
            font=FONTS["main"],  # Match app font size
            wrap=tk.WORD,
            state='disabled',
            relief='flat',
            borderwidth=0
        )
        self.action_message_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)  # Match button padding
        
        # Initialize with welcome message
        self._add_action_message("Welcome! Start a new hand to begin playing.")
    
    def _add_action_message(self, message: str):
        """Add a message to the action message area."""
        if hasattr(self, 'action_message_text'):
            self.action_message_text.config(state='normal')
            self.action_message_text.insert(tk.END, message + "\n")
            self.action_message_text.see(tk.END)  # Auto-scroll to bottom
            self.action_message_text.config(state='disabled')
    
    def _setup_quick_bet_buttons(self, parent):
        """Setup quick bet buttons for faster gameplay."""
        # Quick bet buttons panel
        bet_panel = tk.Frame(parent, bg=THEME["primary_bg"])
        bet_panel.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid for quick bet buttons (2x3 layout - 6 buttons total)
        bet_panel.grid_columnconfigure(0, weight=1)
        bet_panel.grid_columnconfigure(1, weight=1)
        bet_panel.grid_columnconfigure(2, weight=1)
        bet_panel.grid_rowconfigure(0, weight=1)
        bet_panel.grid_rowconfigure(1, weight=1)
        
        # Quick bet buttons using Frame+Label pattern
        bet_buttons_data = [
            ("1/3 POT", "one_third", 0, 0),
            ("1/2 POT", "half", 0, 1),
            ("2/3 POT", "two_thirds", 0, 2),
            ("POT", "pot", 1, 0),
            ("2x POT", "two_x_pot", 1, 1),
            ("ALL IN", "all_in", 1, 2)
        ]
        
        self.quick_bet_buttons = {}
        
        for text, key, row, col in bet_buttons_data:
            # Use dark deep orange color for all bet buttons
            button_color = "#B8460E"  # Dark deep orange for all bet buttons
            
            # Create frame
            bet_frame = tk.Frame(
                bet_panel,
                bg=button_color,
                relief='raised',
                bd=2,
                cursor='hand2'
            )
            bet_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew", ipadx=5, ipady=5)
            
            # Create label
            bet_label = tk.Label(
                bet_frame,
                text=text,
                bg=button_color,
                fg='white',
                font=('Arial', 10, 'bold'),
                cursor='hand2'
            )
            bet_label.pack(fill=tk.BOTH, expand=True)
            
            # Bind click events
            bet_frame.bind("<Button-1>", lambda e, bet_type=key: self._handle_quick_bet(bet_type))
            bet_label.bind("<Button-1>", lambda e, bet_type=key: self._handle_quick_bet(bet_type))
            
            # Store reference
            self.quick_bet_buttons[key] = bet_frame
    
    def _setup_action_buttons(self, parent):
        """Setup modern action buttons in the bottom center area."""
        # Action buttons panel
        action_panel = tk.Frame(parent, bg=THEME["primary_bg"])
        action_panel.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid for equal button distribution
        for i in range(3):  # 3 action buttons only (CHECK, FOLD, BET/RAISE)
            action_panel.grid_columnconfigure(i, weight=1)
        
        # CHECK/CALL button using Frame+Label for proper macOS colors
        check_frame = tk.Frame(
            action_panel,
            bg=THEME['button_check'],
            relief='raised',
            bd=3,
            cursor='hand2'
        )
        check_frame.grid(row=0, column=0, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        check_label = tk.Label(
            check_frame,
            text="CHECK",
            bg=THEME['button_check'],
            fg='white',
            font=('Arial', 14, 'bold'),
            cursor='hand2'
        )
        check_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=8)
        
        # Bind click events to both frame and label
        check_frame.bind("<Button-1>", lambda e: self._handle_action_click('check_call'))
        check_label.bind("<Button-1>", lambda e: self._handle_action_click('check_call'))
        
        check_button = check_frame  # Reference for enable/disable
        
        # FOLD button using Frame+Label for proper macOS colors
        fold_frame = tk.Frame(
            action_panel,
            bg=THEME['button_fold'],
            relief='raised',
            bd=3,
            cursor='hand2'
        )
        fold_frame.grid(row=0, column=1, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        fold_label = tk.Label(
            fold_frame,
            text="FOLD",
            bg=THEME['button_fold'],
            fg='white',
            font=('Arial', 14, 'bold'),
            cursor='hand2'
        )
        fold_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=8)
        
        # Bind click events to both frame and label
        fold_frame.bind("<Button-1>", lambda e: self._handle_action_click('fold'))
        fold_label.bind("<Button-1>", lambda e: self._handle_action_click('fold'))
        
        fold_button = fold_frame  # Reference for enable/disable
        
        # BET/RAISE button using Frame+Label for proper macOS colors
        bet_frame = tk.Frame(
            action_panel,
            bg=THEME['button_raise'],
            relief='raised',
            bd=3,
            cursor='hand2'
        )
        bet_frame.grid(row=0, column=2, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        bet_label = tk.Label(
            bet_frame,
            text="RAISE",
            bg=THEME['button_raise'],
            fg='white',
            font=('Arial', 14, 'bold'),
            cursor='hand2'
        )
        bet_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=8)
        
        # Bind click events to both frame and label
        bet_frame.bind("<Button-1>", lambda e: self._handle_action_click('bet_raise'))
        bet_label.bind("<Button-1>", lambda e: self._handle_action_click('bet_raise'))
        
        bet_button = bet_frame  # Reference for enable/disable
        
        # Store button references and original colors for enabling/disabling
        self.action_buttons = {
            'check_call': check_button,
            'fold': fold_button,
            'bet_raise': bet_button
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
        
        # Initially enable all action buttons (human player starts)
        self._enable_action_buttons()
    
    def _handle_action_click(self, action_key: str):
        """Handle action button clicks and delegate to poker widget."""
        if hasattr(self.poker_widget, '_handle_action_click'):
            self.poker_widget._handle_action_click(action_key)
    
    def _handle_quick_bet(self, bet_type: str):
        """Handle quick bet button clicks and set the bet amount accordingly."""
        try:
            # Get current pot size (this will need to be implemented based on your state machine)
            current_pot = 0  # Default value
            if hasattr(self, 'state_machine') and self.state_machine:
                # Try to get pot size from state machine
                current_pot = getattr(self.state_machine, 'pot', 0)
                if current_pot == 0:
                    current_pot = 20  # Default small pot for calculations
            
            # Calculate bet amount based on type
            if bet_type == "one_third":
                bet_amount = max(2, int(current_pot * 0.33))
            elif bet_type == "half":
                bet_amount = max(2, int(current_pot * 0.5))
            elif bet_type == "two_thirds":
                bet_amount = max(2, int(current_pot * 0.67))
            elif bet_type == "pot":
                bet_amount = max(2, current_pot)
            elif bet_type == "two_x_pot":
                bet_amount = max(2, current_pot * 2)
            elif bet_type == "all_in":
                # For ALL IN, get player's full stack
                if hasattr(self, 'state_machine') and self.state_machine:
                    current_player = getattr(self.state_machine, 'current_player', None)
                    if current_player and hasattr(current_player, 'stack'):
                        bet_amount = current_player.stack
                    else:
                        bet_amount = 1000  # Default stack
                else:
                    bet_amount = 1000  # Default stack
            else:
                bet_amount = 2
            
            # Store the calculated bet amount for use by bet/raise actions
            self.current_bet_amount = bet_amount
            
            # Execute the appropriate action based on bet type
            if bet_type == "all_in":
                self._handle_action_click('all_in')
            else:
                self._handle_action_click('bet_raise')
            
        except Exception as e:
            print(f"Error in quick bet: {e}")
            # Fallback to default bet
            self.current_bet_amount = 2
    
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
            self.start_btn.config(state="disabled")
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
                self.start_btn.config(state="normal")
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
            # Find human player
            human_player = next((p for p in self.state_machine.game_state.players if p.is_human), None)
            
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
            if self.state_machine.hands_played > 0:
                stats = self.state_machine.get_practice_stats()
                
                analysis = f"""📊 Current Hand Analysis:
                
Hands Played: {stats['hands_played']}
Win Rate: {stats['win_rate']:.1f}%
Decision Accuracy: {stats['decision_accuracy']:.1f}%

Position: {self.state_machine._get_human_player_position() or 'Unknown'}
Street: {self.state_machine.game_state.street}
Pot: ${self.state_machine.game_state.pot:.2f}
"""
                
                self._add_educational_message(analysis)
            else:
                self._add_educational_message("📊 Start a hand first to get analysis.")
                
        except Exception as e:
            print(f"⚠️ Error analyzing hand: {e}")
    
    def _handle_hand_started(self, event: GameEvent):
        """Handle practice hand started event."""
        if event.data:
            hand_num = event.data.get("hand_number", 0)
            position = event.data.get("your_position", "Unknown")
            
            message = f"🎯 Hand #{hand_num} started! You are in {position} position."
            self._add_educational_message(message)
        
        # Re-enable start button when hand is complete
        self.start_btn.config(state="normal")
    
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
        """Update font sizes for the educational and stats panels."""
        try:
            new_font = (FONTS["main"][0], font_size)
            self.edu_text.config(font=new_font)
            self.stats_text.config(font=new_font)
            
            # Also update poker widget font size
            if hasattr(self, 'poker_widget') and hasattr(self.poker_widget, 'update_font_size'):
                self.poker_widget.update_font_size(font_size)
        except Exception as e:
            print(f"⚠️ Error updating font size: {e}")
    
    def increase_table_size(self):
        """Increase the poker table size."""
        if hasattr(self.poker_widget, 'increase_table_size'):
            self.poker_widget.increase_table_size()
    
    def decrease_table_size(self):
        """Decrease the poker table size."""
        if hasattr(self.poker_widget, 'decrease_table_size'):
            self.poker_widget.decrease_table_size()
    
    def change_table_felt(self, felt_color: str):
        """Change the poker table felt color."""
        if hasattr(self.poker_widget, 'change_table_felt'):
            self.poker_widget.change_table_felt(felt_color)


# Clean architecture practice session UI is now the main implementation

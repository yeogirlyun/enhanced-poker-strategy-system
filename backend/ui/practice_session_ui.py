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
                self._update_session_stats()
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
            start_new_hand=self._start_new_hand,
            reset_session=self._reset_session
        )
        self.poker_widget.pack(fill=tk.BOTH, expand=True)
        
        # === BOTTOM: Control Strip (Session | Action Buttons | Statistics) ===
        self._setup_bottom_control_strip()
    
    def _setup_bottom_control_strip(self):
        """Setup the bottom control strip with session controls, action buttons, and statistics."""
        # Create bottom control strip frame
        bottom_frame = ttk.Frame(self, style='Dark.TFrame')
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Configure three columns in bottom strip
        bottom_frame.grid_columnconfigure(0, weight=1)  # Left: Session controls
        bottom_frame.grid_columnconfigure(1, weight=2)  # Center: Action buttons (wider)
        bottom_frame.grid_columnconfigure(2, weight=1)  # Right: Statistics
        
        # === LEFT: Session Controls ===
        session_frame = ttk.Frame(bottom_frame, style='Dark.TFrame')
        session_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self._setup_session_controls_bottom(session_frame)
        
        # === CENTER: Action Buttons ===
        action_frame = ttk.Frame(bottom_frame, style='Dark.TFrame')
        action_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        self._setup_action_buttons(action_frame)
        
        # === RIGHT: Statistics ===
        stats_frame = ttk.Frame(bottom_frame, style='Dark.TFrame')
        stats_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        self._setup_statistics_panel_bottom(stats_frame)
    
    def _setup_session_controls_bottom(self, parent):
        """Setup session controls for bottom strip layout."""
        # Start New Hand button - horizontal layout
        self.start_btn = tk.Button(
            parent,
            text="🎯 START NEW HAND",
            command=self._start_new_hand,
            bg=THEME["chip_green"],         # Medium Green (win/positive indicator)
            fg="white",
            activebackground=THEME["table_felt"],  # Emerald Green on hover
            font=FONTS["main"],
            height=2,
            bd=2,
            cursor='hand2',
            relief='raised'
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5), fill=tk.Y)
        
        # Reset Session button
        self.reset_btn = tk.Button(
            parent,
            text="🔄 RESET SESSION",
            command=self._reset_session,
            bg=THEME["button_allin"],       # Orange for reset (matches ALL IN)
            fg="white",
            activebackground=THEME["button_allin_hover"],  # Darker orange on hover
            font=FONTS["main"],
            height=2,
            bd=2,
            cursor='hand2',
            relief='raised'
        )
        self.reset_btn.pack(side=tk.LEFT, fill=tk.Y)
    
    def _setup_statistics_panel_bottom(self, parent):
        """Setup statistics panel for bottom strip layout."""
        # Session Statistics in horizontal layout
        stats_text = tk.Text(
            parent,
            height=3,
            width=25,
            bg=THEME["secondary_bg"],
            fg=THEME["text"],
            font=FONTS["small"],
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Store reference for updates
        self.stats_text = stats_text
        
        # Initialize with default stats
        self._update_session_stats()
    
    def _setup_action_buttons(self, parent):
        """Setup modern action buttons in the bottom center area."""
        # Action buttons panel
        action_panel = tk.Frame(parent, bg=THEME["primary_bg"])
        action_panel.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid for equal button distribution
        for i in range(5):  # 4 buttons + 1 bet amount area
            action_panel.grid_columnconfigure(i, weight=1)
        
        # CHECK/CALL button
        check_button = tk.Button(
            action_panel,
            text="CHECK",
            bg=THEME['button_check'],
            fg='white',
            font=('Arial', 14, 'bold'),
            relief='raised',
            bd=3,
            cursor='hand2',
            activebackground=THEME['button_check_hover'],
            activeforeground='white',
            highlightthickness=0,
            command=lambda: self._handle_action_click('check_call')
        )
        check_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        # FOLD button
        fold_button = tk.Button(
            action_panel,
            text="FOLD",
            bg=THEME['button_fold'],
            fg='white',
            font=('Arial', 14, 'bold'),
            relief='raised',
            bd=3,
            cursor='hand2',
            activebackground=THEME['button_fold_hover'],
            activeforeground='white',
            highlightthickness=0,
            command=lambda: self._handle_action_click('fold')
        )
        fold_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        # BET/RAISE button
        bet_button = tk.Button(
            action_panel,
            text="BET",
            bg=THEME['button_raise'],
            fg='white',
            font=('Arial', 14, 'bold'),
            relief='raised',
            bd=3,
            cursor='hand2',
            activebackground=THEME['button_raise_hover'],
            activeforeground='white',
            highlightthickness=0,
            command=lambda: self._handle_action_click('bet_raise')
        )
        bet_button.grid(row=0, column=2, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        # Bet amount area
        bet_frame = tk.Frame(action_panel, bg=THEME["primary_bg"])
        bet_frame.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        
        tk.Label(bet_frame, text="Bet Amount", bg=THEME["primary_bg"], fg=THEME["text"], font=FONTS["small"]).pack()
        self.bet_amount = tk.StringVar(value="2")
        bet_entry = tk.Entry(bet_frame, textvariable=self.bet_amount, width=8, justify='center')
        bet_entry.pack()
        
        # ALL IN button
        allin_button = tk.Button(
            action_panel,
            text="ALL IN",
            bg=THEME['button_allin'],
            fg='white',
            font=('Arial', 14, 'bold'),
            relief='raised',
            bd=3,
            cursor='hand2',
            activebackground=THEME['button_allin_hover'],
            activeforeground='white',
            highlightthickness=0,
            command=lambda: self._handle_action_click('all_in')
        )
        allin_button.grid(row=0, column=4, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        # Store button references for enabling/disabling
        self.action_buttons = {
            'check_call': check_button,
            'fold': fold_button,
            'bet_raise': bet_button,
            'all_in': allin_button
        }
        
        # Initially disable all action buttons
        self._disable_action_buttons()
    
    def _handle_action_click(self, action_key: str):
        """Handle action button clicks and delegate to poker widget."""
        if hasattr(self.poker_widget, '_handle_action_click'):
            self.poker_widget._handle_action_click(action_key)
    
    def _enable_action_buttons(self):
        """Enable action buttons for human player interaction."""
        for button_widget in self.action_buttons.values():
            button_widget.config(relief='raised', state='normal')
    
    def _disable_action_buttons(self):
        """Disable action buttons (not human player's turn)."""
        disabled_color = THEME['button_fold']  # Use theme gray
        disabled_text = THEME['text_muted']    # Use theme muted text
        
        for button_widget in self.action_buttons.values():
            button_widget.config(
                bg=disabled_color, 
                fg=disabled_text,
                relief='sunken',
                state='disabled'
            )

    def _setup_session_controls(self, parent):
        """Setup industry-standard session control buttons."""
        controls_frame = ttk.LabelFrame(parent, text="Session Controls", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Industry-standard game control button configuration
        control_button_config = {
            'font': ('Arial', 16, 'bold'),  # Large readable font
            'height': 2,                    # Compact height
            'relief': 'raised',
            'bd': 3,                        # Professional border
            'cursor': 'hand2',              # Hand cursor on hover
            'activeforeground': 'white',    # White text on hover
        }
        
        # Start New Hand button - Industry standard green/blue
        self.start_btn = tk.Button(
            controls_frame,
            text="🎯 START NEW HAND",
            command=self._start_new_hand,
            bg=THEME["chip_green"],         # Medium Green (win/positive indicator)
            fg="white",
            activebackground=THEME["table_felt"],  # Emerald Green on hover
            **control_button_config
        )
        self.start_btn.pack(fill=tk.X, pady=(0, 8))
        
        # Reset Session button - Industry standard orange/amber
        self.reset_btn = tk.Button(
            controls_frame,
            text="🔄 RESET SESSION",
            command=self._reset_session,
            bg=THEME["button_allin"],       # Orange for reset (matches ALL IN)
            fg="white",
            activebackground=THEME["button_allin_hover"],  # Darker orange on hover
            **control_button_config
        )
        self.reset_btn.pack(fill=tk.X, pady=(0, 8))
        
        # Coaching Mode toggle
        self.coaching_var = tk.BooleanVar(value=True)
        self.coaching_check = ttk.Checkbutton(
            controls_frame,
            text="🎓 Coaching Mode",
            variable=self.coaching_var,
            command=self._toggle_coaching_mode
        )
        self.coaching_check.pack(fill=tk.X, pady=(0, 5))
        
        # Auto-advance toggle
        self.auto_advance_var = tk.BooleanVar(value=False)
        self.auto_advance_check = ttk.Checkbutton(
            controls_frame,
            text="⚡ Auto-advance",
            variable=self.auto_advance_var
        )
        self.auto_advance_check.pack(fill=tk.X, pady=(0, 5))
    
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

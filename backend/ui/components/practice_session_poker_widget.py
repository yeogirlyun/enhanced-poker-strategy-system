#!/usr/bin/env python3
"""
Practice Session Poker Widget - Hook-Based Architecture

A specialized poker widget that inherits from ReusablePokerGameWidget
and uses the new hook-based architecture for clean extensibility.

This widget provides practice session specific functionality by overriding
simple, focused hook methods instead of complex core logic.
"""

import tkinter as tk
from typing import List, Dict, Any

# Import the base widget
from .reusable_poker_game_widget import ReusablePokerGameWidget

# Import modern UI components
from .modern_poker_widgets import ChipStackDisplay

# Import theme
from core.gui_models import THEME

# Import FPSM components
from core.flexible_poker_state_machine import GameEvent


def debug_log(message: str, category: str = "PRACTICE_WIDGET"):
    """Log debug messages to file instead of console."""
    try:
        from core.session_logger import get_session_logger
        logger = get_session_logger()
        logger.log_system("DEBUG", category, message, {})
    except:
        # Fallback to silent operation if logger not available
        pass


class PracticeSessionPokerWidget(ReusablePokerGameWidget):
    """
    A specialized poker widget for practice sessions using hook-based architecture.
    
    This widget is specifically designed for interactive learning and provides:
    - Human player cards always visible
    - Educational annotations and feedback
    - Interactive action buttons
    - Performance tracking and analysis
    """
    
    def __init__(self, parent, state_machine=None, **kwargs):
        """Initialize the practice session poker widget."""
        # Extract practice-specific parameters before calling parent
        self.strategy_data = kwargs.pop('strategy_data', None)
        
        # Call parent with remaining kwargs (tkinter-safe parameters only)
        super().__init__(parent, state_machine=state_machine, **kwargs)
        
        # Practice session specific properties
        self.practice_mode = True
        self.action_buttons = {}
        self.prebet_buttons = {}
        
        # Setup UI controller for state machine sound calls
        if self.state_machine:
            self._setup_ui_controller()
        
        # Setup practice-specific UI after parent initialization
        self.after_idle(self._setup_practice_ui)
        
        # Initialization debug removed to reduce log spam
    
    # ==============================
    # HOOK OVERRIDES
    # Simple, focused overrides for practice session behavior
    # ==============================
    
    def _should_show_card(self, player_index: int, card: str) -> bool:
        """
        Hook Override: Show cards based on practice session policy.
        
        - Human player: Always show cards (including ** which will be transformed)
        - Bot players: Hide cards (show card backs)
        """
        if hasattr(self, 'state_machine') and self.state_machine:
            try:
                if (hasattr(self.state_machine, 'game_state') and 
                    self.state_machine.game_state and 
                    player_index < len(self.state_machine.game_state.players)):
                    
                    player = self.state_machine.game_state.players[player_index]
                    if hasattr(player, 'is_human') and player.is_human:
                        # Card hook debug removed to reduce log spam
                        return True  # Always show human player cards (including **)
            except Exception as e:
                # Card transform error debug removed
                pass
        
        # For bot players, use default behavior (hide ** cards)
        result = card != "**" and card != ""
        # Card hook debug removed to reduce log spam
        return result
    
    def _transform_card_data(self, player_index: int, card: str, card_index: int = 0) -> str:
        """
        Hook Override: Transform ** to actual cards for human players only.
        
        This ensures human players can always see their cards for learning.
        """
        # Card transform debug removed to reduce log spam
        
        if hasattr(self, 'state_machine') and self.state_machine:
            try:
                if (hasattr(self.state_machine, 'game_state') and 
                    self.state_machine.game_state and 
                    player_index < len(self.state_machine.game_state.players)):
                    
                    player = self.state_machine.game_state.players[player_index]
                    is_human = hasattr(player, 'is_human') and player.is_human
                    # Player type debug removed
                    
                    if is_human:
                        # For human player, ALWAYS return actual cards (even if not **)
                        if hasattr(player, 'cards') and player.cards and card_index < len(player.cards):
                            actual_card = player.cards[card_index]
                            # Card transform debug removed
                            return actual_card
                        else:
                            # Card error debug removed
                            return card
            except Exception:
                # Error debug removed to reduce log spam
                pass
        
        # Bot card debug removed to reduce log spam
        return card  # Return as-is for bot players
    
    def _should_update_display(self, player_index: int, old_cards: list, new_cards: list) -> bool:
        """
        Hook Override: Responsive updates for practice sessions.
        
        Always update for immediate feedback during practice.
        """
        return True  # Always update for responsive practice experience
    
    def _should_update_community_cards(self, old_cards: list, new_cards: list) -> bool:
        """
        Hook Override: Always update community cards for practice.
        
        Immediate updates for better learning experience.
        """
        return True  # Always update community cards
    
    def _customize_player_styling(self, player_index: int, player_info: dict) -> dict:
        """
        Hook Override: Enhanced styling for practice sessions.
        
        Highlight human player, add visual cues for different player types.
        """
        styling = super()._customize_player_styling(player_index, player_info)
        
        if hasattr(self, 'state_machine') and self.state_machine:
            try:
                if (hasattr(self.state_machine, 'game_state') and 
                    self.state_machine.game_state and 
                    player_index < len(self.state_machine.game_state.players)):
                    
                    player = self.state_machine.game_state.players[player_index]
                    if hasattr(player, 'is_human') and player.is_human:
                        # Highlight human player
                        styling.update({
                            'border_color': THEME['text_gold'],  # Gold border for human
                            'background': THEME['primary_bg'],    # Dark Charcoal background
                            'text_color': THEME['text_gold']     # Gold text
                        })
            except Exception:
                pass
        
        return styling
    
    def _handle_card_interaction(self, player_index: int, card_index: int, card: str):
        """
        Hook Override: Add educational features for practice sessions.
        
        Hand strength analysis, strategy suggestions, etc.
        """
        debug_log(f"Practice: Card interaction - Player {player_index}, Card {card_index}: {card}", "CARD_INTERACTION")
        
        # Add hand strength analysis for human player
        if self._is_human_player(player_index):
            self._add_card_analysis(player_index, card_index, card)
    
    # ==============================
    # PRACTICE SESSION SPECIFIC METHODS
    # Additional functionality specific to practice sessions
    # ==============================
    
    def _setup_practice_ui(self):
        """Setup practice-specific UI elements."""
        debug_log("Setting up practice session UI", "PRACTICE_INIT")
        
        # Initialize action button dictionaries
        self.action_buttons = {}
        self.action_labels = {}
        self.action_button_states = {}
        
        # Create modern action buttons panel
        self._create_action_buttons_panel()
        
        # Create feedback display
        self._create_feedback_display()
        
        # Create performance tracking
        self._create_performance_display()
    
    def _create_action_buttons(self):
        """Create interactive action buttons for human player - DISABLED: Using modern panel instead."""
        debug_log("Skipping old action buttons - using modern panel instead", "PRACTICE_INIT")
        return  # Exit early - use _create_action_buttons_panel instead
    
    def set_session_callbacks(self, start_new_hand=None, reset_session=None):
        """Set session control callbacks - required by practice_session_ui.py."""
        debug_log("Session callbacks set", "PRACTICE_INIT")
        # Store callbacks for future use if needed
        self.start_new_hand_callback = start_new_hand
        self.reset_session_callback = reset_session

    def _setup_ui_controller(self):
        """Setup UI controller to handle state machine sound and animation calls."""
        # Create a simple UI controller that the state machine can use
        class SimpleUIController:
            def __init__(self, widget):
                self.widget = widget
            
            def play_sound(self, sound_type: str, **kwargs):
                """Play sound through the widget's sound system."""
                if hasattr(self.widget, 'play_sound'):
                    # Map state machine sound names to widget sound names
                    sound_mapping = {
                        'check_sound': 'check',
                        'call_sound': 'call', 
                        'bet_sound': 'bet',
                        'raise_sound': 'raise',
                        'fold_sound': 'fold',
                        'all_in_sound': 'all_in'
                    }
                    mapped_sound = sound_mapping.get(sound_type, sound_type)
                    self.widget.play_sound(mapped_sound, **kwargs)
            
            def animate(self, animation_type: str, **kwargs):
                """Trigger animation through the widget's animation system."""
                if hasattr(self.widget, 'play_animation'):
                    self.widget.play_animation(animation_type, **kwargs)
            
            def update_ui(self, update_type: str, **kwargs):
                """Handle UI updates from state machine."""
                pass  # Widget handles its own updates
        
        # Set the UI controller on the state machine
        if hasattr(self.state_machine, 'set_ui_controller'):
            self.state_machine.set_ui_controller(SimpleUIController(self))
            debug_log("UI controller set up for state machine", "UI_CONTROLLER")
    
    def _create_feedback_display(self):
        """Create educational feedback display."""
        debug_log("Creating feedback display for practice session", "PRACTICE_INIT")
        
        # Implementation would go here
        pass
    
    def _create_performance_display(self):
        """Create performance tracking display."""
        debug_log("Creating performance display for practice session", "PRACTICE_INIT")
        
        # Implementation would go here
        pass
    
    def _is_human_player(self, player_index: int) -> bool:
        """Check if player is human."""
        if hasattr(self, 'state_machine') and self.state_machine:
            try:
                if (hasattr(self.state_machine, 'game_state') and 
                    self.state_machine.game_state and 
                    player_index < len(self.state_machine.game_state.players)):
                    
                    player = self.state_machine.game_state.players[player_index]
                    return hasattr(player, 'is_human') and player.is_human
            except Exception:
                pass
        return False
    
    def _add_card_analysis(self, player_index: int, card_index: int, card: str):
        """Add educational card analysis."""
        debug_log(f"Adding card analysis for {card}", "CARD_ANALYSIS")
        
        # Implementation would analyze hand strength, provide suggestions, etc.
        pass
    
    def provide_action_feedback(self, action: str, amount: float):
        """Provide educational feedback on player actions."""
        print(f"🎓 Action feedback: {action} ${amount}")
        
        # Implementation would analyze the action and provide learning feedback
        pass
    
    def update_performance_stats(self, decision_quality: str):
        """Update performance tracking stats."""
        print(f"🎓 Performance update: {decision_quality}")
        
        # Implementation would track decision quality, learning progress, etc.
        pass
    
    def _create_action_buttons_panel(self):
        """Create the modern action buttons panel at the bottom of the poker table."""
        # Create a frame at the bottom for action buttons using grid
        action_frame = tk.Frame(self, bg=THEME["primary_bg"])
        action_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Action buttons panel
        action_panel = tk.Frame(action_frame, bg=THEME["primary_bg"])
        action_panel.grid(row=0, column=0, sticky="ew")
        
        # Configure the parent grid to expand the action frame
        self.grid_rowconfigure(1, weight=0)  # Action buttons don't expand
        self.grid_columnconfigure(0, weight=1)  # Fill width
        action_frame.grid_columnconfigure(0, weight=1)
        
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
            highlightthickness=0,  # Remove focus border
            command=lambda: self._handle_action_click('check_call') if self.action_button_states.get('check_call', False) else None
        )
        check_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        self.action_buttons['check_call'] = check_button
        self.action_labels['check_call'] = check_button  # Same reference for consistency
        self.action_button_states['check_call'] = False
        
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
            command=lambda: self._handle_action_click('fold') if self.action_button_states.get('fold', False) else None
        )
        fold_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        self.action_buttons['fold'] = fold_button
        self.action_labels['fold'] = fold_button
        self.action_button_states['fold'] = False
        
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
            command=lambda: self._handle_action_click('bet_raise') if self.action_button_states.get('bet_raise', False) else None
        )
        bet_button.grid(row=0, column=2, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        self.action_buttons['bet_raise'] = bet_button
        self.action_labels['bet_raise'] = bet_button
        self.action_button_states['bet_raise'] = False
        
        # Bet amount section
        bet_amount_frame = tk.Frame(action_panel, bg='#2a2a2a', relief='sunken', bd=2)
        bet_amount_frame.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        
        # Bet amount buttons
        amounts = [2, 5, 10, 20, 50]
        self.bet_amount = tk.StringVar(value="2")
        
        for i, amount in enumerate(amounts):
            btn = tk.Button(
                bet_amount_frame,
                text=f"${amount}",
                font=('Arial', 10),
                bg='#4A5568',
                fg='white',
                command=lambda a=amount: self.bet_amount.set(str(a))
            )
            btn.grid(row=0, column=i, padx=1)
        
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
            command=lambda: self._handle_action_click('all_in') if self.action_button_states.get('all_in', False) else None
        )
        allin_button.grid(row=0, column=4, padx=5, pady=10, sticky="ew", ipadx=10, ipady=8)
        
        self.action_buttons['all_in'] = allin_button
        self.action_labels['all_in'] = allin_button
        self.action_button_states['all_in'] = False
        
        # Initially disable all action buttons
        self._disable_action_buttons()
        
        debug_log("Action buttons panel created with professional styling", "PRACTICE_UI")

    def _handle_action_click(self, action_key: str):
        """Handle action button clicks with safety checks."""
        debug_log(f"Action button clicked: {action_key}", "PRACTICE_UI")
        
        if not hasattr(self, 'state_machine') or not self.state_machine:
            debug_log("No state machine available", "PRACTICE_UI")
            return
        
        # Check if button is enabled
        if not self.action_button_states.get(action_key, False):
            debug_log(f"Button {action_key} is disabled, ignoring click", "PRACTICE_UI")
            return
        
        # Determine the action and amount
        if action_key == 'check_call':
            # Check if we need to call or check
            current_player = self.state_machine.get_current_player()
            if current_player and hasattr(current_player, 'get_call_amount'):
                call_amount = current_player.get_call_amount()
                if call_amount > 0:
                    action = 'call'
                    amount = call_amount
                else:
                    action = 'check'
                    amount = 0
            else:
                action = 'check'
                amount = 0
        elif action_key == 'fold':
            action = 'fold'
            amount = 0
        elif action_key == 'bet_raise':
            action = 'bet'
            amount = float(self.bet_amount.get()) if hasattr(self, 'bet_amount') else 10.0
        elif action_key == 'all_in':
            action = 'all_in'
            current_player = self.state_machine.get_current_player()
            amount = current_player.stack if current_player else 100
        else:
            debug_log(f"Unknown action: {action_key}", "PRACTICE_UI")
            return
        
        # Execute the action
        try:
            self.state_machine.execute_action(action, amount)
            debug_log(f"Action executed: {action} ${amount}", "PRACTICE_UI")
            
            # Disable buttons after action
            self._disable_action_buttons()
            
        except Exception as e:
            debug_log(f"Error executing action {action}: {e}", "PRACTICE_UI")

    def _enable_action_buttons(self):
        """Enable action buttons for human player interaction."""
        for key, button_widget in self.action_buttons.items():
            button_widget.config(
                relief='raised',
                state='normal'  # Enable the button
            )
            self.action_button_states[key] = True
        
        debug_log("Modern action buttons enabled for human player", "PRACTICE_UI")

    def _disable_action_buttons(self):
        """Disable action buttons (not human player's turn)."""
        disabled_color = THEME['button_fold']  # Use theme gray
        disabled_text = THEME['text_muted']    # Use theme muted text
        
        for key, button_widget in self.action_buttons.items():
            button_widget.config(
                bg=disabled_color, 
                fg=disabled_text,
                relief='sunken',
                state='disabled'  # Disable the button
            )
            self.action_button_states[key] = False
        
        debug_log("Modern action buttons disabled", "PRACTICE_UI")

    def _handle_player_turn_change(self, player_index: int):
        """Handle when it becomes a player's turn."""
        # Enable action buttons for human player (Player 1 = index 0)
        if player_index == 0:  # Human player
            self._enable_action_buttons()
            debug_log("Human player turn - buttons enabled", "PRACTICE_UI")
        else:
            self._disable_action_buttons()
            debug_log(f"Bot player {player_index + 1} turn - buttons disabled", "PRACTICE_UI")

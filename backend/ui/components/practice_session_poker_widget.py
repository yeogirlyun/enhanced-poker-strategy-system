#!/usr/bin/env python3
"""
Practice Session Poker Widget - Clean Version for Bottom Control Strip Layout
"""

import tkinter as tk
import tkinter.ttk as ttk
from typing import List, Dict, Any, Optional, Union

# Import dependencies
from core.gui_models import THEME, FONTS
from ui.components.reusable_poker_game_widget import ReusablePokerGameWidget

def debug_log(message, category="DEBUG"):
    """Simple debug logging function."""
    print(f"[{category}] {message}")

class PracticeSessionPokerWidget(ReusablePokerGameWidget):
    """
    Poker widget specialized for practice sessions with human interaction and educational features.
    """
    
    def __init__(self, parent, state_machine=None, **kwargs):
        """Initialize the practice session poker widget."""
        # Initialize attributes first
        self.action_buttons = {}
        self.action_labels = {}
        self.action_button_states = {}
        
        # Extract custom parameters that shouldn't go to ttk.Frame
        self.strategy_data = kwargs.pop('strategy_data', None)
        
        # Call parent constructor with filtered kwargs
        super().__init__(parent, state_machine, **kwargs)
        
        # Setup practice-specific features
        self._setup_practice_ui()
    
    def _setup_practice_ui(self):
        """Setup practice-specific UI elements."""
        # Initialize dictionaries for action buttons
        self.action_buttons = {}
        self.action_labels = {}
        self.action_button_states = {}
        
        # Set up UI controller and session callbacks
        self._setup_ui_controller()

    def set_session_callbacks(self, start_new_hand=None, reset_session=None):
        """Set callbacks for session management."""
        self.start_new_hand_callback = start_new_hand
        self.reset_session_callback = reset_session

    def _setup_ui_controller(self):
        """Setup UI controller to handle state machine sound and animation calls."""
        if hasattr(self, 'state_machine') and self.state_machine:
            class SimpleUIController:
                def __init__(self, widget):
                    self.widget = widget
                
                def play_sound(self, sound_name):
                    """Play sound via widget's sound manager."""
                    if hasattr(self.widget, 'sound_manager'):
                        self.widget.sound_manager.play_sound(sound_name)
                
                def play_action_sound(self, action):
                    """Play action-specific sound."""
                    if hasattr(self.widget, 'sound_manager'):
                        self.widget.sound_manager.play_action_sound(action)
                
                def animate_chips(self, *args, **kwargs):
                    """Handle chip animations."""
                    debug_log("Chip animation requested", "PRACTICE_UI")
                
                def update_display(self):
                    """Update display."""
                    if hasattr(self.widget, '_render_from_display_state'):
                        self.widget._render_from_display_state()

            # Attach UI controller to state machine
            self.state_machine.ui_controller = SimpleUIController(self)

    def _create_action_buttons_panel(self):
        """Create the modern action buttons panel in the bottom center area."""
        # Action buttons are now handled by the practice session UI bottom control strip
        debug_log("Action buttons will be created in bottom control strip", "PRACTICE_UI")
        return

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
            try:
                amount = float(self.bet_amount.get()) if hasattr(self, 'bet_amount') else 2.0
            except (ValueError, AttributeError):
                amount = 2.0
            
            # Determine if this is a bet or raise
            current_bet = getattr(self.state_machine, 'current_bet', 0)
            if current_bet > 0:
                action = 'raise'
            else:
                action = 'bet'
        elif action_key == 'all_in':
            action = 'all_in'
            current_player = self.state_machine.get_current_player()
            if current_player and hasattr(current_player, 'stack'):
                amount = current_player.stack
            else:
                amount = 1000  # Default
        else:
            debug_log(f"Unknown action key: {action_key}", "PRACTICE_UI")
            return
                
        # Execute the action
        debug_log(f"Executing action: {action} with amount: {amount}", "PRACTICE_UI")
        try:
            self.state_machine.execute_action(action, amount)
        except Exception as e:
            debug_log(f"Error executing action {action}: {e}", "PRACTICE_UI")
    
    def _enable_action_buttons(self):
        """Enable action buttons for human player interaction."""
        debug_log("Enabling action buttons for human player", "PRACTICE_UI")
        for key in self.action_button_states:
            self.action_button_states[key] = True
    
    def _disable_action_buttons(self):
        """Disable action buttons (not human player's turn)."""
        debug_log("Disabling action buttons", "PRACTICE_UI")
        for key in self.action_button_states:
            self.action_button_states[key] = False

    def _handle_player_turn_change(self, player_index: int):
        """Handle when it becomes a player's turn."""
        # Enable action buttons for human player (Player 1 = index 0)
        if player_index == 0:  # Human player
            self._enable_action_buttons()
            debug_log("Human player turn - buttons enabled", "PRACTICE_UI")
        else:
            self._disable_action_buttons()
            debug_log(f"Bot player {player_index + 1} turn - buttons disabled", "PRACTICE_UI")

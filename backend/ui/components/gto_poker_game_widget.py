"""
GTO Poker Game Widget

This module provides a poker game widget specifically designed for GTO simulation
where all players are GTO bots. It extends ReusablePokerGameWidget to provide
pure bot vs bot gameplay visualization with GTO decision explanations.
"""

import tkinter as tk
from typing import Optional, Dict, Any

from .reusable_poker_game_widget import ReusablePokerGameWidget
from core.gto_poker_state_machine import GTOPokerStateMachine
from core.types import GameState
from core.gui_models import THEME, FONTS


class GTOPokerGameWidget(ReusablePokerGameWidget):
    """
    GTO Poker Game Widget for pure bot vs bot simulation.
    
    This widget:
    - Displays GTO bot gameplay identical to practice session
    - Shows detailed GTO decision explanations
    - Provides step-by-step navigation through hands
    - Tracks decision history and learning insights
    """
    
    def __init__(self, parent, state_machine: GTOPokerStateMachine = None, **kwargs):
        """Initialize the GTO poker game widget."""
        super().__init__(parent, state_machine, **kwargs)
        
        # Mark this as a GTO widget for conditional positioning
        self._is_gto_widget = True
        
        # GTO-specific attributes
        self.gto_state_machine = state_machine
        self.current_decision: Optional[Dict[str, Any]] = None
        self.decision_explanation_var = tk.StringVar()
        self.decision_history_text = None
        
        # Initialize GTO-specific UI
        self._setup_gto_ui()
        
        # Bind to state machine updates
        self._bind_gto_events()
    
    def _setup_ui(self):
        """Override parent's _setup_ui to use pack instead of grid."""
        # Configure our own grid weights for proper sizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create canvas for the poker table (same as parent, but with pack)
        self.canvas = tk.Canvas(
            self, bg=THEME["table_felt"], highlightthickness=0
        )
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Initialize player seats (will be set dynamically based on actual
        # player count)
        self.player_seats = []

        # Force initial draw immediately
        self._force_initial_draw()

        # Create player seats and pot display when canvas is properly sized
        self._schedule_table_creation()

    def _schedule_table_creation(self):
        """Schedule table creation when canvas is properly sized."""
        # Check if canvas is properly sized
        if self.canvas.winfo_width() > 1 and self.canvas.winfo_height() > 1:
            # Canvas is ready, draw the table now
            self._draw_table()
        else:
            # Canvas not ready yet, schedule retry
            self.after(50, self._schedule_table_creation)

    def _setup_gto_ui(self):
        """Set up GTO-specific UI elements."""
        # No need to create duplicate UI elements - they're already in the bottom panel
        # Just initialize the variables for communication with the parent panel
        self.current_decision: Optional[Dict[str, Any]] = None
        self.decision_explanation_var = tk.StringVar()
        self.decision_history_text = None
    
    def _bind_gto_events(self):
        """Bind to GTO state machine events."""
        # Bind to state machine updates
        if hasattr(self.gto_state_machine, 'on_state_changed'):
            self.gto_state_machine.on_state_changed(self._on_gto_state_changed)
    
    def _start_new_hand(self):
        """Start a new GTO simulation hand."""
        try:
            # Start new hand in state machine
            success = self.gto_state_machine.start_new_hand()
            
            if success:
                # Update display
                self._update_display()
                
                # Get first action
                self._get_next_action()
            else:
                if self.session_logger:
                    self.session_logger.log_system("ERROR", "GTO_WIDGET", 
                                         "Failed to start new hand")
                
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("ERROR", "GTO_WIDGET", 
                                     f"Error starting hand: {e}")
    
    def _next_action(self):
        """Execute the next GTO action."""
        try:
            # Get current decision
            if not self.current_decision:
                self._get_next_action()
                return
            
            # Execute the action
            action = self.current_decision['action']
            amount = self.current_decision['amount']
            
            success = self.gto_state_machine.execute_action(action, amount)
            
            if success:
                # Update display
                self._update_display()
                
                # Get next action
                self._get_next_action()
                
                # Update decision history
                self._update_decision_history()
            else:
                self.status_var.set("Failed to execute action")
                
        except Exception as e:
            self.status_var.set(f"Error executing action: {str(e)}")
            if self.session_logger:
                self.session_logger.log_system("ERROR", "GTO_WIDGET", 
                                     f"Error executing action: {e}")
    
    def _get_next_action(self):
        """Get the next GTO decision."""
        try:
            # Get next action from state machine
            self.current_decision = self.gto_state_machine.get_next_action()
            
            if self.current_decision:
                # Update explanation
                explanation = self.current_decision['explanation']
                if self.decision_explanation_text:
                    self.decision_explanation_text.delete(1.0, tk.END)
                    self.decision_explanation_text.insert(1.0, explanation)
                
                # Update status
                player_name = self.current_decision['player_name']
                action = self.current_decision['action'].value
                amount = self.current_decision['amount']
                
                if amount > 0:
                    self.status_var.set(f"{player_name} to act: {action} ${amount}")
                else:
                    self.status_var.set(f"{player_name} to act: {action}")
                
                # Enable next button
                self.next_button.config(state=tk.NORMAL)
            else:
                # No more actions - hand complete
                self.status_var.set("Hand complete - no more actions")
                self.next_button.config(state=tk.DISABLED)
                self.auto_play_button.config(state=tk.DISABLED)
                
                # Show hand result
                self._show_hand_result()
                
        except Exception as e:
            self.status_var.set(f"Error getting next action: {str(e)}")
            if self.session_logger:
                self.session_logger.log_system("ERROR", "GTO_WIDGET", 
                                     f"Error getting next action: {e}")
    
    def _update_decision_history(self):
        """Update the decision history display."""
        if not self.decision_history_text:
            return
        
        try:
            # Get decision history from state machine
            history = self.gto_state_machine.get_decision_history()
            
            if history:
                # Clear current display
                self.decision_history_text.delete(1.0, tk.END)
                
                # Add each decision
                for i, decision in enumerate(history, 1):
                    player_name = decision['player_name']
                    position = decision['position']
                    action = decision['action']
                    amount = decision['amount']
                    street = decision['street'].value if hasattr(decision['street'], 'value') else str(decision['street'])
                    
                    # Format the decision line
                    if amount > 0:
                        decision_line = f"{i}. {player_name} ({position}) - {action} ${amount} [{street}]\n"
                    else:
                        decision_line = f"{i}. {player_name} ({position}) - {action} [{street}]\n"
                    
                    self.decision_history_text.insert(tk.END, decision_line)
                
                # Scroll to bottom
                self.decision_history_text.see(tk.END)
                
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("ERROR", "GTO_WIDGET", 
                                 f"Error updating decision history: {e}")
    
    def _show_hand_result(self):
        """Show the result of the completed hand."""
        try:
            # Get game summary
            summary = self.gto_state_machine.get_game_summary()
            
            # Find winner(s)
            active_players = [p for p in summary['players'] if not p['folded']]
            
            if len(active_players) == 1:
                winner = active_players[0]
                result_message = f"Hand complete! {winner['name']} wins ${summary['pot']}"
            else:
                result_message = f"Hand complete! {len(active_players)} players remain - showdown needed"
            
            # Log the result
            if self.session_logger:
                self.session_logger.log_system("INFO", "GTO_WIDGET", result_message)
                
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("ERROR", "GTO_WIDGET", 
                                     f"Error showing hand result: {e}")
    
    def _auto_play(self):
        """Automatically play through the hand."""
        # TODO: Implement auto-play functionality
        if self.session_logger:
            self.session_logger.log_system("INFO", "GTO_WIDGET", "Auto-play not yet implemented")
    
    def _pause_auto_play(self):
        """Pause auto-play."""
        # TODO: Implement pause functionality
        if self.session_logger:
            self.session_logger.log_system("INFO", "GTO_WIDGET", "Auto-play not yet implemented")
    
    def _on_gto_state_changed(self, game_state: GameState):
        """Handle GTO state machine state changes."""
        # Update display when state changes
        self._update_display()
    
    def _update_display(self):
        """Update the poker table display."""
        try:
            # Get current game state (also ensures SM is in sync)
            game_info = self.gto_state_machine.get_game_info()
            
            # Update the poker table display via base method
            if hasattr(self, '_update_from_fpsm_state'):
                self._update_from_fpsm_state()
            
            # Update decision history
            self._update_decision_history()
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_system("ERROR", "GTO_WIDGET", 
                                     f"Error updating display: {e}")
    
    def get_current_decision(self) -> Optional[Dict[str, Any]]:
        """Get the current GTO decision."""
        return self.current_decision
    
    def get_decision_explanation(self) -> str:
        """Get the current decision explanation."""
        return self.decision_explanation_var.get()
    
    def get_decision_history(self) -> list:
        """Get the complete decision history."""
        return self.gto_state_machine.get_decision_history()

    def _update_player_from_display_state(self, player_index: int, player_info: dict):
        """Update player UI from display state; no text bet labels in GTO mode.
 
        This mirrors the hands review/practice approach: update name/stack/cards/fold
        and explicitly show chip bet graphics when current_bet > 0 (covers SB/BB and bets).
        """
        # Ensure seat exists
        if (
            player_index >= len(self.player_seats)
            or not self.player_seats[player_index]
        ):
            return
 
        player_seat = self.player_seats[player_index]
 
        # Cached last state for minimal updates
        last_state = getattr(self, "last_player_states", {}).get(player_index, {})
 
        # Extract new state
        name = player_info.get("name", f"Player {player_index + 1}")
        position = player_info.get("position", "")
        stack_amount = player_info.get("stack", 0.0)
        cards = player_info.get("cards", [])
        has_folded = player_info.get("has_folded", False)
        bet_amount = player_info.get("current_bet", 0.0)
 
        # Update name
        name_text = f"{name} ({position})"
        if last_state.get("name_text") != name_text:
            player_seat["name_label"].config(text=name_text)
 
        # Update stack
        if last_state.get("stack", 0.0) != stack_amount:
            player_seat["stack_label"].config(text=f"${int(stack_amount):,}")
 
        # Show chip bet graphics (covers blinds and regular bets)
        if bet_amount and bet_amount > 0:
            # Ensure chip display exists and update it
            try:
                self._show_bet_display_for_player(player_index, "bet", bet_amount)
            except Exception:
                # Create then retry if needed
                self._create_bet_display_for_player(player_index)
                self._show_bet_display_for_player(player_index, "bet", bet_amount)
 
        # Update cards (always visible in GTO sim; already provided by SM)
        last_cards = last_state.get("cards", [])
        if last_cards != cards:
            self._set_player_cards_from_display_state(player_index, cards)
 
        # Folded state
        if last_state.get("has_folded", False) != has_folded:
            if has_folded:
                self._mark_player_folded(player_index)
            else:
                self._unmark_player_folded(player_index)
 
        # Store current state
        if not hasattr(self, "last_player_states"):
            self.last_player_states = {}
        self.last_player_states[player_index] = {
            "name_text": name_text,
            "stack": stack_amount,
            "cards": cards,
            "has_folded": has_folded,
            "current_bet": bet_amount,
        }
 
    # Use base class implementations for bet display (chip graphics)

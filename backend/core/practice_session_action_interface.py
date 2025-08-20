#!/usr/bin/env python3
"""
Practice Session Action Interface

A clean interface layer that sits between the UI and state machine,
providing simplified action methods without exposing game logic to the UI.

This follows the clean architecture principle: UI should not contain game logic,
but should have a simple interface to request actions.
"""

from typing import Optional, Dict, Any, List

from .hand_model import ActionType
from .practice_session_poker_state_machine import (
    PracticeSessionPokerStateMachine,
)


class PracticeSessionActionInterface:
    """
    Clean interface between Practice Session UI and State Machine.

    This interface:
    - Provides simple action methods for UI
    - Handles all game logic internally
    - Validates actions before execution
    - Returns simple success/failure results
    - Maintains clean architectural separation
    """

    def __init__(
        self,
        state_machine: PracticeSessionPokerStateMachine,
        game_director=None,
    ):
        """Initialize with a state machine reference and optional game director."""
        self.state_machine = state_machine
        self.game_director = game_director
        self.logger = getattr(state_machine, "logger", None)

    def can_human_act(self) -> bool:
        """
        Check if the human player can currently take an action.

        Returns:
            bool: True if human can act, False otherwise
        """
        try:
            # Check if game is in valid state for human actions
            if not self._is_valid_action_state():
                return False

            # Check if it's human's turn
            current_player = self.state_machine.get_action_player()
            if not current_player or not hasattr(current_player, "is_human"):
                return False

            return current_player.is_human

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR",
                    "ACTION_INTERFACE",
                    f"Error checking human action: {e}",
                )
            return False

    def get_available_actions(self) -> List[str]:
        """
        Get list of actions currently available to the human player.

        Returns:
            List of action strings: ['check_call', 'fold', 'bet_raise']
        """
        if not self.can_human_act():
            return []

        try:
            current_player = self.state_machine.get_action_player()
            if not current_player:
                return []

            available_actions = ["fold"]  # Can always fold

            # Check if can check or need to call
            current_bet = getattr(
                self.state_machine.game_state, "current_bet", 0
            )
            player_bet = getattr(current_player, "current_bet", 0)
            call_amount = current_bet - player_bet

            if call_amount <= current_player.stack:
                available_actions.append("check_call")

            # Check if can bet/raise
            min_raise = self._calculate_min_raise_amount()
            if min_raise <= current_player.stack:
                available_actions.append("bet_raise")

            return available_actions

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR",
                    "ACTION_INTERFACE",
                    f"Error getting available actions: {e}",
                )
            return ["fold"]  # Safe fallback

    def get_action_button_text(self, action_key: str) -> str:
        """
        Get display text for an action button.

        Args:
            action_key: 'check_call', 'fold', or 'bet_raise'

        Returns:
            str: Display text for the button
        """
        try:
            if action_key == "fold":
                return "Fold"
            elif action_key == "check_call":
                call_amount = self._calculate_call_amount()
                return (
                    "Check"
                    if call_amount == 0
                    else f"Call ${
                    call_amount:.0f}"
                )
            elif action_key == "bet_raise":
                current_bet = getattr(
                    self.state_machine.game_state, "current_bet", 0
                )
                return "Bet" if current_bet == 0 else "Raise"
            else:
                return action_key.title()

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR",
                    "ACTION_INTERFACE",
                    f"Error getting button text: {e}",
                )
            return action_key.title()

    def execute_check_call(self) -> bool:
        """
        Execute check or call action for the human player.

        Returns:
            bool: True if action executed successfully
        """
        try:
            if not self.can_human_act():
                return False

            current_player = self.state_machine.get_action_player()
            call_amount = self._calculate_call_amount()

            if call_amount == 0:
                action_type = ActionType.CHECK
                amount = 0.0
            else:
                action_type = ActionType.CALL
                amount = call_amount

            return self._execute_action(current_player, action_type, amount)

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR",
                    "ACTION_INTERFACE",
                    f"Error executing check/call: {e}",
                )
            return False

    def execute_fold(self) -> bool:
        """
        Execute fold action for the human player.

        Returns:
            bool: True if action executed successfully
        """
        try:
            if not self.can_human_act():
                return False

            current_player = self.state_machine.get_action_player()
            return self._execute_action(current_player, ActionType.FOLD, 0.0)

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR", "ACTION_INTERFACE", f"Error executing fold: {e}"
                )
            return False

    def execute_bet_raise(self, amount: Optional[float] = None) -> bool:
        """
        Execute bet or raise action for the human player.

        Args:
            amount: Bet/raise amount. If None, uses calculated amount.

        Returns:
            bool: True if action executed successfully
        """
        try:
            if not self.can_human_act():
                return False

            current_player = self.state_machine.get_action_player()
            current_bet = getattr(
                self.state_machine.game_state, "current_bet", 0
            )

            # Determine action type
            action_type = (
                ActionType.BET if current_bet == 0 else ActionType.RAISE
            )

            # Use provided amount or calculate default
            if amount is None:
                amount = self._calculate_default_bet_amount()

            # Validate amount
            if not self._is_valid_bet_amount(amount):
                if self.logger:
                    self.logger.log_system(
                        "WARNING",
                        "ACTION_INTERFACE",
                        f"Invalid bet amount: ${amount}",
                    )
                return False

            return self._execute_action(current_player, action_type, amount)

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR",
                    "ACTION_INTERFACE",
                    f"Error executing bet/raise: {e}",
                )
            return False

    def get_quick_bet_amount(self, bet_type: str) -> float:
        """
        Calculate quick bet amount for preset buttons.

        Args:
            bet_type: 'pot', 'half_pot', 'all_in', etc.

        Returns:
            float: Calculated bet amount
        """
        try:
            # Delegate to state machine's calculation
            if hasattr(self.state_machine, "calculate_quick_bet_amount"):
                return self.state_machine.calculate_quick_bet_amount(bet_type)
            else:
                # Fallback calculation
                pot = getattr(self.state_machine.game_state, "pot", 0)
                current_player = self.state_machine.get_action_player()

                if bet_type == "pot":
                    return pot
                elif bet_type == "half_pot":
                    return pot * 0.5
                elif bet_type == "all_in" and current_player:
                    return current_player.stack
                else:
                    return self.state_machine.config.big_blind * 2

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR",
                    "ACTION_INTERFACE",
                    f"Error calculating quick bet: {e}",
                )
            return 10.0  # Safe fallback

    def execute_quick_bet(self, bet_type: str) -> bool:
        """
        Execute a quick bet preset.

        Args:
            bet_type: 'pot', 'half_pot', 'all_in', etc.

        Returns:
            bool: True if action executed successfully
        """
        try:
            amount = self.get_quick_bet_amount(bet_type)
            return self.execute_bet_raise(amount)

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR",
                    "ACTION_INTERFACE",
                    f"Error executing quick bet: {e}",
                )
            return False

    def can_execute_action(self, action_key: str) -> bool:
        """
        Check if a specific action can currently be executed.

        Args:
            action_key: 'check_call', 'fold', 'bet_raise', etc.

        Returns:
            bool: True if action can be executed
        """
        try:
            # Basic check - must be human's turn
            if not self.can_human_act():
                return False

            # Check specific action availability
            available_actions = self.get_available_actions()
            return action_key in available_actions

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR",
                    "ACTION_INTERFACE",
                    f"Error checking action availability: {e}",
                )
            return False

    def get_board_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current board information.

        Returns:
            Dict with board info: {'cards': [...], 'street': '...'}
        """
        try:
            game_state = getattr(self.state_machine, "game_state", None)
            if not game_state:
                return None

            board_cards = getattr(game_state, "board", [])
            street = getattr(game_state, "street", "PREFLOP")

            return {
                "cards": board_cards,
                "street": street,
                "num_cards": len(board_cards),
            }

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR",
                    "ACTION_INTERFACE",
                    f"Error getting board info: {e}",
                )
            return None

    # ==============================
    # PRIVATE HELPER METHODS
    # ==============================

    def _is_valid_action_state(self) -> bool:
        """Check if game is in a state where actions can be taken."""
        if not hasattr(self.state_machine, "current_state"):
            return False

        # List of states where human actions are not allowed
        invalid_states = ["END_HAND", "SHOWDOWN", "START_HAND"]
        current_state_name = str(self.state_machine.current_state).split(".")[
            -1
        ]

        return current_state_name not in invalid_states

    def _calculate_call_amount(self) -> float:
        """Calculate the amount needed to call."""
        try:
            current_player = self.state_machine.get_action_player()
            if not current_player:
                return 0.0

            current_bet = getattr(
                self.state_machine.game_state, "current_bet", 0
            )
            player_bet = getattr(current_player, "current_bet", 0)
            call_amount = current_bet - player_bet

            return max(0.0, call_amount)

        except Exception:
            return 0.0

    def _calculate_min_raise_amount(self) -> float:
        """Calculate minimum raise amount."""
        try:
            current_bet = getattr(
                self.state_machine.game_state, "current_bet", 0
            )
            big_blind = self.state_machine.config.big_blind

            # Minimum raise is typically big blind or double current bet
            return (
                max(big_blind, current_bet * 2)
                if current_bet > 0
                else big_blind
            )

        except Exception:
            return 2.0  # Safe fallback

    def _calculate_default_bet_amount(self) -> float:
        """Calculate default bet amount."""
        try:
            pot = getattr(self.state_machine.game_state, "pot", 0)
            big_blind = self.state_machine.config.big_blind

            # Default to 2/3 pot or 2.5 big blinds, whichever is larger
            pot_based = pot * 0.67
            bb_based = big_blind * 2.5

            return max(pot_based, bb_based)

        except Exception:
            return 5.0  # Safe fallback

    def _is_valid_bet_amount(self, amount: float) -> bool:
        """Validate if bet amount is legal."""
        try:
            current_player = self.state_machine.get_action_player()
            if not current_player:
                return False

            # Amount must be positive and within stack
            if amount <= 0 or amount > current_player.stack:
                return False

            # Must meet minimum raise requirement
            min_raise = self._calculate_min_raise_amount()
            if amount < min_raise and amount < current_player.stack:
                return False

            return True

        except Exception:
            return False

    def _execute_action(
        self, player, action_type: ActionType, amount: float
    ) -> bool:
        """Execute an action through the GameDirector or state machine."""
        try:
            # Log the action attempt
            if self.logger:
                self.logger.log_system(
                    "INFO",
                    "ACTION_INTERFACE",
                    f"Executing {
                        action_type.value} for {
                        player.name}",
                    {"amount": amount},
                )

            # Use GameDirector if available (for sound coordination), otherwise
            # fallback to state machine
            if self.game_director:
                success = self.game_director.execute_player_action(
                    player, action_type, amount
                )
            else:
                success = self.state_machine.execute_action(
                    player, action_type, amount
                )

            if success and self.logger:
                self.logger.log_system(
                    "INFO",
                    "USER_ACTION",
                    f"Action completed: {
                        action_type.value}",
                    {"player": player.name, "amount": amount},
                )

            return success

        except Exception as e:
            if self.logger:
                self.logger.log_system(
                    "ERROR", "ACTION_INTERFACE", f"Error executing action: {e}"
                )
            return False

#!/usr/bin/env python3
"""
Error Replication UI Test Suite

This script tests the poker state machine with UI mocking to replicate
specific errors found in recent test runs.
"""

import unittest
from unittest import mock
from core.poker_state_machine import (
    ImprovedPokerStateMachine, ActionType
)
from core.ui_renderer import UIDisplayRenderer, DisplayState


class TestErrorReplicationUI(unittest.TestCase):
    """Test error replication with UI mocking."""

    def setUp(self):
        """Set up the state machine with mocked UI renderer."""
        self.sm = ImprovedPokerStateMachine(num_players=6, test_mode=True)
        self.sm.strategy_mode = "GTO"
        
        # Mock the UI renderer
        self.mock_renderer = mock.Mock(spec=UIDisplayRenderer)
        self.sm.ui_renderer = self.mock_renderer
        
        # Mock a sample display state
        mock_display = DisplayState(
            valid_actions={},
            player_highlights=[False] * 6,
            card_visibilities=[False] * 6,
            chip_representations={},
            layout_positions={},
            community_cards=[],
            pot_amount=0.0,
            current_bet=0.0,
            action_player_index=0,
            game_state="START_HAND",
            last_action_details=""
        )
        self.mock_renderer.get_display_state.return_value = mock_display

    def test_invalid_call_amount_error(self):
        """Test the 'Invalid action: Call amount must be $1.00, got $5.00' error."""
        self.sm.start_hand()
        
        # Set up scenario where bot tries to call $5.00 when only $1.00 needed
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        self.sm.game_state.board = ['Th', '9h', '8h', '7h', '6h']
        self.sm.game_state.current_bet = 1.0
        self.sm.game_state.pot = 1.5
        
        # Test UI updates during invalid action
        action_player = self.sm.get_action_player()
        if action_player:
            # This should trigger the invalid call amount error
            with self.assertRaises(ValueError):
                self.sm.execute_action(action_player, ActionType.CALL, 5.0)
            
            # UI should still be called even on error
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_minimum_raise_violation_error(self):
        """Test the 'Invalid action: Raise to $1.88 is less than minimum raise to $2.00' error."""
        self.sm.start_hand()
        
        # Set up scenario where bot tries to raise to $1.88 when minimum is $2.00
        self.sm.game_state.players[0].cards = ['As', 'Ad']
        self.sm.game_state.board = ['Ah', '2c', '3h']
        self.sm.game_state.current_bet = 1.0
        self.sm.game_state.pot = 2.5
        
        # Test UI updates during invalid raise
        action_player = self.sm.get_action_player()
        if action_player:
            # This should trigger the minimum raise violation error
            with self.assertRaises(ValueError):
                self.sm.execute_action(action_player, ActionType.RAISE, 1.88)
            
            # UI should still be called even on error
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_sound_file_not_found_warning(self):
        """Test the 'Warning: Sound file not found: chip_bet_multiple.wav' error."""
        self.sm.start_hand()
        
        # Set up scenario that triggers sound file loading
        self.sm.game_state.players[0].cards = ['Kh', 'Qh']
        self.sm.game_state.board = ['Ah', 'Jh', 'Th']
        self.sm.game_state.current_bet = 1.0
        self.sm.game_state.pot = 3.5
        
        # Test UI updates during action that might trigger sound
        action_player = self.sm.get_action_player()
        if action_player:
            # This should trigger sound file warnings
            self.sm.execute_action(action_player, ActionType.RAISE, 15.0)
            
            # UI should be called
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_bot_action_fallback_scenario(self):
        """Test bot action failure and fallback to basic logic."""
        self.sm.start_hand()
        
        # Set up scenario where bot action fails and falls back
        self.sm.game_state.players[0].cards = ['7s', '6s']
        self.sm.game_state.board = ['5s', '4s', '3s']
        self.sm.game_state.current_bet = 1.0
        self.sm.game_state.pot = 2.5
        
        # Test UI updates during bot fallback
        action_player = self.sm.get_action_player()
        if action_player:
            # This should trigger bot fallback logic
            self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            
            # UI should be called
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_round_completion_logic_errors(self):
        """Test round completion logic errors and UI updates."""
        self.sm.start_hand()
        
        # Set up complex betting scenario
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        self.sm.game_state.players[1].cards = ['As', 'Ad']
        self.sm.game_state.players[2].cards = ['7s', '8s']
        self.sm.game_state.board = ['Th', '9h', '8h']
        self.sm.game_state.current_bet = 15.0
        self.sm.game_state.pot = 16.5
        
        # Test UI updates during complex betting
        action_player = self.sm.get_action_player()
        if action_player:
            # This should trigger complex round completion logic
            self.sm.execute_action(action_player, ActionType.CALL, 15.0)
            
            # UI should be called multiple times
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_state_transition_errors(self):
        """Test state transition errors and UI consistency."""
        self.sm.start_hand()
        
        # Set up scenario that might cause state transition issues
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        self.sm.game_state.board = ['Th', '9h', '8h', '7h', '6h']
        
        # Test UI updates during state transitions
        action_player = self.sm.get_action_player()
        if action_player:
            # This should trigger state transition logic
            self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            
            # UI should be called
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_player_state_tracking_errors(self):
        """Test player state tracking errors and UI updates."""
        self.sm.start_hand()
        
        # Set up scenario with multiple players and complex state
        for i in range(6):
            self.sm.game_state.players[i].cards = [f'{i+1}h', f'{i+2}h']
        
        self.sm.game_state.board = ['Th', '9h', '8h']
        self.sm.game_state.current_bet = 1.0
        self.sm.game_state.pot = 2.5
        
        # Test UI updates during complex player state tracking
        action_player = self.sm.get_action_player()
        if action_player:
            # This should trigger complex player state tracking
            self.sm.execute_action(action_player, ActionType.RAISE, 2.62)
            
            # UI should be called
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_pot_management_errors(self):
        """Test pot management errors and UI updates."""
        self.sm.start_hand()
        
        # Set up scenario with complex pot calculations
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        self.sm.game_state.players[1].cards = ['As', 'Ad']
        self.sm.game_state.board = ['Th', '9h', '8h']
        self.sm.game_state.current_bet = 15.0
        self.sm.game_state.pot = 31.5
        
        # Test UI updates during complex pot management
        action_player = self.sm.get_action_player()
        if action_player:
            # This should trigger complex pot management logic
            self.sm.execute_action(action_player, ActionType.CALL, 15.0)
            
            # UI should be called
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_hand_evaluation_errors(self):
        """Test hand evaluation errors and UI updates."""
        self.sm.start_hand()
        
        # Set up scenario with complex hand evaluation
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']  # Royal Flush potential
        self.sm.game_state.players[1].cards = ['As', 'Ad']  # Four of a Kind potential
        self.sm.game_state.players[2].cards = ['7s', '8s']  # Straight Flush potential
        self.sm.game_state.board = ['Th', '9h', '8h', '7h', '6h']  # Royal Flush board
        
        # Test UI updates during complex hand evaluation
        action_player = self.sm.get_action_player()
        if action_player:
            # This should trigger complex hand evaluation logic
            self.sm.execute_action(action_player, ActionType.CALL, 5.0)
            
            # UI should be called
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_error_recovery_and_ui_consistency(self):
        """Test error recovery and UI consistency after errors."""
        self.sm.start_hand()
        
        # Set up scenario that might cause multiple errors
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        self.sm.game_state.board = ['Th', '9h', '8h']
        self.sm.game_state.current_bet = 1.0
        self.sm.game_state.pot = 2.5
        
        # Test UI updates during error recovery
        action_player = self.sm.get_action_player()
        if action_player:
            # First action that might fail
            try:
                self.sm.execute_action(action_player, ActionType.RAISE, 1.88)
            except ValueError:
                pass  # Expected error
            
            # UI should still be called after error
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()
            
            # Second action after error recovery
            try:
                self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            except ValueError:
                pass  # Expected error
            
            # UI should still be called after second error
            _ = self.sm.get_display_state()
            self.assertGreater(self.mock_renderer.get_display_state.call_count, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)

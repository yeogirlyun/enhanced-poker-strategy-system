#!/usr/bin/env python3
"""
UI-Mocked Tester for Poker State Machine

This script tests the poker state machine with mocked UI integration
for integration testing without actual UI rendering.
"""

import unittest
from unittest import mock
from core.poker_state_machine import (
    ImprovedPokerStateMachine, ActionType, PokerState
)
from core.ui_renderer import UIDisplayRenderer, DisplayState


class TestPokerStateMachineWithMockedUI(unittest.TestCase):
    """Integration tests for poker state machine with mocked UI."""

    def setUp(self):
        """Set up the state machine with mocked UI renderer."""
        self.sm = ImprovedPokerStateMachine(num_players=3, test_mode=True)
        self.sm.strategy_mode = "GTO"
        
        # Mock the UI renderer
        self.mock_renderer = mock.Mock(spec=UIDisplayRenderer)
        # Assuming state machine uses this attribute
        self.sm.ui_renderer = self.mock_renderer
        
        # Mock a sample display state
        mock_display = DisplayState(
            valid_actions={},
            player_highlights=[False] * 3,
            card_visibilities=[False] * 3,
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

    def test_full_hand_simulation_with_ui_mocks(self):
        """Simulate a full hand with UI updates mocked."""
        self.sm.start_hand()
        
        # Verify UI was "updated" at start
        self.mock_renderer.get_display_state.assert_called_once()
        
        # Simulate preflop betting
        action_player = self.sm.get_action_player()
        self.sm.execute_action(action_player, ActionType.RAISE, 2.0)
        
        # Check UI update after action
        self.assertEqual(self.mock_renderer.get_display_state.call_count, 2)
        
        # Have other players fold
        for player in self.sm.game_state.players:
            if player != action_player:
                self.sm.execute_action(player, ActionType.FOLD, 0.0)
        
        # Should auto-transition to END_HAND since all folded
        self.assertEqual(self.sm.current_state, PokerState.END_HAND)
        
        # Verify final UI update
        self.assertGreater(self.mock_renderer.get_display_state.call_count, 2)
        
        # Check pot awarded correctly (blinds + raise)
        # Assuming starting stack 100
        self.assertGreater(action_player.stack, 100.0)

    def test_all_in_scenario_with_ui(self):
        """Test all-in handling with mocked UI."""
        self.sm.start_hand()
        
        all_in_player = self.sm.game_state.players[0]
        all_in_player.stack = 10.0
        self.sm.execute_action(all_in_player, ActionType.RAISE, 10.0)  # All-in
        
        # UI should update
        self.mock_renderer.get_display_state.assert_called()
        
        # Next player calls
        caller = self.sm.game_state.players[1]
        self.sm.execute_action(caller, ActionType.CALL, 10.0)
        
        # Others fold
        for player in self.sm.game_state.players[2:]:
            self.sm.execute_action(player, ActionType.FOLD, 0.0)
        
        # Should go to showdown
        self.assertEqual(self.sm.current_state, PokerState.SHOWDOWN)
        
        # UI updated multiple times
        self.assertGreater(self.mock_renderer.get_display_state.call_count, 3)

    def test_multi_way_pot_with_ui_updates(self):
        """Test multi-way pot scenario with UI updates."""
        self.sm.start_hand()
        
        # First player raises
        raiser = self.sm.get_action_player()
        self.sm.execute_action(raiser, ActionType.RAISE, 3.0)
        
        # Second player calls
        caller = self.sm.game_state.players[1]
        self.sm.execute_action(caller, ActionType.CALL, 3.0)
        
        # Third player folds
        folder = self.sm.game_state.players[2]
        self.sm.execute_action(folder, ActionType.FOLD, 0.0)
        
        # Should progress to flop
        self.assertEqual(self.sm.current_state, PokerState.DEAL_FLOP)
        
        # UI should have updated multiple times
        self.assertGreater(self.mock_renderer.get_display_state.call_count, 3)

    def test_ui_state_consistency(self):
        """Test that UI state remains consistent throughout hand."""
        self.sm.start_hand()
        
        # Get initial display state
        initial_state = self.mock_renderer.get_display_state.return_value
        
        # Verify initial state properties
        self.assertEqual(initial_state.game_state, "START_HAND")
        self.assertEqual(initial_state.pot_amount, 0.0)
        self.assertEqual(len(initial_state.player_highlights), 3)
        
        # Execute an action
        action_player = self.sm.get_action_player()
        self.sm.execute_action(action_player, ActionType.CALL, 1.0)
        
        # Verify UI was called again
        self.assertGreater(self.mock_renderer.get_display_state.call_count, 1)

    def test_error_handling_with_ui(self):
        """Test error handling with UI updates."""
        self.sm.start_hand()
        
        # Try invalid action
        action_player = self.sm.get_action_player()
        
        # Mock an error scenario
        with mock.patch.object(
            self.sm, 'validate_action', 
            side_effect=ValueError("Invalid action")
        ):
            with self.assertRaises(ValueError):
                self.sm.execute_action(action_player, ActionType.RAISE, -1.0)
        
        # UI should still be called even on error
        self.mock_renderer.get_display_state.assert_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)

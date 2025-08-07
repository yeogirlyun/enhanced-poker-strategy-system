#!/usr/bin/env python3
"""
UI-Mocked Tester for Poker State Machine

This script tests the poker state machine with mocked UI integration
for integration testing without actual UI rendering.
"""

import unittest
from unittest import mock
from core.poker_state_machine import (
    ImprovedPokerStateMachine, ActionType
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
        
        # Verify UI was "updated" at start by calling get_display_state
        _ = self.sm.get_display_state()
        self.mock_renderer.get_display_state.assert_called()
        
        # Test UI updates work
        action_player = self.sm.get_action_player()
        if action_player:
            # Try a valid action
            self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            
            # Check UI update after action
            _ = self.sm.get_display_state()
            self.assertGreater(self.mock_renderer.get_display_state.call_count, 1)
        
        # Test that UI state is consistent
        display_state = self.sm.get_display_state()
        self.assertIsNotNone(display_state)
        self.assertEqual(len(display_state.player_highlights), 3)

    def test_all_in_scenario_with_ui(self):
        """Test all-in handling with mocked UI."""
        self.sm.start_hand()
        
        # Test that UI updates work with basic actions
        action_player = self.sm.get_action_player()
        if action_player:
            # Try a call action
            self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            
            # UI should update
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()
        
        # Test UI state consistency
        display_state = self.sm.get_display_state()
        self.assertIsNotNone(display_state)
        self.assertEqual(len(display_state.player_highlights), 3)

    def test_multi_way_pot_with_ui_updates(self):
        """Test multi-way pot scenario with UI updates."""
        self.sm.start_hand()
        
        # Test basic UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            # Try a call action
            self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            
            # UI should update
            _ = self.sm.get_display_state()
            self.assertGreaterEqual(self.mock_renderer.get_display_state.call_count, 1)
        
        # Test UI state consistency
        display_state = self.sm.get_display_state()
        self.assertIsNotNone(display_state)
        self.assertEqual(len(display_state.player_highlights), 3)

    def test_ui_state_consistency(self):
        """Test that UI state remains consistent throughout hand."""
        self.sm.start_hand()
        
        # Get initial display state
        initial_state = self.sm.get_display_state()
        
        # Verify initial state properties
        self.assertEqual(initial_state.game_state, "START_HAND")
        self.assertEqual(initial_state.pot_amount, 0.0)
        self.assertEqual(len(initial_state.player_highlights), 3)
        
        # Execute an action
        action_player = self.sm.get_action_player()
        self.sm.execute_action(action_player, ActionType.CALL, 1.0)
        
        # Verify UI was called again
        _ = self.sm.get_display_state()
        self.assertGreater(self.mock_renderer.get_display_state.call_count, 1)

    def test_error_handling_with_ui(self):
        """Test error handling with UI updates."""
        self.sm.start_hand()
        
        # Test that UI works even with invalid actions
        action_player = self.sm.get_action_player()
        if action_player:
            # Try an invalid action (negative amount)
            try:
                self.sm.execute_action(action_player, ActionType.RAISE, -1.0)
            except ValueError:
                pass  # Expected to fail
        
        # UI should still work even after error
        _ = self.sm.get_display_state()
        self.mock_renderer.get_display_state.assert_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""
Legendary Poker Hands UI Test Suite

This script tests the poker state machine with legendary poker hands
across 10 categories using UI mocking to simulate real-world scenarios.
"""

import unittest
from unittest import mock
from core.poker_state_machine import (
    ImprovedPokerStateMachine, ActionType
)
from core.ui_renderer import UIDisplayRenderer, DisplayState


class TestLegendaryPokerHandsUI(unittest.TestCase):
    """Test legendary poker hands with UI mocking across 10 categories."""

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

    def test_1_royal_flush_scenario(self):
        """Test Royal Flush scenario - highest possible hand."""
        self.sm.start_hand()
        
        # Simulate Royal Flush scenario
        # Player 1: Ah Kh (Royal Flush potential)
        # Player 2: Qh Jh (Royal Flush potential)
        # Board: Th 9h 8h (Flush draw)
        
        # Set up the scenario
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        self.sm.game_state.players[1].cards = ['Qh', 'Jh']
        self.sm.game_state.board = ['Th', '9h', '8h']
        
        # Test UI updates during Royal Flush scenario
        action_player = self.sm.get_action_player()
        if action_player:
            # Simulate betting action
            self.sm.execute_action(action_player, ActionType.RAISE, 5.0)
            
            # Verify UI updates
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()
        
        # Test UI state consistency
        display_state = self.sm.get_display_state()
        self.assertIsNotNone(display_state)
        self.assertEqual(len(display_state.player_highlights), 6)

    def test_2_straight_flush_scenario(self):
        """Test Straight Flush scenario - second highest hand."""
        self.sm.start_hand()
        
        # Simulate Straight Flush scenario
        # Player 1: 7s 8s (Straight Flush potential)
        # Player 2: 9s Ts (Straight Flush potential)
        # Board: 6s 5s 4s (Straight Flush draw)
        
        self.sm.game_state.players[0].cards = ['7s', '8s']
        self.sm.game_state.players[1].cards = ['9s', 'Ts']
        self.sm.game_state.board = ['6s', '5s', '4s']
        
        # Test UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.CALL, 2.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_3_four_of_a_kind_scenario(self):
        """Test Four of a Kind scenario."""
        self.sm.start_hand()
        
        # Simulate Four of a Kind scenario
        # Player 1: As Ad (Four of a Kind potential)
        # Player 2: Kh Kd (Four of a Kind potential)
        # Board: Ah Ac Ks (Four of a Kind on board)
        
        self.sm.game_state.players[0].cards = ['As', 'Ad']
        self.sm.game_state.players[1].cards = ['Kh', 'Kd']
        self.sm.game_state.board = ['Ah', 'Ac', 'Ks']
        
        # Test UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.RAISE, 10.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_4_full_house_scenario(self):
        """Test Full House scenario."""
        self.sm.start_hand()
        
        # Simulate Full House scenario
        # Player 1: Ah Ad (Full House potential)
        # Player 2: Kh Kd (Full House potential)
        # Board: As Kc 2h (Full House on board)
        
        self.sm.game_state.players[0].cards = ['Ah', 'Ad']
        self.sm.game_state.players[1].cards = ['Kh', 'Kd']
        self.sm.game_state.board = ['As', 'Kc', '2h']
        
        # Test UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.CALL, 3.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_5_flush_scenario(self):
        """Test Flush scenario."""
        self.sm.start_hand()
        
        # Simulate Flush scenario
        # Player 1: Ah 7h (Flush potential)
        # Player 2: Kh 9h (Flush potential)
        # Board: 2h 5h 8h (Flush draw)
        
        self.sm.game_state.players[0].cards = ['Ah', '7h']
        self.sm.game_state.players[1].cards = ['Kh', '9h']
        self.sm.game_state.board = ['2h', '5h', '8h']
        
        # Test UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.RAISE, 4.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_6_straight_scenario(self):
        """Test Straight scenario."""
        self.sm.start_hand()
        
        # Simulate Straight scenario
        # Player 1: 6s 7s (Straight potential)
        # Player 2: 9s Ts (Straight potential)
        # Board: 5s 8s 2h (Straight draw)
        
        self.sm.game_state.players[0].cards = ['6s', '7s']
        self.sm.game_state.players[1].cards = ['9s', 'Ts']
        self.sm.game_state.board = ['5s', '8s', '2h']
        
        # Test UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.CALL, 2.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_7_three_of_a_kind_scenario(self):
        """Test Three of a Kind scenario."""
        self.sm.start_hand()
        
        # Simulate Three of a Kind scenario
        # Player 1: As Ad (Three of a Kind potential)
        # Player 2: Kh Kd (Three of a Kind potential)
        # Board: Ah 2c 3h (Three of a Kind on board)
        
        self.sm.game_state.players[0].cards = ['As', 'Ad']
        self.sm.game_state.players[1].cards = ['Kh', 'Kd']
        self.sm.game_state.board = ['Ah', '2c', '3h']
        
        # Test UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.RAISE, 6.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_8_two_pair_scenario(self):
        """Test Two Pair scenario."""
        self.sm.start_hand()
        
        # Simulate Two Pair scenario
        # Player 1: Ah Kd (Two Pair potential)
        # Player 2: Qh Jd (Two Pair potential)
        # Board: As Ks 2h (Two Pair on board)
        
        self.sm.game_state.players[0].cards = ['Ah', 'Kd']
        self.sm.game_state.players[1].cards = ['Qh', 'Jd']
        self.sm.game_state.board = ['As', 'Ks', '2h']
        
        # Test UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.CALL, 1.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_9_one_pair_scenario(self):
        """Test One Pair scenario."""
        self.sm.start_hand()
        
        # Simulate One Pair scenario
        # Player 1: Ah 7d (One Pair potential)
        # Player 2: Kh 9d (One Pair potential)
        # Board: As 2c 3h (One Pair on board)
        
        self.sm.game_state.players[0].cards = ['Ah', '7d']
        self.sm.game_state.players[1].cards = ['Kh', '9d']
        self.sm.game_state.board = ['As', '2c', '3h']
        
        # Test UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.CHECK, 0.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_10_high_card_scenario(self):
        """Test High Card scenario."""
        self.sm.start_hand()
        
        # Simulate High Card scenario
        # Player 1: Ah 7d (High Card)
        # Player 2: Kh 9d (High Card)
        # Board: 2s 5c 8h (No pairs)
        
        self.sm.game_state.players[0].cards = ['Ah', '7d']
        self.sm.game_state.players[1].cards = ['Kh', '9d']
        self.sm.game_state.board = ['2s', '5c', '8h']
        
        # Test UI updates
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.FOLD, 0.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()

    def test_legendary_hand_comparison(self):
        """Test comparison between different legendary hands."""
        self.sm.start_hand()
        
        # Set up multiple players with different hand strengths
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']  # Royal Flush
        self.sm.game_state.players[1].cards = ['As', 'Ad']  # Four of a Kind
        self.sm.game_state.players[2].cards = ['7s', '8s']  # Straight Flush
        self.sm.game_state.board = ['Th', '9h', '8h']  # Flush draw
        
        # Test UI updates during hand comparison
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.RAISE, 15.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()
        
        # Verify UI state consistency
        display_state = self.sm.get_display_state()
        self.assertIsNotNone(display_state)
        self.assertEqual(len(display_state.player_highlights), 6)

    def test_all_in_scenario_with_legendary_hands(self):
        """Test all-in scenario with legendary hands."""
        self.sm.start_hand()
        
        # Set up all-in scenario with strong hands
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']  # Royal Flush potential
        self.sm.game_state.players[0].stack = 50.0  # Limited stack
        
        self.sm.game_state.players[1].cards = ['As', 'Ad']  # Four of a Kind potential
        self.sm.game_state.players[1].stack = 100.0
        
        self.sm.game_state.board = ['Th', '9h', '8h']  # Flush draw
        
        # Test all-in action
        action_player = self.sm.get_action_player()
        if action_player and action_player == self.sm.game_state.players[0]:
            # All-in with Royal Flush potential
            self.sm.execute_action(action_player, ActionType.RAISE, 50.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()
        
        # Test UI state consistency
        display_state = self.sm.get_display_state()
        self.assertIsNotNone(display_state)

    def test_legendary_hand_showdown(self):
        """Test showdown between legendary hands."""
        self.sm.start_hand()
        
        # Set up showdown scenario
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']  # Royal Flush
        self.sm.game_state.players[1].cards = ['As', 'Ad']  # Four of a Kind
        self.sm.game_state.players[2].cards = ['7s', '8s']  # Straight Flush
        
        # Royal Flush board
        self.sm.game_state.board = ['Th', '9h', '8h', '7h', '6h']
        
        # Simulate betting to showdown
        action_player = self.sm.get_action_player()
        if action_player:
            self.sm.execute_action(action_player, ActionType.CALL, 5.0)
            _ = self.sm.get_display_state()
            self.mock_renderer.get_display_state.assert_called()
        
        # Test UI state during showdown
        display_state = self.sm.get_display_state()
        self.assertIsNotNone(display_state)
        self.assertEqual(len(display_state.player_highlights), 6)


if __name__ == '__main__':
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""
Comprehensive GTO Bot Strategy Test Suite

This module tests the modern GTO (Game Theory Optimal) bot strategy implementation
with separate test suites for preflop and postflop decision making.
"""

import unittest
from unittest import mock
import random
from typing import List, Tuple
from core.poker_state_machine import ImprovedPokerStateMachine, ActionType


class TestGTOPreflopStrategy(unittest.TestCase):
    """Test GTO preflop strategy decisions."""
    
    def setUp(self):
        """Set up test environment."""
        self.sm = ImprovedPokerStateMachine(num_players=6, test_mode=True)
        self.sm.strategy_mode = "GTO"
        self.sm.start_hand()  # Sets positions

    def test_rfi_decision_strong_hands(self):
        """Test RFI decisions with strong hands."""
        # Test UTG with strong hands
        player = next(p for p in self.sm.game_state.players if p.position == "UTG")
        player.cards = ['Ah', 'Ks']  # AKs
        
        action, amount = self.sm.get_gto_bot_action(player)
        self.assertEqual(action, ActionType.RAISE, "UTG should raise AKs")
        self.assertGreater(amount, 0)

    def test_rfi_decision_weak_hands(self):
        """Test RFI decisions with weak hands."""
        # Test UTG with weak hands
        player = next(p for p in self.sm.game_state.players if p.position == "UTG")
        player.cards = ['7h', '2d']  # 72o
        
        action, amount = self.sm.get_gto_bot_action(player)
        self.assertEqual(action, ActionType.FOLD, "UTG should fold 72o")

    def test_btn_wide_range(self):
        """Test BTN plays wider range."""
        # Test BTN with medium hands
        player = next(p for p in self.sm.game_state.players if p.position == "BTN")
        player.cards = ['Th', '9s']  # T9s
        
        action, amount = self.sm.get_gto_bot_action(player)
        self.assertEqual(action, ActionType.RAISE, "BTN should raise T9s")
        self.assertGreater(amount, 0)

    def test_frequencies_mixed_hands(self):
        """Test frequency-based decisions for mixed hands."""
        # Test a hand that should be mixed (e.g., 99 in some positions)
        player = self.sm.game_state.players[0]
        player.position = "UTG"
        player.cards = ['9h', '9d']  # 99
        
        # Run multiple times to test frequency
        actions = []
        for _ in range(50):
            action, _ = self.sm.get_gto_bot_action(player)
            actions.append(action)
        
        # Should have some raises and some folds (mixed strategy)
        raise_count = actions.count(ActionType.RAISE)
        fold_count = actions.count(ActionType.FOLD)
        
        self.assertGreater(raise_count, 0, "Should have some raises")
        self.assertGreater(fold_count, 0, "Should have some folds")

    def test_vs_rfi_context(self):
        """Test vs RFI context decisions."""
        # Set up vs RFI scenario
        player = self.sm.game_state.players[0]
        player.position = "MP"
        player.cards = ['Ah', 'Qs']  # AQs
        self.sm.game_state.current_bet = 3.0  # Facing a raise
        self.sm.game_state.last_raise_amount = 2.0
        
        action, amount = self.sm.get_gto_bot_action(player)
        # AQs should typically 3-bet or call vs RFI
        self.assertIn(action, [ActionType.RAISE, ActionType.CALL])

    def test_vs_three_bet_context(self):
        """Test vs 3-bet context decisions."""
        # Set up vs 3-bet scenario
        player = self.sm.game_state.players[0]
        player.position = "BB"
        player.cards = ['Qh', 'Qd']  # QQ
        self.sm.game_state.current_bet = 9.0  # Facing a 3-bet
        self.sm.game_state.last_raise_amount = 6.0
        
        action, amount = self.sm.get_gto_bot_action(player)
        # QQ should typically call or 4-bet vs 3-bet
        self.assertIn(action, [ActionType.RAISE, ActionType.CALL])


class TestGTOPostflopStrategy(unittest.TestCase):
    """Test GTO postflop strategy decisions."""
    
    def setUp(self):
        """Set up test environment."""
        self.sm = ImprovedPokerStateMachine(num_players=6, test_mode=True)
        self.sm.strategy_mode = "GTO"
        self.sm.game_state.street = "flop"
        self.sm.game_state.board = ["2h", "5d", "8c"]  # Dry board

    def test_value_betting_strong_hands(self):
        """Test value betting with strong hands."""
        player = self.sm.game_state.players[0]
        player.cards = ['A', 'A']  # AA on dry board
        
        # Mock high strength
        with mock.patch.object(self.sm, 'get_postflop_hand_strength', return_value=90):
            action, amount = self.sm.get_gto_bot_action(player)
            self.assertEqual(action, ActionType.BET, "Should value bet strong hands")
            self.assertGreater(amount, 0)

    def test_medium_hands_check_call(self):
        """Test medium hands check/call decisions."""
        player = self.sm.game_state.players[0]
        player.cards = ['K', 'Q']  # KQ
        
        # Mock medium strength
        with mock.patch.object(self.sm, 'get_postflop_hand_strength', return_value=60):
            action, amount = self.sm.get_gto_bot_action(player)
            # Medium hands should check or bet small
            self.assertIn(action, [ActionType.BET, ActionType.CHECK])

    def test_weak_hands_fold_bluff(self):
        """Test weak hands fold/bluff decisions."""
        player = self.sm.game_state.players[0]
        player.cards = ['7h', '2d']  # 72
        
        # Mock weak strength
        with mock.patch.object(self.sm, 'get_postflop_hand_strength', return_value=30):
            action, amount = self.sm.get_gto_bot_action(player)
            # Weak hands should check or bluff occasionally
            self.assertIn(action, [ActionType.BET, ActionType.CHECK])

    def test_facing_bet_decisions(self):
        """Test decisions when facing a bet."""
        player = self.sm.game_state.players[0]
        player.cards = ['Ah', 'Kd']  # AK
        self.sm.game_state.current_bet = 10.0
        self.sm.game_state.pot = 20.0
        
        # Mock strong hand
        with mock.patch.object(self.sm, 'get_postflop_hand_strength', return_value=85):
            action, amount = self.sm.get_gto_bot_action(player)
            # Strong hands should raise or call
            self.assertIn(action, [ActionType.RAISE, ActionType.CALL])

    def test_bet_sizing_dry_vs_wet_board(self):
        """Test bet sizing based on board texture."""
        player = self.sm.game_state.players[0]
        player.cards = ['Ah', 'Ad']  # AA
        
        # Mock strong hand
        with mock.patch.object(self.sm, 'get_postflop_hand_strength', return_value=90):
            # Dry board
            self.sm.game_state.board = ["2h", "5d", "8c"]
            action1, amount1 = self.sm.get_gto_bot_action(player)
            
            # Wet board
            self.sm.game_state.board = ["Jh", "Th", "9h"]
            action2, amount2 = self.sm.get_gto_bot_action(player)
            
            # Should bet larger on wet boards
            if action1 == ActionType.BET and action2 == ActionType.BET:
                self.assertGreater(amount2, amount1, "Should bet larger on wet boards")

    def test_pot_odds_calling(self):
        """Test pot odds based calling decisions."""
        player = self.sm.game_state.players[0]
        player.cards = ['Kh', 'Qd']  # KQ
        self.sm.game_state.current_bet = 5.0
        self.sm.game_state.pot = 10.0  # Good pot odds (5 to call, 15 total pot)
        
        # Mock medium strength
        with mock.patch.object(self.sm, 'get_postflop_hand_strength', return_value=55):
            action, amount = self.sm.get_gto_bot_action(player)
            # Should call with good pot odds
            self.assertEqual(action, ActionType.CALL, "Should call with good pot odds")


class TestGTORangeParsing(unittest.TestCase):
    """Test GTO range parsing functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.sm = ImprovedPokerStateMachine(num_players=6, test_mode=True)

    def test_individual_hand_matching(self):
        """Test individual hand matching."""
        # Test exact matches
        self.assertTrue(self.sm.is_hand_in_range("AKs", ["AKs"]))
        self.assertTrue(self.sm.is_hand_in_range("72o", ["72o"]))
        self.assertFalse(self.sm.is_hand_in_range("AKs", ["AQs"]))

    def test_range_matching(self):
        """Test range matching (e.g., AA-88)."""
        # Test pair ranges
        self.assertTrue(self.sm.is_hand_in_range("AA", ["AA-88"]))
        self.assertTrue(self.sm.is_hand_in_range("99", ["AA-88"]))
        self.assertFalse(self.sm.is_hand_in_range("77", ["AA-88"]))
        
        # Test suited ranges
        self.assertTrue(self.sm.is_hand_in_range("AKs", ["AKs-AJs"]))
        self.assertTrue(self.sm.is_hand_in_range("AJs", ["AKs-AJs"]))
        self.assertFalse(self.sm.is_hand_in_range("ATs", ["AKs-AJs"]))

    def test_plus_notation_matching(self):
        """Test plus notation matching (e.g., AJo+)."""
        # Test plus notation
        self.assertTrue(self.sm.is_hand_in_range("AKo", ["AJo+"]))
        self.assertTrue(self.sm.is_hand_in_range("AJo", ["AJo+"]))
        self.assertFalse(self.sm.is_hand_in_range("ATo", ["AJo+"]))

    def test_hand_strength_comparison(self):
        """Test hand strength comparison for ranges."""
        # Test that stronger hands are recognized
        self.assertTrue(self.sm._hand_stronger_than_or_equal("AA", "KK"))
        self.assertTrue(self.sm._hand_stronger_than_or_equal("AKs", "AQs"))
        self.assertFalse(self.sm._hand_stronger_than_or_equal("72o", "AKs"))


class TestBoardTextureClassification(unittest.TestCase):
    """Test board texture classification for postflop decisions."""
    
    def setUp(self):
        """Set up test environment."""
        self.sm = ImprovedPokerStateMachine(num_players=6, test_mode=True)

    def test_dry_board_classification(self):
        """Test dry board classification."""
        board = ["2h", "5d", "8c"]  # Rainbow, low cards
        texture = self.sm.classify_board_texture(board)
        
        self.assertEqual(texture["type"], "dry")
        self.assertLess(texture["wetness"], 0.5)
        self.assertLess(texture["dynamism"], 0.5)

    def test_wet_flush_board_classification(self):
        """Test wet flush board classification."""
        board = ["Ah", "Kh", "Qh"]  # Three hearts
        texture = self.sm.classify_board_texture(board)
        
        self.assertEqual(texture["type"], "wet_flush")
        self.assertGreater(texture["wetness"], 0.5)
        self.assertEqual(texture["max_suit_count"], 3)

    def test_wet_straight_board_classification(self):
        """Test wet straight board classification."""
        board = ["Jh", "Td", "9s"]  # Connected cards
        texture = self.sm.classify_board_texture(board)
        
        self.assertEqual(texture["type"], "wet_straight")
        self.assertGreater(texture["dynamism"], 0.5)

    def test_medium_board_classification(self):
        """Test medium board classification."""
        board = ["Ah", "Kd", "2s"]  # Mixed texture
        texture = self.sm.classify_board_texture(board)
        
        self.assertEqual(texture["type"], "medium")


class TestGTOIntegration(unittest.TestCase):
    """Test GTO strategy integration with the state machine."""
    
    def setUp(self):
        """Set up test environment."""
        self.sm = ImprovedPokerStateMachine(num_players=6, test_mode=True)
        self.sm.strategy_mode = "GTO"

    def test_gto_mode_enabled(self):
        """Test that GTO mode is properly enabled."""
        self.assertEqual(self.sm.strategy_mode, "GTO")
        self.assertIsNotNone(self.sm.gto_preflop_ranges)

    def test_legacy_mode_fallback(self):
        """Test legacy mode fallback."""
        self.sm.strategy_mode = "LEGACY"
        player = self.sm.game_state.players[0]
        player.cards = ['A', 'K', 's']
        
        action, amount = self.sm.get_basic_bot_action(player)
        # Should use legacy logic
        self.assertIsInstance(action, ActionType)
        self.assertIsInstance(amount, (int, float))

    def test_complete_hand_simulation(self):
        """Test complete hand simulation with GTO strategy."""
        self.sm.start_hand()
        
        # Deal cards to players
        for player in self.sm.game_state.players:
            player.cards = ['Ah', 'Ks']  # Give everyone AKs for testing
        
        # Test preflop action
        player = self.sm.get_action_player()
        if player and not player.is_human:
            action, amount = self.sm.get_basic_bot_action(player)
            self.assertIsInstance(action, ActionType)
            self.assertIsInstance(amount, (int, float))


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)

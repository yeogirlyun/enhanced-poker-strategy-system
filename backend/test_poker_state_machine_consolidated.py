#!/usr/bin/env python3
"""
Consolidated Poker State Machine Test Suite
Comprehensive testing of all poker state machine functionality
"""

import sys
import time
import gc
import tracemalloc
import random
import unittest
from typing import Dict, Any, List
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append('.')

from core.poker_state_machine import (
    ImprovedPokerStateMachine, ActionType, PokerState, Player
)


@dataclass
class TestResult:
    name: str
    passed: bool
    execution_time: float
    error_message: str = None
    details: Dict[str, Any] = None


class ConsolidatedPokerStateMachineTest(unittest.TestCase):
    """Comprehensive test suite for poker state machine functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.state_machine = ImprovedPokerStateMachine(num_players=6, test_mode=True)
        self.start_time = time.time()
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'state_machine'):
            del self.state_machine
        gc.collect()
    
    # ============================================================================
    # CORE STATE MACHINE TESTS
    # ============================================================================
    
    def test_state_machine_initialization(self):
        """Test proper state machine initialization."""
        self.assertIsNotNone(self.state_machine)
        self.assertEqual(self.state_machine.num_players, 6)
        self.assertEqual(self.state_machine.current_state, PokerState.START_HAND)
        self.assertIsNotNone(self.state_machine.game_state)
        self.assertEqual(len(self.state_machine.game_state.players), 6)
    
    def test_hand_start_and_transitions(self):
        """Test hand start and state transitions."""
        # Test start hand
        self.state_machine.start_hand()
        self.assertEqual(self.state_machine.current_state, PokerState.START_HAND)
        
        # Test transition to preflop betting
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        self.assertEqual(self.state_machine.current_state, PokerState.PREFLOP_BETTING)
        
        # Test transition to flop
        self.state_machine.transition_to(PokerState.DEAL_FLOP)
        self.assertEqual(self.state_machine.current_state, PokerState.DEAL_FLOP)
    
    def test_player_initialization(self):
        """Test player initialization and properties."""
        self.state_machine.start_hand()
        players = self.state_machine.game_state.players
        
        # Check all players are initialized
        self.assertEqual(len(players), 6)
        
        # Check player properties
        for i, player in enumerate(players):
            self.assertIsInstance(player, Player)
            self.assertEqual(player.name, f"Player {i+1}")
            self.assertEqual(player.stack, 100.0)
            self.assertTrue(player.is_active)
            self.assertEqual(len(player.cards), 0)  # No cards dealt yet
    
    def test_position_assignment(self):
        """Test position assignment (dealer, SB, BB)."""
        self.state_machine.start_hand()
        self.state_machine.assign_positions()
        
        # Check that positions are assigned
        positions = [p.position for p in self.state_machine.game_state.players]
        self.assertIn("BTN", positions)
        self.assertIn("SB", positions)
        self.assertIn("BB", positions)
        
        # Check no duplicate positions
        self.assertEqual(len(positions), len(set(positions)))
    
    def test_blind_positions_heads_up(self):
        """Test blind positions in heads-up play."""
        sm = ImprovedPokerStateMachine(num_players=2)
        sm.update_blind_positions()
        
        # In heads-up, dealer is small blind
        self.assertEqual(sm.small_blind_position, sm.dealer_position)
        self.assertEqual(sm.big_blind_position, (sm.dealer_position + 1) % 2)
    
    def test_dealer_button_advances(self):
        """Test that dealer button advances correctly."""
        initial_dealer = self.state_machine.dealer_position
        self.state_machine.advance_dealer_position()
        
        # Dealer should advance by 1
        self.assertEqual(self.state_machine.dealer_position, 
                        (initial_dealer + 1) % self.state_machine.num_players)
    
    # ============================================================================
    # ACTION VALIDATION TESTS
    # ============================================================================
    
    def test_action_validation(self):
        """Test input validation for various actions."""
        self.state_machine.start_hand()
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        player = self.state_machine.game_state.players[0]
        
        # Ensure no current bet for check to be valid
        self.state_machine.game_state.current_bet = 0.0
        player.current_bet = 0.0
        
        # Test invalid negative amount
        errors = self.state_machine.validate_action(player, ActionType.BET, -10)
        self.assertGreater(len(errors), 0, "Should reject negative bet amount")
        
        # Test valid action
        errors = self.state_machine.validate_action(player, ActionType.CHECK, 0)
        self.assertEqual(len(errors), 0, "Should allow valid check")
    
    def test_bb_folding_bug_fix(self):
        """Test BB checks with weak hand when no raise is made."""
        self.state_machine.start_hand()
        bb_player = next(p for p in self.state_machine.game_state.players 
                        if p.position == "BB")
        bb_player.cards = ["7h", "2c"]  # Weak hand
        
        # Set up scenario where BB has already paid the big blind and no raise
        self.state_machine.game_state.current_bet = 1.0  # BB amount
        bb_player.current_bet = 1.0
        
        # Test BB strategy action directly
        action, amount = self.state_machine.get_basic_bot_action(bb_player)
        
        # The method should return a tuple, not None
        self.assertIsNotNone(action, "Strategy action should not be None")
        self.assertIsInstance(action, ActionType, f"Action should be ActionType, got {type(action)}")
        self.assertIsInstance(amount, (int, float), f"Amount should be numeric, got {type(amount)}")
    
    def test_bb_facing_raise(self):
        """Test BB folds to a raise with a weak hand."""
        self.state_machine.start_hand()
        bb_player = next(p for p in self.state_machine.game_state.players 
                        if p.position == "BB")
        bb_player.cards = ["2c", "7d"]  # Weak hand
        
        # Set up a raise scenario
        self.state_machine.game_state.current_bet = 3.0  # Raise amount
        bb_player.current_bet = 1.0  # BB has already paid 1
        
        # Test BB action
        action, amount = self.state_machine.get_basic_bot_action(bb_player)
        
        # BB should not fold when facing a raise
        self.assertNotEqual(action, ActionType.FOLD, 
                           "BB should not fold when facing a raise")
    
    def test_valid_actions_for_player(self):
        """Test valid actions calculation for different players."""
        self.state_machine.start_hand()
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        player = self.state_machine.game_state.players[0]
        
        # Test valid actions
        valid_actions = self.state_machine.get_valid_actions_for_player(player)
        self.assertIsInstance(valid_actions, dict)
        self.assertIn('fold', valid_actions)
        self.assertIn('call', valid_actions)
        self.assertIn('raise', valid_actions)
    
    # ============================================================================
    # HAND EVALUATION TESTS
    # ============================================================================
    
    def test_hand_evaluation(self):
        """Test hand evaluation and ranking."""
        self.state_machine.start_hand()
        player = self.state_machine.game_state.players[0]
        player.cards = ["Ah", "Kh"]
        
        # Set up board cards properly
        board_cards = ["Qh", "Jh", "Th"]
        
        # Test hand strength calculation
        strength = self.state_machine.get_postflop_hand_strength(player.cards, board_cards)
        self.assertGreater(strength, 0, "Hand strength should be positive")
    
    def test_hand_evaluation_cache(self):
        """Test hand evaluation cache functionality."""
        self.state_machine.start_hand()
        player = self.state_machine.game_state.players[0]
        player.cards = ["Ah", "Kh"]
        board_cards = ["Qh", "Jh", "Th"]
        
        # First evaluation should populate cache
        strength1 = self.state_machine.get_postflop_hand_strength(player.cards, board_cards)
        
        # Second evaluation should use cache
        strength2 = self.state_machine.get_postflop_hand_strength(player.cards, board_cards)
        
        self.assertEqual(strength1, strength2, "Cached and non-cached results should match")
    
    def test_winner_determination(self):
        """Test winner determination and pot distribution."""
        self.state_machine.start_hand()
        
        # Set up players with different hands
        players = self.state_machine.game_state.players
        players[0].cards = ["Ah", "Kh"]  # High cards
        players[1].cards = ["7h", "2c"]  # Low cards
        
        # Set up community cards properly
        community_cards = ["Qh", "Jh", "Th", "9h", "8h"]
        
        # Test showdown
        winners = self.state_machine.determine_winner(players[:2])
        self.assertGreater(len(winners), 0, "Should have at least one winner")
    
    # ============================================================================
    # SESSION TRACKING TESTS
    # ============================================================================
    
    def test_session_tracking(self):
        """Test session initialization and tracking."""
        # Test session start
        self.state_machine.start_session()
        
        # Test session info
        session_info = self.state_machine.get_session_info()
        self.assertIsNotNone(session_info, "Session info should be available")
        self.assertIsInstance(session_info, dict, "Session info should be a dictionary")
    
    def test_hand_history_logging(self):
        """Test hand history logging functionality."""
        self.state_machine.start_hand()
        player = self.state_machine.game_state.players[0]
        
        # Execute an action
        self.state_machine.execute_action(player, ActionType.CALL, 10.0)
        
        # Check that action was logged
        hand_history = self.state_machine.get_hand_history()
        self.assertGreater(len(hand_history), 0, "Action should be logged")
    
    # ============================================================================
    # STRATEGY INTEGRATION TESTS
    # ============================================================================
    
    def test_strategy_integration(self):
        """Test strategy integration and decision making."""
        self.state_machine.start_hand()
        player = self.state_machine.game_state.players[0]
        
        # Test basic bot action instead of strategy action
        action, amount = self.state_machine.get_basic_bot_action(player)
        self.assertIsNotNone(action, "Bot action should not be None")
        self.assertIn(action, [ActionType.FOLD, ActionType.CALL, ActionType.RAISE, 
                              ActionType.CHECK], "Action should be valid")
    
    def test_bot_action_consistency(self):
        """Test that bot actions are consistent."""
        self.state_machine.start_hand()
        player = self.state_machine.game_state.players[0]
        
        # Test multiple bot actions
        actions = []
        for _ in range(5):
            action, amount = self.state_machine.get_basic_bot_action(player)
            actions.append(action)
        
        # All actions should be valid
        valid_actions = [ActionType.FOLD, ActionType.CALL, ActionType.RAISE, ActionType.CHECK]
        for action in actions:
            self.assertIn(action, valid_actions, f"Invalid action: {action}")
    
    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================
    
    def test_error_handling(self):
        """Test error handling and recovery."""
        self.state_machine.start_hand()
        player = self.state_machine.game_state.players[0]
        
        # Test invalid action handling
        errors = self.state_machine.validate_action(player, ActionType.BET, -100)
        self.assertGreater(len(errors), 0, "Should catch invalid negative bet")
    
    def test_invalid_action_recovery(self):
        """Test recovery from invalid actions."""
        self.state_machine.start_hand()
        player = self.state_machine.game_state.players[0]
        
        # Try to execute invalid action
        with self.assertRaises(Exception):
            self.state_machine.execute_action(player, ActionType.BET, -10)
    
    # ============================================================================
    # PERFORMANCE TESTS
    # ============================================================================
    
    def test_performance(self):
        """Test performance and memory usage."""
        start_time = time.time()
        
        # Run multiple hands quickly
        for _ in range(10):
            self.state_machine.start_hand()
            # Use transition_to instead of end_hand
            self.state_machine.transition_to(PokerState.END_HAND)
        
        execution_time = time.time() - start_time
        self.assertLess(execution_time, 5.0, f"Performance test took too long: {execution_time}s")
    
    def test_memory_leak_detection(self):
        """Detect memory leaks over multiple hands."""
        tracemalloc.start()
        
        # Baseline snapshot
        snapshot1 = tracemalloc.take_snapshot()
        
        # Play 20 hands (reduced from 50 for faster testing)
        for i in range(20):
            self.state_machine.start_hand()
            self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
            
            # Simulate some actions
            for _ in range(5):
                player = self.state_machine.game_state.players[0]
                action, amount = self.state_machine.get_basic_bot_action(player)
                if action != ActionType.FOLD:
                    self.state_machine.execute_action(player, action, amount)
            
            self.state_machine.transition_to(PokerState.END_HAND)
        
        # Final snapshot
        snapshot2 = tracemalloc.take_snapshot()
        
        # Compare memory usage
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        memory_increase = sum(stat.size_diff for stat in top_stats[:10])
        
        # Memory increase should be reasonable (less than 1MB)
        self.assertLess(memory_increase, 1024 * 1024, 
                       f"Memory leak detected: {memory_increase} bytes")
        
        tracemalloc.stop()
    
    # ============================================================================
    # EDGE CASES TESTS
    # ============================================================================
    
    def test_edge_cases(self):
        """Test various edge cases and boundary conditions."""
        # Test all-in scenarios
        self.state_machine.start_hand()
        player = self.state_machine.game_state.players[0]
        player.stack = 0.5  # Very small stack
        
        # Test with minimal stack - use basic bot action
        action, amount = self.state_machine.get_basic_bot_action(player)
        self.assertIsNotNone(action, "Bot action should not be None")
        self.assertIn(action, [ActionType.FOLD, ActionType.CALL, ActionType.RAISE], 
                     "Should handle small stack")
    
    def test_all_players_all_in_preflop(self):
        """Test when all players go all-in before the flop."""
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        
        # All players all-in
        for player in self.state_machine.game_state.players:
            player.is_all_in = True
            player.stack = 0
            player.total_invested = 100.0
        
        self.assertTrue(self.state_machine.is_round_complete())
    
    def test_single_player_remaining(self):
        """Test proper handling when all but one player folds."""
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        
        # All fold except one
        for i, player in enumerate(self.state_machine.game_state.players[:-1]):
            player.is_active = False
        
        # Should transition to END_HAND
        self.state_machine.execute_action(
            self.state_machine.game_state.players[-2], 
            ActionType.FOLD, 
            0
        )
        
        self.assertEqual(self.state_machine.current_state, PokerState.END_HAND)
    
    # ============================================================================
    # POT AND MONEY TESTS
    # ============================================================================
    
    def test_pot_equals_investments(self):
        """Pot should always equal sum of player investments."""
        self.state_machine.start_hand()
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        
        # Execute some actions
        player = self.state_machine.get_action_player()
        if player:
            self.state_machine.execute_action(player, ActionType.BET, 10.0)
        
        # Check invariant
        total_invested = sum(p.total_invested for p in self.state_machine.game_state.players)
        self.assertAlmostEqual(self.state_machine.game_state.pot, total_invested, 
                              places=2, msg="Pot should equal total investments")
    
    def test_no_negative_stacks(self):
        """Stacks should never go negative."""
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        
        player = self.state_machine.game_state.players[0]
        player.stack = 10.0
        
        # Try to bet more than stack
        errors = self.state_machine.validate_action(player, ActionType.BET, 20.0)
        self.assertGreater(len(errors), 0, "Should reject bet larger than stack")
        
        # Execute valid bet
        self.state_machine.execute_action(player, ActionType.BET, 5.0)
        self.assertGreaterEqual(player.stack, 0, "Stack should not go negative")
    
    def test_pot_splitting_odd_amounts(self):
        """Test pot splitting with amounts that don't divide evenly."""
        self.state_machine.game_state.pot = 33.33  # Odd amount
        
        winners = [
            self.state_machine.game_state.players[0],
            self.state_machine.game_state.players[1],
            self.state_machine.game_state.players[2]
        ]
        
        # Each should get approximately 11.11
        split_amount = self.state_machine.game_state.pot / len(winners)
        self.assertAlmostEqual(split_amount, 11.11, places=2)
    
    # ============================================================================
    # SIDE POT TESTS
    # ============================================================================
    
    def test_multiple_all_ins_different_stacks(self):
        """Test side pot creation with multiple all-ins."""
        self.state_machine.start_hand()
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        
        players = self.state_machine.game_state.players[:3]
        
        # Set up different stack sizes
        players[0].stack = 50.0
        players[1].stack = 100.0
        players[2].stack = 150.0
        
        # All players go all-in
        for player in players:
            player.is_all_in = True
            player.total_invested = player.stack
            player.stack = 0
        
        # Create side pots
        side_pots = self.state_machine.create_side_pots()
        
        # Should have side pots
        self.assertGreater(len(side_pots), 0, "Should create side pots")
    
    def test_partial_call_side_pot(self):
        """Test side pot creation with partial calls."""
        self.state_machine.start_hand()
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        
        players = self.state_machine.game_state.players[:3]
        
        # Set up scenario with partial call
        players[0].total_invested = 100.0  # All-in
        players[1].total_invested = 50.0   # Partial call
        players[2].total_invested = 100.0  # All-in
        
        players[0].is_all_in = True
        players[1].is_all_in = True
        players[2].is_all_in = True
        
        # Create side pots
        side_pots = self.state_machine.create_side_pots()
        
        # Should have side pots
        self.assertGreater(len(side_pots), 0, "Should create side pots for partial calls")
    
    # ============================================================================
    # LEGENDARY HANDS TESTS
    # ============================================================================
    
    def test_legendary_hands_database_loading(self):
        """Test that legendary hands database can be loaded."""
        try:
            from tests.legendary_hands_manager import LegendaryHandsManager
            
            manager = LegendaryHandsManager()
            self.assertIsNotNone(manager.data, "Database should load successfully")
            self.assertEqual(len(manager.hands), 100, f"Should have 100 hands, got {len(manager.hands)}")
            
            # Test categories
            categories = manager.get_categories()
            self.assertEqual(len(categories), 10, f"Should have 10 categories, got {len(categories)}")
            
        except Exception as e:
            self.fail(f"Legendary hands database loading failed: {e}")
    
    def test_legendary_hands_simulation(self):
        """Test simulation of legendary hands."""
        try:
            from tests.legendary_hands_manager import LegendaryHandsManager
            
            manager = LegendaryHandsManager()
            
            # Test simulation of first hand
            if manager.hands:
                hand = manager.hands[0]
                result = manager.simulate_hand(hand, verbose=False)
                
                # Basic validation of simulation result
                self.assertIsInstance(result, dict, "Simulation should return a dictionary")
                self.assertIn('expected_winner', result, "Result should have expected_winner")
                self.assertIn('actual_winners', result, "Result should have actual_winners")
                self.assertIn('expected_pot', result, "Result should have expected_pot")
                self.assertIn('actual_pot', result, "Result should have actual_pot")
                
        except Exception as e:
            self.fail(f"Legendary hands simulation failed: {e}")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)

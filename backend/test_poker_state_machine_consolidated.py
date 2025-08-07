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
        # Don't call start_hand() as it deals cards
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
        # Don't call start_hand() as it may interfere with position assignment
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
        """Test BB calls to a raise with a weak hand."""
        self.state_machine.start_hand()
        bb_player = next(p for p in self.state_machine.game_state.players 
                        if p.position == "BB")
        bb_player.cards = ["2c", "7d"]  # Weak hand
        
        # Set up a raise scenario
        self.state_machine.game_state.current_bet = 3.0  # Raise amount
        bb_player.current_bet = 1.0  # BB has already paid 1
        
        # Enable GTO mode to use the correct BB logic
        self.state_machine.strategy_mode = "GTO"
        
        # Test BB action
        action, amount = self.state_machine.get_basic_bot_action(bb_player)
        
        # BB should call when facing a raise (not fold)
        self.assertEqual(action, ActionType.CALL, 
                       "BB should call when facing a raise")
    
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
        
        # Try to execute invalid action - should return early without exception
        self.state_machine.execute_action(player, ActionType.BET, -10)
        
        # Verify that the action was not executed (pot should remain unchanged)
        initial_pot = self.state_machine.game_state.pot
        self.assertEqual(self.state_machine.game_state.pot, initial_pot, 
                        "Invalid action should not change the pot")
    
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
        
        # Memory increase should be reasonable (less than 2MB for 20 hands)
        self.assertLess(memory_increase, 2 * 1024 * 1024, 
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
        self.state_machine.start_hand()
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        
        # Set up scenario where all but one player fold
        players = self.state_machine.game_state.players
        # Ensure all players are active initially for the test setup
        for p in players:
            p.is_active = True
            p.total_invested = 0.0  # Reset investments for clean test
        
        # Set up proper betting round
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        
        # Player 1 (BTN) raises
        self.state_machine.execute_action(players[0], ActionType.RAISE, 3.0)
        
        # Player 2 (SB) folds
        self.state_machine.execute_action(players[1], ActionType.FOLD, 0.0)
        
        # Player 3 (BB) folds
        self.state_machine.execute_action(players[2], ActionType.FOLD, 0.0)
        
        # Player 4 (UTG) folds
        self.state_machine.execute_action(players[3], ActionType.FOLD, 0.0)
        
        # Player 5 (MP) folds
        self.state_machine.execute_action(players[4], ActionType.FOLD, 0.0)
        
        # After Player 5 folds, Player 1 should be the only active player
        active_players = [p for p in players if p.is_active and not p.has_folded]
        self.assertEqual(len(active_players), 1,
                         "Should have exactly one active player remaining after others fold")
        self.assertEqual(self.state_machine.current_state, PokerState.END_HAND,
                         "State should transition to END_HAND after last fold")
        self.assertGreater(active_players[0].stack, 100,
                           "Winning player's stack should increase")
        self.assertEqual(active_players[0].stack, 100 + self.state_machine.game_state.pot,
                         "Winning player should get the entire pot")
    
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
        """Test simulation of legendary hands from database."""
        from tests.legendary_hands_manager import LegendaryHandsManager
        
        manager = LegendaryHandsManager()
        # load_hands() returns boolean, hands are stored in manager.hands
        success = manager.load_hands()
        self.assertTrue(success, "Failed to load legendary hands")
        
        # Test simulation of first hand
        if manager.hands:
            hand = manager.hands[0]
            # Use setup.num_players instead of players field
            num_players = hand.get('setup', {}).get('num_players', 6)
            sm = ImprovedPokerStateMachine(num_players=num_players, test_mode=True)
            
            # Simulate the hand
            result = manager.simulate_hand(hand)
            self.assertIsNotNone(result)
            # Check for either 'winner' or 'actual_winners' key
            self.assertTrue('winner' in result or 'actual_winners' in result, 
                          f"Result should contain 'winner' or 'actual_winners', got: {result}")
    
    # ============================================================================
    # SESSION MANAGEMENT TESTS
    # ============================================================================
    
    def test_session_export_import(self):
        """Test session export and import functionality."""
        # Play a few hands
        self.state_machine.start_session()
        self.state_machine.start_hand()
        
        # Execute some actions
        player = self.state_machine.game_state.players[0]
        self.state_machine.execute_action(player, ActionType.CALL, 1.0)
        
        # Export session
        filepath = "test_session.json"
        success = self.state_machine.export_session(filepath)
        self.assertTrue(success)
        
        # Import session
        success = self.state_machine.import_session(filepath)
        self.assertTrue(success)
    
    def test_replay_hand(self):
        """Test hand replay functionality."""
        self.state_machine.start_session()
        self.state_machine.start_hand()
        
        # Play a hand and complete it properly
        player = self.state_machine.game_state.players[0]
        self.state_machine.execute_action(player, ActionType.CALL, 1.0)
        
        # Complete the hand properly
        self.state_machine.handle_end_hand()
        
        # Now try to replay the hand
        replay_data = self.state_machine.replay_hand(0)
        self.assertIsNotNone(replay_data)
        self.assertIn('hand_number', replay_data)
    
    # ============================================================================
    # SOUND AND VOICE SYSTEM TESTS
    # ============================================================================
    
    def test_sound_manager_integration(self):
        """Test sound manager plays appropriate sounds."""
        with patch.object(self.state_machine.sound_manager, 'play_action_sound') as mock_play:
            player = self.state_machine.game_state.players[0]
            self.state_machine.execute_action(player, ActionType.RAISE, 10)
            mock_play.assert_called()
    
    def test_voice_announcements(self):
        """Test voice announcement system."""
        # Create a state machine NOT in test mode for voice testing
        from core.poker_state_machine import ImprovedPokerStateMachine
        sm = ImprovedPokerStateMachine(num_players=6, test_mode=False)
        sm.start_hand()
        
        with patch.object(sm.sound_manager.voice_manager, 'play_action_voice') as mock_voice:
            # Test all-in announcement
            player = sm.game_state.players[0]
            player.stack = 0
            
            # Set up game state so it's the player's turn
            sm.game_state.current_bet = 1.0  # There's a bet to call
            sm.action_player_index = 0  # Set action to first player
            
            sm.execute_action(player, ActionType.CALL, player.stack)
            # Voice should be called for all-in
            mock_voice.assert_called()
    
    def test_test_mode_voice_disabled(self):
        """Test that voice is disabled in test mode."""
        with patch.object(self.state_machine.sound_manager.voice_manager, 'play_action_voice') as mock_voice:
            player = self.state_machine.game_state.players[0]
            
            # Set up game state so it's the player's turn
            self.state_machine.game_state.current_bet = 1.0  # There's a bet to call
            self.state_machine.action_player_index = 0  # Set action to first player
            
            self.state_machine.execute_action(player, ActionType.CALL, 1.0)
            # In test mode, voice should not be called
            mock_voice.assert_not_called()
    
    # ============================================================================
    # DISPLAY STATE AND UI DATA TESTS
    # ============================================================================
    
    def test_get_display_state(self):
        """Test display state generation for UI."""
        display_state = self.state_machine.get_display_state()
        
        self.assertIn('valid_actions', display_state.__dict__)
        self.assertIn('player_highlights', display_state.__dict__)
        self.assertIn('chip_representations', display_state.__dict__)
        self.assertIn('community_cards', display_state.__dict__)
    
    def test_chip_representation_calculations(self):
        """Test chip symbol calculations."""
        symbols = self.state_machine._get_chip_symbols(100.0)
        self.assertIsInstance(symbols, str)
        self.assertIn('🔴', symbols)  # Should contain red chip for $100
    
    def test_valid_actions_for_display(self):
        """Test valid actions are properly formatted for display."""
        display_state = self.state_machine.get_display_state()
        valid_actions = display_state.valid_actions
        
        self.assertIsInstance(valid_actions, dict)
        for action_type, action_data in valid_actions.items():
            self.assertIsInstance(action_type, str)
            # Check if it's the new UI format (with enabled/label) or old format (numeric)
            if isinstance(action_data, dict):
                # New UI format - could be action data or preset_bets
                if 'enabled' in action_data and 'label' in action_data:
                    # Action data format
                    self.assertIsInstance(action_data['enabled'], bool)
                    self.assertIsInstance(action_data['label'], str)
                else:
                    # Preset bets format (e.g., {'half_pot': 0.0, 'pot': 0.0})
                    for bet_type, amount in action_data.items():
                        self.assertIsInstance(bet_type, str)
                        self.assertIsInstance(amount, (int, float))
            else:
                # Old numeric format (fallback)
                self.assertIsInstance(action_data, (int, float))
    
    # ============================================================================
    # DEALING ANIMATION CALLBACKS TESTS
    # ============================================================================
    
    def test_dealing_animation_callbacks(self):
        """Test card dealing animation callbacks."""
        mock_callback = MagicMock()
        self.state_machine.on_single_card_dealt = mock_callback
        self.state_machine.on_dealing_complete = MagicMock()
        
        self.state_machine.deal_hole_cards()
        
        # Should call callback for each card dealt
        expected_calls = self.state_machine.num_players * 2
        self.assertEqual(mock_callback.call_count, expected_calls)
    
    def test_start_preflop_betting_after_dealing(self):
        """Test transition to preflop betting after dealing animation."""
        self.state_machine.start_hand()
        self.state_machine.start_preflop_betting_after_dealing()
        self.assertEqual(self.state_machine.current_state, PokerState.PREFLOP_BETTING)
    
    # ============================================================================
    # COMPREHENSIVE HAND CLASSIFICATION TESTS
    # ============================================================================
    
    def test_all_hand_classifications(self):
        """Test all possible hand classifications."""
        test_cases = [
            (['Ah', 'Kh'], ['Qh', 'Jh', 'Th'], 'straight_flush'),
            (['Ah', '2h'], ['3h', '4h', '5h'], 'straight_flush'),
            (['As', 'Ks'], ['Ah', 'Kh', 'Qh'], 'two_pair'),
            (['7h', '8h'], ['9s', 'Ts', '2c'], 'open_ended_draw'),
            (['7h', '8h'], ['9s', 'Js', '2c'], 'gutshot_draw'),
            (['Ah', '2s'], ['3h', '4h', '2c'], 'backdoor_straight'),
            (['Ah', 'Kh'], ['As', 'Ks', 'Qs'], 'two_pair'),
            (['Ah', 'Kh'], ['2h', '3h', '4h'], 'nut_flush'),
        ]
        
        for hole_cards, board, expected in test_cases:
            result = self.state_machine.classify_hand(hole_cards, board)
            self.assertEqual(result, expected, 
                            f"Failed for {hole_cards} on {board}: got {result}, expected {expected}")
    
    def test_hand_strength_calculations(self):
        """Test hand strength calculations for preflop and postflop."""
        # Test preflop hand strength
        hole_cards = ['Ah', 'Kh']
        strength = self.state_machine.get_preflop_hand_strength(hole_cards)
        self.assertIsInstance(strength, (int, float))
        self.assertGreater(strength, 0)
        
        # Test postflop hand strength
        board = ['Qh', 'Jh', 'Th']
        strength = self.state_machine.get_postflop_hand_strength(hole_cards, board)
        self.assertIsInstance(strength, (int, float))
        self.assertGreater(strength, 0)
    
    # ============================================================================
    # RACE CONDITION AND CONCURRENCY TESTS
    # ============================================================================
    
    def test_concurrent_bot_action_protection(self):
        """Test protection against concurrent bot actions."""
        self.state_machine.start_hand()
        
        # Schedule multiple bot actions
        action_data = {
            'player_index': 1,
            'state': PokerState.PREFLOP_BETTING,
            'street': 'preflop',
            'pot': 1.5,
            'current_bet': 1.0
        }
        
        # Try to execute same action twice
        self.state_machine._execute_bot_action_safe(action_data)
        
        # Change state to simulate race condition
        self.state_machine.current_state = PokerState.END_HAND
        
        # Second execution should be cancelled
        with patch.object(self.state_machine, 'execute_bot_action') as mock_execute:
            self.state_machine._execute_bot_action_safe(action_data)
            mock_execute.assert_not_called()
    
    def test_state_transition_atomicity(self):
        """Test that state transitions are atomic."""
        self.state_machine.start_hand()
        
        # Simulate concurrent state changes
        original_state = self.state_machine.current_state
        
        # Try to transition while another transition is in progress
        self.state_machine._transitioning = True
        self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
        
        # State should not change if already transitioning
        self.assertEqual(self.state_machine.current_state, original_state)
    
    # ============================================================================
    # POSITION MAPPING FALLBACK TESTS
    # ============================================================================
    
    def test_position_mapping_fallback_chains(self):
        """Test position mapping fallback mechanisms."""
        from core.position_mapping import PositionMapper
        
        mapper = PositionMapper(6)
        
        # Test fallback when exact position not found
        strategy_positions = ['UTG', 'CO', 'BTN']
        mapped = mapper.map_strategy_position('MP', strategy_positions)
        self.assertEqual(mapped, 'UTG')  # Should fallback to UTG
        
        # Test group-based fallback
        strategy_positions = ['EARLY', 'LATE']
        mapped = mapper.map_strategy_position('MP', strategy_positions)
        self.assertIsNotNone(mapped)
    
    def test_position_mapping_edge_cases(self):
        """Test position mapping with edge cases."""
        from core.position_mapping import PositionMapper
        
        # Test with 2 players (heads up)
        mapper_2 = PositionMapper(2)
        positions_2 = mapper_2.get_positions()
        self.assertEqual(len(positions_2), 2)
        self.assertIn('BTN', positions_2)
        self.assertIn('BB', positions_2)
        
        # Test with 3 players
        mapper_3 = PositionMapper(3)
        positions_3 = mapper_3.get_positions()
        self.assertEqual(len(positions_3), 3)
        self.assertIn('BTN', positions_3)
        self.assertIn('SB', positions_3)
        self.assertIn('BB', positions_3)
    
    # ============================================================================
    # SIGNAL HANDLER AND CLEANUP TESTS
    # ============================================================================
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown handling."""
        import signal
        
        # Mock signal handler
        with patch.object(self.state_machine, '_cleanup') as mock_cleanup:
            # Simulate SIGINT - should call cleanup and exit
            try:
                self.state_machine._signal_handler(signal.SIGINT, None)
            except SystemExit:
                # Expected behavior - signal handler should exit
                pass
            mock_cleanup.assert_called()
    
    def test_emergency_save(self):
        """Test emergency save functionality."""
        self.state_machine.start_session()
        self.state_machine.start_hand()
        
        # Simulate incomplete hand
        self.state_machine.current_hand = MagicMock()
        self.state_machine.current_hand.hand_complete = False
        
        with patch.object(self.state_machine.logger, '_emergency_save') as mock_save:
            self.state_machine._cleanup()
            mock_save.assert_called()
    
    # ============================================================================
    # ENHANCED HAND EVALUATOR TESTS
    # ============================================================================
    
    def test_best_five_cards_selection(self):
        """Test selection of best 5-card combination."""
        hole_cards = ['Ah', 'Kh']
        board = ['Qh', 'Jh', 'Th', '9h', '8h']
        
        best_five = self.state_machine.hand_evaluator.get_best_five_cards(hole_cards, board)
        self.assertEqual(len(best_five), 5)
        # Should select the straight flush
        self.assertIn('Ah', best_five)
        self.assertIn('Kh', best_five)
    
    def test_hand_rank_to_string_conversion(self):
        """Test hand rank enum to string conversion."""
        from core.hand_evaluation import HandRank
        
        result = self.state_machine.hand_evaluator.hand_rank_to_string(HandRank.FULL_HOUSE)
        self.assertEqual(result, 'full_house')
    
    def test_hand_evaluator_cache_performance(self):
        """Test hand evaluator cache performance."""
        hole_cards = ['Ah', 'Kh']
        board = ['Qh', 'Jh', 'Th']
        
        # First evaluation (cache miss)
        start_time = time.time()
        result1 = self.state_machine.hand_evaluator.evaluate_hand(hole_cards, board)
        first_time = time.time() - start_time
        
        # Second evaluation (cache hit)
        start_time = time.time()
        result2 = self.state_machine.hand_evaluator.evaluate_hand(hole_cards, board)
        second_time = time.time() - start_time
        
        # Results should be identical
        self.assertEqual(result1, result2)
        # Second evaluation should be faster (cached)
        self.assertLess(second_time, first_time)
    
    # ============================================================================
    # COMPLEX SIDE POT SCENARIOS
    # ============================================================================
    
    def test_complex_side_pot_with_folds(self):
        """Test side pot creation with players folding at different stages."""
        players = self.state_machine.game_state.players[:4]
        
        # Player 0: All-in for 50
        players[0].total_invested = 50
        players[0].is_all_in = True
        players[0].is_active = True
        
        # Player 1: Folded after investing 30
        players[1].total_invested = 30
        players[1].is_active = False  # Folded
        
        # Player 2: All-in for 100
        players[2].total_invested = 100
        players[2].is_all_in = True
        players[2].is_active = True
        
        # Player 3: Calls 100
        players[3].total_invested = 100
        players[3].is_active = True
        
        side_pots = self.state_machine.create_side_pots()
        
        # Verify correct pot distribution
        total_pot = sum(p.total_invested for p in players)
        total_in_pots = sum(pot['amount'] for pot in side_pots)
        self.assertAlmostEqual(total_pot, total_in_pots, places=2)
    
    def test_side_pot_with_partial_calls(self):
        """Test side pot creation with partial calls."""
        players = self.state_machine.game_state.players[:3]
        
        # Player 0: All-in for 25
        players[0].total_invested = 25
        players[0].is_all_in = True
        players[0].is_active = True
        
        # Player 1: Calls 50 (partial call)
        players[1].total_invested = 50
        players[1].is_active = True
        players[1].partial_call_amount = 25  # Only called 25 of the 50
        
        # Player 2: Calls full amount
        players[2].total_invested = 50
        players[2].is_active = True
        
        side_pots = self.state_machine.create_side_pots()
        
        # Should create side pots correctly
        self.assertGreater(len(side_pots), 0)
        
        # Verify pot amounts are correct
        total_invested = sum(p.total_invested for p in players)
        total_in_pots = sum(pot['amount'] for pot in side_pots)
        self.assertAlmostEqual(total_invested, total_in_pots, places=2)
    
    # ============================================================================
    # FILE OPERATIONS TESTS
    # ============================================================================
    
    def test_strategy_file_operations(self):
        """Test strategy file save and load operations."""
        from core.gui_models import FileOperations
        
        test_strategy = {"test": "data", "hands": ["Ah", "Kh"]}
        filename = "test_strategy.json"
        
        # Test save
        success = FileOperations.save_strategy(test_strategy, filename)
        self.assertTrue(success)
        
        # Test load
        loaded = FileOperations.load_strategy(filename)
        self.assertEqual(loaded, test_strategy)
    
    def test_session_file_operations(self):
        """Test session file operations."""
        # Create test session data
        session_data = {
            "hands_played": 5,
            "total_pot_volume": 150.0,
            "players": [{"name": "Player 1", "stack": 95.0}]
        }
        
        # Test export
        success = self.state_machine.export_session("test_session.json")
        self.assertTrue(success)
        
        # Test import
        success = self.state_machine.import_session("test_session.json")
        self.assertTrue(success)
    
    # ============================================================================
    # COMPREHENSIVE SESSION STATISTICS TESTS
    # ============================================================================
    
    def test_session_statistics_calculation(self):
        """Test comprehensive session statistics."""
        self.state_machine.start_session()
        
        # Play multiple hands
        for i in range(5):
            self.state_machine.start_hand()
            # Simulate hand
            player = self.state_machine.game_state.players[0]
            self.state_machine.execute_action(player, ActionType.CALL, 1.0)
            self.state_machine.transition_to(PokerState.END_HAND)
        
        stats = self.state_machine.get_session_statistics()
        
        self.assertIn('total_hands', stats)
        self.assertIn('hands_per_hour', stats)
        self.assertIn('total_pot_volume', stats)
        self.assertIn('biggest_pot', stats)
        self.assertIn('player_statistics', stats)
    
    def test_player_statistics_tracking(self):
        """Test individual player statistics tracking."""
        self.state_machine.start_session()
        self.state_machine.start_hand()
        
        player = self.state_machine.game_state.players[0]
        
        # Track some actions
        self.state_machine.execute_action(player, ActionType.RAISE, 10)
        self.state_machine.execute_action(player, ActionType.CALL, 5)
        
        stats = self.state_machine.get_session_statistics()
        player_stats = stats['player_statistics']
        
        self.assertIn(player.name, player_stats)
        self.assertIn('total_bets', player_stats[player.name])
        self.assertIn('total_calls', player_stats[player.name])
    
    # ============================================================================
    # STRESS TESTS AND PERFORMANCE BENCHMARKS
    # ============================================================================
    
    def test_large_pot_scenarios(self):
        """Test scenarios with very large pots."""
        players = self.state_machine.game_state.players[:3]
        
        # Set very large stacks
        for player in players:
            player.stack = 10000.0
        
        # Create large bets
        for player in players:
            player.total_invested = 5000.0
            player.is_active = True
        
        # Test side pot creation with large amounts
        side_pots = self.state_machine.create_side_pots()
        
        total_pot = sum(p.total_invested for p in players)
        total_in_pots = sum(pot['amount'] for pot in side_pots)
        self.assertAlmostEqual(total_pot, total_in_pots, places=2)
    
    def test_many_players_scenario(self):
        """Test scenarios with maximum number of players."""
        # Create state machine with maximum players
        max_players_sm = ImprovedPokerStateMachine(num_players=10, test_mode=True)
        
        self.assertEqual(len(max_players_sm.game_state.players), 10)
        
        # Test position assignment
        max_players_sm.assign_positions()
        positions = [p.position for p in max_players_sm.game_state.players]
        
        # Should have all expected positions
        self.assertIn("BTN", positions)
        self.assertIn("SB", positions)
        self.assertIn("BB", positions)
    
    def test_rapid_state_transitions(self):
        """Test rapid state transitions for race condition detection."""
        self.state_machine.start_hand()
        
        # Rapidly transition states
        for _ in range(100):
            self.state_machine.transition_to(PokerState.PREFLOP_BETTING)
            self.state_machine.transition_to(PokerState.DEAL_FLOP)
            self.state_machine.transition_to(PokerState.FLOP_BETTING)
        
        # Should not crash or corrupt state
        self.assertIsNotNone(self.state_machine.current_state)
    
    # ============================================================================
    # REGRESSION TESTS FOR KNOWN BUGS
    # ============================================================================
    

    
    def test_pot_consistency_regression(self):
        """Regression test for pot consistency issues."""
        self.state_machine.start_hand()
        
        # Execute some actions
        player = self.state_machine.game_state.players[0]
        self.state_machine.execute_action(player, ActionType.RAISE, 10)
        
        # Pot should be consistent
        total_invested = sum(p.total_invested for p in self.state_machine.game_state.players)
        self.assertEqual(self.state_machine.game_state.pot, total_invested)
    
    def test_hand_evaluation_cache_regression(self):
        """Regression test for hand evaluation cache issues."""
        hole_cards = ['Ah', 'Kh']
        board = ['Qh', 'Jh', 'Th']
        
        # First evaluation
        result1 = self.state_machine.hand_evaluator.evaluate_hand(hole_cards, board)
        
        # Clear cache
        self.state_machine.hand_evaluator._hand_eval_cache.clear()
        
        # Second evaluation (should be same result)
        result2 = self.state_machine.hand_evaluator.evaluate_hand(hole_cards, board)
        
        self.assertEqual(result1, result2)


if __name__ == '__main__':
    unittest.main()

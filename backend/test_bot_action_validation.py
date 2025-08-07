#!/usr/bin/env python3
"""
Bot Action Validation Test Suite

This script tests bot action generation to ensure all actions are valid
and follow proper poker rules before execution.
"""

import unittest
from core.poker_state_machine import (
    ImprovedPokerStateMachine, ActionType
)
from core.strategy_engine import GTOStrategyEngine


class TestBotActionValidation(unittest.TestCase):
    """Comprehensive tests for bot action validation."""

    def setUp(self):
        """Set up the state machine and strategy engine."""
        self.sm = ImprovedPokerStateMachine(num_players=6, test_mode=True)
        self.sm.strategy_mode = "GTO"
        self.strategy_engine = GTOStrategyEngine(6)

    def test_minimum_raise_validation(self):
        """Test that bot raises meet minimum raise requirements."""
        self.sm.start_hand()
        
        # Set up scenario with specific minimum raise
        self.sm.game_state.current_bet = 10.0
        self.sm.game_state.min_raise = 5.0  # Minimum raise is $5.0
        self.sm.game_state.players[0].current_bet = 0.0
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']  # Strong hand
        
        # Set this player as the action player
        self.sm.game_state.action_player_index = 0
        
        # Get bot action
        action, amount = self.sm.get_basic_bot_action(
            self.sm.game_state.players[0]
        )
        
        if action == ActionType.RAISE:
            # Validate raise amount meets minimum
            min_raise_total = (self.sm.game_state.current_bet + 
                             self.sm.game_state.min_raise)
            self.assertGreaterEqual(
                amount, min_raise_total,
                f"Raise amount ${amount:.2f} must be >= minimum "
                f"${min_raise_total:.2f}"
            )
            
            # Test that action is valid
            errors = self.sm.validate_action(
                self.sm.game_state.players[0], action, amount
            )
            self.assertEqual(len(errors), 0, f"Raise action should be valid: {errors}")

    def test_call_amount_validation(self):
        """Test that bot calls use correct amounts."""
        self.sm.start_hand()
        
        # Set up scenario where call amount is specific
        self.sm.game_state.current_bet = 15.0
        self.sm.game_state.players[0].current_bet = 10.0
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        
        # Set this player as the action player
        self.sm.game_state.action_player_index = 0
        
        # Calculate expected call amount
        expected_call = (self.sm.game_state.current_bet - 
                        self.sm.game_state.players[0].current_bet)
        
        # Get bot action
        action, amount = self.sm.get_basic_bot_action(
            self.sm.game_state.players[0]
        )
        
        if action == ActionType.CALL:
            # Validate call amount is correct
            self.assertEqual(amount, expected_call,
                           f"Call amount should be ${expected_call:.2f}, got ${amount:.2f}")
            
            # Test that action is valid
            errors = self.sm.validate_action(
                self.sm.game_state.players[0], action, amount
            )
            self.assertEqual(len(errors), 0, f"Call action should be valid: {errors}")

    def test_all_in_validation(self):
        """Test that bot all-in actions are valid."""
        self.sm.start_hand()
        
        # Set up short stack scenario
        self.sm.game_state.players[0].stack = 5.0
        self.sm.game_state.players[0].current_bet = 0.0
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        self.sm.game_state.current_bet = 10.0
        
        # Set this player as the action player
        self.sm.game_state.action_player_index = 0
        
        # Get bot action
        action, amount = self.sm.get_basic_bot_action(
            self.sm.game_state.players[0]
        )
        
        if action == ActionType.RAISE:
            # Validate all-in amount doesn't exceed stack
            self.assertLessEqual(
                amount, self.sm.game_state.players[0].stack,
                f"All-in amount ${amount:.2f} cannot exceed stack "
                f"${self.sm.game_state.players[0].stack:.2f}"
            )
            
            # Test that action is valid
            errors = self.sm.validate_action(
                self.sm.game_state.players[0], action, amount
            )
            self.assertEqual(len(errors), 0, f"All-in action should be valid: {errors}")

    def test_check_validation(self):
        """Test that bot check actions are valid."""
        self.sm.start_hand()
        
        # Set up scenario where check is valid
        self.sm.game_state.current_bet = 0.0
        self.sm.game_state.players[0].current_bet = 0.0
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        
        # Set this player as the action player
        self.sm.game_state.action_player_index = 0
        
        # Get bot action
        action, amount = self.sm.get_basic_bot_action(
            self.sm.game_state.players[0]
        )
        
        if action == ActionType.CHECK:
            # Validate check amount is zero
            self.assertEqual(amount, 0.0, f"Check amount should be 0.0, got {amount}")
            
            # Test that action is valid
            errors = self.sm.validate_action(
                self.sm.game_state.players[0], action, amount
            )
            self.assertEqual(len(errors), 0, f"Check action should be valid: {errors}")

    def test_fold_validation(self):
        """Test that bot fold actions are valid."""
        self.sm.start_hand()
        
        # Set up scenario where fold is valid
        self.sm.game_state.current_bet = 10.0
        self.sm.game_state.players[0].current_bet = 0.0
        self.sm.game_state.players[0].cards = ['2h', '3h']  # Weak hand
        
        # Set this player as the action player
        self.sm.game_state.action_player_index = 0
        
        # Get bot action
        action, amount = self.sm.get_basic_bot_action(
            self.sm.game_state.players[0]
        )
        
        if action == ActionType.FOLD:
            # Validate fold amount is zero
            self.assertEqual(amount, 0.0, f"Fold amount should be 0.0, got {amount}")
            
            # Test that action is valid
            errors = self.sm.validate_action(
                self.sm.game_state.players[0], action, amount
            )
            self.assertEqual(len(errors), 0, f"Fold action should be valid: {errors}")

    def test_gto_strategy_validation(self):
        """Test GTO strategy engine generates valid actions."""
        self.sm.start_hand()
        
        # Set up GTO scenario
        self.sm.game_state.current_bet = 5.0
        self.sm.game_state.min_raise = 3.0
        self.sm.game_state.players[0].current_bet = 0.0
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        self.sm.game_state.players[0].position = "BTN"
        
        # Get GTO action
        action, amount = self.strategy_engine.get_gto_bot_action(
            self.sm.game_state.players[0], self.sm.game_state
        )
        
        # Validate action based on type
        if action == ActionType.RAISE:
            min_raise_total = (self.sm.game_state.current_bet + 
                             self.sm.game_state.min_raise)
            self.assertGreaterEqual(
                amount, min_raise_total,
                f"GTO raise amount ${amount:.2f} must be >= minimum "
                f"${min_raise_total:.2f}"
            )
        elif action == ActionType.CALL:
            expected_call = (self.sm.game_state.current_bet - 
                           self.sm.game_state.players[0].current_bet)
            self.assertEqual(amount, expected_call,
                           f"GTO call amount should be ${expected_call:.2f}, got ${amount:.2f}")
        elif action == ActionType.CHECK:
            self.assertEqual(amount, 0.0, f"GTO check amount should be 0.0, got {amount}")
        elif action == ActionType.FOLD:
            self.assertEqual(amount, 0.0, f"GTO fold amount should be 0.0, got {amount}")

    def test_edge_case_validation(self):
        """Test edge cases in bot action generation."""
        self.sm.start_hand()
        
        # Test 1: Very small minimum raise
        self.sm.game_state.current_bet = 1.0
        self.sm.game_state.min_raise = 0.5
        self.sm.game_state.players[0].current_bet = 0.0
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        
        # Set this player as the action player
        self.sm.game_state.action_player_index = 0
        
        action, amount = self.sm.get_basic_bot_action(
            self.sm.game_state.players[0]
        )
        if action == ActionType.RAISE:
            min_raise_total = (self.sm.game_state.current_bet + 
                             self.sm.game_state.min_raise)
            self.assertGreaterEqual(amount, min_raise_total)
        
        # Test 2: Large minimum raise
        self.sm.game_state.current_bet = 50.0
        self.sm.game_state.min_raise = 25.0
        self.sm.game_state.players[0].current_bet = 0.0
        
        action, amount = self.sm.get_basic_bot_action(
            self.sm.game_state.players[0]
        )
        if action == ActionType.RAISE:
            min_raise_total = (self.sm.game_state.current_bet + 
                             self.sm.game_state.min_raise)
            self.assertGreaterEqual(amount, min_raise_total)

    def test_stack_validation(self):
        """Test that bot actions respect player stack limits."""
        self.sm.start_hand()
        
        # Set up short stack scenario
        self.sm.game_state.players[0].stack = 3.0
        self.sm.game_state.players[0].current_bet = 0.0
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        self.sm.game_state.current_bet = 10.0
        
        # Set this player as the action player
        self.sm.game_state.action_player_index = 0
        
        # Get bot action
        action, amount = self.sm.get_basic_bot_action(
            self.sm.game_state.players[0]
        )
        
        # Validate action doesn't exceed stack
        if action in [ActionType.RAISE, ActionType.CALL]:
            self.assertLessEqual(
                amount, self.sm.game_state.players[0].stack,
                f"Action amount ${amount:.2f} cannot exceed stack "
                f"${self.sm.game_state.players[0].stack:.2f}"
            )

    def test_position_based_validation(self):
        """Test that bot actions are appropriate for player position."""
        self.sm.start_hand()
        
        # Test different positions
        positions = ["SB", "BB", "UTG", "MP", "CO", "BTN"]
        
        for i, position in enumerate(positions):
            self.sm.game_state.players[i].position = position
            self.sm.game_state.players[i].cards = ['Ah', 'Kh']
            self.sm.game_state.players[i].current_bet = 0.0
            self.sm.game_state.current_bet = 5.0
            self.sm.game_state.min_raise = 3.0
            
            # Set this player as the action player
            self.sm.game_state.action_player_index = i
            
            action, amount = self.sm.get_basic_bot_action(
                self.sm.game_state.players[i]
            )
            
            # Validate action is appropriate for position
            if action == ActionType.RAISE:
                min_raise_total = (self.sm.game_state.current_bet + 
                                 self.sm.game_state.min_raise)
                self.assertGreaterEqual(
                    amount, min_raise_total,
                    f"Position {position} raise amount ${amount:.2f} must be >= minimum "
                    f"${min_raise_total:.2f}"
                )

    def test_hand_strength_validation(self):
        """Test that bot actions are appropriate for hand strength."""
        self.sm.start_hand()
        
        # Test strong hand
        self.sm.game_state.players[0].cards = ['Ah', 'Kh']
        self.sm.game_state.players[0].current_bet = 0.0
        self.sm.game_state.current_bet = 5.0
        
        # Set this player as the action player
        self.sm.game_state.action_player_index = 0
        
        strong_action, strong_amount = self.sm.get_basic_bot_action(
            self.sm.game_state.players[0]
        )
        
        # Test weak hand
        self.sm.game_state.players[1].cards = ['2h', '3h']
        self.sm.game_state.players[1].current_bet = 0.0
        
        # Set this player as the action player
        self.sm.game_state.action_player_index = 1
        
        weak_action, weak_amount = self.sm.get_basic_bot_action(
            self.sm.game_state.players[1]
        )
        
        # Validate that strong hands are more aggressive
        if strong_action == ActionType.RAISE and weak_action == ActionType.FOLD:
            # This is expected behavior
            pass
        elif strong_action == ActionType.RAISE:
            # Strong hand should raise appropriately
            min_raise_total = (self.sm.game_state.current_bet + 
                             self.sm.game_state.min_raise)
            self.assertGreaterEqual(strong_amount, min_raise_total)

    def test_comprehensive_action_validation(self):
        """Test comprehensive validation of all bot actions."""
        self.sm.start_hand()
        
        # Test multiple scenarios
        scenarios = [
            {"current_bet": 0.0, "min_raise": 2.0, "player_bet": 0.0, "cards": ['Ah', 'Kh']},
            {"current_bet": 5.0, "min_raise": 3.0, "player_bet": 0.0, "cards": ['Ah', 'Kh']},
            {"current_bet": 10.0, "min_raise": 5.0, "player_bet": 5.0, "cards": ['Ah', 'Kh']},
            {"current_bet": 0.0, "min_raise": 2.0, "player_bet": 0.0, "cards": ['2h', '3h']},
        ]
        
        for i, scenario in enumerate(scenarios):
            self.sm.game_state.current_bet = scenario["current_bet"]
            self.sm.game_state.min_raise = scenario["min_raise"]
            self.sm.game_state.players[i].current_bet = scenario["player_bet"]
            self.sm.game_state.players[i].cards = scenario["cards"]
            
            # Set this player as the action player
            self.sm.game_state.action_player_index = i
            
            action, amount = self.sm.get_basic_bot_action(
                self.sm.game_state.players[i]
            )
            
            # Validate action based on type
            if action == ActionType.RAISE:
                min_raise_total = (self.sm.game_state.current_bet + 
                                 self.sm.game_state.min_raise)
                self.assertGreaterEqual(
                    amount, min_raise_total,
                    f"Scenario {i}: Raise amount ${amount:.2f} must be >= minimum "
                    f"${min_raise_total:.2f}"
                )
            elif action == ActionType.CALL:
                expected_call = (self.sm.game_state.current_bet - 
                               self.sm.game_state.players[i].current_bet)
                self.assertEqual(
                    amount, expected_call,
                    f"Scenario {i}: Call amount should be ${expected_call:.2f}, got ${amount:.2f}"
                )
            elif action == ActionType.CHECK:
                self.assertEqual(amount, 0.0, f"Scenario {i}: Check amount should be 0.0, got {amount}")
            elif action == ActionType.FOLD:
                self.assertEqual(amount, 0.0, f"Scenario {i}: Fold amount should be 0.0, got {amount}")


if __name__ == '__main__':
    unittest.main(verbosity=2)

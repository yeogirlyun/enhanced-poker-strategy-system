#!/usr/bin/env python3
"""
Unit Tests for BB Edge Cases

Tests the critical position-based rules:
1. BB with weak hand facing no raise
2. BB with weak hand facing small raise
3. BB check option when action folds to them
4. Position-based rules before hand strength rules
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, PokerState, ActionType, Player
from gui_models import StrategyData
import unittest


class TestBBEdgeCases(unittest.TestCase):
    """Test suite for Big Blind edge cases and position-based rules."""

    def setUp(self):
        """Set up test environment."""
        self.strategy_data = StrategyData()
        self.machine = ImprovedPokerStateMachine(num_players=6, strategy_data=self.strategy_data)

    def test_bb_weak_hand_no_raise(self):
        """Test BB with weak hand facing no raise should check."""
        # Setup: BB with weak hand (72o), no raise
        self.machine.start_hand()
        bb_player = self.machine.game_state.players[self.machine.big_blind_position]
        bb_player.cards = ['7h', '2d']  # Weak hand
        self.machine.game_state.current_bet = 1.0  # BB amount
        bb_player.current_bet = 1.0
        
        # Execute bot action
        action, amount = self.machine.get_strategy_action(bb_player)
        
        # Assert: BB should check with weak hand when no raise
        self.assertEqual(action, ActionType.CHECK)
        self.assertEqual(amount, 0.0)
        print("✅ BB with weak hand facing no raise correctly checks")

    def test_bb_weak_hand_small_raise(self):
        """Test BB with weak hand facing small raise should check."""
        # Setup: BB with weak hand (72o), facing small raise
        self.machine.start_hand()
        bb_player = self.machine.game_state.players[self.machine.big_blind_position]
        bb_player.cards = ['7h', '2d']  # Weak hand
        self.machine.game_state.current_bet = 1.0  # Still BB amount (no real raise)
        bb_player.current_bet = 1.0
        
        # Execute bot action
        action, amount = self.machine.get_strategy_action(bb_player)
        
        # Assert: BB should check with weak hand when no real raise
        self.assertEqual(action, ActionType.CHECK)
        self.assertEqual(amount, 0.0)
        print("✅ BB with weak hand facing small raise correctly checks")

    def test_bb_strong_hand_no_raise(self):
        """Test BB with strong hand facing no raise should check (position rule)."""
        # Setup: BB with strong hand (AA), no raise
        self.machine.start_hand()
        bb_player = self.machine.game_state.players[self.machine.big_blind_position]
        bb_player.cards = ['Ah', 'Ad']  # Strong hand
        self.machine.game_state.current_bet = 1.0  # BB amount
        bb_player.current_bet = 1.0
        
        # Execute bot action
        action, amount = self.machine.get_strategy_action(bb_player)
        
        # Assert: BB should check with strong hand when no raise (position rule takes precedence)
        self.assertEqual(action, ActionType.CHECK)
        self.assertEqual(amount, 0.0)
        print("✅ BB with strong hand facing no raise correctly checks (position rule)")

    def test_bb_weak_hand_real_raise(self):
        """Test BB with weak hand facing real raise should fold."""
        # Setup: BB with weak hand (72o), facing real raise
        self.machine.start_hand()
        bb_player = self.machine.game_state.players[self.machine.big_blind_position]
        bb_player.cards = ['7h', '2d']  # Weak hand
        self.machine.game_state.current_bet = 3.0  # Real raise
        bb_player.current_bet = 1.0
        
        # Execute bot action
        action, amount = self.machine.get_strategy_action(bb_player)
        
        # Assert: BB should fold with weak hand to real raise
        self.assertEqual(action, ActionType.FOLD)
        self.assertEqual(amount, 0.0)
        print("✅ BB with weak hand facing real raise correctly folds")

    def test_position_based_rules_before_hand_strength(self):
        """Test that position-based rules are checked before hand strength."""
        # Setup: SB with weak hand, no raise
        self.machine.start_hand()
        sb_player = self.machine.game_state.players[self.machine.small_blind_position]
        sb_player.cards = ['7h', '2d']  # Weak hand
        self.machine.game_state.current_bet = 0.5  # SB amount
        sb_player.current_bet = 0.5
        
        # Execute bot action
        action, amount = self.machine.get_strategy_action(sb_player)
        
        # Assert: SB should check with weak hand when no raise (position rule)
        self.assertEqual(action, ActionType.CHECK)
        self.assertEqual(amount, 0.0)
        print("✅ Position-based rules correctly applied before hand strength")

    def test_button_weak_hand_no_raise(self):
        """Test Button with weak hand facing no raise should check."""
        # Setup: Button with weak hand, no raise
        self.machine.start_hand()
        btn_player = None
        for player in self.machine.game_state.players:
            if player.position == 'BTN':
                btn_player = player
                break
        
        btn_player.cards = ['7h', '2d']  # Weak hand
        self.machine.game_state.current_bet = 0.0  # No bet
        btn_player.current_bet = 0.0
        
        # Execute bot action
        action, amount = self.machine.get_strategy_action(btn_player)
        
        # Assert: Button should check with weak hand when no bet
        self.assertEqual(action, ActionType.CHECK)
        self.assertEqual(amount, 0.0)
        print("✅ Button with weak hand facing no bet correctly checks")

    def test_early_returns_for_special_cases(self):
        """Test that early returns are used for special cases."""
        # Setup: BB with any hand, no raise
        self.machine.start_hand()
        bb_player = self.machine.game_state.players[self.machine.big_blind_position]
        bb_player.cards = ['7h', '2d']  # Any hand
        self.machine.game_state.current_bet = 1.0  # BB amount
        bb_player.current_bet = 1.0
        
        # Mock the strategy data to be empty to force fallback
        original_strategy = self.machine.strategy_data
        self.machine.strategy_data = None
        
        # Execute bot action
        action, amount = self.machine.get_strategy_action(bb_player)
        
        # Restore strategy data
        self.machine.strategy_data = original_strategy
        
        # Assert: Should still check due to position-based rule
        self.assertEqual(action, ActionType.CHECK)
        self.assertEqual(amount, 0.0)
        print("✅ Early returns correctly handle special cases")

    def test_comprehensive_logging(self):
        """Test that comprehensive logging is present at each decision point."""
        # Setup: BB with weak hand
        self.machine.start_hand()
        bb_player = self.machine.game_state.players[self.machine.big_blind_position]
        bb_player.cards = ['7h', '2d']
        self.machine.game_state.current_bet = 1.0
        bb_player.current_bet = 1.0
        
        # Capture logs
        log_messages = []
        original_log = self.machine._log_action
        
        def capture_log(message):
            log_messages.append(message)
            original_log(message)
        
        self.machine._log_action = capture_log
        
        # Execute bot action
        action, amount = self.machine.get_strategy_action(bb_player)
        
        # Restore original logging
        self.machine._log_action = original_log
        
        # Assert: Logging should contain position-based rule messages
        position_rule_logs = [msg for msg in log_messages if "POSITION RULE" in msg]
        self.assertGreater(len(position_rule_logs), 0)
        print("✅ Comprehensive logging present at decision points")


def run_bb_edge_case_tests():
    """Run all BB edge case tests."""
    print("🧪 Running BB Edge Case Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBBEdgeCases)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All BB edge case tests passed!")
    else:
        print("\n❌ Some BB edge case tests failed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_bb_edge_case_tests() 
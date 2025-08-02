#!/usr/bin/env python3
"""
Comprehensive Test Suite for Improved Poker State Machine

Tests all critical fixes:
1. BB folding bug (BB should check with weak hands when no raise)
2. Dynamic position tracking
3. Correct raise logic
4. All-in state tracking
5. Strategy integration
6. Input validation
"""

import sys
import os
from typing import List, Dict, Any
from dataclasses import dataclass

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, ActionType, PokerState
from gui_models import StrategyData

# Test result tracking
@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    details: Dict[str, Any] = None


class PokerStateMachineTestSuite:
    def __init__(self):
        self.results: List[TestResult] = []
        self.strategy_data = self._create_test_strategy()
        
    def _create_test_strategy(self) -> StrategyData:
        """Create a test strategy with minimal hands to test BB folding."""
        strategy = StrategyData()
        # Only include premium hands in tiers
        # This ensures weak hands like 72o are NOT in any tier
        strategy.strategy_dict = {
            "hand_strength_tables": {
                "preflop": {
                    "AA": 85, "KK": 82, "QQ": 80, "JJ": 77,
                    "AKs": 67, "AKo": 65, "AQs": 66, "AQo": 64
                },
                "postflop": {
                    "high_card": 5, "pair": 15, "two_pair": 45,
                    "set": 60, "straight": 70, "flush": 80
                }
            },
            "preflop": {
                "open_rules": {
                    "UTG": {"threshold": 60, "sizing": 3.0},
                    "MP": {"threshold": 55, "sizing": 3.0},
                    "CO": {"threshold": 48, "sizing": 2.5},
                    "BTN": {"threshold": 40, "sizing": 2.5},
                    "SB": {"threshold": 50, "sizing": 3.0}
                },
                "vs_raise": {
                    "UTG": {"value_thresh": 75, "call_thresh": 65, "sizing": 3.0},
                    "MP": {"value_thresh": 72, "call_thresh": 62, "sizing": 3.0},
                    "CO": {"value_thresh": 70, "call_thresh": 60, "sizing": 2.5},
                    "BTN": {"value_thresh": 68, "call_thresh": 55, "sizing": 2.5},
                    "SB": {"value_thresh": 70, "call_thresh": 60, "sizing": 3.0}
                }
            },
            "postflop": {
                "pfa": {
                    "flop": {
                        "UTG": {"val_thresh": 35, "check_thresh": 15, "sizing": 0.75}
                    }
                }
            }
        }
        
        # Create tiers with only premium hands
        from gui_models import HandStrengthTier
        strategy.tiers = [
            HandStrengthTier("Premium", 60, 100, "#ff0000", {"AA", "KK", "QQ", "JJ", "AKs", "AKo", "AQs", "AQo"})
        ]
        
        return strategy
    
    def log_test(self, name: str, passed: bool, message: str, details: Dict = None):
        """Log a test result."""
        self.results.append(TestResult(name, passed, message, details))
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            print(f"    Message: {message}")
            if details:
                for key, value in details.items():
                    print(f"    {key}: {value}")
        print()
    
    def test_bb_folding_bug_fix(self):
        """Test the critical BB folding bug fix."""
        print("\n" + "="*60)
        print("TEST 1: BB FOLDING BUG FIX")
        print("="*60)
        
        # Create a state machine with test strategy
        sm = ImprovedPokerStateMachine(num_players=6, strategy_data=self.strategy_data)
        
        # Track actions
        actions_taken = []
        
        def track_action(message):
            if "decided:" in message:
                actions_taken.append(message)
        
        sm.on_log_entry = track_action
        
        # Start a hand
        sm.start_hand()
        
        # Give BB a weak hand that's NOT in any tier (72o)
        bb_player = None
        for player in sm.game_state.players:
            if player.position == "BB":
                bb_player = player
                # Force a weak hand
                player.cards = ["7h", "2c"]  # 72 offsuit - worst hand in poker
                break
        
        if not bb_player:
            self.log_test("BB Position Found", False, "Could not find BB player")
            return
        
        # Simulate everyone folding to BB
        print(f"Simulating all players folding to BB who has {bb_player.cards}")
        
        # Execute folds for all players except BB
        for i in range(5):  # 5 players need to fold
            current_player = sm.get_action_player()
            if current_player and current_player.position != "BB":
                print(f"  {current_player.name} ({current_player.position}) folds")
                sm.execute_action(current_player, ActionType.FOLD)
        
        # Now it should be BB's turn
        current_player = sm.get_action_player()
        
        # Force BB to act by calling execute_bot_action directly
        if current_player and current_player.position == "BB":
            print(f"  {current_player.name} ({current_player.position}) is acting")
            sm.execute_bot_action(current_player)
        else:
            print(f"  ERROR: Expected BB to act, but got {current_player.name if current_player else 'None'}")
        
        # Find BB's action in the log
        bb_action = None
        for action in actions_taken:
            if "BB" in action or "Player 3" in action:
                bb_action = action
                break
        
        # Check results
        if bb_action and "CHECK" in bb_action:
            self.log_test(
                "BB Checks with Weak Hand",
                True,
                f"BB correctly checked with {bb_player.cards} when everyone folded",
                {"bb_action": bb_action, "bb_cards": bb_player.cards}
            )
        elif bb_action and "FOLD" in bb_action:
            self.log_test(
                "BB Checks with Weak Hand",
                False,
                f"BUG STILL EXISTS: BB folded with {bb_player.cards} instead of checking!",
                {"bb_action": bb_action, "bb_cards": bb_player.cards}
            )
        else:
            self.log_test(
                "BB Checks with Weak Hand",
                False,
                "Could not determine BB's action",
                {"actions": actions_taken}
            )
    
    def test_position_tracking(self):
        """Test dynamic position tracking for different table sizes."""
        print("\n" + "="*60)
        print("TEST 2: DYNAMIC POSITION TRACKING")
        print("="*60)
        
        table_sizes = [2, 3, 6, 9]
        
        for size in table_sizes:
            sm = ImprovedPokerStateMachine(num_players=size)
            sm.start_hand()
            
            positions = [p.position for p in sm.game_state.players]
            
            # Check that we have the right positions
            if size == 2:
                expected = ["BTN/SB", "BB"]
            elif size == 3:
                expected = ["BTN", "SB", "BB"]
            elif size == 6:
                expected = ["BTN", "SB", "BB", "UTG", "MP", "CO"]
            elif size == 9:
                expected = ["BTN", "SB", "BB", "UTG", "UTG+1", "MP", "MP+1", "CO", "LJ"]
            
            # Positions might be rotated, so check they're all present
            all_present = all(pos in positions for pos in expected)
            
            self.log_test(
                f"Position Tracking ({size} players)",
                all_present,
                f"Positions: {positions}",
                {"expected": expected, "actual": positions}
            )
    
    def test_raise_logic(self):
        """Test correct raise logic and minimum raise tracking."""
        print("\n" + "="*60)
        print("TEST 3: RAISE LOGIC")
        print("="*60)
        
        sm = ImprovedPokerStateMachine(num_players=6)
        sm.start_hand()
        
        # Get first player after BB (UTG)
        utg_player = sm.get_action_player()
        
        # UTG raises to 3 BB
        sm.execute_action(utg_player, ActionType.RAISE, 3.0)
        
        # Check min raise is correct
        expected_min_raise = 2.0  # UTG raised by 2 (from 1 to 3)
        actual_min_raise = sm.game_state.min_raise
        
        self.log_test(
            "Minimum Raise Calculation",
            actual_min_raise == expected_min_raise,
            f"Min raise after 3BB raise",
            {"expected": expected_min_raise, "actual": actual_min_raise}
        )
        
        # Next player tries invalid raise
        next_player = sm.get_action_player()
        errors = sm.validate_action(next_player, ActionType.RAISE, 4.0)  # Less than min raise (should be 5.0)
        
        self.log_test(
            "Invalid Raise Detection",
            len(errors) > 0,
            "Raise to 4.0 when min is 5.0 should fail",
            {"errors": errors}
        )
    
    def test_all_in_tracking(self):
        """Test all-in state tracking."""
        print("\n" + "="*60)
        print("TEST 4: ALL-IN TRACKING")
        print("="*60)
        
        sm = ImprovedPokerStateMachine(num_players=6)
        sm.start_hand()
        
        # Give a player a small stack
        player = sm.get_action_player()
        player.stack = 5.0  # Only 5 BB
        
        # Player goes all-in
        sm.execute_action(player, ActionType.RAISE, 10.0)  # More than stack
        
        self.log_test(
            "All-In State",
            player.is_all_in,
            "Player should be marked all-in",
            {"stack": player.stack, "all_in": player.is_all_in}
        )
    
    def test_strategy_integration(self):
        """Test bot strategy integration."""
        print("\n" + "="*60)
        print("TEST 5: STRATEGY INTEGRATION")
        print("="*60)
        
        sm = ImprovedPokerStateMachine(num_players=6, strategy_data=self.strategy_data)
        
        # Track bot decisions
        bot_actions = []
        
        def track_bot_action(message):
            if "Bot" in message and "decided:" in message:
                bot_actions.append(message)
        
        sm.on_log_entry = track_bot_action
        
        # Start hand and let bots play
        sm.start_hand()
        
        # Give a bot AA (premium hand)
        utg_bot = None
        for player in sm.game_state.players:
            if not player.is_human and player.position == "UTG":
                player.cards = ["Ah", "As"]  # Pocket aces
                utg_bot = player
                break
        
        # Skip to bot's turn by folding human
        if sm.get_action_player().is_human:
            sm.execute_action(sm.get_action_player(), ActionType.FOLD)
        
        # Force bot to act
        current_player = sm.get_action_player()
        if current_player and not current_player.is_human:
            print(f"  Bot {current_player.name} ({current_player.position}) acting with {current_player.cards}")
            sm.execute_bot_action(current_player)
        else:
            print(f"  ERROR: Expected bot to act, but got {current_player.name if current_player else 'None'}")
        
        # Check if bot made a strong action with AA
        strong_action = any("RAISE" in action or "BET" in action for action in bot_actions)
        
        self.log_test(
            "Bot Strategy Decision",
            strong_action,
            "Bot should raise/bet with AA",
            {"bot_actions": bot_actions}
        )
    
    def test_input_validation(self):
        """Test input validation."""
        print("\n" + "="*60)
        print("TEST 6: INPUT VALIDATION")
        print("="*60)
        
        sm = ImprovedPokerStateMachine(num_players=6)
        sm.start_hand()
        
        player = sm.get_action_player()
        
        # Test various invalid actions
        tests = [
            ("Negative Amount", ActionType.BET, -10, "Amount cannot be negative"),
            ("Check with Bet", ActionType.CHECK, 0, "Cannot check when bet"),
            ("Bet over Raise", ActionType.BET, 5, "Cannot bet when there's already a bet"),
        ]
        
        # First make a bet so we can test invalid actions
        sm.execute_action(player, ActionType.RAISE, 3.0)
        player = sm.get_action_player()
        
        for test_name, action, amount, expected_error in tests:
            errors = sm.validate_action(player, action, amount)
            has_expected_error = any(expected_error in error for error in errors)
            
            self.log_test(
                f"Validation: {test_name}",
                has_expected_error or len(errors) > 0,
                f"Should detect: {expected_error}",
                {"errors": errors}
            )
    
    def test_state_transitions(self):
        """Test proper state transitions."""
        print("\n" + "="*60)
        print("TEST 7: STATE TRANSITIONS")
        print("="*60)
        
        sm = ImprovedPokerStateMachine(num_players=2)  # Heads up for quick test
        
        # Track state transitions
        states = []
        
        def track_state(new_state=None):
            if new_state:
                states.append(new_state.value if hasattr(new_state, 'value') else str(new_state))
        
        sm.on_state_change = track_state
        
        # Start hand
        sm.start_hand()
        
        # Both players call/check through all streets
        for _ in range(8):  # Max 8 actions to get through all streets
            player = sm.get_action_player()
            if player and sm.current_state != PokerState.END_HAND:
                if sm.game_state.current_bet > player.current_bet:
                    sm.execute_action(player, ActionType.CALL)
                else:
                    sm.execute_action(player, ActionType.CHECK)
            else:
                break  # Stop if hand is over
        
        # Check we went through all streets
        expected_sequence = [
            "preflop_betting", "deal_flop", "flop_betting", 
            "deal_turn", "turn_betting", "deal_river", 
            "river_betting", "showdown", "end_hand"
        ]
        
        all_present = all(state in states for state in expected_sequence)
        
        self.log_test(
            "State Transitions",
            all_present,
            "All states should be visited",
            {"states": states}
        )
    
    def run_all_tests(self):
        """Run all tests and generate report."""
        print("\n" + "="*60)
        print("POKER STATE MACHINE TEST SUITE")
        print("="*60)
        
        # Run all test methods
        self.test_bb_folding_bug_fix()
        self.test_position_tracking()
        self.test_raise_logic()
        self.test_all_in_tracking()
        self.test_strategy_integration()
        self.test_input_validation()
        self.test_state_transitions()
        
        # Generate summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed < total:
            print("\nFailed Tests:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}: {result.message}")
        
        return passed == total


def main():
    """Run the test suite."""
    print("Starting Poker State Machine Test Suite...")
    print("This will test all critical fixes, especially the BB folding bug.")
    
    test_suite = PokerStateMachineTestSuite()
    all_passed = test_suite.run_all_tests()
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED! The poker state machine is working correctly.")
    else:
        print("\n❌ SOME TESTS FAILED! Please review the failures above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main()) 
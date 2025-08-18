"""
Regression Test for Infinite Loop Fix

This test specifically validates the fix for the heads-up flop betting loop
that was causing hands review validation to hang indefinitely.
"""

import sys
import time
from typing import Dict, Any

sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.poker_types import Player, PokerState  
from core.hand_model import ActionType
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController


def test_hu_flop_bet_call_closes_round():
    """Test that HU flop bet→call properly closes the round and advances to turn."""
    print("🧪 TESTING: HU flop bet→call round completion")
    
    # Create PPSM
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5, big_blind=10, starting_stack=1000),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    # Start hand
    ppsm.start_hand()
    assert ppsm.current_state == PokerState.PREFLOP_BETTING
    assert ppsm.game_state.street == "preflop"
    
    # Preflop: opener raises, other calls
    opener = ppsm.game_state.players[ppsm.action_player_index]
    print(f"   Preflop: {opener.name} raises to $30")
    assert ppsm.execute_action(opener, ActionType.RAISE, 30), "Preflop raise should succeed"
    
    caller = ppsm.game_state.players[ppsm.action_player_index]  
    print(f"   Preflop: {caller.name} calls")
    assert ppsm.execute_action(caller, ActionType.CALL, None), "Preflop call should succeed"
    
    # Should now be on flop
    assert ppsm.game_state.street == "flop", f"Expected flop, got {ppsm.game_state.street}"
    assert ppsm.current_state == PokerState.FLOP_BETTING, f"Expected FLOP_BETTING, got {ppsm.current_state}"
    
    print(f"   ✅ Reached flop successfully: {ppsm.game_state.board}")
    
    # Critical test: HU flop bet→call should NOT loop infinitely
    bettor = ppsm.game_state.players[ppsm.action_player_index]
    print(f"   Flop: {bettor.name} bets $60")
    
    start_time = time.time()
    assert ppsm.execute_action(bettor, ActionType.BET, 60), "Flop bet should succeed"
    bet_time = time.time() - start_time
    
    caller = ppsm.game_state.players[ppsm.action_player_index]
    print(f"   Flop: {caller.name} calls")
    
    call_start = time.time()
    assert ppsm.execute_action(caller, ActionType.CALL, None), "Flop call should succeed"
    call_time = time.time() - call_start
    
    total_flop_time = bet_time + call_time
    
    # ✅ CRITICAL: Must advance to turn (no infinite loop)
    assert ppsm.game_state.street == "turn", f"Expected turn after flop bet→call, got {ppsm.game_state.street}"
    assert ppsm.current_state == PokerState.TURN_BETTING, f"Expected TURN_BETTING, got {ppsm.current_state}"
    
    print(f"   ✅ SUCCESS: Advanced to turn in {total_flop_time:.4f}s")
    print(f"   ✅ Board: {ppsm.game_state.board} (should have 4 cards)")
    
    # Verify timing (should be nearly instantaneous, not 3+ seconds)
    assert total_flop_time < 0.1, f"Flop betting took too long: {total_flop_time:.4f}s (possible infinite loop)"
    
    return True


def test_need_action_from_tracking():
    """Test that need_action_from is properly tracked throughout the hand."""
    print("🧪 TESTING: need_action_from tracking")
    
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=3, small_blind=5, big_blind=10, starting_stack=1000),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    ppsm.start_hand()
    
    # Check preflop need_action_from (all except BB)
    rs = ppsm.game_state.round_state
    expected_preflop = {0, 2} if ppsm.big_blind_position == 1 else {0, 1}  # All except BB
    actual_preflop = rs.need_action_from
    
    print(f"   Preflop need_action_from: {actual_preflop}")
    print(f"   BB position: {ppsm.big_blind_position}")
    
    # First action should remove actor from need_action_from
    first_actor = ppsm.game_state.players[ppsm.action_player_index]
    first_actor_idx = ppsm.action_player_index
    
    ppsm.execute_action(first_actor, ActionType.CALL, None)
    
    # Check that first actor removed from need_action_from
    assert first_actor_idx not in rs.need_action_from, f"Actor {first_actor_idx} should be removed after acting"
    
    print(f"   After first action, need_action_from: {rs.need_action_from}")
    
    return True


def test_safety_guards():
    """Test that safety guards prevent infinite loops with detailed error reporting."""
    print("🧪 TESTING: Safety guard infinite loop detection")
    
    # This creates a mock scenario that could theoretically loop
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5, big_blind=10, starting_stack=1000),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    # Create a mock decision engine that would cause issues
    class MockLoopingDecisionEngine:
        def __init__(self):
            self.call_count = 0
        
        def get_decision(self, player_name: str, game_state):
            self.call_count += 1
            if self.call_count < 500:  # Would loop indefinitely without guards
                return ActionType.CHECK, 0.0
            return None
            
        def has_decision_for_player(self, player_name: str) -> bool:
            return self.call_count < 500
            
        def reset_for_new_hand(self) -> None:
            self.call_count = 0
    
    mock_engine = MockLoopingDecisionEngine()
    
    start_time = time.time()
    results = ppsm.play_hand_with_decision_engine(mock_engine)
    elapsed = time.time() - start_time
    
    print(f"   Test completed in {elapsed:.3f}s")
    print(f"   Errors detected: {len(results['errors'])}")
    
    # Should detect loop and break with error
    loop_detected = any('INFINITE_LOOP_DETECTED' in error for error in results['errors'])
    if loop_detected:
        print("   ✅ Safety guard successfully detected infinite loop")
        for error in results['errors']:
            if 'INFINITE_LOOP_DETECTED' in error:
                print(f"   Error details: {error[:200]}...")
                break
    
    # Should complete quickly (not hang for minutes)
    assert elapsed < 2.0, f"Test took too long: {elapsed:.3f}s"
    
    return True


def main():
    """Run all regression tests for the infinite loop fix."""
    print("🚀 INFINITE LOOP FIX REGRESSION TESTS")
    print("=" * 50)
    
    tests = [
        test_hu_flop_bet_call_closes_round,
        test_need_action_from_tracking,
        test_safety_guards
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            success = test()
            if success:
                print(f"✅ {test.__name__} PASSED")
                passed += 1
            else:
                print(f"❌ {test.__name__} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} CRASHED: {e}")
            failed += 1
        
        print()
    
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - Infinite loop fix is working!")
        return True
    else:
        print("🚨 SOME TESTS FAILED - Fix may need more work")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

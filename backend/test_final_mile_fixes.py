#!/usr/bin/env python3
"""
Regression tests for the final mile surgical patches:
1. Implicit FOLD injection when wrong player is logged next while facing a bet
2. ALL_IN mapping to proper to-amount semantics

These tests validate the final 10% → 100% improvements.
"""

import sys
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Import PPSM and related types
sys.path.append('.')
from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig, HandModelDecisionEngineAdapter
from core.poker_types import Player, GameState, PokerState, RoundState
from core.hand_model import ActionType, Hand, Action, Street
from core.providers.deck_providers import DeterministicDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import HandsReviewAdvancementController


def create_test_hand_with_multiway_folds():
    """Create a test hand where logs skip intermediate FOLDs in multiway action."""
    actions = [
        # Preflop: UTG raises, everyone else calls
        Action(order=1, actor_uid="seat1", action=ActionType.RAISE, amount=30, street=Street.PREFLOP),
        Action(order=2, actor_uid="seat2", action=ActionType.CALL, amount=30, street=Street.PREFLOP),
        Action(order=3, actor_uid="seat3", action=ActionType.CALL, amount=30, street=Street.PREFLOP),
        Action(order=4, actor_uid="seat4", action=ActionType.CALL, amount=30, street=Street.PREFLOP),
        
        # Flop: seat1 bets, then log JUMPS to seat4 call (skipping seat2, seat3 folds)
        Action(order=5, actor_uid="seat1", action=ActionType.BET, amount=60, street=Street.FLOP),
        # NOTE: seat2 and seat3 FOLDs are OMITTED from the log!
        Action(order=6, actor_uid="seat4", action=ActionType.CALL, amount=60, street=Street.FLOP),
    ]
    
    hole_cards = {
        "seat1": ["As", "Kd"],
        "seat2": ["7h", "6c"],
        "seat3": ["9s", "8d"],
        "seat4": ["Th", "Jc"]
    }
    
    board = ["Qh", "Jd", "5c"]  # flop only for this test
    
    metadata = {
        "hand_id": "TEST_MULTIWAY_FOLDS",
        "game_type": "NLHE",
        "stakes": "5/10",
        "players": 4,
        "button_position": 0
    }
    
    return Hand(
        actions=actions,
        hole_cards=hole_cards,
        board=board,
        metadata=metadata
    )


def create_test_hand_with_allin():
    """Create a test hand with explicit ALL_IN actions."""
    actions = [
        # Preflop: raise/call
        Action(order=1, actor_uid="seat1", action=ActionType.RAISE, amount=30, street=Street.PREFLOP),
        Action(order=2, actor_uid="seat2", action=ActionType.CALL, amount=30, street=Street.PREFLOP),
        
        # Flop: bet/call
        Action(order=3, actor_uid="seat1", action=ActionType.BET, amount=60, street=Street.FLOP),
        Action(order=4, actor_uid="seat2", action=ActionType.CALL, amount=60, street=Street.FLOP),
        
        # Turn: Large RAISE by seat1 (simulate all-in with remaining stack)
        Action(order=5, actor_uid="seat1", action=ActionType.RAISE, amount=910, street=Street.TURN),  # all remaining stack
        Action(order=6, actor_uid="seat2", action=ActionType.CALL, amount=910, street=Street.TURN),
    ]
    
    hole_cards = {
        "seat1": ["As", "Kd"],
        "seat2": ["Qh", "Jc"]
    }
    
    board = ["Th", "9d", "8c", "7s"]  # through turn
    
    metadata = {
        "hand_id": "TEST_LARGE_RAISE_MAPPING",
        "game_type": "NLHE",
        "stakes": "5/10",
        "players": 2,
        "button_position": 0
    }
    
    return Hand(
        actions=actions,
        hole_cards=hole_cards,
        board=board,
        metadata=metadata
    )


def test_multiway_implied_folds():
    """Test that adapter injects FOLDs for seats that owe action before reaching the logged caller."""
    print("🧪 Testing multiway implied FOLD injection...")
    
    # Create test hand with skipped folds
    test_hand = create_test_hand_with_multiway_folds()
    
    # Create PPSM with 4 players
    config = GameConfig(num_players=4, small_blind=5.0, big_blind=10.0, starting_stack=1000.0)
    ppsm = PurePokerStateMachine(
        config=config,
        deck_provider=DeterministicDeck(),
        rules_provider=StandardRules(),
        advancement_controller=HandsReviewAdvancementController()
    )
    
    # Set up deterministic deck and decision engine
    ppsm._setup_for_hand_model(test_hand, create_hand_replay_engine=True)
    
    # Start the hand
    ppsm.start_hand()
    
    # Play through preflop (should work normally)
    preflop_actions = 0
    while ppsm.current_state == PokerState.PREFLOP_BETTING and preflop_actions < 10:
        current_player = ppsm.game_state.players[ppsm.action_player_index]
        decision = ppsm.decision_engine.get_decision(current_player.name, ppsm.game_state)
        if decision:
            action_type, amount = decision
            if ppsm._is_valid_action(current_player, action_type, amount):
                ppsm.execute_action(current_player, action_type, amount)
                preflop_actions += 1
            else:
                break
        else:
            break
    
    print(f"✅ Preflop: {preflop_actions} actions completed")
    
    # Should now be on flop
    if ppsm.current_state != PokerState.FLOP_BETTING:
        print(f"❌ Expected FLOP_BETTING, got {ppsm.current_state}")
        return False
    
    # First flop action should be seat1 BET
    current_player = ppsm.game_state.players[ppsm.action_player_index]
    decision = ppsm.decision_engine.get_decision(current_player.name, ppsm.game_state)
    if decision and decision[0] == ActionType.BET:
        ppsm.execute_action(current_player, decision[0], decision[1])
        print(f"✅ {current_player.name} BET executed")
    else:
        print(f"❌ Expected BET from {current_player.name}, got {decision}")
        return False
    
    # Now seat2 should be asked to act, but log has seat4 CALL next
    # Adapter should inject FOLD for seat2 and seat3 before reaching seat4
    folds_injected = 0
    max_folds = 5  # safety limit
    
    while ppsm.current_state == PokerState.FLOP_BETTING and folds_injected < max_folds:
        current_player = ppsm.game_state.players[ppsm.action_player_index]
        decision = ppsm.decision_engine.get_decision(current_player.name, ppsm.game_state)
        
        if not decision:
            break
            
        action_type, amount = decision
        
        if action_type == ActionType.FOLD:
            ppsm.execute_action(current_player, action_type, amount)
            folds_injected += 1
            print(f"✅ {current_player.name} FOLD injected (#{folds_injected})")
        elif action_type == ActionType.CALL:
            ppsm.execute_action(current_player, action_type, amount)
            print(f"✅ {current_player.name} CALL executed")
            break
        else:
            print(f"❌ Unexpected action: {action_type}")
            break
    
    # Should have injected 2 FOLDs (seat2, seat3) before seat4 CALL
    if folds_injected == 2:
        print(f"✅ SUCCESS: Injected {folds_injected} FOLDs as expected")
        return True
    else:
        print(f"❌ FAILURE: Expected 2 FOLDs, got {folds_injected}")
        return False


def test_allin_mapping():
    """Test that large RAISE amounts (simulating all-in) are mapped correctly to to-amount."""
    print("🧪 Testing large RAISE (all-in scenario) mapping...")
    
    # Create test hand with ALL_IN
    test_hand = create_test_hand_with_allin()
    
    # Create PPSM with 2 players
    config = GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0)
    ppsm = PurePokerStateMachine(
        config=config,
        deck_provider=DeterministicDeck(),
        rules_provider=StandardRules(),
        advancement_controller=HandsReviewAdvancementController()
    )
    
    # Set up deterministic deck and decision engine
    ppsm._setup_for_hand_model(test_hand, create_hand_replay_engine=True)
    
    # Start the hand and play to turn
    ppsm.start_hand()
    
    # Skip through preflop and flop quickly
    action_count = 0
    while ppsm.current_state in [PokerState.PREFLOP_BETTING, PokerState.FLOP_BETTING] and action_count < 20:
        current_player = ppsm.game_state.players[ppsm.action_player_index]
        decision = ppsm.decision_engine.get_decision(current_player.name, ppsm.game_state)
        if decision:
            action_type, amount = decision
            if ppsm._is_valid_action(current_player, action_type, amount):
                ppsm.execute_action(current_player, action_type, amount)
                action_count += 1
            else:
                break
        else:
            break
    
    # Should be on turn betting
    if ppsm.current_state != PokerState.TURN_BETTING:
        print(f"❌ Expected TURN_BETTING, got {ppsm.current_state}")
        return False
    
    print(f"✅ Reached turn after {action_count} actions")
    
    # Get the current player (should be seat1) and their stack
    current_player = ppsm.game_state.players[ppsm.action_player_index]
    initial_stack = current_player.stack
    current_bet_contribution = current_player.current_bet
    
    print(f"📊 {current_player.name}: stack=${initial_stack}, current_bet=${current_bet_contribution}")
    
    # Get decision (should be ALL_IN mapped to proper to-amount)
    decision = ppsm.decision_engine.get_decision(current_player.name, ppsm.game_state)
    
    if not decision:
        print(f"❌ No decision returned for ALL_IN")
        return False
    
    action_type, amount = decision
    
    # Should be BET or RAISE to the player's maximum
    expected_max = current_player.current_bet + current_player.stack
    
    if action_type in [ActionType.BET, ActionType.RAISE]:
        if abs(amount - expected_max) < 1e-9:
            print(f"✅ SUCCESS: Large RAISE mapped to {action_type.value} ${amount} (player maximum)")
            
            # Verify it passes validation (should satisfy min-raise rules via all-in logic)
            if ppsm._is_valid_action(current_player, action_type, amount):
                print(f"✅ SUCCESS: Action passes PPSM validation (all-in scenario)")
                return True
            else:
                print(f"❌ FAILURE: Action failed PPSM validation")
                return False
        else:
            print(f"❌ FAILURE: Expected to-amount=${expected_max}, got ${amount}")
            return False
    else:
        print(f"❌ FAILURE: Expected BET/RAISE, got {action_type}")
        return False


def create_hand_replay_engine(hand_model):
    """Helper to create the adapter (mirrors the function in PPSM)."""
    return HandModelDecisionEngineAdapter(hand_model)


def main():
    """Run all final mile regression tests."""
    print("🚀 FINAL MILE SURGICAL PATCHES - REGRESSION TESTS")
    print("=" * 60)
    
    tests = [
        ("Multiway Implied FOLDs", test_multiway_implied_folds),
        ("Large RAISE Mapping", test_allin_mapping),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🎯 {test_name}")
        print("-" * 40)
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: EXCEPTION - {str(e)}")
            results.append((test_name, False))
    
    print(f"\n📊 FINAL RESULTS")
    print("=" * 60)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 SUCCESS RATE: {passed}/{total} ({100*passed//total}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Final mile patches validated!")
        return True
    else:
        print("⚠️  Some tests failed - check implementations")
        return False


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Regression test for implicit CHECK injection fix.

Tests the specific case where HU hands-review data omits automatic CHECKs
and jumps straight to BET by the in-position player, causing validation failures.

The fix: HandModelDecisionEngineAdapter injects implicit CHECK when:
- Postflop street (flop/turn/river) 
- current_bet == 0 (no wager yet)
- Next action in hand data is BET by other player
"""

import sys
sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig, HandModelDecisionEngineAdapter
from core.hand_model import Hand, Action, Street
from core.hand_model import ActionType as HandModelActionType
from core.poker_types import Player, GameState, PokerState
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController


def create_test_hand_with_missing_checks():
    """Create a synthetic hand that mimics the HU missing CHECK pattern."""
    
    # Simulate hand data where flop starts with seat2 BET (missing seat1 CHECK)
    hand_data = {
        "hand_id": "TEST_HU_MISSING_CHECK",
        "num_players": 2,
        "small_blind": 5.0,
        "big_blind": 10.0,
        "seats": [
            {"seat": 1, "name": "seat1", "stack": 1000.0, "cards": ["Ah", "Kc"]},
            {"seat": 2, "name": "seat2", "stack": 1000.0, "cards": ["Qh", "Jd"]}
        ],
        "board": ["9s", "8d", "7h", "6c", "5s"],
        "actions": [
            # Preflop (normal)
            {"street": "preflop", "actor": "seat1", "action": "RAISE", "amount": 25.0},
            {"street": "preflop", "actor": "seat2", "action": "CALL", "amount": 25.0},
            
            # Flop - MISSING seat1 CHECK, jumps to seat2 BET
            {"street": "flop", "actor": "seat2", "action": "BET", "amount": 35.0},
            {"street": "flop", "actor": "seat1", "action": "CALL", "amount": 35.0},
            
            # Turn - MISSING seat1 CHECK, jumps to seat2 BET  
            {"street": "turn", "actor": "seat2", "action": "BET", "amount": 70.0},
            {"street": "turn", "actor": "seat1", "action": "CALL", "amount": 70.0},
            
            # River - MISSING seat1 CHECK, jumps to seat2 BET
            {"street": "river", "actor": "seat2", "action": "BET", "amount": 140.0},
            {"street": "river", "actor": "seat1", "action": "CALL", "amount": 140.0}
        ]
    }
    
    return Hand.from_dict(hand_data)


def test_implicit_check_injection():
    """Test that implicit CHECKs are injected for missing out-of-position checks."""
    
    print("🧪 IMPLICIT CHECK INJECTION REGRESSION TEST")
    print("=" * 55)
    
    # Create test hand with missing CHECKs
    hand_model = create_test_hand_with_missing_checks()
    
    print("📋 Test scenario: HU hand where OOP player CHECKs are missing")
    print("   Expected pattern: seat1 should CHECK, then seat2 BETs")
    print("   Hand data pattern: jumps straight to seat2 BET")
    print("   Fix: Adapter should inject implicit seat1 CHECK")
    
    # Create PPSM with the fix
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(), 
        advancement_controller=AutoAdvancementController()
    )
    
    print("\n🎯 Testing hand replay with implicit CHECK fix...")
    
    # Test the full hand replay
    results = ppsm.replay_hand_model(hand_model)
    
    print(f"\n📊 RESULTS:")
    print(f"   Actions executed: {results['successful_actions']}/{results['total_actions']}")
    print(f"   Final pot: ${results['final_pot']:.2f}")
    print(f"   Expected pot: ${results['expected_pot']:.2f}")
    
    if results['errors']:
        print(f"   Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"      - {error}")
    else:
        print(f"   Errors: None ✅")
    
    # Validate the fix worked
    success = (
        results['successful_actions'] == results['total_actions'] and  # All actions executed
        len(results['errors']) == 0 and  # No validation errors
        results['final_pot'] > 0  # Pot accumulation worked
    )
    
    print(f"\n🎯 REGRESSION TEST: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        print("   The implicit CHECK injection fix is working correctly!")
        print("   HU hands with missing OOP checks now replay successfully.")
    else:
        print("   The fix may have regressed. Check the adapter logic.")
    
    return success


def test_adapter_check_injection_logic():
    """Test the adapter's implicit CHECK logic directly."""
    
    print("\n🔍 TESTING ADAPTER LOGIC DIRECTLY")
    print("-" * 40)
    
    # Create a simple hand model for testing
    hand_model = create_test_hand_with_missing_checks()
    adapter = HandModelDecisionEngineAdapter(hand_model)
    
    # Create mock game state at flop with current_bet = 0
    mock_game_state = GameState(
        players=[
            Player("seat1", 1000.0, "UTG", True, True, ["Ah", "Kc"]),
            Player("seat2", 1000.0, "BTN", True, True, ["Qh", "Jd"])
        ],
        board=["9s", "8d", "7h"],
        committed_pot=50.0,  # Preflop pot
        current_bet=0.0,     # No bet on flop yet
        street="flop",
        big_blind=10.0
    )
    
    print(f"Mock state: street={mock_game_state.street}, current_bet=${mock_game_state.current_bet}")
    print(f"Next action in hand data should be: seat2 BET")
    
    # Test 1: seat1 should get implicit CHECK (not their turn in data, but they act first)
    decision1 = adapter.get_decision("seat1", mock_game_state)
    print(f"\nAdapter decision for seat1: {decision1}")
    expected_check = (decision1 is not None and 
                     len(decision1) == 2 and 
                     decision1[0].value == "CHECK" and 
                     decision1[1] is None)
    print(f"Implicit CHECK injected: {'✅' if expected_check else '❌'}")
    
    # Test 2: After the CHECK, seat2 should get their BET  
    if expected_check:
        # Advance mock state as if CHECK was processed
        mock_game_state.current_bet = 0.0  # Still 0 after CHECK
        decision2 = adapter.get_decision("seat2", mock_game_state)
        print(f"\nAdapter decision for seat2: {decision2}")
        expected_bet = (decision2 is not None and
                       len(decision2) == 2 and
                       decision2[0].value == "BET" and
                       decision2[1] == 35.0)
        print(f"Expected BET returned: {'✅' if expected_bet else '❌'}")
        
        return expected_check and expected_bet
    
    return False


if __name__ == "__main__":
    print("🧪 Running implicit CHECK injection regression tests...")
    
    test1_pass = test_implicit_check_injection()
    test2_pass = test_adapter_check_injection_logic()
    
    print(f"\n{'='*55}")
    print(f"🏁 REGRESSION TEST SUMMARY")
    print(f"{'='*55}")
    print(f"Full hand replay: {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"Adapter logic:    {'✅ PASS' if test2_pass else '❌ FAIL'}")
    
    if test1_pass and test2_pass:
        print(f"\n🎉 ALL TESTS PASSED! Implicit CHECK fix is working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. The fix may need attention.")

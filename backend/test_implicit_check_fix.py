#!/usr/bin/env python3
"""
Test the implicit CHECK fix specifically.
"""

import sys
import json
sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.hand_model import Hand
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController


def test_implicit_check_fix():
    """Test that implicit CHECK injection works for HU postflop scenarios."""
    
    print("🔧 TESTING IMPLICIT CHECK INJECTION FIX")
    print("=" * 50)
    
    # Load a specific HC hand that should have the issue
    with open('data/legendary_hands_normalized.json') as f:
        data = json.load(f)
    
    # Test HC001 (hand 10 in 0-indexed array)
    hc_hand = data['hands'][10]
    
    print("🎯 Testing HC001 (the problematic river BET/CALL case)")
    print(f"Hand ID: {hc_hand.get('hand_id', 'Unknown')}")
    
    # Parse hand
    hand_model = Hand.from_dict(hc_hand)
    all_actions = hand_model.get_all_actions()
    
    print(f"\n📋 Hand Model Actions ({len(all_actions)} total):")
    for i, action in enumerate(all_actions):
        street = action.street.value if hasattr(action.street, 'value') else str(action.street)
        print(f"  {i}: {action.actor_uid} {action.action.value} {getattr(action, 'amount', 0)} ({street})")
    
    # Create PPSM with our fix
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    print(f"\n🎮 REPLAYING WITH IMPLICIT CHECK FIX:")
    
    # Test the replay
    results = ppsm.replay_hand_model(hand_model)
    
    print(f"\n📊 RESULTS:")
    print(f"   Total actions: {results['total_actions']}")
    print(f"   Successful: {results['successful_actions']}")
    print(f"   Failed: {results['failed_actions']}")
    print(f"   Final pot: ${results['final_pot']}")
    print(f"   Expected: ${results['expected_pot']}")
    
    if results['errors']:
        print(f"   Errors:")
        for error in results['errors']:
            print(f"      - {error}")
    
    print(f"\n🎯 SUCCESS METRICS:")
    success_rate = results['successful_actions'] / results['total_actions'] * 100 if results['total_actions'] > 0 else 0
    print(f"   Action success: {success_rate:.1f}% ({results['successful_actions']}/{results['total_actions']})")
    
    pot_diff = abs(results['final_pot'] - results['expected_pot'])
    pot_match = pot_diff < 5.0  # Allow small variance
    print(f"   Pot match: {'✅' if pot_match else '❌'} (diff: ${pot_diff:.2f})")
    
    # Check if we resolved the specific issues
    has_bet_error = any('Invalid action: BET' in error for error in results['errors'])
    has_call_error = any('Invalid action: CALL None' in error for error in results['errors'])
    
    print(f"\n🔍 SPECIFIC ISSUE RESOLUTION:")
    print(f"   BET errors: {'❌ Still present' if has_bet_error else '✅ Resolved'}")
    print(f"   CALL errors: {'❌ Still present' if has_call_error else '✅ Resolved'}")
    
    if results['successful_actions'] == results['total_actions'] and pot_match:
        print(f"\n🎉 COMPLETE SUCCESS! All issues resolved.")
    elif results['successful_actions'] > 6:  # Was 6/8 before fix
        print(f"\n✅ MAJOR IMPROVEMENT! Significantly more actions successful.")
    else:
        print(f"\n⚠️  Still needs work.")


if __name__ == "__main__":
    test_implicit_check_fix()

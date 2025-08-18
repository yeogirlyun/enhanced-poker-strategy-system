#!/usr/bin/env python3
"""
Test the HC series fix specifically.
"""

import sys
import json
sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.hand_model import Hand
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController


def test_hc_series():
    """Test HC series with detailed debugging."""
    
    # Load HC001 hand
    with open('data/legendary_hands_normalized.json') as f:
        data = json.load(f)
    hc_hand = data['hands'][10]
    
    print("🔍 TESTING HC001 HAND WITH NEW FIXES")
    print("=" * 50)
    
    # Parse hand
    hand_model = Hand.from_dict(hc_hand)
    all_actions = hand_model.get_all_actions()
    
    print("📋 Expected Action Sequence:")
    for i, action in enumerate(all_actions):
        print(f"  {i}: {action.actor_uid} {action.action.value} {getattr(action, 'amount', 0)} ({action.street.value})")
    
    print()
    
    # Create PPSM
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    # Test replay
    print("🎯 REPLAYING WITH NEW FIXES:")
    results = ppsm.replay_hand_model(hand_model)
    
    print(f"   Actions: {results['successful_actions']}/{results['total_actions']}")
    print(f"   Final pot: ${results['final_pot']}")
    print(f"   Expected: ${results['expected_pot']}")
    if results['errors']:
        print("   Errors:")
        for error in results['errors']:
            print(f"      {error}")
    
    print()
    
    # Expected vs actual
    if results['successful_actions'] == results['total_actions']:
        print("✅ SUCCESS: All actions executed!")
    else:
        print("❌ PARTIAL: Some actions failed")
        
    if abs(results['final_pot'] - results['expected_pot']) < 0.01:
        print("✅ SUCCESS: Pot calculation correct!")
    else:
        print("❌ FAILED: Pot calculation mismatch")

if __name__ == "__main__":
    test_hc_series()

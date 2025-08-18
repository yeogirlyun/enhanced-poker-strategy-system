#!/usr/bin/env python3
"""
Quick test of enhanced fixes on problematic hands.
"""

import sys
import json
sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.hand_model import Hand
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController


def test_enhanced_fixes():
    """Test the enhanced fixes on first few hands."""
    
    print("🧪 TESTING ENHANCED ADAPTER FIXES")
    print("=" * 40)
    
    # Load test data
    with open('data/legendary_hands_normalized.json') as f:
        data = json.load(f)
    
    # Test first few hands from both series
    test_hands = [
        (0, "BB001 - Known failure case"),
        (1, "BB002 - Another BB series"), 
        (10, "HC001 - Known working case"),
        (11, "HC002 - Another HC series")
    ]
    
    for hand_idx, description in test_hands:
        hand_data = data['hands'][hand_idx]
        hand_id = hand_data.get('hand_id', f'Hand_{hand_idx+1}')
        
        print(f"\n🎯 Testing {hand_id}: {description}")
        
        try:
            # Parse hand
            hand_model = Hand.from_dict(hand_data)
            
            # Create PPSM
            ppsm = PurePokerStateMachine(
                config=GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0),
                deck_provider=StandardDeck(),
                rules_provider=StandardRules(),
                advancement_controller=AutoAdvancementController()
            )
            
            # Test replay
            replay_results = ppsm.replay_hand_model(hand_model)
            
            # Analyze results
            total_actions = replay_results['total_actions']
            successful_actions = replay_results['successful_actions']
            errors = replay_results['errors']
            final_pot = replay_results['final_pot']
            expected_pot = replay_results['expected_pot']
            
            # Check for infinite loop
            has_infinite_loop = any('INFINITE_LOOP_DETECTED' in error for error in errors)
            
            # Success criteria
            success = (
                successful_actions == total_actions and
                not has_infinite_loop and
                len(errors) == 0
            )
            
            if success:
                print(f"   ✅ SUCCESS: {successful_actions}/{total_actions} actions")
                print(f"      Pot: ${final_pot:.2f} (expected ${expected_pot:.2f})")
            else:
                print(f"   ❌ FAILED: {successful_actions}/{total_actions} actions")
                print(f"      Pot: ${final_pot:.2f} (expected ${expected_pot:.2f})")
                if has_infinite_loop:
                    print(f"      🔄 Infinite loop detected")
                if errors:
                    print(f"      Errors ({len(errors)}):")
                    for error in errors[:3]:  # Show first 3 errors
                        print(f"         {error}")
            
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
    
    print(f"\n" + "=" * 40)
    print(f"Ready for full validation test if fixes are working")


if __name__ == "__main__":
    test_enhanced_fixes()

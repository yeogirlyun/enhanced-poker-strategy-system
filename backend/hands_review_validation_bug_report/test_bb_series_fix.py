#!/usr/bin/env python3
"""
Test script for validating BB series fix.
Use this to verify enhanced implicit CHECK injection.
"""

import sys
import json
sys.path.append('..')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.hand_model import Hand
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules
from core.providers.advancement_controllers import AutoAdvancementController


def test_bb_series_fix():
    """Test BB series hands with the enhanced fix."""
    
    print("🧪 TESTING BB SERIES FIX")
    print("=" * 40)
    
    # Load test data
    with open('../data/legendary_hands_normalized.json') as f:
        data = json.load(f)
    
    # Test first few BB hands (indices 0-4 = BB001-BB005)
    bb_hands = data['hands'][:5]
    
    results = {
        'total_hands': len(bb_hands),
        'successful_hands': 0,
        'total_actions': 0,
        'successful_actions': 0,
        'infinite_loops': 0,
        'details': []
    }
    
    for i, hand_data in enumerate(bb_hands):
        hand_id = hand_data.get('hand_id', f'BB{i+1:03d}')
        print(f"\n🎯 Testing {hand_id}")
        
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
            if has_infinite_loop:
                results['infinite_loops'] += 1
            
            # Success criteria
            success = (
                successful_actions == total_actions and  # All actions completed
                not has_infinite_loop and                # No infinite loops
                len(errors) == 0                        # No validation errors
            )
            
            if success:
                results['successful_hands'] += 1
                status = "✅ SUCCESS"
            else:
                status = "❌ FAILED"
            
            results['total_actions'] += total_actions
            results['successful_actions'] += successful_actions
            
            print(f"   {status}: {successful_actions}/{total_actions} actions")
            print(f"   Pot: ${final_pot:.2f} (expected ${expected_pot:.2f})")
            if has_infinite_loop:
                print(f"   ⚠️  Infinite loop detected")
            if errors and not has_infinite_loop:
                print(f"   Errors: {len(errors)}")
                for error in errors[:2]:  # Show first 2 errors
                    print(f"      {error}")
            
            # Store details
            results['details'].append({
                'hand_id': hand_id,
                'success': success,
                'actions': f"{successful_actions}/{total_actions}",
                'pot_match': abs(final_pot - expected_pot) < 5.0,
                'infinite_loop': has_infinite_loop,
                'error_count': len(errors)
            })
            
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            results['details'].append({
                'hand_id': hand_id,
                'success': False,
                'exception': str(e)
            })
    
    # Summary
    print(f"\n" + "=" * 40)
    print(f"📊 BB SERIES TEST RESULTS")
    print(f"=" * 40)
    print(f"Hands: {results['successful_hands']}/{results['total_hands']} successful")
    print(f"Actions: {results['successful_actions']}/{results['total_actions']} successful")
    print(f"Success rate: {results['successful_actions']/results['total_actions']*100:.1f}%")
    print(f"Infinite loops: {results['infinite_loops']}")
    
    # Expected results after fix
    print(f"\n🎯 TARGET AFTER FIX:")
    print(f"✅ Hands: 5/5 successful (100%)")
    print(f"✅ Actions: 40/40 successful (100%)")  # 8 actions per hand
    print(f"✅ Infinite loops: 0")
    
    # Overall assessment
    if results['successful_hands'] == results['total_hands']:
        print(f"\n🎉 BB SERIES FIX: SUCCESSFUL!")
        print(f"All hands now complete successfully.")
    elif results['successful_hands'] > 0:
        print(f"\n✅ BB SERIES FIX: PARTIAL SUCCESS")
        print(f"Some improvement detected, may need refinement.")
    else:
        print(f"\n⚠️  BB SERIES FIX: NEEDS WORK")
        print(f"No improvement detected, fix may not be applied correctly.")
    
    return results


if __name__ == "__main__":
    test_bb_series_fix()

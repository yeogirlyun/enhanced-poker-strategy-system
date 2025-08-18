"""
Isolate Infinite Loop in Hands Review Validation

This script tests each hand individually with strict timeouts to identify
exactly which hand is causing the infinite loop.
"""

import sys
import json
import time
import signal
from pathlib import Path

sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.hand_model import Hand
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules  
from core.providers.advancement_controllers import AutoAdvancementController


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Hand validation timed out")


def load_hands(limit=None):
    """Load hands data."""
    hands_file = Path("data/legendary_hands_normalized.json")
    
    with open(hands_file) as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "hands" in data:
        hands_data = data["hands"]
    else:
        hands_data = data
    
    return hands_data[:limit] if limit else hands_data


def test_single_hand_with_timeout(ppsm, hand_data, hand_index, timeout_seconds=3):
    """Test a single hand with strict timeout."""
    
    hand_id = hand_data.get('id', f'hand_{hand_index}')
    print(f"🔍 Testing Hand {hand_index + 1}: {hand_id}")
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        # Parse hand
        hand_model = Hand.from_dict(hand_data)
        all_actions = hand_model.get_all_actions()
        expected_pot = sum(action.amount for action in all_actions 
                          if hasattr(action, 'amount') and action.amount)
        
        print(f"   Players: {len(hand_model.seats)}, Actions: {len(all_actions)}, Expected: ${expected_pot}")
        
        # Replay hand
        start_time = time.time()
        replay_results = ppsm.replay_hand_model(hand_model)
        elapsed = time.time() - start_time
        
        # Cancel timeout
        signal.alarm(0)
        
        # Extract results
        final_pot = replay_results['final_pot']
        total_actions = replay_results['total_actions']
        successful_actions = replay_results['successful_actions']
        pot_match = replay_results['pot_match']
        
        print(f"   ✅ SUCCESS: {elapsed:.3f}s, Pot ${final_pot} (expected ${expected_pot}), {successful_actions}/{total_actions} actions")
        
        return {
            'hand_id': hand_id,
            'success': True,
            'elapsed': elapsed,
            'final_pot': final_pot,
            'expected_pot': expected_pot,
            'pot_match': pot_match,
            'actions': f"{successful_actions}/{total_actions}"
        }
        
    except TimeoutError:
        signal.alarm(0)
        print(f"   ⏰ TIMEOUT: Hand {hand_id} exceeded {timeout_seconds}s - INFINITE LOOP DETECTED!")
        
        return {
            'hand_id': hand_id,
            'success': False,
            'error': 'TIMEOUT_INFINITE_LOOP',
            'timeout': timeout_seconds,
            'issue': 'Infinite loop detected in hand replay'
        }
        
    except Exception as e:
        signal.alarm(0)
        print(f"   ❌ EXCEPTION: {str(e)}")
        
        return {
            'hand_id': hand_id,
            'success': False,
            'error': 'EXCEPTION',
            'exception': str(e)
        }


def main():
    """Test hands one by one to isolate infinite loop."""
    print("🐛 ISOLATING INFINITE LOOP IN HANDS VALIDATION")
    print("=" * 60)
    
    # Load hands
    hands_data = load_hands(limit=10)  # Test first 10 hands
    print(f"📊 Testing {len(hands_data)} hands individually")
    
    # Create PPSM
    ppsm = PurePokerStateMachine(
        config=GameConfig(num_players=2, small_blind=5.0, big_blind=10.0, starting_stack=1000.0),
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )
    
    # Test results
    results = []
    timeout_hands = []
    
    for i, hand_data in enumerate(hands_data):
        result = test_single_hand_with_timeout(ppsm, hand_data, i, timeout_seconds=3)
        results.append(result)
        
        if result.get('error') == 'TIMEOUT_INFINITE_LOOP':
            timeout_hands.append(result)
            print(f"\n🚨 FOUND PROBLEMATIC HAND: {result['hand_id']}")
            
            # Save detailed info about the problematic hand
            print(f"   Hand details: {json.dumps(hand_data, indent=2)}")
            
            # Stop after first timeout to analyze
            break
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 ISOLATION RESULTS:")
    print(f"   Total tested: {len(results)}")
    print(f"   Successful: {len([r for r in results if r['success']])}")
    print(f"   Timeouts/Loops: {len(timeout_hands)}")
    
    if timeout_hands:
        print(f"\n🚨 INFINITE LOOP HANDS:")
        for hand in timeout_hands:
            print(f"   - {hand['hand_id']}: {hand['issue']}")
    
    # Save results
    output_file = "infinite_loop_isolation_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'total_tested': len(results),
            'results': results,
            'timeout_hands': timeout_hands,
            'summary': f"Found {len(timeout_hands)} hands with infinite loops"
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    if timeout_hands:
        return False  # Found infinite loop
    else:
        return True   # All good


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

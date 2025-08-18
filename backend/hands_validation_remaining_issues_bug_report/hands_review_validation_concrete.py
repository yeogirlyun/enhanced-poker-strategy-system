"""
Hands Review Validation for Concrete PPSM Architecture

This validation tester uses the new concrete PPSM architecture with:
- replay_hand_model() method 
- DecisionEngineProtocol interface
- Proper bet amount translation
- Deterministic deck setup
- Clean pot accounting

This is the ultimate test - validating PPSM against real poker hand data.
"""

import sys
import json
import time
from pathlib import Path

sys.path.append('.')

from core.pure_poker_state_machine import PurePokerStateMachine, GameConfig
from core.hand_model import Hand
from core.providers.deck_providers import StandardDeck
from core.providers.rules_providers import StandardRules  
from core.providers.advancement_controllers import AutoAdvancementController


def load_legendary_hands(limit=20):
    """Load normalized legendary hands data."""
    hands_file = Path("data/legendary_hands_normalized.json")
    
    if not hands_file.exists():
        print(f"❌ Hands file not found: {hands_file}")
        return []
    
    with open(hands_file) as f:
        data = json.load(f)
    
    # Handle both formats: {"hands": [...]} and [...]
    if isinstance(data, dict) and "hands" in data:
        hands_data = data["hands"]
    else:
        hands_data = data
    
    print(f"✅ Loaded {len(hands_data)} hands from {hands_file}")
    return hands_data[:limit] if limit else hands_data


def create_concrete_ppsm():
    """Create PPSM with concrete architecture."""
    config = GameConfig(
        num_players=2,  # Will be updated per hand
        small_blind=5.0,  # Will be updated per hand
        big_blind=10.0,   # Will be updated per hand
        starting_stack=1000.0  # Will be updated per hand
    )
    
    return PurePokerStateMachine(
        config=config,
        deck_provider=StandardDeck(),
        rules_provider=StandardRules(),
        advancement_controller=AutoAdvancementController()
    )


def validate_hands(max_hands=20):
    """Validate PPSM against legendary hands using concrete architecture."""
    
    print("🏆 CONCRETE PPSM HANDS REVIEW VALIDATION")
    print("=" * 70)
    print("🎯 Testing concrete PPSM architecture against real poker data")  
    print("🃏 Using new replay_hand_model() interface with DecisionEngineProtocol")
    print("=" * 70)
    
    # Load hands data
    hands_data = load_legendary_hands(limit=max_hands)
    if not hands_data:
        return False
    
    print(f"📊 Testing {len(hands_data)} hands with concrete architecture\n")
    
    # Create PPSM
    ppsm = create_concrete_ppsm()
    
    # Validation results
    results = {
        'total_hands': len(hands_data),
        'successful_hands': 0,
        'failed_hands': 0,
        'total_actions': 0,
        'successful_actions': 0,
        'hands': []
    }
    
    start_time = time.time()
    
    for hand_index, hand_data in enumerate(hands_data):
        hand_id = hand_data.get('id', f'hand_{hand_index}')
        print(f"🎲 Testing Hand {hand_index + 1}: {hand_id}")
        
        try:
            # Parse hand using Hand model
            hand_model = Hand.from_dict(hand_data)
            
            # Get all actions from the hand model
            all_actions = hand_model.get_all_actions()
            print(f"   Players: {len(hand_model.seats)}, Actions: {len(all_actions)}")
            
            # Calculate expected final pot from hand model
            expected_pot = sum(action.amount for action in all_actions 
                             if hasattr(action, 'amount') and action.amount)
            print(f"   Expected final pot: ${expected_pot}")
            
            # Use new concrete interface to replay the hand
            replay_results = ppsm.replay_hand_model(hand_model)
            
            # Extract results
            final_pot = replay_results['final_pot']
            total_actions = replay_results['total_actions']
            successful_actions = replay_results['successful_actions']
            failed_actions = replay_results['failed_actions']
            pot_match = replay_results['pot_match']
            errors = replay_results.get('errors', [])
            
            # Determine success
            success = (
                pot_match and
                failed_actions == 0 and
                total_actions > 0
            )
            
            if success:
                print(f"   ✅ SUCCESS: Pot ${final_pot:.2f} (expected ${expected_pot}), {successful_actions}/{total_actions} actions")
                results['successful_hands'] += 1
            else:
                print(f"   ❌ FAILED: Pot ${final_pot:.2f} (expected ${expected_pot}), {successful_actions}/{total_actions} actions")
                if errors:
                    for error in errors[:3]:  # Show first 3 errors
                        print(f"      Error: {error}")
                results['failed_hands'] += 1
            
            # Update totals
            results['total_actions'] += total_actions
            results['successful_actions'] += successful_actions
            
            # Store detailed result
            hand_result = {
                'hand_id': hand_id,
                'hand_index': hand_index + 1,
                'success': success,
                'final_pot': final_pot,
                'expected_pot': expected_pot,
                'pot_match': pot_match,
                'total_actions': total_actions,
                'successful_actions': successful_actions,
                'failed_actions': failed_actions,
                'errors': errors[:5]  # Store first 5 errors
            }
            results['hands'].append(hand_result)
            
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
            results['failed_hands'] += 1
            
            error_result = {
                'hand_id': hand_id,
                'hand_index': hand_index + 1,
                'success': False,
                'exception': str(e),
                'final_pot': 0,
                'expected_pot': expected_pot if 'expected_pot' in locals() else 0,
                'pot_match': False,
                'total_actions': 0,
                'successful_actions': 0,
                'failed_actions': 0,
                'errors': [str(e)]
            }
            results['hands'].append(error_result)
        
        print()  # Blank line between hands
    
    # Calculate final metrics
    end_time = time.time()
    duration = end_time - start_time
    hands_per_sec = len(hands_data) / duration if duration > 0 else 0
    success_rate = (results['successful_hands'] / results['total_hands'] * 100) if results['total_hands'] > 0 else 0
    action_success_rate = (results['successful_actions'] / results['total_actions'] * 100) if results['total_actions'] > 0 else 0
    
    # Print summary
    print("=" * 70)
    print("🏆 CONCRETE PPSM VALIDATION RESULTS")
    print("=" * 70)
    print(f"📊 Hands tested: {results['total_hands']}")
    print(f"✅ Successful: {results['successful_hands']} ({success_rate:.1f}%)")
    print(f"❌ Failed: {results['failed_hands']}")
    print(f"⚡ Actions: {results['successful_actions']}/{results['total_actions']} successful ({action_success_rate:.1f}%)")
    print(f"⏱️  Time: {duration:.1f}s ({hands_per_sec:.1f} hands/sec)")
    print()
    
    # Final verdict
    if success_rate >= 90 and action_success_rate >= 95:
        print("🎯 FINAL VERDICT:")
        print("🟢 PRODUCTION READY - Concrete PPSM architecture validated!")
        verdict = "PRODUCTION_READY"
    elif success_rate >= 75:
        print("🎯 FINAL VERDICT:")
        print("🟡 MOSTLY READY - Minor issues to address")
        verdict = "MOSTLY_READY"  
    else:
        print("🎯 FINAL VERDICT:")
        print("🔴 NOT READY - Major problems detected")
        verdict = "NOT_READY"
    
    # Save results
    results.update({
        'duration': duration,
        'hands_per_sec': hands_per_sec,
        'success_rate': success_rate,
        'action_success_rate': action_success_rate,
        'verdict': verdict,
        'architecture': 'concrete_ppsm_with_replay_hand_model'
    })
    
    output_file = Path("concrete_ppsm_validation_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to: {output_file}")
    return success_rate >= 75


if __name__ == "__main__":
    success = validate_hands(max_hands=20)
    sys.exit(0 if success else 1)

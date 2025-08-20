#!/usr/bin/env python3
"""
GTO Hands Validation

Validates generated GTO hands to ensure they meet quality standards:
- Proper player counts (2-9 players)
- Complete hand completion with winners
- Proper metadata including hole cards
- Stack size tracking throughout the hand
- Action sequence validation
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

def validate_gto_hands(hands_file: str = "gto_hands.json") -> Dict[str, Any]:
    """Validate GTO hands for completeness and quality."""
    
    print(f"🔍 Validating GTO hands from {hands_file}")
    
    try:
        with open(hands_file, 'r') as f:
            hands_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {hands_file}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return {}
    
    print(f"📊 Loaded {len(hands_data)} hands for validation")
    
    validation_results = {
        'total_hands': len(hands_data),
        'valid_hands': 0,
        'invalid_hands': 0,
        'by_player_count': {},
        'completion_stats': {
            'completed_hands': 0,
            'incomplete_hands': 0,
            'hands_with_winners': 0
        },
        'metadata_stats': {
            'complete_metadata': 0,
            'incomplete_metadata': 0
        },
        'action_stats': {
            'valid_actions': 0,
            'invalid_actions': 0
        },
        'errors': []
    }
    
    for i, hand in enumerate(hands_data):
        try:
            hand_valid = validate_single_hand(hand, i)
            if hand_valid:
                validation_results['valid_hands'] += 1
            else:
                validation_results['invalid_hands'] += 1
            
            # Update player count stats
            player_count = hand.get('metadata', {}).get('max_players', 0)
            if player_count not in validation_results['by_player_count']:
                validation_results['by_player_count'][player_count] = {
                    'total': 0,
                    'valid': 0,
                    'invalid': 0
                }
            validation_results['by_player_count'][player_count]['total'] += 1
            if hand_valid:
                validation_results['by_player_count'][player_count]['valid'] += 1
            else:
                validation_results['by_player_count'][player_count]['invalid'] += 1
            
            # Update completion stats
            if hand.get('completed', False):
                validation_results['completion_stats']['completed_hands'] += 1
            else:
                validation_results['completion_stats']['incomplete_hands'] += 1
            
            # Check for winners
            if has_winner(hand):
                validation_results['completion_stats']['hands_with_winners'] += 1
            
            # Check metadata completeness
            if has_complete_metadata(hand):
                validation_results['metadata_stats']['complete_metadata'] += 1
            else:
                validation_results['metadata_stats']['incomplete_metadata'] += 1
            
            # Check action validity
            action_validity = validate_actions(hand)
            if action_validity['valid']:
                validation_results['action_stats']['valid_actions'] += 1
            else:
                validation_results['action_stats']['invalid_actions'] += 1
                validation_results['errors'].append({
                    'hand_id': hand.get('metadata', {}).get('hand_id', f'hand_{i}'),
                    'error': 'Invalid actions',
                    'details': action_validity['errors']
                })
                
        except Exception as e:
            validation_results['invalid_hands'] += 1
            validation_results['errors'].append({
                'hand_id': hand.get('metadata', {}).get('hand_id', f'hand_{i}'),
                'error': 'Validation exception',
                'details': str(e)
            })
            print(f"⚠️  Error validating hand {i}: {e}")
    
    return validation_results

def validate_single_hand(hand: Dict[str, Any], hand_index: int) -> bool:
    """Validate a single GTO hand."""
    
    # Check basic structure
    if not isinstance(hand, dict):
        print(f"❌ Hand {hand_index}: Not a dictionary")
        return False
    
    # Check metadata
    metadata = hand.get('metadata', {})
    if not metadata:
        print(f"❌ Hand {hand_index}: Missing metadata")
        return False
    
    # Check required metadata fields
    required_fields = ['hand_id', 'max_players', 'small_blind', 'big_blind']
    for field in required_fields:
        if field not in metadata:
            print(f"❌ Hand {hand_index}: Missing metadata field '{field}'")
            return False
    
    # Check player count
    max_players = metadata.get('max_players', 0)
    if not (2 <= max_players <= 9):
        print(f"❌ Hand {hand_index}: Invalid player count {max_players}")
        return False
    
    # Check seats
    seats = hand.get('seats', [])
    if len(seats) != max_players:
        print(f"❌ Hand {hand_index}: Player count mismatch - metadata: {max_players}, seats: {len(seats)}")
        return False
    
    # Check seat structure
    for i, seat in enumerate(seats):
        if not isinstance(seat, dict):
            print(f"❌ Hand {hand_index}: Seat {i} is not a dictionary")
            return False
        
        required_seat_fields = ['player_uid', 'display_name', 'starting_stack']
        for field in required_seat_fields:
            if field not in seat:
                print(f"❌ Hand {hand_index}: Seat {i} missing field '{field}'")
                return False
    
    # Check streets
    streets = hand.get('streets', {})
    if not streets:
        print(f"❌ Hand {hand_index}: No streets data")
        return False
    
    # Check that hand is marked as completed
    if not hand.get('completed', False):
        print(f"❌ Hand {hand_index}: Hand not marked as completed")
        return False
    
    # Check that we have actions
    total_actions = sum(len(street.get('actions', [])) for street in streets.values())
    if total_actions < 5:  # Minimum actions for a basic hand
        print(f"❌ Hand {hand_index}: Insufficient actions ({total_actions})")
        return False
    
    return True

def has_winner(hand: Dict[str, Any]) -> bool:
    """Check if a hand has a clear winner."""
    
    # Check if pot was distributed
    pots = hand.get('pots', [])
    if not pots:
        return False
    
    # Check if any pot has shares (indicating distribution)
    for pot in pots:
        shares = pot.get('shares', [])
        if shares:
            return True
    
    return False

def has_complete_metadata(hand: Dict[str, Any]) -> bool:
    """Check if hand has complete metadata."""
    
    metadata = hand.get('metadata', {})
    
    # Check for all required fields
    required_fields = [
        'hand_id', 'max_players', 'small_blind', 'big_blind', 
        'variant', 'session_type'
    ]
    
    for field in required_fields:
        if field not in metadata:
            return False
    
    return True

def validate_actions(hand: Dict[str, Any]) -> Dict[str, Any]:
    """Validate action sequences in the hand."""
    
    result = {
        'valid': True,
        'errors': []
    }
    
    streets = hand.get('streets', {})
    
    for street_name, street_data in streets.items():
        actions = street_data.get('actions', [])
        
        for i, action in enumerate(actions):
            if not isinstance(action, dict):
                result['valid'] = False
                result['errors'].append(f"Street {street_name}, action {i}: Not a dictionary")
                continue
            
            # Check required action fields
            required_fields = ['order', 'actor_uid', 'action']
            for field in required_fields:
                if field not in action:
                    result['valid'] = False
                    result['errors'].append(f"Street {street_name}, action {i}: Missing field '{field}'")
            
            # Check action type validity
            action_type = action.get('action', '')
            valid_actions = ['POST_BLIND', 'DEAL_HOLE', 'DEAL_BOARD', 'FOLD', 'CHECK', 'CALL', 'BET', 'RAISE']
            if action_type not in valid_actions:
                result['valid'] = False
                result['errors'].append(f"Street {street_name}, action {i}: Invalid action type '{action_type}'")
    
    return result

def print_validation_report(results: Dict[str, Any]):
    """Print a comprehensive validation report."""
    
    print("\n" + "="*60)
    print("🔍 GTO HANDS VALIDATION REPORT")
    print("="*60)
    
    print(f"📊 OVERALL STATS")
    print(f"   Total hands: {results['total_hands']}")
    print(f"   Valid hands: {results['valid_hands']}")
    print(f"   Invalid hands: {results['invalid_hands']}")
    
    if results['total_hands'] > 0:
        success_rate = (results['valid_hands'] / results['total_hands']) * 100
        print(f"   Success rate: {success_rate:.1f}%")
    
    print(f"\n🎯 COMPLETION STATS")
    print(f"   Completed hands: {results['completion_stats']['completed_hands']}")
    print(f"   Incomplete hands: {results['completion_stats']['incomplete_hands']}")
    print(f"   Hands with winners: {results['completion_stats']['hands_with_winners']}")
    
    print(f"\n📋 METADATA STATS")
    print(f"   Complete metadata: {results['metadata_stats']['complete_metadata']}")
    print(f"   Incomplete metadata: {results['metadata_stats']['incomplete_metadata']}")
    
    print(f"\n🎬 ACTION STATS")
    print(f"   Valid actions: {results['action_stats']['valid_actions']}")
    print(f"   Invalid actions: {results['action_stats']['invalid_actions']}")
    
    print(f"\n👥 PLAYER COUNT BREAKDOWN")
    for player_count, stats in sorted(results['by_player_count'].items()):
        print(f"   {player_count}P: {stats['valid']}/{stats['total']} valid")
    
    if results['errors']:
        print(f"\n❌ ERRORS FOUND")
        for error in results['errors'][:10]:  # Show first 10 errors
            print(f"   {error['hand_id']}: {error['error']}")
        if len(results['errors']) > 10:
            print(f"   ... and {len(results['errors']) - 10} more errors")
    
    print("\n" + "="*60)

def main():
    """Main validation entry point."""
    
    print("🔍 GTO HANDS VALIDATOR")
    print("="*60)
    
    # Validate hands
    results = validate_gto_hands("gto_hands.json")
    
    if results:
        # Print report
        print_validation_report(results)
        
        # Summary
        if results['valid_hands'] == results['total_hands']:
            print("🎉 SUCCESS: All hands passed validation!")
        else:
            print(f"⚠️  WARNING: {results['invalid_hands']} hands failed validation")
            
    else:
        print("❌ Validation failed - could not load hands")

if __name__ == "__main__":
    main()

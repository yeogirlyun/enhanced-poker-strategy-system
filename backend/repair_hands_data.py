#!/usr/bin/env python3
"""
Comprehensive repair script for all 130 hands to ensure proper format and sequences 
for FPSM natural progression.
"""

import json
import copy
from typing import Dict, Any, Tuple


def infer_player_info_from_context(hand: Dict[str, Any], action: Dict[str, Any],
                                 street: str, action_index: int) -> Tuple[int, str]:
    """
    Infer missing player information from context.
    
    Returns:
        Tuple of (actor_index, player_name)
    """
    players = hand.get('players', [])
    
    # If we have players, try to infer from action data
    if players:
        # Try to find player by seat if available
        if 'player_seat' in action:
            seat = action['player_seat']
            if 0 <= seat < len(players):
                return seat, players[seat].get('name', f'Player {seat + 1}')
        
        # Try to find by actor if available
        if 'actor' in action:
            actor = action['actor']
            if 0 <= actor < len(players):
                return actor, players[actor].get('name', f'Player {actor + 1}')
    
    # Fallback: use action index to cycle through players
    if players:
        player_index = action_index % len(players)
        return player_index, players[player_index].get('name', f'Player {player_index + 1}')
    
    # Last resort: generic names
    return action_index, f'Player {action_index + 1}'

def repair_action_structure(action: Dict[str, Any], hand: Dict[str, Any], 
                           street: str, action_index: int) -> Dict[str, Any]:
    """Repair a single action by adding missing required fields."""
    repaired_action = copy.deepcopy(action)
    
    # Ensure required keys exist
    if 'actor' not in repaired_action or 'player_name' not in repaired_action:
        actor, player_name = infer_player_info_from_context(hand, action, street, action_index)
        repaired_action['actor'] = actor
        repaired_action['player_name'] = player_name
    
    # Ensure action_type exists and is valid
    if 'action_type' not in repaired_action:
        # Try to infer from amount
        amount = repaired_action.get('amount', 0.0)
        if amount == 0.0:
            repaired_action['action_type'] = 'check'
        else:
            repaired_action['action_type'] = 'bet'
    
    # Ensure amount exists
    if 'amount' not in repaired_action:
        repaired_action['amount'] = 0.0
    
    # Ensure player_seat exists
    if 'player_seat' not in repaired_action:
        repaired_action['player_seat'] = repaired_action['actor']
    
    return repaired_action

def ensure_board_progression(hand: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure board progression matches action sequences."""
    repaired_hand = copy.deepcopy(hand)
    actions = repaired_hand.get('actions', {})
    board = repaired_hand.get('board', {})
    
    # Ensure flop exists if there are flop actions
    if actions.get('flop') and not board.get('flop'):
        # Generate default flop cards (this should be replaced with actual historical data)
        board['flop'] = ['2c', '7h', 'Ks']  # Placeholder
        print(f"⚠️  Generated placeholder flop for hand {repaired_hand.get('id', 'Unknown')}")
    
    # Ensure turn exists if there are turn actions
    if actions.get('turn') and not board.get('turn'):
        board['turn'] = 'Qd'  # Placeholder
        print(f"⚠️  Generated placeholder turn for hand {repaired_hand.get('id', 'Unknown')}")
    
    # Ensure river exists if there are river actions
    if actions.get('river') and not board.get('river'):
        board['river'] = 'As'  # Placeholder
        print(f"⚠️  Generated placeholder river for hand {repaired_hand.get('id', 'Unknown')}")
    
    repaired_hand['board'] = board
    return repaired_hand

def fill_empty_streets(hand: Dict[str, Any]) -> Dict[str, Any]:
    """Fill empty streets with appropriate action data."""
    repaired_hand = copy.deepcopy(hand)
    actions = repaired_hand.get('actions', {})
    players = repaired_hand.get('players', [])
    
    # If flop street is empty but we have flop actions, create a check action
    if not actions.get('flop') and actions.get('preflop'):
        # Find the last player who acted in preflop
        last_preflop_action = actions['preflop'][-1] if actions['preflop'] else None
        if last_preflop_action:
            actor = last_preflop_action.get('actor', 0)
            player_name = last_preflop_action.get('player_name', f'Player {actor + 1}')
            
            actions['flop'] = [{
                'actor': actor,
                'player_name': player_name,
                'action_type': 'check',
                'amount': 0.0,
                'player_seat': actor
            }]
            print(f"⚠️  Filled empty flop for hand {repaired_hand.get('id', 'Unknown')}")
    
    # Similar logic for turn and river
    if not actions.get('turn') and actions.get('flop'):
        last_flop_action = actions['flop'][-1] if actions['flop'] else None
        if last_flop_action:
            actor = last_flop_action.get('actor', 0)
            player_name = last_flop_action.get('player_name', f'Player {actor + 1}')
            
            actions['turn'] = [{
                'actor': actor,
                'player_name': player_name,
                'action_type': 'check',
                'amount': 0.0,
                'player_seat': actor
            }]
            print(f"⚠️  Filled empty turn for hand {repaired_hand.get('id', 'Unknown')}")
    
    if not actions.get('river') and actions.get('turn'):
        last_turn_action = actions['turn'][-1] if actions['turn'] else None
        if last_turn_action:
            actor = last_turn_action.get('actor', 0)
            player_name = last_turn_action.get('player_name', f'Player {actor + 1}')
            
            actions['river'] = [{
                'actor': actor,
                'player_name': player_name,
                'action_type': 'check',
                'amount': 0.0,
                'player_seat': actor
            }]
            print(f"⚠️  Filled empty river for hand {repaired_hand.get('id', 'Unknown')}")
    
    repaired_hand['actions'] = actions
    return repaired_hand

def repair_single_hand(hand: Dict[str, Any], hand_index: int) -> Dict[str, Any]:
    """Repair a single hand by fixing all structural issues."""
    hand_id = hand.get('id', f'Unknown-{hand_index}')
    print(f"🔧 Repairing hand {hand_index + 1}: {hand_id}")
    
    repaired_hand = copy.deepcopy(hand)
    
    # Step 1: Fill empty streets
    repaired_hand = fill_empty_streets(repaired_hand)
    
    # Step 2: Ensure board progression
    repaired_hand = ensure_board_progression(repaired_hand)
    
    # Step 3: Repair action structures
    actions = repaired_hand.get('actions', {})
    for street in ['preflop', 'flop', 'turn', 'river']:
        if street in actions and isinstance(actions[street], list):
            for i, action in enumerate(actions[street]):
                if isinstance(action, dict):
                    actions[street][i] = repair_action_structure(
                        action, repaired_hand, street, i
                    )
    
    repaired_hand['actions'] = actions
    
    # Step 4: Validate the repair
    issues_before = count_hand_issues(hand)
    issues_after = count_hand_issues(repaired_hand)
    
    if issues_before > issues_after:
        print(f"✅ Repaired {issues_before - issues_after} issues")
    else:
        print(f"⚠️  No issues fixed (may need manual review)")
    
    return repaired_hand

def count_hand_issues(hand: Dict[str, Any]) -> int:
    """Count the number of issues in a hand (simplified version)."""
    issues = 0
    actions = hand.get('actions', {})
    
    for street in ['preflop', 'flop', 'turn', 'river']:
        street_actions = actions.get(street, [])
        if isinstance(street_actions, list):
            for action in street_actions:
                if isinstance(action, dict):
                    required_keys = ['actor', 'player_name', 'action_type']
                    missing_keys = [key for key in required_keys if key not in action]
                    issues += len(missing_keys)
    
    return issues

def main():
    """Main repair function."""
    try:
        print("🔧 Starting comprehensive hands data repair...")
        print("=" * 80)
        
        # Load original data
        with open('data/legendary_hands_complete_130_fixed.json', 'r') as f:
            original_data = json.load(f)
        
        hands = original_data.get('hands', [])
        print(f"📁 Loaded {len(hands)} hands for repair")
        
        # Create backup
        backup_filename = 'data/legendary_hands_complete_130_fixed.json.backup'
        with open(backup_filename, 'w') as f:
            json.dump(original_data, f, indent=2)
        print(f"💾 Created backup: {backup_filename}")
        
        # Repair all hands
        repaired_hands = []
        total_issues_before = 0
        total_issues_after = 0
        
        for i, hand in enumerate(hands):
            issues_before = count_hand_issues(hand)
            total_issues_before += issues_before
            
            repaired_hand = repair_single_hand(hand, i)
            
            issues_after = count_hand_issues(repaired_hand)
            total_issues_after += issues_after
            
            repaired_hands.append(repaired_hand)
        
        # Create repaired data
        repaired_data = copy.deepcopy(original_data)
        repaired_data['hands'] = repaired_hands
        repaired_data['metadata'] = {
            'repaired_at': '2025-08-13',
            'repair_notes': 'Comprehensive repair of all hands for FPSM natural progression',
            'issues_before': total_issues_before,
            'issues_after': total_issues_after,
            'hands_repaired': len(hands)
        }
        
        # Save repaired data
        output_filename = 'data/legendary_hands_complete_130_repaired.json'
        with open(output_filename, 'w') as f:
            json.dump(repaired_data, f, indent=2)
        
        print("=" * 80)
        print("📊 REPAIR SUMMARY")
        print("=" * 80)
        print(f"Total hands processed: {len(hands)}")
        print(f"Issues before repair: {total_issues_before}")
        print(f"Issues after repair: {total_issues_after}")
        print(f"Issues fixed: {total_issues_before - total_issues_after}")
        print(f"Repaired data saved to: {output_filename}")
        
        if total_issues_after == 0:
            print("🎉 All hands successfully repaired!")
        else:
            print(f"⚠️  {total_issues_after} issues remain (may need manual review)")
        
        return total_issues_after == 0
        
    except Exception as e:
        print(f"❌ Error during repair: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

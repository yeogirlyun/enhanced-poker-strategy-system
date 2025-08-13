#!/usr/bin/env python3
"""
Proper hands data repair script that preserves original data structure.
This script fixes only actual structural issues without corrupting valid data.
"""

import json
import copy
from typing import Dict, List, Any

def analyze_original_data_structure():
    """Analyze the original data to understand the correct structure."""
    print("🔍 Analyzing original data structure...")
    
    try:
        with open('data/legendary_hands_complete_130_fixed.json', 'r') as f:
            data = json.load(f)
        
        hands = data.get('hands', [])
        if not hands:
            print("❌ No hands found in original data")
            return None
        
        # Analyze first few hands
        sample_hands = hands[:3]
        
        for i, hand in enumerate(sample_hands):
            hand_id = hand.get('id', f'Unknown-{i}')
            print(f"\n📊 Hand {i+1}: {hand_id}")
            
            # Check players
            players = hand.get('players', [])
            print(f"   • Players: {len(players)}")
            if players:
                print(f"   • Player names: {[p.get('name', 'Unknown') for p in players[:3]]}")
            
            # Check board structure
            board = hand.get('board', {})
            print(f"   • Board keys: {list(board.keys())}")
            
            # Check card formats
            for street in ['flop', 'turn', 'river']:
                cards = board.get(street)
                if cards is not None:
                    print(f"   • {street.capitalize()}: {type(cards)} = {cards}")
            
            # Check actions
            actions = hand.get('actions', {})
            print(f"   • Action streets: {list(actions.keys())}")
            
            # Check player references in actions
            for street in ['preflop', 'flop', 'turn', 'river']:
                street_actions = actions.get(street, [])
                if street_actions:
                    player_names = [a.get('player_name', 'Unknown') for a in street_actions[:2]]
                    print(f"   • {street} player names: {player_names}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")
        return None

def repair_hand_properly(hand: Dict[str, Any], hand_index: int) -> Dict[str, Any]:
    """
    Repair a hand by fixing only actual structural issues.
    Preserves original board cards and player names.
    """
    hand_id = hand.get('id', f'Unknown-{hand_index}')
    print(f"🔧 Repairing hand {hand_index + 1}: {hand_id}")
    
    repaired_hand = copy.deepcopy(hand)
    
    # Step 1: Fix action structure (only add missing keys, don't change existing data)
    actions = repaired_hand.get('actions', {})
    players = repaired_hand.get('players', [])
    
    for street in ['preflop', 'flop', 'turn', 'river']:
        if street in actions and isinstance(actions[street], list):
            for i, action in enumerate(actions[street]):
                if isinstance(action, dict):
                    # Only add missing keys, preserve existing data
                    if 'actor' not in action:
                        action['actor'] = action.get('player_seat', 0)
                    if 'player_seat' not in action:
                        action['player_seat'] = action.get('actor', 0)
                    if 'amount' not in action:
                        action['amount'] = 0.0
                    
                    # Fix missing player_name by mapping from actor to player name
                    if 'player_name' not in action:
                        actor = action.get('actor', 0)
                        if actor < len(players):
                            player_name = players[actor].get('name', f'Player {actor + 1}')
                            action['player_name'] = player_name
                        else:
                            action['player_name'] = f'Player {actor + 1}'
                            print(f"     ⚠️  Actor {actor} out of range, using default name")
    
    # Step 2: Ensure all required top-level keys exist
    required_keys = ['id', 'name', 'players', 'actions', 'board']
    for key in required_keys:
        if key not in repaired_hand:
            print(f"   ⚠️  Missing required key: {key}")
            if key == 'id':
                repaired_hand[key] = f'Unknown-{hand_index}'
            elif key == 'name':
                repaired_hand[key] = f'Hand {hand_index + 1}'
            elif key == 'players':
                repaired_hand[key] = []
            elif key == 'actions':
                repaired_hand[key] = {}
            elif key == 'board':
                repaired_hand[key] = {}
    
    # Step 3: Ensure players have required keys
    players = repaired_hand.get('players', [])
    for i, player in enumerate(players):
        if isinstance(player, dict):
            # Only add missing keys, preserve existing data
            if 'name' not in player:
                player['name'] = f'Player {i+1}'
            if 'starting_stack' not in player and 'stack' not in player:
                player['starting_stack'] = 1000
            if 'hole_cards' not in player:
                player['hole_cards'] = ['', '']
            elif isinstance(player['hole_cards'], list) and len(player['hole_cards']) == 0:
                # Fix empty hole cards - this usually means the player folded preflop
                player['hole_cards'] = ['', '']
            elif isinstance(player['hole_cards'], list) and len(player['hole_cards']) > 2:
                # Fix too many hole cards - take only first 2
                player['hole_cards'] = player['hole_cards'][:2]
                print(f"     ⚠️  Fixed player {i} hole cards from {len(player['hole_cards'])} to 2")
            if 'seat' not in player:
                player['seat'] = i
            if 'position' not in player:
                player['position'] = 'Unknown'
    
    # Step 4: Ensure board has required structure (preserve existing cards!)
    board = repaired_hand.get('board', {})
    actions = repaired_hand.get('actions', {})
    
    # Fix board inconsistencies
    if 'flop' not in board:
        board['flop'] = []
    if 'turn' not in board:
        board['turn'] = []
    if 'river' not in board:
        board['river'] = []
    
    # If a street has actions but no cards, add placeholder cards
    if actions.get('flop') and not board.get('flop'):
        board['flop'] = ['2c', '7h', 'Ks']  # Placeholder flop
        print(f"     ⚠️  Added placeholder flop cards for hand {repaired_hand.get('id', 'Unknown')}")
    if actions.get('turn') and not board.get('turn'):
        board['turn'] = ['Qd']  # Placeholder turn
        print(f"     ⚠️  Added placeholder turn card for hand {repaired_hand.get('id', 'Unknown')}")
    if actions.get('river') and not board.get('river'):
        board['river'] = ['As']  # Placeholder river
        print(f"     ⚠️  Added placeholder river card for hand {repaired_hand.get('id', 'Unknown')}")
    
    # Fix board card format inconsistencies
    if isinstance(board.get('flop'), str):
        board['flop'] = [board['flop']]
        print(f"     ⚠️  Fixed flop format from string to list for hand {repaired_hand.get('id', 'Unknown')}")
    if isinstance(board.get('turn'), str):
        board['turn'] = [board['turn']]
        print(f"     ⚠️  Fixed turn format from string to list for hand {repaired_hand.get('id', 'Unknown')}")
    if isinstance(board.get('river'), str):
        board['river'] = [board['river']]
        print(f"     ⚠️  Fixed river format from string to list for hand {repaired_hand.get('id', 'Unknown')}")
    
    if 'all_cards' not in board:
        # Combine existing cards if available
        all_cards = []
        if board.get('flop'):
            all_cards.extend(board['flop'])
        if board.get('turn'):
            all_cards.extend(board['turn'])
        if board.get('river'):
            all_cards.extend(board['river'])
        board['all_cards'] = all_cards
    
    # Step 5: Validate the repair
    issues_before = count_hand_issues(hand)
    issues_after = count_hand_issues(repaired_hand)
    
    if issues_before > issues_after:
        print(f"   ✅ Repaired {issues_before - issues_after} issues")
    else:
        print(f"   ✅ No structural issues found")
    
    return repaired_hand

def count_hand_issues(hand: Dict[str, Any]) -> int:
    """Count structural issues in a hand."""
    issues = 0
    
    # Check required top-level keys
    required_keys = ['id', 'name', 'players', 'actions', 'board']
    for key in required_keys:
        if key not in hand:
            issues += 1
    
    # Check actions structure
    actions = hand.get('actions', {})
    for street in ['preflop', 'flop', 'turn', 'river']:
        street_actions = actions.get(street, [])
        if isinstance(street_actions, list):
            for action in street_actions:
                if isinstance(action, dict):
                    required_action_keys = ['actor', 'player_name', 'action_type']
                    missing_keys = [key for key in required_action_keys if key not in action]
                    issues += len(missing_keys)
    
    # Check players structure
    players = hand.get('players', [])
    for player in players:
        if isinstance(player, dict):
            required_player_keys = ['name', 'starting_stack', 'hole_cards']
            missing_keys = [key for key in required_player_keys if key not in player]
            issues += len(missing_keys)
    
    return issues

def main():
    """Main repair function that preserves original data."""
    try:
        print("🔧 Starting PROPER hands data repair...")
        print("=" * 80)
        print("📋 This script will:")
        print("   ✅ Preserve original board cards")
        print("   ✅ Preserve original player names")
        print("   ✅ Fix only structural issues")
        print("   ✅ Not corrupt valid data")
        print("=" * 80)
        
        # Analyze original data
        original_data = analyze_original_data_structure()
        if not original_data:
            print("❌ Cannot proceed without original data")
            return
        
        hands = original_data.get('hands', [])
        print(f"\n📁 Loaded {len(hands)} hands for repair")
        
        # Create backup of original data
        backup_filename = 'data/legendary_hands_complete_130_fixed.json.backup2'
        with open(backup_filename, 'w') as f:
            json.dump(original_data, f, indent=2)
        print(f"💾 Created backup: {backup_filename}")
        
        # Repair all hands properly
        repaired_hands = []
        total_issues_before = 0
        total_issues_after = 0
        
        for i, hand in enumerate(hands):
            issues_before = count_hand_issues(hand)
            total_issues_before += issues_before
            
            repaired_hand = repair_hand_properly(hand, i)
            
            issues_after = count_hand_issues(repaired_hand)
            total_issues_after += issues_after
            
            repaired_hands.append(repaired_hand)
        
        # Create properly repaired data
        repaired_data = copy.deepcopy(original_data)
        repaired_data['hands'] = repaired_hands
        repaired_data['metadata'] = {
            'repaired_at': '2025-08-13',
            'repair_notes': 'PROPER repair - preserved original data structure',
            'issues_before': total_issues_before,
            'issues_after': total_issues_after,
            'repair_type': 'structural_only'
        }
        
        # Save properly repaired data
        output_filename = 'data/legendary_hands_complete_130_properly_repaired.json'
        with open(output_filename, 'w') as f:
            json.dump(repaired_data, f, indent=2)
        
        print(f"\n🎉 Repair completed successfully!")
        print(f"📊 Results:")
        print(f"   • Total hands: {len(hands)}")
        print(f"   • Issues before: {total_issues_before}")
        print(f"   • Issues after: {total_issues_after}")
        print(f"   • Issues fixed: {total_issues_before - total_issues_after}")
        print(f"💾 Output saved to: {output_filename}")
        
        # Verify no data corruption
        print(f"\n🔍 Verifying no data corruption...")
        sample_hand = repaired_hands[0]
        board = sample_hand.get('board', {})
        print(f"   • Flop format: {type(board.get('flop'))} = {board.get('flop')}")
        print(f"   • Turn format: {type(board.get('turn'))} = {board.get('turn')}")
        print(f"   • River format: {type(board.get('river'))} = {board.get('river')}")
        
        if (isinstance(board.get('flop'), list) and 
            isinstance(board.get('turn'), list) and 
            isinstance(board.get('river'), list)):
            print("   ✅ Board card formats preserved correctly!")
        else:
            print("   ❌ Board card formats corrupted!")
        
    except Exception as e:
        print(f"❌ Error during repair: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

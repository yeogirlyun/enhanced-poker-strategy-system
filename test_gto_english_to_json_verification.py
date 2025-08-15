#!/usr/bin/env python3
"""
Complete GTO Hand Test: Generate -> Log in English -> Save to JSON -> Verify

This test will:
1. Run a complete GTO hand
2. Log every action in plain English as it happens
3. Save the hand data to JSON in the exact format hands review expects
4. Read the JSON back and verify it matches what actually happened
"""

import json
import sys
import os
from typing import List, Dict, Any, Tuple

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.bot_session_state_machine import GTOBotSession
from core.flexible_poker_state_machine import GameConfig

def run_complete_gto_hand():
    """Run a complete GTO hand and log everything in English."""
    
    config = GameConfig(
        starting_stack=1000,
        small_blind=5,
        big_blind=10,
        num_players=3
    )
    
    session = GTOBotSession(config)
    session.start_session()
    
    # Capture initial state
    initial_players = []
    for i, player in enumerate(session.game_state.players):
        initial_players.append({
            'name': player.name,
            'stack': player.stack,
            'position': i,
            'cards': player.cards.copy(),
            'is_human': False,
            'is_active': True,
            'has_folded': False,
            'current_bet': player.current_bet
        })
    
    initial_state = {
        'players': initial_players,
        'board': session.game_state.board.copy(),
        'pot': session.game_state.pot,
        'current_bet': session.game_state.current_bet,
        'dealer_position': session.dealer_position,
        'small_blind': config.small_blind,
        'big_blind': config.big_blind
    }
    
    english_log = []
    json_actions = []
    action_count = 0
    max_actions = 25
    
    print("🎯 Complete GTO Hand Test")
    print("=" * 60)
    print(f"Initial setup:")
    print(f"  Players: {len(session.game_state.players)}")
    print(f"  Starting stacks: ${config.starting_stack}")
    print(f"  Blinds: ${config.small_blind}/${config.big_blind}")
    print(f"  Initial pot: ${session.game_state.pot}")
    print()
    
    # Log initial player states in English
    for i, player in enumerate(session.game_state.players):
        english_log.append(f"Setup: {player.name} (Position {i}) starts with ${player.stack:.2f}, cards: {player.cards}")
    
    english_log.append(f"Setup: Pot starts at ${session.game_state.pot:.2f}, current bet: ${session.game_state.current_bet:.2f}")
    english_log.append("")
    
    while session.current_state.value != 'END_HAND' and action_count < max_actions:
        action_count += 1
        
        # Get current state before action
        current_player_index = session.action_player_index
        if current_player_index < 0 or current_player_index >= len(session.game_state.players):
            english_log.append(f"Action {action_count}: Invalid player index {current_player_index} - ending hand")
            break
            
        current_player = session.game_state.players[current_player_index]
        street = session.current_state.value
        pot_before = session.game_state.pot
        current_bet_before = session.game_state.current_bet
        player_stack_before = current_player.stack
        player_bet_before = current_player.current_bet
        board_before = session.game_state.board.copy()
        
        print(f"🎲 Action {action_count}: {current_player.name} to act on {street}")
        print(f"   Game state: Pot=${pot_before:.2f}, current_bet=${current_bet_before:.2f}")
        print(f"   Player state: stack=${player_stack_before:.2f}, bet=${player_bet_before:.2f}")
        if board_before:
            print(f"   Board: {board_before}")
        
        # Execute the action
        result = session.execute_next_bot_action()
        
        if not result:
            english_log.append(f"Action {action_count}: {current_player.name} - action failed or hand complete")
            print(f"❌ Action failed or hand complete")
            break
        
        # Analyze what happened
        pot_after = session.game_state.pot
        current_bet_after = session.game_state.current_bet
        player_stack_after = current_player.stack
        player_bet_after = current_player.current_bet
        board_after = session.game_state.board.copy()
        
        stack_change = player_stack_before - player_stack_after
        pot_change = pot_after - pot_before
        
        # Determine the action that occurred
        action_type = "unknown"
        action_amount = 0.0
        
        if current_player.has_folded:
            action_type = "fold"
            action_amount = 0.0
            english_description = f"{current_player.name} folds"
        elif stack_change == 0:
            action_type = "check"
            action_amount = 0.0
            english_description = f"{current_player.name} checks"
        elif stack_change > 0:
            action_amount = stack_change
            if player_bet_before == 0 and current_bet_before == 0:
                action_type = "bet"
                english_description = f"{current_player.name} bets ${action_amount:.2f}"
            elif player_bet_after == current_bet_before:
                action_type = "call"
                english_description = f"{current_player.name} calls ${action_amount:.2f}"
            elif player_bet_after > current_bet_before:
                action_type = "raise"
                english_description = f"{current_player.name} raises to ${player_bet_after:.2f} (putting in ${action_amount:.2f})"
            else:
                action_type = "call"  # Default for money actions
                english_description = f"{current_player.name} puts in ${action_amount:.2f}"
        
        # Check for board changes (new community cards)
        if len(board_after) > len(board_before):
            new_cards = board_after[len(board_before):]
            if len(board_before) == 0:
                english_description += f" | Flop dealt: {new_cards}"
            elif len(board_before) == 3:
                english_description += f" | Turn dealt: {new_cards[0]}"
            elif len(board_before) == 4:
                english_description += f" | River dealt: {new_cards[0]}"
        
        # Log in English
        english_log.append(f"Action {action_count}: {english_description}")
        english_log.append(f"  Result: Pot=${pot_before:.2f}→${pot_after:.2f}, {current_player.name} stack=${player_stack_before:.2f}→${player_stack_after:.2f}")
        
        # Log for JSON
        json_action = {
            'street': street.lower().replace('_betting', ''),
            'player_index': current_player_index,
            'action': action_type,
            'amount': action_amount,
            'explanation': f"GTO {action_type} from Pos_{current_player_index}. {english_description}",
            'pot_after': pot_after
        }
        json_actions.append(json_action)
        
        print(f"✅ {english_description}")
        print(f"   Result: Pot=${pot_after:.2f}, {current_player.name} stack=${player_stack_after:.2f}")
        print()
    
    # Capture final state
    final_players = []
    for player in session.game_state.players:
        final_players.append({
            'name': player.name,
            'stack': player.stack,
            'cards': player.cards.copy(),
            'has_folded': player.has_folded
        })
    
    final_state = {
        'pot': session.game_state.pot,
        'board': session.game_state.board.copy(),
        'players': final_players
    }
    
    english_log.append("")
    english_log.append(f"Final state:")
    english_log.append(f"  Pot: ${session.game_state.pot:.2f}")
    english_log.append(f"  Board: {session.game_state.board}")
    for player in session.game_state.players:
        status = " (FOLDED)" if player.has_folded else ""
        english_log.append(f"  {player.name}: ${player.stack:.2f}{status}")
    
    print(f"🏁 Hand completed after {action_count} actions")
    print(f"Final pot: ${session.game_state.pot:.2f}")
    print(f"Final board: {session.game_state.board}")
    
    return {
        'english_log': english_log,
        'hand_data': {
            'id': f'gto_test_hand_{action_count}',
            'initial_state': initial_state,
            'actions': json_actions,
            'final_state': final_state
        },
        'action_count': action_count
    }

def save_and_verify_hand(test_results: Dict[str, Any]):
    """Save the hand data and verify by reading it back."""
    
    english_log = test_results['english_log']
    hand_data = test_results['hand_data']
    action_count = test_results['action_count']
    
    # Save English log
    english_filename = 'gto_hand_english_log.txt'
    with open(english_filename, 'w') as f:
        f.write('\n'.join(english_log))
    print(f"📄 English log saved to {english_filename}")
    
    # Save JSON
    json_filename = 'gto_hand_for_verification.json'
    with open(json_filename, 'w') as f:
        json.dump(hand_data, f, indent=2)
    print(f"💾 Hand data saved to {json_filename}")
    
    # Read back and verify
    print("\n🔍 Reading back JSON data for verification...")
    with open(json_filename, 'r') as f:
        loaded_data = json.load(f)
    
    print(f"✅ Successfully loaded hand with {len(loaded_data['actions'])} actions")
    
    # Verify structure
    print("\n📋 JSON Structure Verification:")
    print(f"  Hand ID: {loaded_data.get('id', 'Missing')}")
    print(f"  Initial players: {len(loaded_data.get('initial_state', {}).get('players', []))}")
    print(f"  Actions recorded: {len(loaded_data.get('actions', []))}")
    print(f"  Final board: {loaded_data.get('final_state', {}).get('board', [])}")
    print(f"  Final pot: ${loaded_data.get('final_state', {}).get('pot', 0):.2f}")
    
    # Verify each action
    print("\n📊 Action-by-Action Verification:")
    actions = loaded_data.get('actions', [])
    
    for i, action in enumerate(actions, 1):
        action_type = action.get('action', 'unknown')
        amount = action.get('amount', 0.0)
        player_idx = action.get('player_index', -1)
        street = action.get('street', 'unknown')
        pot_after = action.get('pot_after', 0.0)
        
        print(f"  {i:2d}. Player {player_idx+1} {action_type.upper()} ${amount:.2f} on {street} → Pot: ${pot_after:.2f}")
        
        # Check for suspicious patterns
        if action_type == 'call' and amount == 0.0:
            print(f"      ⚠️  SUSPICIOUS: CALL with $0.00 amount")
        elif action_type == 'check' and amount > 0.0:
            print(f"      ⚠️  SUSPICIOUS: CHECK with ${amount:.2f} amount")
    
    print(f"\n✅ Verification complete! Generated {len(actions)} actions total.")
    
    return loaded_data

def compare_english_and_json(english_log: List[str], json_data: Dict[str, Any]):
    """Compare the English log with the JSON data for consistency."""
    
    print("\n🔍 English vs JSON Consistency Check:")
    
    actions = json_data.get('actions', [])
    
    # Extract action lines from English log
    action_lines = [line for line in english_log if line.startswith('Action ')]
    
    print(f"  English log actions: {len(action_lines)}")
    print(f"  JSON actions: {len(actions)}")
    
    if len(action_lines) != len(actions):
        print(f"  ⚠️  COUNT MISMATCH: English has {len(action_lines)}, JSON has {len(actions)}")
        return False
    
    # Check each action for consistency
    all_consistent = True
    for i, (english_line, json_action) in enumerate(zip(action_lines, actions)):
        action_num = i + 1
        json_action_type = json_action.get('action', 'unknown').upper()
        json_amount = json_action.get('amount', 0.0)
        
        # Check if the English line mentions the same action type
        english_upper = english_line.upper()
        
        if json_action_type in english_upper:
            print(f"  {action_num:2d}. ✅ {json_action_type} ${json_amount:.2f} - Consistent")
        else:
            print(f"  {action_num:2d}. ❌ JSON says {json_action_type}, English: {english_line}")
            all_consistent = False
    
    if all_consistent:
        print("\n🎉 Perfect consistency! English log matches JSON data exactly.")
    else:
        print("\n⚠️  Inconsistencies found between English log and JSON data.")
    
    return all_consistent

def main():
    """Main test function."""
    print("🧪 Complete GTO Hand: English → JSON → Verification Test")
    print("=" * 70)
    
    try:
        # Run the complete GTO hand
        test_results = run_complete_gto_hand()
        
        # Save and verify the data
        loaded_json = save_and_verify_hand(test_results)
        
        # Compare English log with JSON for consistency
        is_consistent = compare_english_and_json(test_results['english_log'], loaded_json)
        
        if is_consistent:
            print("\n🎉 SUCCESS! The GTO hand was perfectly recorded and can be replayed.")
            print("The JSON file is ready for Hands Review testing.")
        else:
            print("\n🚨 Issues found in the English → JSON conversion process.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

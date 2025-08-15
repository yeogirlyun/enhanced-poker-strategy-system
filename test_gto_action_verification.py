#!/usr/bin/env python3
"""
Test GTO bot session action recording and JSON conversion.
Creates a GTO hand, logs actions in English, saves to JSON, and verifies consistency.
"""

import json
import sys
import os
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.bot_session_state_machine import GTOBotSession
from core.flexible_poker_state_machine import GameConfig
from core.session_logger import SessionLogger

def create_gto_session():
    """Create a GTO bot session with standard config."""
    config = GameConfig(
        starting_stack=1000,
        small_blind=5,
        big_blind=10,
        num_players=3
    )
    
    session = GTOBotSession(config)
    return session

def log_game_state(session, action_log: List[str]):
    """Log current game state in English."""
    state = session.game_state
    
    # Log current street and pot
    street = session.current_state.value
    pot = state.pot
    current_bet = state.current_bet
    
    action_log.append(f"=== {street.upper()} ===")
    action_log.append(f"Pot: ${pot:.2f}, Current bet: ${current_bet:.2f}")
    
    # Log player states
    for i, player in enumerate(state.players):
        status = ""
        if player.has_folded:
            status = " (FOLDED)"
        elif i == session.action_player_index:
            status = " (TO ACT)"
        
        action_log.append(f"Player {i+1} ({player.name}): ${player.stack:.2f}, bet: ${player.current_bet:.2f}, cards: {player.cards}{status}")
    
    # Log community cards
    if state.board:
        action_log.append(f"Community cards: {state.board}")
    
    action_log.append("")

def run_gto_hand():
    """Run a complete GTO hand and log all actions."""
    print("🎯 Creating GTO bot session...")
    session = create_gto_session()
    
    action_log = []
    action_sequence = []  # For JSON
    
    print("🚀 Starting session...")
    session.start_session()
    
    # Log initial state
    action_log.append("=== HAND START ===")
    log_game_state(session, action_log)
    
    action_count = 0
    max_actions = 50  # Safety limit
    
    while session.current_state.value != 'END_HAND' and action_count < max_actions:
        action_count += 1
        
        # Get current player info before action
        current_player_index = session.action_player_index
        if current_player_index < 0 or current_player_index >= len(session.game_state.players):
            print(f"❌ Invalid action player index: {current_player_index}")
            break
            
        current_player = session.game_state.players[current_player_index]
        
        print(f"🎲 Action {action_count}: Player {current_player_index+1} ({current_player.name}) to act")
        
        # Store before state
        pot_before = session.game_state.pot
        player_stack_before = current_player.stack
        player_bet_before = current_player.current_bet
        
        # Execute next action
        result = session.execute_next_bot_action()
        
        if not result:
            print(f"❌ Action {action_count} failed or session complete")
            break
            
        # Calculate what happened based on state changes
        pot_after = session.game_state.pot
        player_stack_after = current_player.stack
        player_bet_after = current_player.current_bet
        
        # Infer action type and amount
        stack_change = player_stack_before - player_stack_after
        bet_change = player_bet_after - player_bet_before
        
        action_type = "unknown"
        action_amount = 0.0
        
        if stack_change > 0:
            action_amount = stack_change
            if bet_change == stack_change:
                if player_bet_before == 0:
                    action_type = "bet" if session.game_state.current_bet == player_bet_after else "call"
                else:
                    action_type = "raise" if player_bet_after > session.game_state.current_bet else "call"
            else:
                action_type = "call"
        elif stack_change == 0 and bet_change == 0:
            action_type = "check"
        elif current_player.has_folded:
            action_type = "fold"
        
        print(f"📊 Detected: {action_type.upper()} ${action_amount:.2f} (stack: {player_stack_before:.2f} -> {player_stack_after:.2f})")
        
        # Log what happened
        action_log.append(f"Action {action_count}: Player {current_player_index+1} {action_type.upper()} ${action_amount:.2f}")
        log_game_state(session, action_log)
        
        # Record action for JSON
        action_data = {
            'street': session.current_state.value,
            'player_index': current_player_index,
            'action': action_type,
            'amount': action_amount,
            'explanation': f"GTO {action_type} from Pos_{current_player_index}",
            'pot_after': pot_after
        }
        action_sequence.append(action_data)
        print(f"📝 Recorded: {action_data}")
    
    print(f"✅ Hand completed after {action_count} actions")
    
    # Create final hand data
    hand_data = {
        'id': f'test_hand_{action_count}',
        'initial_state': {
            'players': [
                {
                    'name': p.name,
                    'stack': 1000,  # Starting stack
                    'position': i,
                    'cards': p.cards,
                    'is_human': False,
                    'is_active': True,
                    'has_folded': False,
                    'current_bet': 0.0
                }
                for i, p in enumerate(session.game_state.players)
            ],
            'board': [],
            'pot': 0.0,
            'current_bet': 0.0,
            'dealer_position': 0,
            'small_blind': 5,
            'big_blind': 10
        },
        'actions': action_sequence,
        'final_state': {
            'pot': session.game_state.pot,
            'board': session.game_state.board,
            'winner': None  # Would need to determine winner
        }
    }
    
    return hand_data, action_log

def save_and_verify_hand(hand_data: Dict[str, Any], action_log: List[str]):
    """Save hand to JSON and verify by reading it back."""
    
    # Save action log
    log_filename = 'test_gto_action_log.txt'
    with open(log_filename, 'w') as f:
        f.write('\n'.join(action_log))
    print(f"📄 Action log saved to {log_filename}")
    
    # Save JSON
    json_filename = 'test_gto_hand_verification.json'
    with open(json_filename, 'w') as f:
        json.dump(hand_data, f, indent=2)
    print(f"💾 Hand data saved to {json_filename}")
    
    # Read back and verify
    print("\n🔍 Reading back JSON data...")
    with open(json_filename, 'r') as f:
        loaded_data = json.load(f)
    
    print(f"✅ Successfully loaded hand with {len(loaded_data['actions'])} actions")
    
    # Verify action sequence
    print("\n📋 Action verification:")
    for i, action in enumerate(loaded_data['actions']):
        action_type = action.get('action', 'unknown')
        amount = action.get('amount', 0.0)
        player_idx = action.get('player_index', -1)
        street = action.get('street', 'unknown')
        
        print(f"  {i+1}. Player {player_idx+1} {action_type.upper()} ${amount:.2f} on {street}")
        
        # Check for suspicious patterns
        if action_type == 'call' and amount == 0.0:
            print(f"    ⚠️  SUSPICIOUS: CALL with $0.00 amount")
        elif action_type == 'check' and amount > 0.0:
            print(f"    ⚠️  SUSPICIOUS: CHECK with ${amount:.2f} amount")
    
    return loaded_data

def main():
    """Main test function."""
    print("🧪 GTO Action Verification Test")
    print("=" * 50)
    
    try:
        # Run GTO hand
        hand_data, action_log = run_gto_hand()
        
        # Save and verify
        loaded_data = save_and_verify_hand(hand_data, action_log)
        
        print("\n✅ Test completed successfully!")
        print(f"Generated {len(loaded_data['actions'])} actions")
        
        # Summary
        action_types = {}
        for action in loaded_data['actions']:
            action_type = action.get('action', 'unknown')
            action_types[action_type] = action_types.get(action_type, 0) + 1
        
        print(f"\nAction summary: {action_types}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

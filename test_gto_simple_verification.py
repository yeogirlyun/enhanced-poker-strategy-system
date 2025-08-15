#!/usr/bin/env python3
"""
Simple GTO verification test - just run the session and see if actions are valid.
This avoids the issue of calling the decision engine twice.
"""

import json
import sys
import os
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.bot_session_state_machine import GTOBotSession
from core.flexible_poker_state_machine import GameConfig

def run_simple_gto_test():
    """Run GTO session and verify all actions are valid."""
    
    config = GameConfig(
        starting_stack=1000,
        small_blind=5,
        big_blind=10,
        num_players=3
    )
    
    session = GTOBotSession(config)
    session.start_session()
    
    action_log = []
    action_count = 0
    max_actions = 15
    invalid_actions = []
    
    print("🎯 Simple GTO Verification Test")
    print(f"Initial state: Pot=${session.game_state.pot}, Current bet=${session.game_state.current_bet}")
    
    while session.current_state.value != 'END_HAND' and action_count < max_actions:
        action_count += 1
        
        # Get current player and game state
        current_player_index = session.action_player_index
        if current_player_index < 0 or current_player_index >= len(session.game_state.players):
            print(f"❌ Invalid action player index: {current_player_index}")
            break
            
        current_player = session.game_state.players[current_player_index]
        pot_before = session.game_state.pot
        player_stack_before = current_player.stack
        current_bet_before = session.game_state.current_bet
        player_bet_before = current_player.current_bet
        
        print(f"\n🎲 Action {action_count}: Player {current_player_index+1} ({current_player.name}) to act")
        print(f"   State: Pot=${pot_before}, current_bet=${current_bet_before}, player_bet=${player_bet_before}, stack=${player_stack_before}")
        
        # Execute the action
        result = session.execute_next_bot_action()
        
        if not result:
            print(f"❌ Action {action_count} failed or session complete")
            invalid_actions.append({
                'action_number': action_count,
                'error': 'Action execution failed',
                'player_index': current_player_index,
                'game_state': {
                    'pot': pot_before,
                    'current_bet': current_bet_before,
                    'player_bet': player_bet_before,
                    'player_stack': player_stack_before
                }
            })
            break
        
        # Check the outcome
        pot_after = session.game_state.pot
        player_stack_after = current_player.stack
        current_bet_after = session.game_state.current_bet
        player_bet_after = current_player.current_bet
        
        stack_change = player_stack_before - player_stack_after
        bet_change = player_bet_after - player_bet_before
        
        # Determine what action actually happened
        actual_action = "unknown"
        if current_player.has_folded:
            actual_action = "FOLD"
        elif stack_change == 0 and bet_change == 0:
            actual_action = "CHECK"
        elif stack_change > 0:
            if player_bet_before == 0 and current_bet_before == 0:
                actual_action = "BET"
            elif player_bet_after == current_bet_after and current_bet_after > current_bet_before:
                actual_action = "RAISE"
            elif player_bet_after == current_bet_before:
                actual_action = "CALL"
            else:
                actual_action = f"UNKNOWN_MONEY_ACTION (stack_change=${stack_change}, bet_change=${bet_change})"
        
        print(f"📊 Result: {actual_action} ${stack_change:.2f}")
        print(f"   Stack: ${player_stack_before:.2f} -> ${player_stack_after:.2f}")
        print(f"   Player bet: ${player_bet_before:.2f} -> ${player_bet_after:.2f}")
        print(f"   Game current_bet: ${current_bet_before:.2f} -> ${current_bet_after:.2f}")
        print(f"   Pot: ${pot_before:.2f} -> ${pot_after:.2f}")
        
        # Check for suspicious patterns that indicate invalid actions
        issues = []
        
        # CALL with $0 when there's a bet to call
        if actual_action == "CALL" and stack_change == 0 and current_bet_before > player_bet_before:
            issues.append(f"CALL $0 when bet to call was ${current_bet_before - player_bet_before:.2f}")
        
        # CHECK when there's a bet to call
        if actual_action == "CHECK" and current_bet_before > player_bet_before:
            issues.append(f"CHECK when bet to call was ${current_bet_before - player_bet_before:.2f}")
        
        # Any other invalid patterns
        if "UNKNOWN" in actual_action:
            issues.append(f"Unrecognized action pattern")
        
        if issues:
            print(f"⚠️  POTENTIAL ISSUES:")
            for issue in issues:
                print(f"     - {issue}")
            invalid_actions.append({
                'action_number': action_count,
                'actual_action': actual_action,
                'issues': issues,
                'player_index': current_player_index,
                'game_state_before': {
                    'pot': pot_before,
                    'current_bet': current_bet_before,
                    'player_bet': player_bet_before,
                    'player_stack': player_stack_before
                },
                'game_state_after': {
                    'pot': pot_after,
                    'current_bet': current_bet_after,
                    'player_bet': player_bet_after,
                    'player_stack': player_stack_after
                }
            })
        else:
            print(f"✅ Action valid")
        
        action_log.append(f"Action {action_count}: {actual_action} ${stack_change:.2f} - {'✅ Valid' if not issues else '❌ Invalid'}")
    
    print(f"\n✅ Completed {action_count} actions")
    
    # Save results
    results = {
        'test_summary': {
            'total_actions': action_count,
            'valid_actions': action_count - len(invalid_actions),
            'invalid_actions': len(invalid_actions)
        },
        'action_log': action_log,
        'invalid_actions': invalid_actions
    }
    
    with open('test_gto_simple_verification.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to test_gto_simple_verification.json")
    
    # Print summary
    valid_count = results['test_summary']['valid_actions']
    total_count = results['test_summary']['total_actions']
    
    print(f"\n📊 SUMMARY:")
    print(f"   Valid actions: {valid_count}/{total_count}")
    print(f"   Success rate: {100*valid_count/total_count:.1f}%")
    
    if invalid_actions:
        print(f"\n⚠️  Found {len(invalid_actions)} invalid actions!")
        for invalid in invalid_actions:
            print(f"   Action {invalid['action_number']}: {invalid.get('actual_action', 'Failed')}")
            for issue in invalid.get('issues', ['Action execution failed']):
                print(f"     - {issue}")
    else:
        print(f"\n🎉 ALL ACTIONS VALID! The GTO session is working correctly.")
    
    return results

def main():
    """Main test function."""
    try:
        results = run_simple_gto_test()
        
        if results['test_summary']['invalid_actions'] == 0:
            print("\n🎉 SUCCESS! All GTO actions are valid. CALL vs CHECK logic is working correctly.")
        else:
            print("\n🚨 ISSUES FOUND! There may be problems with action validation or game logic.")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

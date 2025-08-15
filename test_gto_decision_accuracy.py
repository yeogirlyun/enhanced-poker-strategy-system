#!/usr/bin/env python3
"""
Test GTO decision engine accuracy by logging actual decisions vs executed actions.
This will verify that CALL vs CHECK is handled correctly without faulty inference.
"""

import json
import sys
import os
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.bot_session_state_machine import GTOBotSession
from core.flexible_poker_state_machine import GameConfig

def run_gto_with_decision_logging():
    """Run GTO session and log actual decisions vs state machine outcomes."""
    
    config = GameConfig(
        starting_stack=1000,
        small_blind=5,
        big_blind=10,
        num_players=3
    )
    
    session = GTOBotSession(config)
    session.start_session()
    
    action_log = []
    decisions_vs_execution = []
    
    action_count = 0
    max_actions = 20
    
    print("🎯 Starting GTO decision logging test...")
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
        print(f"   Game state: Pot=${pot_before}, current_bet=${current_bet_before}, player_bet=${player_bet_before}")
        print(f"   Player stack: ${player_stack_before}")
        
        # Get the decision BEFORE execution
        game_info = session.get_game_info()
        decision = session.decision_engine.get_decision(current_player_index, game_info)
        
        print(f"🧠 Decision engine says: {decision['action'].value.upper()} ${decision['amount']:.2f}")
        
        # Execute the action
        result = session.execute_next_bot_action()
        
        if not result:
            print(f"❌ Action execution failed")
            break
        
        # Check the outcome
        pot_after = session.game_state.pot
        player_stack_after = current_player.stack
        current_bet_after = session.game_state.current_bet
        player_bet_after = current_player.current_bet
        
        stack_change = player_stack_before - player_stack_after
        bet_change = player_bet_after - player_bet_before
        
        print(f"📊 Execution result:")
        print(f"   Stack change: ${stack_change:.2f} ({player_stack_before:.2f} -> {player_stack_after:.2f})")
        print(f"   Player bet change: ${bet_change:.2f} ({player_bet_before:.2f} -> {player_bet_after:.2f})")
        print(f"   Pot change: ${pot_after - pot_before:.2f} ({pot_before:.2f} -> {pot_after:.2f})")
        print(f"   Game current_bet: ${current_bet_before:.2f} -> ${current_bet_after:.2f}")
        
        # Verify consistency
        decision_action = decision['action'].value
        decision_amount = decision['amount']
        
        consistent = True
        issues = []
        
        if decision_action == 'call':
            if stack_change != decision_amount:
                issues.append(f"CALL amount mismatch: expected ${decision_amount}, actual ${stack_change}")
                consistent = False
            if decision_amount == 0 and current_bet_before > 0:
                issues.append(f"SUSPICIOUS: CALL $0 when bet is ${current_bet_before}")
                consistent = False
                
        elif decision_action == 'check':
            if stack_change != 0:
                issues.append(f"CHECK with stack change: ${stack_change}")
                consistent = False
            if decision_amount != 0:
                issues.append(f"CHECK with non-zero amount: ${decision_amount}")
                consistent = False
                
        elif decision_action == 'bet':
            if stack_change != decision_amount:
                issues.append(f"BET amount mismatch: expected ${decision_amount}, actual ${stack_change}")
                consistent = False
                
        elif decision_action == 'raise':
            if stack_change != decision_amount:
                issues.append(f"RAISE amount mismatch: expected ${decision_amount}, actual ${stack_change}")
                consistent = False
        
        status = "✅ CONSISTENT" if consistent else "❌ INCONSISTENT"
        print(f"🔍 Verification: {status}")
        
        if issues:
            for issue in issues:
                print(f"   ⚠️  {issue}")
        
        # Log for JSON
        log_entry = {
            'action_number': action_count,
            'street': session.current_state.value,
            'player_index': current_player_index,
            'decision_action': decision_action,
            'decision_amount': decision_amount,
            'actual_stack_change': stack_change,
            'actual_bet_change': bet_change,
            'consistent': consistent,
            'issues': issues,
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
        }
        
        decisions_vs_execution.append(log_entry)
        action_log.append(f"Action {action_count}: {decision_action.upper()} ${decision_amount:.2f} -> {status}")
    
    print(f"\n✅ Completed {action_count} actions")
    
    # Save results
    results = {
        'test_summary': {
            'total_actions': action_count,
            'consistent_actions': sum(1 for entry in decisions_vs_execution if entry['consistent']),
            'inconsistent_actions': sum(1 for entry in decisions_vs_execution if not entry['consistent'])
        },
        'action_log': action_log,
        'detailed_log': decisions_vs_execution
    }
    
    with open('test_gto_decision_accuracy.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to test_gto_decision_accuracy.json")
    
    # Print summary
    consistent_count = results['test_summary']['consistent_actions']
    total_count = results['test_summary']['total_actions']
    
    print(f"\n📊 SUMMARY:")
    print(f"   Consistent actions: {consistent_count}/{total_count}")
    print(f"   Accuracy: {100*consistent_count/total_count:.1f}%")
    
    if consistent_count < total_count:
        print(f"\n⚠️  Found {total_count - consistent_count} inconsistencies!")
        for entry in decisions_vs_execution:
            if not entry['consistent']:
                print(f"   Action {entry['action_number']}: {entry['decision_action'].upper()} ${entry['decision_amount']:.2f}")
                for issue in entry['issues']:
                    print(f"     - {issue}")
    
    return results

def main():
    """Main test function."""
    try:
        results = run_gto_with_decision_logging()
        
        if results['test_summary']['consistent_actions'] == results['test_summary']['total_actions']:
            print("\n🎉 ALL ACTIONS CONSISTENT! The decision engine and state machine are working correctly.")
        else:
            print("\n🚨 INCONSISTENCIES FOUND! There may be issues with decision adaptation or state machine execution.")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Debug Test for execute_action Method

This test focuses specifically on debugging the execute_action method
and pot change tracking to identify why pot changes are not working.
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'backend'))

from core.poker_state_machine import (
    ImprovedPokerStateMachine, ActionType, PokerState, Player, GameState
)


def debug_execute_action():
    """Debug the execute_action method step by step."""
    print("🔍 DEBUGGING execute_action METHOD")
    print("=" * 60)
    
    # Create state machine
    state_machine = ImprovedPokerStateMachine(num_players=6)
    state_machine.start_hand()
    
    print(f"🏗️ State machine created: {state_machine}")
    print(f"🎯 Current state: {state_machine.get_current_state()}")
    print(f"💰 Initial pot: ${state_machine.game_state.pot:.2f}")
    
    # Get a player
    player = state_machine.game_state.players[0]
    print(f"👤 Player: {player.name}")
    print(f"💵 Player stack: ${player.stack:.2f}")
    print(f"🎯 Player current bet: ${player.current_bet:.2f}")
    
    # Set up betting situation
    state_machine.game_state.current_bet = 10.0
    player.current_bet = 5.0
    
    print(f"💰 Current bet: ${state_machine.game_state.current_bet:.2f}")
    print(f"🎯 Player current bet: ${player.current_bet:.2f}")
    
    # Test CALL action
    print("\n🔄 TESTING CALL ACTION")
    print("-" * 30)
    
    old_pot = state_machine.game_state.pot
    old_stack = player.stack
    old_current_bet = player.current_bet
    
    print(f"💰 Before CALL - Pot: ${old_pot:.2f}")
    print(f"💵 Before CALL - Stack: ${old_stack:.2f}")
    print(f"🎯 Before CALL - Current bet: ${old_current_bet:.2f}")
    
    # Execute CALL action
    try:
        state_machine.execute_action(player, ActionType.CALL, 5.0)
        print("✅ CALL action executed successfully")
    except Exception as e:
        print(f"❌ CALL action failed: {e}")
        return
    
    new_pot = state_machine.game_state.pot
    new_stack = player.stack
    new_current_bet = player.current_bet
    
    print(f"💰 After CALL - Pot: ${new_pot:.2f}")
    print(f"💵 After CALL - Stack: ${new_stack:.2f}")
    print(f"🎯 After CALL - Current bet: ${new_current_bet:.2f}")
    
    pot_change = new_pot - old_pot
    stack_change = old_stack - new_stack
    bet_change = new_current_bet - old_current_bet
    
    print(f"💰 Pot change: ${pot_change:.2f}")
    print(f"💵 Stack change: ${stack_change:.2f}")
    print(f"🎯 Bet change: ${bet_change:.2f}")
    
    # Test BET action
    print("\n🔄 TESTING BET ACTION")
    print("-" * 30)
    
    # Reset for BET test
    state_machine.start_hand()
    player = state_machine.game_state.players[0]
    state_machine.game_state.current_bet = 0.0
    player.current_bet = 0.0
    
    old_pot = state_machine.game_state.pot
    old_stack = player.stack
    
    print(f"💰 Before BET - Pot: ${old_pot:.2f}")
    print(f"💵 Before BET - Stack: ${old_stack:.2f}")
    
    try:
        state_machine.execute_action(player, ActionType.BET, 15.0)
        print("✅ BET action executed successfully")
    except Exception as e:
        print(f"❌ BET action failed: {e}")
        return
    
    new_pot = state_machine.game_state.pot
    new_stack = player.stack
    
    print(f"💰 After BET - Pot: ${new_pot:.2f}")
    print(f"💵 After BET - Stack: ${new_stack:.2f}")
    
    pot_change = new_pot - old_pot
    stack_change = old_stack - new_stack
    
    print(f"💰 Pot change: ${pot_change:.2f}")
    print(f"💵 Stack change: ${stack_change:.2f}")
    
    # Test RAISE action
    print("\n🔄 TESTING RAISE ACTION")
    print("-" * 30)
    
    # Reset for RAISE test
    state_machine.start_hand()
    player = state_machine.game_state.players[0]
    state_machine.game_state.current_bet = 10.0
    player.current_bet = 5.0
    
    old_pot = state_machine.game_state.pot
    old_stack = player.stack
    
    print(f"💰 Before RAISE - Pot: ${old_pot:.2f}")
    print(f"💵 Before RAISE - Stack: ${old_stack:.2f}")
    print(f"🎯 Current bet: ${state_machine.game_state.current_bet:.2f}")
    print(f"🎯 Player current bet: ${player.current_bet:.2f}")
    
    try:
        state_machine.execute_action(player, ActionType.RAISE, 20.0)
        print("✅ RAISE action executed successfully")
    except Exception as e:
        print(f"❌ RAISE action failed: {e}")
        return
    
    new_pot = state_machine.game_state.pot
    new_stack = player.stack
    
    print(f"💰 After RAISE - Pot: ${new_pot:.2f}")
    print(f"💵 After RAISE - Stack: ${new_stack:.2f}")
    print(f"🎯 New current bet: ${state_machine.game_state.current_bet:.2f}")
    print(f"🎯 New player current bet: ${player.current_bet:.2f}")
    
    pot_change = new_pot - old_pot
    stack_change = old_stack - new_stack
    
    print(f"💰 Pot change: ${pot_change:.2f}")
    print(f"💵 Stack change: ${stack_change:.2f}")
    
    print("\n🔍 DEBUGGING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    debug_execute_action() 
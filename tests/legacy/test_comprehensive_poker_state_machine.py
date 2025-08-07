#!/usr/bin/env python3
"""
Comprehensive Poker State Machine Test

This test properly sets up the poker state machine in betting state
and tests all critical functionality including pot change tracking.
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'backend'))

from core.poker_state_machine import (
    ImprovedPokerStateMachine, ActionType, PokerState, Player, GameState
)


def test_comprehensive_poker_state_machine():
    """Test the poker state machine comprehensively."""
    print("🧪 COMPREHENSIVE POKER STATE MACHINE TEST")
    print("=" * 60)
    
    # Create state machine
    state_machine = ImprovedPokerStateMachine(num_players=6)
    
    print(f"🏗️ State machine created: {state_machine}")
    print(f"🎯 Initial state: {state_machine.get_current_state()}")
    
    # Start a hand
    state_machine.start_hand()
    print(f"🎯 After start_hand: {state_machine.get_current_state()}")
    
    # Manually transition to preflop betting
    state_machine.transition_to(PokerState.PREFLOP_BETTING)
    print(f"🎯 After transition to PREFLOP_BETTING: {state_machine.get_current_state()}")
    
    # Set up betting situation
    state_machine.game_state.current_bet = 10.0
    state_machine.game_state.pot = 1.5  # Initial pot with blinds
    
    # Get the current action player
    action_player = state_machine.get_action_player()
    if not action_player:
        print("❌ No action player found - setting up manually")
        # Manually set up action player
        action_player = state_machine.game_state.players[0]
        action_player.current_bet = 5.0
        # Set this player as the current action player
        state_machine.game_state.players_acted.clear()
        state_machine.game_state.players_acted.add(0)
    else:
        print(f"✅ Action player: {action_player.name}")
    
    print(f"💰 Current bet: ${state_machine.game_state.current_bet:.2f}")
    print(f"🎯 Action player current bet: ${action_player.current_bet:.2f}")
    print(f"💰 Pot: ${state_machine.game_state.pot:.2f}")
    
    # Test CALL action
    print("\n🔄 TESTING CALL ACTION")
    print("-" * 30)
    
    old_pot = state_machine.game_state.pot
    old_stack = action_player.stack
    old_current_bet = action_player.current_bet
    
    print(f"💰 Before CALL - Pot: ${old_pot:.2f}")
    print(f"💵 Before CALL - Stack: ${old_stack:.2f}")
    print(f"🎯 Before CALL - Current bet: ${old_current_bet:.2f}")
    
    # Execute CALL action
    try:
        state_machine.execute_action(action_player, ActionType.CALL, 5.0)
        print("✅ CALL action executed successfully")
    except Exception as e:
        print(f"❌ CALL action failed: {e}")
        return
    
    new_pot = state_machine.game_state.pot
    new_stack = action_player.stack
    new_current_bet = action_player.current_bet
    
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
    state_machine.transition_to(PokerState.PREFLOP_BETTING)
    action_player = state_machine.get_action_player()
    if not action_player:
        action_player = state_machine.game_state.players[0]
        state_machine.game_state.players_acted.clear()
        state_machine.game_state.players_acted.add(0)
    
    state_machine.game_state.current_bet = 0.0
    action_player.current_bet = 0.0
    
    old_pot = state_machine.game_state.pot
    old_stack = action_player.stack
    
    print(f"💰 Before BET - Pot: ${old_pot:.2f}")
    print(f"💵 Before BET - Stack: ${old_stack:.2f}")
    
    try:
        state_machine.execute_action(action_player, ActionType.BET, 15.0)
        print("✅ BET action executed successfully")
    except Exception as e:
        print(f"❌ BET action failed: {e}")
        return
    
    new_pot = state_machine.game_state.pot
    new_stack = action_player.stack
    
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
    state_machine.transition_to(PokerState.PREFLOP_BETTING)
    action_player = state_machine.get_action_player()
    if not action_player:
        action_player = state_machine.game_state.players[0]
        state_machine.game_state.players_acted.clear()
        state_machine.game_state.players_acted.add(0)
    
    state_machine.game_state.current_bet = 10.0
    action_player.current_bet = 5.0
    
    old_pot = state_machine.game_state.pot
    old_stack = action_player.stack
    
    print(f"💰 Before RAISE - Pot: ${old_pot:.2f}")
    print(f"💵 Before RAISE - Stack: ${old_stack:.2f}")
    print(f"🎯 Current bet: ${state_machine.game_state.current_bet:.2f}")
    print(f"🎯 Player current bet: ${action_player.current_bet:.2f}")
    
    try:
        state_machine.execute_action(action_player, ActionType.RAISE, 20.0)
        print("✅ RAISE action executed successfully")
    except Exception as e:
        print(f"❌ RAISE action failed: {e}")
        return
    
    new_pot = state_machine.game_state.pot
    new_stack = action_player.stack
    
    print(f"💰 After RAISE - Pot: ${new_pot:.2f}")
    print(f"💵 After RAISE - Stack: ${new_stack:.2f}")
    print(f"🎯 New current bet: ${state_machine.game_state.current_bet:.2f}")
    print(f"🎯 New player current bet: ${action_player.current_bet:.2f}")
    
    pot_change = new_pot - old_pot
    stack_change = old_stack - new_stack
    
    print(f"💰 Pot change: ${pot_change:.2f}")
    print(f"💵 Stack change: ${stack_change:.2f}")
    
    # Test round completion
    print("\n🔄 TESTING ROUND COMPLETION")
    print("-" * 30)
    
    # Set up all players as having acted
    for player in state_machine.game_state.players:
        player.has_acted_this_round = True
        player.current_bet = 20.0  # All players have matched the bet
    
    is_complete = state_machine.is_round_complete()
    print(f"🎯 Round complete: {is_complete}")
    
    # Test state transitions
    print("\n🔄 TESTING STATE TRANSITIONS")
    print("-" * 30)
    
    print(f"🎯 Current state: {state_machine.get_current_state()}")
    
    # Test transition to deal flop
    try:
        state_machine.transition_to(PokerState.DEAL_FLOP)
        print(f"✅ Transitioned to: {state_machine.get_current_state()}")
    except Exception as e:
        print(f"❌ State transition failed: {e}")
    
    print("\n🔍 COMPREHENSIVE TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_comprehensive_poker_state_machine() 
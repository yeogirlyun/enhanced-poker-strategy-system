#!/usr/bin/env python3
"""
Test script to debug Player 4 stalling issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, PokerState, ActionType

def debug_player_4_stall():
    """Debug the Player 4 stalling issue."""
    print("🔍 DEBUGGING PLAYER 4 STALL ISSUE")
    print("=" * 40)
    
    # Create a poker state machine
    poker_machine = ImprovedPokerStateMachine(num_players=6)
    
    # Start a hand
    poker_machine.start_hand()
    
    print(f"🎯 Current State: {poker_machine.current_state}")
    print(f"🎯 Action Player Index: {poker_machine.action_player_index}")
    
    # Get current action player
    action_player = poker_machine.get_action_player()
    if action_player:
        print(f"🎯 Current Action Player: {action_player.name} ({action_player.position})")
    else:
        print("❌ No action player found!")
    
    # Print all players and their states
    print("\n📊 PLAYER STATES:")
    for i, player in enumerate(poker_machine.game_state.players):
        print(f"  Player {i}: {player.name} ({player.position})")
        print(f"    Active: {player.is_active}")
        print(f"    Human: {player.is_human}")
        print(f"    Stack: ${player.stack:.2f}")
        print(f"    Current Bet: ${player.current_bet:.2f}")
        print(f"    Has Acted: {player.has_acted_this_round}")
        print(f"    Is All-In: {player.is_all_in}")
        print()
    
    # Check round completion
    is_complete = poker_machine.is_round_complete()
    print(f"🔄 Round Complete: {is_complete}")
    
    # Get game info
    game_info = poker_machine.get_game_info()
    print(f"💰 Pot: ${game_info.get('pot', 0):.2f}")
    print(f"🎯 Current Bet: ${game_info.get('current_bet', 0):.2f}")
    print(f"🎯 Street: {game_info.get('state', 'unknown')}")
    
    # Test bot action for Player 4 (index 3)
    if len(poker_machine.game_state.players) > 3:
        player_4 = poker_machine.game_state.players[3]
        print(f"\n🤖 TESTING PLAYER 4 ({player_4.name}) BOT ACTION:")
        print(f"  Position: {player_4.position}")
        print(f"  Active: {player_4.is_active}")
        print(f"  Human: {player_4.is_human}")
        print(f"  Stack: ${player_4.stack:.2f}")
        print(f"  Current Bet: ${player_4.current_bet:.2f}")
        
        if not player_4.is_human:
            print("  🤖 Player 4 is a bot - testing action...")
            try:
                # Temporarily set action player to Player 4
                original_index = poker_machine.action_player_index
                poker_machine.action_player_index = 3
                
                # Test bot action
                poker_machine.execute_bot_action(player_4)
                
                # Restore original index
                poker_machine.action_player_index = original_index
                print("  ✅ Bot action executed successfully")
            except Exception as e:
                print(f"  ❌ Bot action failed: {e}")
        else:
            print("  👤 Player 4 is human")
    
    # Test round completion logic
    print(f"\n🔍 ROUND COMPLETION ANALYSIS:")
    active_players = [p for p in poker_machine.game_state.players if p.is_active]
    players_who_can_act = [p for p in active_players if not p.is_all_in]
    
    print(f"  Active Players: {len(active_players)}")
    print(f"  Players Who Can Act: {len(players_who_can_act)}")
    
    for player in players_who_can_act:
        print(f"    {player.name}: acted={player.has_acted_this_round}, bet=${player.current_bet:.2f}")
    
    # Check if all have acted
    all_have_acted = all(p.has_acted_this_round for p in players_who_can_act)
    print(f"  All Have Acted: {all_have_acted}")
    
    # Check if bets are equal
    if active_players:
        highest_bet = max(p.current_bet for p in active_players)
        bets_are_equal = all(
            p.current_bet == highest_bet or (p.is_all_in and p.partial_call_amount is not None)
            for p in players_who_can_act
        )
        print(f"  Highest Bet: ${highest_bet:.2f}")
        print(f"  Bets Are Equal: {bets_are_equal}")
    
    print(f"\n🎯 FINAL ROUND COMPLETE: {is_complete}")

if __name__ == "__main__":
    debug_player_4_stall() 
#!/usr/bin/env python3
"""
Simple debug script to isolate Player 4 stalling issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine

def debug_stall():
    """Debug the stalling issue without running the full game."""
    print("🔍 DEBUGGING STALL ISSUE")
    print("=" * 30)
    
    # Create poker machine
    poker_machine = ImprovedPokerStateMachine(num_players=6)
    
    # Start hand
    poker_machine.start_hand()
    
    print(f"🎯 State: {poker_machine.current_state}")
    print(f"🎯 Action Player Index: {poker_machine.action_player_index}")
    
    # Check Player 4 specifically
    if len(poker_machine.game_state.players) > 3:
        player_4 = poker_machine.game_state.players[3]
        print(f"\n🎯 Player 4 Analysis:")
        print(f"  Name: {player_4.name}")
        print(f"  Position: {player_4.position}")
        print(f"  Active: {player_4.is_active}")
        print(f"  Human: {player_4.is_human}")
        print(f"  Stack: ${player_4.stack:.2f}")
        print(f"  Current Bet: ${player_4.current_bet:.2f}")
        print(f"  Has Acted: {player_4.has_acted_this_round}")
        
        # Check if Player 4 should be the action player
        if poker_machine.action_player_index == 3:
            print("  ✅ Player 4 is the current action player")
        else:
            print(f"  ❌ Player 4 is NOT the action player (index {poker_machine.action_player_index})")
    
    # Check round completion
    is_complete = poker_machine.is_round_complete()
    print(f"\n🔄 Round Complete: {is_complete}")
    
    # Check all players
    print(f"\n📊 ALL PLAYERS:")
    for i, player in enumerate(poker_machine.game_state.players):
        status = "🎯 ACTION" if i == poker_machine.action_player_index else ""
        print(f"  {i}: {player.name} ({player.position}) - Active:{player.is_active} Human:{player.is_human} {status}")
    
    print(f"\n✅ Debug complete!")

if __name__ == "__main__":
    debug_stall() 
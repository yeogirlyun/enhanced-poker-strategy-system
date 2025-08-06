#!/usr/bin/env python3
"""
Debug script to check blind positions and action player calculation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine

def debug_blind_positions():
    """Debug the blind positions and action player calculation."""
    print("🔍 DEBUGGING BLIND POSITIONS")
    print("=" * 35)
    
    # Create poker machine
    poker_machine = ImprovedPokerStateMachine(num_players=6)
    
    # Start hand
    poker_machine.start_hand()
    
    print(f"🎯 Dealer Position: {poker_machine.dealer_position}")
    print(f"🎯 Small Blind Position: {poker_machine.small_blind_position}")
    print(f"🎯 Big Blind Position: {poker_machine.big_blind_position}")
    print(f"🎯 Action Player Index: {poker_machine.action_player_index}")
    
    # Calculate expected action player
    expected_action = (poker_machine.big_blind_position + 1) % poker_machine.num_players
    print(f"🎯 Expected Action Player: {expected_action}")
    
    # Check all players
    print(f"\n📊 ALL PLAYERS:")
    for i, player in enumerate(poker_machine.game_state.players):
        status = "🎯 ACTION" if i == poker_machine.action_player_index else ""
        expected = "✅ EXPECTED" if i == expected_action else ""
        print(f"  {i}: {player.name} ({player.position}) - {status} {expected}")
    
    # Check if the fix worked
    if poker_machine.action_player_index == expected_action:
        print(f"\n✅ FIX WORKED! Action player is correct.")
    else:
        print(f"\n❌ FIX FAILED! Action player should be {expected_action} but is {poker_machine.action_player_index}")
    
    print(f"\n✅ Debug complete!")

if __name__ == "__main__":
    debug_blind_positions() 
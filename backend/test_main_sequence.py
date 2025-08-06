#!/usr/bin/env python3
"""
Test script to simulate the exact sequence from main.py.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine

def test_main_sequence():
    """Test the exact sequence from main.py."""
    print("🔍 TESTING MAIN SEQUENCE")
    print("=" * 30)
    
    # Simulate the exact sequence from main.py
    strategy_data = None  # We'll use None for now
    state_machine = ImprovedPokerStateMachine(num_players=6, strategy_data=strategy_data)
    
    print(f"🎯 After __init__: action_player_index = {state_machine.action_player_index}")
    
    # Start session (like in main.py line 43)
    state_machine.start_session()
    print(f"🎯 After start_session: action_player_index = {state_machine.action_player_index}")
    
    # Start hand (like in main.py line 44)
    state_machine.start_hand()
    print(f"🎯 After start_hand: action_player_index = {state_machine.action_player_index}")
    
    # Check the final state
    print(f"\n📊 FINAL STATE:")
    print(f"  Dealer Position: {state_machine.dealer_position}")
    print(f"  Big Blind Position: {state_machine.big_blind_position}")
    print(f"  Action Player Index: {state_machine.action_player_index}")
    print(f"  Expected Action Player: {(state_machine.big_blind_position + 1) % state_machine.num_players}")
    
    # Check all players
    print(f"\n📊 ALL PLAYERS:")
    for i, player in enumerate(state_machine.game_state.players):
        status = "🎯 ACTION" if i == state_machine.action_player_index else ""
        expected = "✅ EXPECTED" if i == (state_machine.big_blind_position + 1) % state_machine.num_players else ""
        print(f"  {i}: {player.name} ({player.position}) - {status} {expected}")
    
    print(f"\n✅ Test complete!")

if __name__ == "__main__":
    test_main_sequence() 
#!/usr/bin/env python3
"""
Test to check the initial game state when starting a new hand.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine

def test_game_start_state():
    """Test what the initial game state should be when starting a new hand."""
    print("🎯 TESTING GAME START STATE")
    print("=" * 40)
    
    try:
        # Create poker machine
        print("Creating poker machine...")
        poker_machine = ImprovedPokerStateMachine(num_players=6)
        print("✅ Poker machine created")
        
        # Start session
        print("Starting session...")
        poker_machine.start_session()
        print("✅ Session started")
        
        # Check initial state before starting hand
        print(f"\n📊 INITIAL STATE BEFORE START_HAND:")
        print(f"  Current state: {poker_machine.current_state}")
        print(f"  Action player index: {poker_machine.action_player_index}")
        print(f"  Game state exists: {poker_machine.game_state is not None}")
        
        # Start hand
        print("\nStarting hand...")
        poker_machine.start_hand()
        print("✅ Hand started")
        
        # Check state after starting hand
        print(f"\n📊 STATE AFTER START_HAND:")
        print(f"  Current state: {poker_machine.current_state}")
        print(f"  Action player index: {poker_machine.action_player_index}")
        print(f"  Action player: {poker_machine.get_action_player().name if poker_machine.get_action_player() else 'None'}")
        print(f"  Big blind position: {poker_machine.big_blind_position}")
        print(f"  Small blind position: {poker_machine.small_blind_position}")
        print(f"  Pot: ${poker_machine.game_state.pot}")
        print(f"  Current bet: ${poker_machine.game_state.current_bet}")
        
        # Check all players
        print(f"\n📊 ALL PLAYERS:")
        for i, player in enumerate(poker_machine.game_state.players):
            status = "🎯 ACTION" if i == poker_machine.action_player_index else ""
            expected = "✅ EXPECTED" if i == (poker_machine.big_blind_position + 1) % poker_machine.num_players else ""
            print(f"  {i}: {player.name} ({player.position}) - Stack: ${player.stack:.2f} - Bet: ${player.current_bet:.2f} - {status} {expected}")
        
        # Check if this is the expected behavior
        expected_action_player = (poker_machine.big_blind_position + 1) % poker_machine.num_players
        if poker_machine.action_player_index == expected_action_player:
            print(f"\n✅ SUCCESS! Game starts correctly with action player {poker_machine.action_player_index}")
            print("This is the expected behavior for a poker game - cards are dealt and betting begins immediately.")
        else:
            print(f"\n❌ ISSUE! Action player should be {expected_action_player} but is {poker_machine.action_player_index}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_game_start_state() 
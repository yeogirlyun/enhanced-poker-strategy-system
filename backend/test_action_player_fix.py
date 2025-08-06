#!/usr/bin/env python3
"""
Test to verify action player is set correctly after start_hand.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine

def test_action_player_fix():
    """Test that action player is set correctly after start_hand."""
    print("🔍 TESTING ACTION PLAYER FIX")
    print("=" * 35)
    
    try:
        # Create poker machine
        print("Creating poker machine...")
        poker_machine = ImprovedPokerStateMachine(num_players=6)
        print("✅ Poker machine created")
        
        # Start session
        print("Starting session...")
        poker_machine.start_session()
        print("✅ Session started")
        
        # Start hand
        print("Starting hand...")
        poker_machine.start_hand()
        print("✅ Hand started")
        
        # Check action player IMMEDIATELY after start_hand
        print(f"\n📊 IMMEDIATE CHECK AFTER START_HAND:")
        print(f"  Action player index: {poker_machine.action_player_index}")
        print(f"  Big blind position: {poker_machine.big_blind_position}")
        print(f"  Expected action player: {(poker_machine.big_blind_position + 1) % poker_machine.num_players}")
        
        # Check all players
        print(f"\n📊 ALL PLAYERS:")
        for i, player in enumerate(poker_machine.game_state.players):
            status = "🎯 ACTION" if i == poker_machine.action_player_index else ""
            expected = "✅ EXPECTED" if i == (poker_machine.big_blind_position + 1) % poker_machine.num_players else ""
            print(f"  {i}: {player.name} ({player.position}) - {status} {expected}")
        
        # Verify the fix worked
        expected_action_player = (poker_machine.big_blind_position + 1) % poker_machine.num_players
        if poker_machine.action_player_index == expected_action_player:
            print(f"\n✅ SUCCESS! Action player is correctly set to {poker_machine.action_player_index}")
        else:
            print(f"\n❌ FAILED! Action player should be {expected_action_player} but is {poker_machine.action_player_index}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_action_player_fix() 
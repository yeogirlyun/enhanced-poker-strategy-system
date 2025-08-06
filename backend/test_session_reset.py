#!/usr/bin/env python3
"""
Test to check if session and game state are properly reset when starting a new hand.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine

def test_session_reset():
    """Test if session and game state are properly reset when starting a new hand."""
    print("🎯 TESTING SESSION RESET")
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
        
        # Start first hand
        print("\n🔄 STARTING FIRST HAND...")
        poker_machine.start_hand()
        
        # Check first hand state
        print(f"  State: {poker_machine.current_state}")
        print(f"  Action player: {poker_machine.get_action_player().name}")
        print(f"  Pot: ${poker_machine.game_state.pot}")
        print(f"  Hands played: {poker_machine.session_state.current_hand_number}")
        
        # Simulate some actions to complete the hand
        print("\n🎮 Simulating hand completion...")
        action_player = poker_machine.get_action_player()
        if action_player:
            # Player 4 folds
            poker_machine.execute_action(action_player, poker_machine.ActionType.FOLD, 0)
            print(f"  {action_player.name} folded")
        
        # Advance through other players
        for i in range(5):  # Skip the rest of the players
            poker_machine.advance_to_next_player()
            action_player = poker_machine.get_action_player()
            if action_player and action_player.is_active:
                poker_machine.execute_action(action_player, poker_machine.ActionType.FOLD, 0)
                print(f"  {action_player.name} folded")
        
        # Check if hand is complete
        print(f"\n📊 AFTER FIRST HAND:")
        print(f"  State: {poker_machine.current_state}")
        print(f"  Hands played: {poker_machine.session_state.current_hand_number}")
        print(f"  Total hands in session: {len(poker_machine.session_state.hands_played)}")
        
        # Start second hand
        print("\n🔄 STARTING SECOND HAND...")
        poker_machine.start_hand()
        
        # Check second hand state
        print(f"  State: {poker_machine.current_state}")
        print(f"  Action player: {poker_machine.get_action_player().name}")
        print(f"  Pot: ${poker_machine.game_state.pot}")
        print(f"  Hands played: {poker_machine.session_state.current_hand_number}")
        
        # Check if pot was reset
        if poker_machine.game_state.pot == 1.5:
            print("✅ Pot correctly reset to $1.50 (blinds)")
        else:
            print(f"❌ Pot not reset correctly: ${poker_machine.game_state.pot}")
        
        # Check if action player is correct
        expected_action_player = (poker_machine.big_blind_position + 1) % poker_machine.num_players
        if poker_machine.action_player_index == expected_action_player:
            print("✅ Action player correctly set")
        else:
            print(f"❌ Action player incorrect: {poker_machine.action_player_index} vs expected {expected_action_player}")
        
        # Check if all players are active
        active_players = [p for p in poker_machine.game_state.players if p.is_active]
        if len(active_players) == 6:
            print("✅ All players are active")
        else:
            print(f"❌ Only {len(active_players)} players are active")
        
        # Check if all bets are reset
        all_bets_reset = all(p.current_bet == 0.0 for p in poker_machine.game_state.players 
                            if p.position not in ['SB', 'BB'])
        if all_bets_reset:
            print("✅ All player bets reset correctly")
        else:
            print("❌ Some player bets not reset")
        
        print(f"\n📊 FINAL SESSION STATE:")
        print(f"  Total hands played: {len(poker_machine.session_state.hands_played)}")
        print(f"  Current hand number: {poker_machine.session_state.current_hand_number}")
        print(f"  Session duration: {poker_machine.get_session_info().get('session_duration', 0):.2f}s")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_session_reset() 
#!/usr/bin/env python3
"""
Test Voice Integration

Tests that voice announcements work in the poker game.
"""

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine
from voice_announcement_system import voice_system

def main():
    """Test voice integration with poker game."""
    print("🎤 TESTING VOICE INTEGRATION")
    print("=" * 40)
    
    # Create a poker state machine
    print(f"🔄 Creating poker state machine...")
    state_machine = ImprovedPokerStateMachine(num_players=6)
    
    # Check if voice system is integrated
    if hasattr(state_machine, 'voice_system'):
        print(f"✅ Voice system integrated with state machine")
    else:
        print(f"❌ Voice system not integrated")
        return
    
    # Test voice announcements
    print(f"\n🎤 Testing voice announcements:")
    
    # Test different voice types
    voice_types = voice_system.get_available_voice_types()
    for voice_type in voice_types:
        print(f"🎤 Testing voice type: {voice_type}")
        voice_system.set_voice_type(voice_type)
        
        # Test basic announcements
        test_actions = ['check', 'call', 'bet', 'raise', 'fold']
        for action in test_actions:
            try:
                voice_system.play_voice_announcement(action)
                print(f"  ✅ {action} announcement played")
            except Exception as e:
                print(f"  ❌ {action} announcement failed: {e}")
    
    print(f"\n🎮 Testing with poker actions:")
    
    # Start a hand
    try:
        state_machine.start_hand()
        print(f"✅ Hand started successfully")
        
        # Get the first player
        if state_machine.game_state.players:
            player = state_machine.game_state.players[0]
            print(f"🎯 Testing with player: {player.name}")
            
            # Test different actions
            from shared.poker_state_machine_enhanced import ActionType
            
            test_actions = [
                (ActionType.CHECK, 0),
                (ActionType.CALL, 10),
                (ActionType.BET, 20),
                (ActionType.RAISE, 30),
                (ActionType.FOLD, 0)
            ]
            
            for action, amount in test_actions:
                try:
                    print(f"🎤 Testing action: {action.value} ${amount}")
                    state_machine.execute_action(player, action, amount)
                    print(f"  ✅ Action executed with voice")
                except Exception as e:
                    print(f"  ❌ Action failed: {e}")
                    
        else:
            print(f"❌ No players available for testing")
            
    except Exception as e:
        print(f"❌ Error starting hand: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • Voice system should be integrated with poker game")
    print(f"  • Voice announcements should play during poker actions")
    print(f"  • Different voice types should be available")
    print(f"  • All-in and special events should have voice announcements")

if __name__ == "__main__":
    main() 
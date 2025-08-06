#!/usr/bin/env python3
"""
Test Card Deal in Game

Tests that card dealing sounds work in the actual poker game.
"""

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine
from enhanced_sound_manager import sound_manager
from sound_persistence import SoundPersistence

def main():
    """Test card dealing sounds in the game."""
    print("🎴 TESTING CARD DEAL IN GAME")
    print("=" * 40)
    
    # First, set up a custom card_deal mapping
    persistence = SoundPersistence()
    persistence.set_custom_sound("card_deal", "card_deal_custom.wav")
    print(f"📝 Set custom mapping: card_deal → card_deal_custom.wav")
    
    # Check the enhanced sound manager
    if "card_deal" in sound_manager.sound_configs:
        config = sound_manager.sound_configs["card_deal"]
        print(f"📝 Enhanced sound manager config: card_deal → {config.name}")
    else:
        print(f"❌ card_deal not found in enhanced sound manager")
    
    # Create a poker state machine
    print(f"🔄 Creating poker state machine...")
    state_machine = ImprovedPokerStateMachine(num_players=6)
    
    # Check the state machine's sound manager
    if hasattr(state_machine.sfx, 'sound_configs'):
        if "card_deal" in state_machine.sfx.sound_configs:
            config = state_machine.sfx.sound_configs["card_deal"]
            print(f"📝 State machine sound config: card_deal → {config.name}")
        else:
            print(f"❌ card_deal not found in state machine sound configs")
    else:
        print(f"❌ State machine doesn't have sound_configs")
    
    # Test starting a hand (this should trigger card dealing)
    print(f"🎴 Starting a hand...")
    try:
        state_machine.start_hand()
        print(f"✅ Hand started successfully")
    except Exception as e:
        print(f"❌ Error starting hand: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • The state machine should now use the enhanced sound manager")
    print(f"  • Custom card_deal mappings should work in the game")
    print(f"  • Card dealing sounds should play with custom files")

if __name__ == "__main__":
    main() 
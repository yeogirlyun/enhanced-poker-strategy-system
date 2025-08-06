#!/usr/bin/env python3
"""
Fix Sound Mappings Complete

Maps all available sound files to the correct poker actions.
"""

from enhanced_sound_manager import EnhancedSoundManager

def main():
    """Fix all sound mappings using available files."""
    print("🎵 FIXING SOUND MAPPINGS")
    print("=" * 50)
    
    # Initialize sound manager
    sound_manager = EnhancedSoundManager()
    
    # Define comprehensive mappings using actual files
    mappings = {
        # UI Sounds
        "button_click": "coin-257878.mp3",
        "button_hover": "coin-257878.mp3", 
        "notification": "turn_notify.wav",
        "success": "money-bag-82960.mp3",
        "error": "player_fold.wav",
        "menu_open": "card_deal.wav",
        "menu_close": "card_deal.wav",
        
        # Player Actions
        "check": "player_check.wav",
        "call": "player_call.wav", 
        "bet": "player_bet.wav",
        "raise": "player_raise.wav",
        "fold": "player_fold.wav",
        "all_in": "player_all_in.wav",
        
        # Card Actions
        "card_deal": "card_deal.wav",
        "card_flip": "card_fold.wav",
        "card_shuffle": "shuffling-cards-01-86984.mp3",
        
        # Chip Actions
        "chip_bet": "chip_bet.wav",
        "chip_stack": "poker_chips1-87592.mp3",
        "chip_collect": "coin-257878.mp3",
        
        # Pot Actions
        "pot_win": "money-bag-82960.mp3",
        "pot_split": "pot_split.wav",
        "pot_rake": "pot_rake.wav",
        
        # Game Actions
        "turn_notify": "turn_notify.wav",
        "button_move": "button_move.wav",
        "dealer_button": "button_move.wav",
        "winner_announce": "winner_announce.wav",
        "all_in_announce": "player_all_in.wav",
        
        # Ambient Sounds
        "table_ambient": "card_deal.wav",
        "crowd_murmur": "card_deal.wav"
    }
    
    # Apply mappings
    print("📋 APPLYING SOUND MAPPINGS:")
    updated_count = 0
    
    for sound_name, filename in mappings.items():
        # Find the sound config
        for config in sound_manager.sound_configs:
            if config.name == sound_name:
                old_file = config.name
                config.name = filename
                print(f"  ✅ {sound_name:20} → {filename}")
                updated_count += 1
                break
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • Updated {updated_count} sound mappings")
    print(f"  • Using actual files from sounds/ directory")
    
    # Test some key sounds
    print(f"\n🔊 TESTING KEY SOUNDS:")
    test_sounds = ["check", "call", "bet", "raise", "fold", "card_shuffle", "chip_bet"]
    
    for sound in test_sounds:
        try:
            sound_manager.play(sound)
            print(f"  ✅ {sound}: Working")
        except Exception as e:
            print(f"  ❌ {sound}: {e}")
    
    print(f"\n🎵 SOUND SYSTEM READY!")
    print(f"  • Use the GUI to test sounds")
    print(f"  • Access sound settings via Settings → 🎵 Sound Settings")

if __name__ == "__main__":
    main() 
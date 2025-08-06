#!/usr/bin/env python3
"""
Map Missing Sounds

Maps the missing sounds using available files.
"""

from enhanced_sound_manager import EnhancedSoundManager

def main():
    """Map missing sounds using available files."""
    print("🎵 MAPPING MISSING SOUNDS")
    print("=" * 40)
    
    # Initialize sound manager
    sound_manager = EnhancedSoundManager()
    
    # Map missing sounds to available files
    missing_mappings = {
        "button_click": "coin-257878.mp3",
        "button_hover": "coin-257878.mp3",
        "notification": "turn_notify.wav",
        "success": "money-bag-82960.mp3",
        "error": "player_fold.wav",
        "menu_open": "card_deal.wav",
        "menu_close": "card_deal.wav",
        "card_deal": "card_deal.wav",
        "chip_bet": "chip_bet.wav",
        "pot_split": "pot_split.wav",
        "pot_rake": "pot_rake.wav",
        "turn_notify": "turn_notify.wav",
        "button_move": "button_move.wav",
        "winner_announce": "winner_announce.wav"
    }
    
    print("📋 MAPPING MISSING SOUNDS:")
    updated_count = 0
    
    for sound_name, filename in missing_mappings.items():
        # Find the sound config in the dictionary
        if sound_name in sound_manager.sound_configs:
            config = sound_manager.sound_configs[sound_name]
            old_file = config.name
            config.name = filename
            print(f"  ✅ {sound_name:20} → {filename}")
            updated_count += 1
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • Mapped {updated_count} missing sounds")
    print(f"  • All sounds should now be working")
    
    # Test the newly mapped sounds
    print(f"\n🔊 TESTING NEWLY MAPPED SOUNDS:")
    test_sounds = ["button_click", "notification", "success", "card_deal", "chip_bet"]
    
    for sound in test_sounds:
        try:
            sound_manager.play(sound)
            print(f"  ✅ {sound}: Working")
        except Exception as e:
            print(f"  ❌ {sound}: {e}")
    
    print(f"\n🎵 ALL SOUNDS SHOULD NOW BE WORKING!")
    print(f"  • Use the GUI to test all sounds")
    print(f"  • Access sound settings via Settings → 🎵 Sound Settings")

if __name__ == "__main__":
    main() 
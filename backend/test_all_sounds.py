#!/usr/bin/env python3
"""
Test All Sounds

Comprehensive test of all sound mappings.
"""

from enhanced_sound_manager import EnhancedSoundManager

def main():
    """Test all sound mappings."""
    print("🎵 TESTING ALL SOUNDS")
    print("=" * 50)
    
    # Initialize sound manager
    sound_manager = EnhancedSoundManager()
    
    # All sound actions to test
    all_sounds = [
        # UI Sounds
        "button_click", "button_hover", "notification", "success", "error",
        "menu_open", "menu_close",
        
        # Player Actions
        "check", "call", "bet", "raise", "fold", "all_in",
        
        # Card Actions
        "card_deal", "card_flip", "card_shuffle",
        
        # Chip Actions
        "chip_bet", "chip_stack", "chip_collect",
        
        # Pot Actions
        "pot_win", "pot_split", "pot_rake",
        
        # Game Actions
        "turn_notify", "button_move", "dealer_button", "winner_announce", "all_in_announce",
        
        # Ambient Sounds
        "table_ambient", "crowd_murmur"
    ]
    
    print("📋 TESTING ALL SOUNDS:")
    working_count = 0
    missing_count = 0
    
    for sound in all_sounds:
        try:
            sound_manager.play(sound)
            print(f"  ✅ {sound:20} → Working")
            working_count += 1
        except Exception as e:
            print(f"  ❌ {sound:20} → Missing")
            missing_count += 1
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • Working sounds: {working_count}")
    print(f"  • Missing sounds: {missing_count}")
    print(f"  • Total sounds: {len(all_sounds)}")
    
    if missing_count == 0:
        print(f"\n🎉 ALL SOUNDS ARE WORKING!")
    else:
        print(f"\n🔧 {missing_count} sounds still need mapping")
    
    print(f"\n🎵 SOUND SYSTEM STATUS:")
    print(f"  • Use the GUI to test sounds")
    print(f"  • Access sound settings via Settings → 🎵 Sound Settings")
    print(f"  • All mapped sounds should play correctly")

if __name__ == "__main__":
    main() 
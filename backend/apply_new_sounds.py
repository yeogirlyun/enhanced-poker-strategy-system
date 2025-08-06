#!/usr/bin/env python3
"""
Apply New Sounds to Sound System

Directly applies the new high-quality sounds to improve the audio experience.
"""

from enhanced_sound_manager import sound_manager, SoundCategory

def apply_new_sounds():
    """Apply the new high-quality sounds to the sound system."""
    
    print("🎵 APPLYING NEW HIGH-QUALITY SOUNDS")
    print("=" * 50)
    
    # Create new sound mappings based on the new files
    new_mappings = {
        # High-quality card shuffle sounds
        'card_shuffle': 'cards-shuffling-87543.mp3',  # 326KB - High quality
        'card_deal': 'shuffling-cards-01-86984.mp3',  # 113KB - High quality
        
        # Chip and money sounds
        'chip_bet': 'poker_chips1-87592.mp3',  # 20KB - Better than original
        'chip_collect': 'coin-257878.mp3',  # 43KB - Coin sound for collecting
        'chip_stack': 'money-bag-82960.mp3',  # 35KB - Money bag sound for stacking
        
        # All-in dramatic sound
        'player_all_in': 'allinpushchips2-39133.mp3',  # 28KB - Dramatic all-in
        
        # Winner sounds
        'winner_announce': 'cash-register-kaching-376867.mp3',  # 35KB - Cash register for wins
        'pot_win': 'money-bag-82960.mp3',  # 35KB - Money bag for pot wins
        
        # UI sounds
        'button_click': 'coin-257878.mp3',  # 43KB - Coin sound for clicks
        'notification': 'turn_notify.wav',  # Keep original for notifications
    }
    
    print("📋 NEW SOUND MAPPINGS:")
    for sound_name, file_name in new_mappings.items():
        print(f"  • {sound_name} → {file_name}")
    
    # Apply the mappings to the sound manager
    applied_count = 0
    for sound_name, file_name in new_mappings.items():
        if hasattr(sound_manager, 'sound_configs'):
            # Find the sound config and update it
            for config_name, config in sound_manager.sound_configs.items():
                if config_name == sound_name:
                    old_file = config.name
                    config.name = file_name
                    print(f"✅ Updated {sound_name}: {old_file} → {file_name}")
                    applied_count += 1
                    break
    
    print(f"\n✅ Applied {applied_count} new sound mappings!")
    
    # Test the new sounds
    print("\n🎵 TESTING NEW SOUNDS:")
    test_sounds = ['chip_bet', 'card_shuffle', 'player_all_in', 'winner_announce']
    
    for sound in test_sounds:
        if sound in new_mappings:
            print(f"🎵 Testing {sound}...")
            sound_manager.play(sound)
    
    print("\n🎉 NEW SOUNDS APPLIED!")
    print("Your poker app now uses the high-quality sounds you added!")

def print_sound_quality_report():
    """Print a report of the current sound quality."""
    print("\n📊 SOUND QUALITY REPORT")
    print("=" * 30)
    
    # Analyze current sounds
    high_quality = []
    medium_quality = []
    low_quality = []
    
    for config_name, config in sound_manager.sound_configs.items():
        file_name = config.name
        if 'mp3' in file_name.lower():
            if '87543' in file_name or '86984' in file_name:  # High quality files
                high_quality.append((config_name, file_name))
            else:
                medium_quality.append((config_name, file_name))
        else:
            low_quality.append((config_name, file_name))
    
    print(f"🎯 HIGH QUALITY ({len(high_quality)}):")
    for sound_name, file_name in high_quality:
        print(f"  • {sound_name}: {file_name}")
    
    print(f"\n🎯 MEDIUM QUALITY ({len(medium_quality)}):")
    for sound_name, file_name in medium_quality:
        print(f"  • {sound_name}: {file_name}")
    
    print(f"\n🎯 LOW QUALITY ({len(low_quality)}):")
    for sound_name, file_name in low_quality[:5]:  # Show first 5
        print(f"  • {sound_name}: {file_name}")
    if len(low_quality) > 5:
        print(f"  ... and {len(low_quality) - 5} more")

if __name__ == "__main__":
    apply_new_sounds()
    print_sound_quality_report() 
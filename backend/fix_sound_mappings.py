#!/usr/bin/env python3
"""
Fix Sound Mappings

Properly maps all existing sound files and updates the sound manager.
"""

from enhanced_sound_manager import sound_manager
from pathlib import Path

def main():
    """Fix all sound mappings."""
    print("🔧 FIXING SOUND MAPPINGS")
    print("=" * 50)
    
    # Define the mappings based on the mapping script results
    mappings = {
        'card_shuffle': 'shuffling-cards-01-86984.mp3',
        'player_all_in': 'player_all_in.wav',
        'pot_rake': 'pot_rake.wav',
        'player_check': 'player_check.wav',
        'player_call': 'player_call.wav',
        'chip_bet': 'poker_chips1-87592.mp3',
        'winner_announce': 'money-bag-82960.mp3',
        'player_raise': 'player_raise.wav',
        'player_fold': 'player_fold.wav',
        'player_bet': 'player_bet.wav',
        'card_deal': 'card_deal.wav',
        'card_fold': 'card_fold.wav',
        'chip_collect': 'coin-257878.mp3',
        'chip_stack': 'money-bag-82960.mp3',
        'pot_win': 'money-bag-82960.mp3',
        'button_click': 'coin-257878.mp3',
        'button_move': 'button_move.wav',
        'turn_notify': 'turn_notify.wav',
        'pot_split': 'pot_split.wav',
        'notification': 'turn_notify.wav'
    }
    
    print(f"📊 MAPPING {len(mappings)} SOUNDS:")
    
    # Update sound manager
    if hasattr(sound_manager, 'sound_configs'):
        updated_count = 0
        
        for action, file_name in mappings.items():
            if action in sound_manager.sound_configs:
                config = sound_manager.sound_configs[action]
                old_file = config.name
                config.name = file_name
                print(f"  ✅ {action:20s} → {file_name}")
                updated_count += 1
            else:
                print(f"  ⚠️  {action:20s} → {file_name} (not in sound configs)")
        
        print(f"\n✅ UPDATED {updated_count} SOUND MAPPINGS")
        
        # Show current mappings
        print(f"\n🎵 CURRENT SOUND MAPPINGS:")
        for action, config in sound_manager.sound_configs.items():
            if hasattr(config, 'name'):
                print(f"  • {action:20s} → {config.name}")
        
    else:
        print("❌ Sound manager not properly initialized")

if __name__ == "__main__":
    main() 
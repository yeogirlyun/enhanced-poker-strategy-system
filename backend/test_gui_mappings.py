#!/usr/bin/env python3
"""
Test GUI Mappings

Shows what the GUI will display for current sound mappings.
"""

from enhanced_sound_manager import sound_manager

def main():
    """Test what the GUI will show for current mappings."""
    print("🎵 TESTING GUI MAPPINGS")
    print("=" * 50)
    
    if hasattr(sound_manager, 'sound_configs'):
        print(f"📊 SOUND MANAGER CONFIGS ({len(sound_manager.sound_configs)}):")
        
        mapped_sounds = []
        unmapped_sounds = []
        
        for config_name, config in sound_manager.sound_configs.items():
            if hasattr(config, 'name') and config.name and config.name != config_name:
                mapped_sounds.append((config_name, config.name))
                print(f"  ✅ {config_name:20s} → {config.name}")
            else:
                unmapped_sounds.append(config_name)
                print(f"  ❌ {config_name:20s} → No file mapped")
        
        print(f"\n📊 SUMMARY:")
        print(f"  • Total configs: {len(sound_manager.sound_configs)}")
        print(f"  • Mapped sounds: {len(mapped_sounds)}")
        print(f"  • Unmapped sounds: {len(unmapped_sounds)}")
        
        if len(mapped_sounds) == 0:
            print(f"\n⚠️  NO SOUNDS MAPPED!")
            print(f"   The GUI will show 'No file mapped' for all sounds.")
            print(f"   You need to add sound files using the Browse button.")
        elif len(mapped_sounds) < len(sound_manager.sound_configs):
            print(f"\n✅ {len(mapped_sounds)} SOUNDS MAPPED")
            print(f"   The GUI will show the mapped files for these sounds:")
            for sound_name, file_name in mapped_sounds:
                print(f"   • {sound_name} → {file_name}")
            
            print(f"\n❌ {len(unmapped_sounds)} SOUNDS NEED FILES")
            print(f"   The GUI will show 'No file mapped' for these sounds:")
            for sound_name in unmapped_sounds:
                print(f"   • {sound_name}")
        else:
            print(f"\n🎉 ALL SOUNDS MAPPED!")
            print(f"   The GUI will show all mapped files.")
        
    else:
        print("❌ Sound manager not properly initialized")

if __name__ == "__main__":
    main() 
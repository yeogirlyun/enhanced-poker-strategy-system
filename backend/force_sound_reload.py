#!/usr/bin/env python3
"""
Force Sound Reload

Forces the sound manager to reload after sound replacement.
"""

from enhanced_sound_manager import EnhancedSoundManager
import os

def main():
    """Force reload the sound manager."""
    print("🔄 FORCING SOUND MANAGER RELOAD")
    print("=" * 40)
    
    # Initialize sound manager
    sound_manager = EnhancedSoundManager()
    
    # Check current card_deal mapping
    print("📋 CURRENT MAPPING:")
    if "card_deal" in sound_manager.sound_configs:
        config = sound_manager.sound_configs["card_deal"]
        print(f"  card_deal → {config.name}")
    
    # Check if the new file exists
    new_file = "sounds/coin-257878.mp3"
    if os.path.exists(new_file):
        print(f"  ✅ New file exists: {new_file}")
        
        # Update the mapping
        if "card_deal" in sound_manager.sound_configs:
            config = sound_manager.sound_configs["card_deal"]
            old_name = config.name
            config.name = "coin-257878.mp3"
            print(f"  🔄 Updated mapping: {old_name} → {config.name}")
            
            # Clear the sound cache
            if "card_deal" in sound_manager.sounds:
                del sound_manager.sounds["card_deal"]
                print(f"  🗑️  Cleared sound cache for card_deal")
            
            # Reload sounds
            try:
                sound_manager._load_sounds()
                print(f"  ✅ Reloaded sounds")
            except Exception as e:
                print(f"  ❌ Error reloading: {e}")
    
    # Test the sound
    print(f"\n🔊 TESTING UPDATED SOUND:")
    try:
        sound_manager.play("card_deal")
        print(f"  ✅ Sound plays successfully")
    except Exception as e:
        print(f"  ❌ Sound test failed: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • Sound manager should now use the new file")
    print(f"  • Test the sound in the GUI")
    print(f"  • The new sound should play when you test it")

if __name__ == "__main__":
    main() 
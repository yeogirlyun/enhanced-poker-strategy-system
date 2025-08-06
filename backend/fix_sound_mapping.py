#!/usr/bin/env python3
"""
Fix Sound Mapping

Fixes the sound mapping to use the new replacement files.
"""

from enhanced_sound_manager import EnhancedSoundManager
import os

def main():
    """Fix the sound mapping."""
    print("🔧 FIXING SOUND MAPPING")
    print("=" * 40)
    
    # Initialize sound manager
    sound_manager = EnhancedSoundManager()
    
    # Check current mapping
    print("📋 CURRENT MAPPING:")
    if "card_deal" in sound_manager.sound_configs:
        config = sound_manager.sound_configs["card_deal"]
        print(f"  card_deal → {config.name}")
    
    # Check available files
    print(f"\n📁 AVAILABLE FILES:")
    sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
    for filename in os.listdir(sound_dir):
        if "card_deal" in filename:
            file_path = os.path.join(sound_dir, filename)
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {filename} ({file_size} bytes)")
    
    # Update the mapping to use the newest file
    print(f"\n🔄 UPDATING MAPPING:")
    if "card_deal" in sound_manager.sound_configs:
        config = sound_manager.sound_configs["card_deal"]
        old_name = config.name
        config.name = "card_deal_cash-register-kaching-376867.mp3"
        print(f"  {old_name} → {config.name}")
        
        # Reload the sound
        if sound_manager.reload_sound("card_deal"):
            print(f"  ✅ Sound reloaded successfully")
        else:
            print(f"  ❌ Sound reload failed")
    
    # Test the sound
    print(f"\n🔊 TESTING FIXED SOUND:")
    try:
        sound_manager.play("card_deal")
        print(f"  ✅ Sound plays successfully")
    except Exception as e:
        print(f"  ❌ Sound test failed: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • Sound mapping should now use the new file")
    print(f"  • Test the sound in the GUI")
    print(f"  • The new sound should play when you test it")

if __name__ == "__main__":
    main() 
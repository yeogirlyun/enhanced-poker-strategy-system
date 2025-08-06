#!/usr/bin/env python3
"""
Test Improved Sound Loading

Tests the improved sound loading mechanism.
"""

from enhanced_sound_manager import EnhancedSoundManager
import os

def main():
    """Test the improved sound loading."""
    print("🎵 TESTING IMPROVED SOUND LOADING")
    print("=" * 50)
    
    # Initialize sound manager
    sound_manager = EnhancedSoundManager()
    
    # Test card_deal sound
    print("📋 TESTING CARD_DEAL SOUND:")
    
    # Check current mapping
    if "card_deal" in sound_manager.sound_configs:
        config = sound_manager.sound_configs["card_deal"]
        print(f"  📁 Current mapping: card_deal → {config.name}")
        
        # Check if file exists
        sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
        sound_path = os.path.join(sound_dir, config.name)
        
        if os.path.exists(sound_path):
            print(f"  ✅ File exists: {config.name}")
            file_size = os.path.getsize(sound_path)
            print(f"  📊 File size: {file_size} bytes")
        else:
            print(f"  ❌ File missing: {config.name}")
    
    # Test playing the sound
    print(f"\n🔊 TESTING SOUND PLAYBACK:")
    try:
        sound_manager.play("card_deal")
        print(f"  ✅ Sound play command executed")
    except Exception as e:
        print(f"  ❌ Sound play failed: {e}")
    
    # Test reloading the sound
    print(f"\n🔄 TESTING SOUND RELOAD:")
    try:
        success = sound_manager.reload_sound("card_deal")
        if success:
            print(f"  ✅ Sound reload successful")
        else:
            print(f"  ❌ Sound reload failed")
    except Exception as e:
        print(f"  ❌ Sound reload error: {e}")
    
    # Test playing again after reload
    print(f"\n🔊 TESTING SOUND AFTER RELOAD:")
    try:
        sound_manager.play("card_deal")
        print(f"  ✅ Sound play after reload successful")
    except Exception as e:
        print(f"  ❌ Sound play after reload failed: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • Sound loading should now work better")
    print(f"  • Missing sounds will be loaded on demand")
    print(f"  • Sound replacement should work properly")

if __name__ == "__main__":
    main() 
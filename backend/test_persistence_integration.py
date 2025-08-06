#!/usr/bin/env python3
"""
Test Persistence Integration

Tests that custom sound mappings are loaded and applied correctly.
"""

from enhanced_sound_manager import EnhancedSoundManager
from sound_persistence import SoundPersistence
import os

def main():
    """Test the persistence integration."""
    print("💾 TESTING PERSISTENCE INTEGRATION")
    print("=" * 40)
    
    # First, set up a custom mapping
    persistence = SoundPersistence()
    persistence.set_custom_sound("fold", "card_fold.wav")
    print(f"📝 Set custom mapping: fold → card_fold.wav")
    
    # Now create a new sound manager (simulating app restart)
    print(f"🔄 Creating new sound manager...")
    sound_manager = EnhancedSoundManager()
    
    # Check if the custom mapping was applied
    if "fold" in sound_manager.sound_configs:
        config = sound_manager.sound_configs["fold"]
        print(f"📝 Sound config name: {config.name}")
        
        if config.name == "card_fold":
            print(f"✅ Custom mapping applied correctly!")
        else:
            print(f"❌ Custom mapping not applied. Expected 'card_fold', got '{config.name}'")
    else:
        print(f"❌ Sound 'fold' not found in configs")
    
    # Test playing the sound
    try:
        print(f"🔊 Testing play...")
        sound_manager.play("fold")
        print(f"✅ Play test successful")
    except Exception as e:
        print(f"❌ Play test failed: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • Custom mappings should persist between app restarts")
    print(f"  • Sound manager should load custom mappings on startup")
    print(f"  • Custom sounds should play correctly")

if __name__ == "__main__":
    main() 
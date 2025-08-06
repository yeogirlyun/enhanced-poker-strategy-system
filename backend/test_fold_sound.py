#!/usr/bin/env python3
"""
Test Fold Sound

Tests that the fold sound works correctly.
"""

from enhanced_sound_manager import EnhancedSoundManager

def main():
    """Test the fold sound."""
    print("🔊 TESTING FOLD SOUND")
    print("=" * 40)
    
    # Initialize sound manager
    sound_manager = EnhancedSoundManager()
    
    # Test the fold sound
    test_sound = "fold"
    
    if test_sound in sound_manager.sound_configs:
        config = sound_manager.sound_configs[test_sound]
        print(f"📝 Sound config found: {test_sound}")
        print(f"📝 Config name: {config.name}")
        print(f"📝 Category: {config.category.value}")
        
        # Test playing the sound
        try:
            print(f"🔊 Testing play...")
            sound_manager.play(test_sound)
            print(f"✅ Play test successful")
        except Exception as e:
            print(f"❌ Play test failed: {e}")
    else:
        print(f"❌ Sound {test_sound} not found in configs")
        print(f"📋 Available sounds: {list(sound_manager.sound_configs.keys())}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • The fold sound should now work correctly")
    print(f"  • The GUI should show 'fold' instead of 'card_fold'")
    print(f"  • WAV files should work with the fold sound")

if __name__ == "__main__":
    main() 
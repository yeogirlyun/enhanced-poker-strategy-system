#!/usr/bin/env python3
"""
Test WAV File Support

Tests the sound replacement system with WAV files.
"""

from enhanced_sound_manager import EnhancedSoundManager
import os

def main():
    """Test WAV file support in sound replacement."""
    print("🔊 TESTING WAV FILE SUPPORT")
    print("=" * 40)
    
    # Initialize sound manager
    sound_manager = EnhancedSoundManager()
    
    # Test with a WAV file
    test_sound = "fold"
    test_file = "sounds/card_fold.wav"
    
    if os.path.exists(test_file):
        print(f"📊 Test file: {test_file}")
        print(f"📊 File exists: ✅")
        
        # Simulate the replacement process
        print(f"🔄 Simulating sound replacement...")
        
        # Update the config name (like the GUI does)
        if test_sound in sound_manager.sound_configs:
            config = sound_manager.sound_configs[test_sound]
            original_name = config.name
            
            # Simulate what the GUI does
            new_filename = f"{test_sound}_test_replacement.wav"
            filename_without_ext = os.path.splitext(new_filename)[0]
            config.name = filename_without_ext
            
            print(f"📝 Original config name: {original_name}")
            print(f"📝 New config name: {config.name}")
            
            # Test reloading
            success = sound_manager.reload_sound(test_sound)
            print(f"🔄 Reload result: {'✅ Success' if success else '❌ Failed'}")
            
            # Test playing
            try:
                print(f"🔊 Testing play...")
                sound_manager.play(test_sound)
                print(f"✅ Play test successful")
            except Exception as e:
                print(f"❌ Play test failed: {e}")
        else:
            print(f"❌ Sound {test_sound} not found in configs")
    else:
        print(f"❌ Test file not found: {test_file}")
        print(f"📁 Available WAV files:")
        for filename in os.listdir("sounds"):
            if filename.endswith(".wav"):
                print(f"  • {filename}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • WAV files should now work with sound replacement")
    print(f"  • The system looks for files with .wav extension")
    print(f"  • Config names are stored without extensions")

if __name__ == "__main__":
    main() 
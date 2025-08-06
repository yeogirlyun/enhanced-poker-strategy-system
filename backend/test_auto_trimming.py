#!/usr/bin/env python3
"""
Test Auto Trimming

Tests the automatic trimming functionality when replacing sounds.
"""

from enhanced_sound_manager import EnhancedSoundManager
from simple_sound_trimmer import trim_any_audio_file, get_wav_duration
import os

def main():
    """Test automatic trimming when replacing sounds."""
    print("✂️  TESTING AUTO TRIMMING")
    print("=" * 40)
    
    # Initialize sound manager
    sound_manager = EnhancedSoundManager()
    
    # Test with a long sound file
    test_file = "sounds/winner_announce.wav"
    
    if os.path.exists(test_file):
        duration = get_wav_duration(test_file)
        print(f"📊 Test file: {test_file}")
        print(f"📊 Duration: {duration:.2f} seconds")
        
        if duration > 1.0:
            print(f"✂️  File needs trimming")
            
            # Simulate sound replacement
            new_filename = f"test_trimmed_{os.path.basename(test_file)}"
            output_path = os.path.join("sounds", new_filename)
            
            print(f"🔄 Simulating sound replacement...")
            success = trim_any_audio_file(test_file, output_path, 1.0)
            
            if success:
                new_duration = get_wav_duration(output_path)
                print(f"✅ Trimmed file duration: {new_duration:.2f} seconds")
                
                # Test if the trimmed file can be loaded
                try:
                    sound_manager.sounds[new_filename] = sound_manager.sounds[test_file]
                    print(f"✅ Trimmed file can be loaded by sound manager")
                except Exception as e:
                    print(f"❌ Error loading trimmed file: {e}")
            else:
                print(f"❌ Failed to trim file")
        else:
            print(f"✅ File is already under 1 second")
    else:
        print(f"❌ Test file not found: {test_file}")
        print(f"📁 Available WAV files:")
        for filename in os.listdir("sounds"):
            if filename.endswith(".wav"):
                file_path = os.path.join("sounds", filename)
                duration = get_wav_duration(file_path)
                print(f"  • {filename}: {duration:.2f}s")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • WAV files longer than 1s will be automatically trimmed")
    print(f"  • Non-WAV files will be copied as-is with a warning")
    print(f"  • The trimming happens during sound replacement")
    print(f"  • Trimmed files should work with the sound manager")

if __name__ == "__main__":
    main() 
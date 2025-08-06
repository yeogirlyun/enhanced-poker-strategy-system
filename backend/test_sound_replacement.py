#!/usr/bin/env python3
"""
Test Sound Replacement

Tests sound replacement and loading functionality.
"""

from enhanced_sound_manager import EnhancedSoundManager
import os

def main():
    """Test sound replacement functionality."""
    print("🎵 TESTING SOUND REPLACEMENT")
    print("=" * 40)
    
    # Initialize sound manager
    sound_manager = EnhancedSoundManager()
    
    # Test sound before replacement
    print("📋 TESTING ORIGINAL SOUND:")
    try:
        sound_manager.play("card_deal")
        print("  ✅ Original sound plays")
    except Exception as e:
        print(f"  ❌ Original sound failed: {e}")
    
    # Check current sound file
    if "card_deal" in sound_manager.sound_configs:
        config = sound_manager.sound_configs["card_deal"]
        print(f"  📁 Current file: {config.name}")
    
    # Check if file exists
    sound_file = "sounds/card_deal.wav"
    if os.path.exists(sound_file):
        print(f"  ✅ File exists: {sound_file}")
        file_size = os.path.getsize(sound_file)
        print(f"  📊 File size: {file_size} bytes")
    else:
        print(f"  ❌ File missing: {sound_file}")
    
    # Test the new file you replaced with
    new_file = "sounds/coin-257878.mp3"
    if os.path.exists(new_file):
        print(f"\n📁 NEW FILE INFO:")
        print(f"  ✅ File exists: {new_file}")
        file_size = os.path.getsize(new_file)
        print(f"  📊 File size: {file_size} bytes")
        
        # Try to load it directly
        try:
            import pygame
            pygame.mixer.init()
            sound = pygame.mixer.Sound(new_file)
            print(f"  ✅ File loads successfully")
            
            # Try to play it
            sound.play()
            print(f"  ✅ File plays successfully")
            
        except Exception as e:
            print(f"  ❌ File load/play failed: {e}")
    else:
        print(f"  ❌ New file missing: {new_file}")
    
    print(f"\n🎯 DIAGNOSIS:")
    print(f"  • Check if the new file is in the correct format")
    print(f"  • Check if pygame can load the file")
    print(f"  • Check if the sound manager is reloading correctly")

if __name__ == "__main__":
    main() 
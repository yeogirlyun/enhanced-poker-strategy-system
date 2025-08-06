#!/usr/bin/env python3
"""
Test script for poker sound system.
Run this after downloading sounds to verify everything works.
"""

import os
import sys
from pathlib import Path

# Add your app directory to path if needed
sys.path.append('.')

try:
    from enhanced_sound_manager import sound_manager
    
    def test_sounds():
        """Test all major sound categories."""
        print("🎵 Testing Poker Sound System...")
        
        # Test poker actions
        print("\n🎯 Testing poker actions...")
        actions = ["check", "call", "bet", "raise", "fold"]
        for action in actions:
            print(f"  Playing: {action}")
            sound_manager.play(action)
            input(f"  Did you hear '{action}'? (Press Enter to continue)")
        
        # Test card sounds
        print("\n🎴 Testing card sounds...")
        card_sounds = ["card_deal", "card_shuffle", "card_flip"]
        for sound in card_sounds:
            print(f"  Playing: {sound}")
            sound_manager.play(sound) 
            input(f"  Did you hear '{sound}'? (Press Enter to continue)")
        
        # Test UI sounds
        print("\n🖱️  Testing UI sounds...")
        ui_sounds = ["button_click", "turn_notify", "winner_announce"]
        for sound in ui_sounds:
            print(f"  Playing: {sound}")
            sound_manager.play(sound)
            input(f"  Did you hear '{sound}'? (Press Enter to continue)")
        
        # Test volume controls
        print("\n🔊 Testing volume controls...")
        print("  Setting low volume...")
        sound_manager.set_master_volume(0.3)
        sound_manager.play("chip_bet")
        input("  Did you hear quieter sound? (Press Enter)")
        
        print("  Setting normal volume...")
        sound_manager.set_master_volume(0.8)
        sound_manager.play("chip_bet")
        input("  Did you hear normal volume? (Press Enter)")
        
        print("\n✅ Sound system test complete!")
        
        # Print sound report
        report = sound_manager.get_sound_quality_report()
        print(f"\n📊 Sound System Report:")
        print(f"  Total sounds loaded: {report['total_sounds']}")
        print(f"  Sound enabled: {report['sound_enabled']}")
        print(f"  Pygame available: {report['pygame_available']}")
        
    if __name__ == "__main__":
        test_sounds()
        
except ImportError as e:
    print(f"❌ Error importing sound manager: {e}")
    print("Make sure enhanced_sound_manager.py is in your project directory.")

#!/usr/bin/env python3
"""
Test Voice Announcement System

Demonstrates the voice announcement system for poker actions.
"""

from voice_announcement_system import voice_system
import time

def main():
    """Test the voice announcement system."""
    print("🎤 VOICE ANNOUNCEMENT SYSTEM TEST")
    print("=" * 50)
    
    # Test voice types
    print("\n📋 Available Voice Types:")
    for voice_type in voice_system.get_available_voice_types():
        info = voice_system.get_voice_type_info(voice_type)
        print(f"  • {voice_type}: {info.get('description', 'N/A')}")
    
    # Test voice announcements
    print("\n🎤 Testing Voice Announcements:")
    test_actions = [
        'check', 'call', 'bet', 'raise', 'fold', 'all_in',
        'winner', 'your_turn', 'dealing', 'shuffling'
    ]
    
    for action in test_actions:
        print(f"🎤 Testing: {action}")
        voice_system.play_voice_announcement(action)
        time.sleep(1.5)  # Wait between announcements
    
    # Test voice type switching
    print("\n🎤 Testing Voice Type Switching:")
    voice_types = voice_system.get_available_voice_types()
    
    for voice_type in voice_types:
        print(f"🎤 Switching to: {voice_type}")
        voice_system.set_voice_type(voice_type)
        voice_system.play_voice_announcement('check')
        time.sleep(1)
    
    # Test combined sound + voice
    print("\n🎤 Testing Combined Sound + Voice:")
    voice_system.play_action_with_voice('player_bet')
    time.sleep(2)
    
    voice_system.play_action_with_voice('player_call')
    time.sleep(2)
    
    voice_system.play_action_with_voice('player_raise')
    time.sleep(2)
    
    print("\n✅ Voice announcement system test complete!")
    print("\n🎯 Next Steps:")
    print("  1. Install professional voice files in sounds/voice/")
    print("  2. Use the GUI to test and configure voices")
    print("  3. Integrate with your poker game actions")

if __name__ == "__main__":
    main() 
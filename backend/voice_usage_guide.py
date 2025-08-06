#!/usr/bin/env python3
"""
Voice Announcement System Usage Guide

This guide shows you how to use the AI voice features for poker actions.
"""

from voice_announcement_system import voice_system
from enhanced_sound_manager import sound_manager

def main():
    """Show how to use the voice announcement system."""
    print("🎤 VOICE ANNOUNCEMENT SYSTEM USAGE GUIDE")
    print("=" * 50)
    
    print("\n📋 AVAILABLE VOICE TYPES:")
    voice_types = voice_system.get_available_voice_types()
    for voice_type in voice_types:
        info = voice_system.get_voice_type_info(voice_type)
        print(f"  • {voice_type}: {info['description']}")
        print(f"    Style: {info['style']}")
        print(f"    Best for: {info['best_for']}")
    
    print("\n🎯 SUPPORTED POKER ACTIONS:")
    actions = [
        'check', 'call', 'bet', 'raise', 'fold', 'all_in',
        'winner', 'your_turn', 'dealing', 'shuffling'
    ]
    for action in actions:
        print(f"  • {action}")
    
    print("\n🚀 HOW TO USE:")
    print("1. Add voice files to sounds/voice/[voice_type]/")
    print("2. Use the GUI: Settings → 🎵 Sound Settings → 🎤 Voice Settings")
    print("3. Test voices in the voice settings panel")
    print("4. Voices will play automatically during poker actions")
    
    print("\n📁 VOICE FILE STRUCTURE:")
    print("sounds/voice/")
    print("├── dealer_male/")
    print("│   ├── check.wav")
    print("│   ├── call.wav")
    print("│   ├── bet.wav")
    print("│   └── raise.wav")
    print("├── dealer_female/")
    print("│   ├── check.wav")
    print("│   ├── call.wav")
    print("│   └── ...")
    print("├── announcer_male/")
    print("└── announcer_female/")
    
    print("\n🎮 INTEGRATION WITH POKER GAME:")
    print("• Voices play automatically when players make actions")
    print("• Different voice types for different situations")
    print("• Combines with sound effects for immersive experience")
    
    print("\n⚙️  CONFIGURATION:")
    print("• Change voice type in voice settings")
    print("• Adjust volume levels")
    print("• Enable/disable specific announcements")
    
    print("\n🎯 EXAMPLE USAGE:")
    print("# Play a voice announcement")
    print("voice_system.play_voice_announcement('check')")
    print()
    print("# Play action with both sound and voice")
    print("voice_system.play_action_with_voice('player_bet', amount=50)")
    print()
    print("# Change voice type")
    print("voice_system.set_voice_type('dealer_female')")

if __name__ == "__main__":
    main() 
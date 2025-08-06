#!/usr/bin/env python3
"""
Real Voice Generator

Creates actual spoken voice files for poker actions using text-to-speech.
"""

import os
import time
from pathlib import Path
import subprocess

def create_real_voice_files():
    """Create real voice files using text-to-speech."""
    print("🎤 REAL VOICE GENERATOR")
    print("=" * 30)
    
    # Create voice directory
    voice_dir = Path("sounds/voice")
    voice_dir.mkdir(exist_ok=True)
    
    # Voice types and their characteristics
    voice_types = {
        'dealer_male': {
            'description': 'Professional male casino dealer',
            'voice': 'Alex',  # macOS default male voice
            'rate': 150
        },
        'dealer_female': {
            'description': 'Professional female casino dealer',
            'voice': 'Victoria',  # macOS default female voice
            'rate': 160
        },
        'announcer_male': {
            'description': 'Casino announcer voice',
            'voice': 'Tom',  # Another male voice
            'rate': 140
        },
        'announcer_female': {
            'description': 'Female casino announcer',
            'voice': 'Samantha',  # Another female voice
            'rate': 155
        }
    }
    
    # Poker actions with natural speech
    actions = {
        'check': 'Check',
        'call': 'Call',
        'bet': 'Bet',
        'raise': 'Raise',
        'fold': 'Fold',
        'all_in': 'All in',
        'winner': 'Winner',
        'your_turn': 'Your turn',
        'dealing': 'Dealing cards',
        'shuffling': 'Shuffling deck'
    }
    
    for voice_type, config in voice_types.items():
        print(f"\n🎤 Generating {voice_type}:")
        voice_type_dir = voice_dir / voice_type
        voice_type_dir.mkdir(exist_ok=True)
        
        for action, text in actions.items():
            voice_file = voice_type_dir / f"{action}.wav"
            print(f"  🎤 Creating: {action}.wav - '{text}'")
            
            # Use macOS say command for text-to-speech
            cmd = [
                'say',
                '-v', config['voice'],
                '-r', str(config['rate']),
                '-o', str(voice_file),
                text
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"    ✅ Created successfully")
            except subprocess.CalledProcessError as e:
                print(f"    ❌ Error: {e}")
                # Fallback to default voice
                try:
                    fallback_cmd = [
                        'say',
                        '-o', str(voice_file),
                        text
                    ]
                    subprocess.run(fallback_cmd, check=True, capture_output=True)
                    print(f"    ✅ Created with fallback voice")
                except subprocess.CalledProcessError as e2:
                    print(f"    ❌ Fallback also failed: {e2}")
            except FileNotFoundError:
                print(f"    ❌ 'say' command not available (macOS only)")
                break
    
    print(f"\n✅ Voice generation complete!")
    print(f"📁 Files created in: {voice_dir}")

def test_voice_files():
    """Test the generated voice files."""
    print("\n🎤 TESTING VOICE FILES")
    print("=" * 25)
    
    voice_dir = Path("sounds/voice")
    
    for voice_type in ['dealer_male', 'dealer_female', 'announcer_male', 'announcer_female']:
        voice_type_dir = voice_dir / voice_type
        if voice_type_dir.exists():
            print(f"\n🎤 Testing {voice_type}:")
            
            for action in ['check', 'call', 'bet', 'raise', 'fold']:
                voice_file = voice_type_dir / f"{action}.wav"
                if voice_file.exists():
                    file_size = voice_file.stat().st_size
                    print(f"  ✅ {action}.wav ({file_size} bytes)")
                else:
                    print(f"  ❌ {action}.wav (missing)")

def main():
    """Main function."""
    print("🎤 REAL VOICE GENERATOR FOR POKER ACTIONS")
    print("=" * 50)
    
    # Check if we're on macOS
    if os.name != 'posix':
        print("❌ This script requires macOS for text-to-speech")
        return
    
    # Check if 'say' command is available
    try:
        subprocess.run(['say', 'test'], capture_output=True, check=True)
        print("✅ Text-to-speech available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Text-to-speech not available")
        print("💡 This script requires macOS with text-to-speech")
        return
    
    # Generate voice files
    create_real_voice_files()
    
    # Test the files
    test_voice_files()
    
    print(f"\n🎉 REAL VOICE GENERATION COMPLETE!")
    print(f"🎮 Launch the app to test the real voices!")

if __name__ == "__main__":
    main() 
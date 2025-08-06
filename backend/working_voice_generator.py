#!/usr/bin/env python3
"""
Working Voice Generator

Creates real voice files using available macOS voices.
"""

import subprocess
from pathlib import Path

def create_voice_files():
    """Create voice files using available voices."""
    print("🎤 WORKING VOICE GENERATOR")
    print("=" * 30)
    
    # Create voice directory
    voice_dir = Path("sounds/voice")
    voice_dir.mkdir(exist_ok=True)
    
    # Available voices (tested to work)
    voice_types = {
        'dealer_male': {
            'description': 'Professional male casino dealer',
            'voice': 'Daniel',  # Available male voice
        },
        'dealer_female': {
            'description': 'Professional female casino dealer',
            'voice': 'Samantha',  # Available female voice
        },
        'announcer_male': {
            'description': 'Casino announcer voice',
            'voice': 'Daniel',  # Use same voice for now
        },
        'announcer_female': {
            'description': 'Female casino announcer',
            'voice': 'Samantha',  # Use same voice for now
        }
    }
    
    # Poker actions
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
            
            # Use say command with available voice
            cmd = [
                'say',
                '-v', config['voice'],
                '-o', str(voice_file),
                text
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"    ✅ Created successfully")
                else:
                    print(f"    ❌ Error: {result.stderr}")
            except Exception as e:
                print(f"    ❌ Exception: {e}")
    
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
                    if file_size > 0:
                        print(f"  ✅ {action}.wav ({file_size} bytes)")
                    else:
                        print(f"  ❌ {action}.wav (empty file)")
                else:
                    print(f"  ❌ {action}.wav (missing)")

def main():
    """Main function."""
    print("🎤 WORKING VOICE GENERATOR FOR POKER ACTIONS")
    print("=" * 50)
    
    # Test say command
    try:
        result = subprocess.run(['say', 'test'], capture_output=True)
        if result.returncode == 0:
            print("✅ Text-to-speech available")
        else:
            print("❌ Text-to-speech not working")
            return
    except FileNotFoundError:
        print("❌ 'say' command not available")
        return
    
    # Generate voice files
    create_voice_files()
    
    # Test the files
    test_voice_files()
    
    print(f"\n🎉 VOICE GENERATION COMPLETE!")
    print(f"🎮 Launch the app to test the real voices!")

if __name__ == "__main__":
    main() 
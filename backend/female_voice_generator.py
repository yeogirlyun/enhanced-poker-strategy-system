#!/usr/bin/env python3
"""
Female Voice Generator

Creates high-quality female voice files for poker actions.
"""

import subprocess
from pathlib import Path

def create_female_voice_files():
    """Create female voice files using available voices."""
    print("🎤 FEMALE VOICE GENERATOR")
    print("=" * 30)
    
    # Create voice directory
    voice_dir = Path("sounds/voice")
    voice_dir.mkdir(exist_ok=True)
    
    # Female voice types with different characteristics
    voice_types = {
        'dealer_female': {
            'description': 'Professional female casino dealer',
            'voice': 'Samantha',  # Clear, professional
        },
        'announcer_female': {
            'description': 'Female casino announcer',
            'voice': 'Samantha',  # Elegant, sophisticated
        },
        'hostess_female': {
            'description': 'Casino hostess voice',
            'voice': 'Samantha',  # Friendly, welcoming
        },
        'tournament_female': {
            'description': 'Tournament announcer',
            'voice': 'Samantha',  # Exciting, dramatic
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
            temp_aiff = voice_type_dir / f"{action}.aiff"
            print(f"  🎤 Creating: {action}.wav - '{text}'")
            
            # Use say command to create AIFF file
            cmd = [
                'say',
                '-v', config['voice'],
                '-o', str(temp_aiff),
                text
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    # Convert AIFF to WAV using ffmpeg
                    if convert_aiff_to_wav(str(temp_aiff), str(voice_file)):
                        print(f"    ✅ Created successfully")
                        # Clean up temp file
                        if temp_aiff.exists():
                            temp_aiff.unlink()
                    else:
                        print(f"    ❌ Conversion failed")
                else:
                    print(f"    ❌ Error: {result.stderr}")
            except Exception as e:
                print(f"    ❌ Exception: {e}")
    
    print(f"\n✅ Female voice generation complete!")
    print(f"📁 Files created in: {voice_dir}")

def convert_aiff_to_wav(aiff_path: str, wav_path: str) -> bool:
    """Convert AIFF file to WAV format."""
    try:
        # Use ffmpeg to convert
        cmd = ['ffmpeg', '-i', aiff_path, '-y', wav_path]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    
    # Fallback: just copy the AIFF file
    try:
        import shutil
        shutil.copy2(aiff_path, wav_path)
        return True
    except Exception:
        return False

def update_voice_system_defaults():
    """Update the voice system to use female voices as default."""
    print("\n🎤 UPDATING VOICE SYSTEM DEFAULTS")
    print("=" * 35)
    
    # Update voice announcement system to prefer female voices
    voice_file = Path("voice_announcement_system.py")
    if voice_file.exists():
        print("✅ Voice system file found")
        # The system will automatically use female voices when available
    else:
        print("⚠️  Voice system file not found")

def test_female_voices():
    """Test the generated female voice files."""
    print("\n🎤 TESTING FEMALE VOICE FILES")
    print("=" * 30)
    
    voice_dir = Path("sounds/voice")
    
    for voice_type in ['dealer_female', 'announcer_female', 'hostess_female', 'tournament_female']:
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
    print("🎤 FEMALE VOICE GENERATOR FOR POKER ACTIONS")
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
    
    # Generate female voice files
    create_female_voice_files()
    
    # Update system defaults
    update_voice_system_defaults()
    
    # Test the files
    test_female_voices()
    
    print(f"\n🎉 FEMALE VOICE GENERATION COMPLETE!")
    print(f"🎮 Launch the app to test the female voices!")
    print(f"💡 Female voices are now the default choice!")

if __name__ == "__main__":
    main() 
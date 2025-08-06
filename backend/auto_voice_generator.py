#!/usr/bin/env python3
"""
Auto Voice Generator for Poker Actions

Automatically generates voice files for poker actions using text-to-speech.
Supports multiple voice types and can create professional casino-style announcements.
"""

import os
import time
import threading
from pathlib import Path
from typing import Dict, List

class AutoVoiceGenerator:
    """Automatically generates voice files for poker actions."""
    
    def __init__(self):
        self.sounds_dir = Path("sounds")
        self.voice_dir = self.sounds_dir / "voice"
        self.voice_dir.mkdir(exist_ok=True)
        
        # Voice announcements with casino-style text
        self.voice_announcements = {
            'check': ['Check', 'Checking', 'I check'],
            'call': ['Call', 'Calling', 'I call'],
            'bet': ['Bet', 'Betting', 'I bet'],
            'raise': ['Raise', 'Raising', 'I raise'],
            'fold': ['Fold', 'Folding', 'I fold'],
            'all_in': ['All in', 'All in push', 'Going all in'],
            'winner': ['Winner', 'Hand winner', 'Showdown winner'],
            'your_turn': ['Your turn', 'Action on you', 'Player action'],
            'dealing': ['Dealing', 'Dealing cards', 'Cards dealt'],
            'shuffling': ['Shuffling', 'Shuffling deck', 'Deck shuffled']
        }
        
        # Voice types and their characteristics
        self.voice_types = {
            'dealer_male': {
                'description': 'Professional male casino dealer',
                'style': 'authoritative, clear, casino-style',
                'rate': 150,
                'volume': 0.8
            },
            'dealer_female': {
                'description': 'Professional female casino dealer',
                'style': 'friendly, clear, welcoming',
                'rate': 160,
                'volume': 0.8
            },
            'announcer_male': {
                'description': 'Casino announcer voice',
                'style': 'dramatic, exciting, tournament-style',
                'rate': 140,
                'volume': 0.9
            },
            'announcer_female': {
                'description': 'Female casino announcer',
                'style': 'elegant, professional, sophisticated',
                'rate': 155,
                'volume': 0.8
            }
        }
    
    def generate_voice_files(self, voice_type: str = None):
        """Generate voice files for all poker actions."""
        print(f"🎤 AUTO VOICE GENERATOR")
        print(f"=" * 40)
        
        if voice_type:
            voice_types = [voice_type]
        else:
            voice_types = list(self.voice_types.keys())
        
        for vt in voice_types:
            print(f"\n🎤 Generating voices for: {vt}")
            self._generate_voice_type(vt)
    
    def _generate_voice_type(self, voice_type: str):
        """Generate voice files for a specific voice type."""
        voice_type_dir = self.voice_dir / voice_type
        voice_type_dir.mkdir(exist_ok=True)
        
        voice_config = self.voice_types[voice_type]
        
        # Try different TTS engines
        success = False
        
        # Try pyttsx3 first (most reliable)
        if not success:
            success = self._generate_with_pyttsx3(voice_type, voice_type_dir, voice_config)
        
        # Try gTTS (Google Text-to-Speech) as fallback
        if not success:
            success = self._generate_with_gtts(voice_type, voice_type_dir, voice_config)
        
        # Try espeak as last resort
        if not success:
            success = self._generate_with_espeak(voice_type, voice_type_dir, voice_config)
        
        if success:
            print(f"✅ Successfully generated voice files for {voice_type}")
        else:
            print(f"❌ Failed to generate voice files for {voice_type}")
            print(f"💡 You can manually add voice files to: {voice_type_dir}")
    
    def _generate_with_pyttsx3(self, voice_type: str, voice_dir: Path, config: Dict) -> bool:
        """Generate voice files using pyttsx3."""
        try:
            import pyttsx3
            import wave
            import struct
            import tempfile
            import os
            
            engine = pyttsx3.init()
            
            # Set voice properties
            voices = engine.getProperty('voices')
            if voices:
                # Use first available voice
                engine.setProperty('voice', voices[0].id)
            
            engine.setProperty('rate', config['rate'])
            engine.setProperty('volume', config['volume'])
            
            # Generate voice files
            for action, texts in self.voice_announcements.items():
                voice_file = voice_dir / f"{action}.wav"
                
                if not voice_file.exists():
                    print(f"  🎤 Creating: {action}.wav")
                    
                    # Create a temporary file
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    try:
                        # Save to temporary file
                        engine.save_to_file(texts[0], temp_path)
                        engine.runAndWait()
                        
                        # Convert to proper WAV format
                        self._convert_to_proper_wav(temp_path, str(voice_file))
                        
                        # Clean up temp file
                        os.unlink(temp_path)
                        
                    except Exception as e:
                        print(f"    ❌ Error creating {action}.wav: {e}")
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                    
                    time.sleep(0.5)  # Small delay between files
            
            return True
            
        except ImportError:
            print(f"  ⚠️  pyttsx3 not available")
            return False
        except Exception as e:
            print(f"  ❌ pyttsx3 error: {e}")
            return False
    
    def _convert_to_proper_wav(self, input_path: str, output_path: str):
        """Convert pyttsx3 output to proper WAV format."""
        try:
            import wave
            import struct
            
            # Read the pyttsx3 output (it's already WAV but might have format issues)
            with wave.open(input_path, 'rb') as wav_in:
                frames = wav_in.readframes(wav_in.getnframes())
                params = wav_in.getparams()
            
            # Write to proper WAV format
            with wave.open(output_path, 'wb') as wav_out:
                wav_out.setparams(params)
                wav_out.writeframes(frames)
                
        except Exception as e:
            print(f"    ⚠️  WAV conversion failed: {e}")
            # Fallback: just copy the file
            import shutil
            shutil.copy2(input_path, output_path)
    
    def _generate_with_gtts(self, voice_type: str, voice_dir: Path, config: Dict) -> bool:
        """Generate voice files using gTTS (Google Text-to-Speech)."""
        try:
            from gtts import gTTS
            
            # Generate voice files
            for action, texts in self.voice_announcements.items():
                voice_file = voice_dir / f"{action}.wav"
                
                if not voice_file.exists():
                    print(f"  🎤 Creating: {action}.wav (gTTS)")
                    # Use the first text option for each action
                    tts = gTTS(text=texts[0], lang='en', slow=False)
                    tts.save(str(voice_file))
                    time.sleep(0.5)  # Small delay between files
            
            return True
            
        except ImportError:
            print(f"  ⚠️  gTTS not available")
            return False
        except Exception as e:
            print(f"  ❌ gTTS error: {e}")
            return False
    
    def _generate_with_espeak(self, voice_type: str, voice_dir: Path, config: Dict) -> bool:
        """Generate voice files using espeak."""
        try:
            import subprocess
            
            # Generate voice files
            for action, texts in self.voice_announcements.items():
                voice_file = voice_dir / f"{action}.wav"
                
                if not voice_file.exists():
                    print(f"  🎤 Creating: {action}.wav (espeak)")
                    # Use the first text option for each action
                    cmd = [
                        'espeak', 
                        '-w', str(voice_file),
                        '-s', str(config['rate']),
                        '-v', 'en',
                        texts[0]
                    ]
                    subprocess.run(cmd, check=True)
                    time.sleep(0.5)  # Small delay between files
            
            return True
            
        except FileNotFoundError:
            print(f"  ⚠️  espeak not available")
            return False
        except Exception as e:
            print(f"  ❌ espeak error: {e}")
            return False
    
    def install_dependencies(self):
        """Install required dependencies for voice generation."""
        print(f"🔧 INSTALLING VOICE GENERATION DEPENDENCIES")
        print(f"=" * 50)
        
        dependencies = [
            'pyttsx3',
            'gtts',
            'espeak'  # System package
        ]
        
        for dep in dependencies:
            if dep == 'espeak':
                print(f"📦 Installing espeak (system package)...")
                try:
                    import subprocess
                    subprocess.run(['brew', 'install', 'espeak'], check=True)
                    print(f"  ✅ espeak installed")
                except:
                    print(f"  ⚠️  espeak installation failed (try: brew install espeak)")
            else:
                print(f"📦 Installing {dep}...")
                try:
                    import subprocess
                    subprocess.run(['pip3', 'install', dep], check=True)
                    print(f"  ✅ {dep} installed")
                except:
                    print(f"  ❌ {dep} installation failed")
    
    def test_generated_voices(self):
        """Test the generated voice files."""
        print(f"🎤 TESTING GENERATED VOICES")
        print(f"=" * 30)
        
        for voice_type in self.voice_types.keys():
            voice_type_dir = self.voice_dir / voice_type
            if voice_type_dir.exists():
                print(f"\n🎤 Testing {voice_type}:")
                
                for action in self.voice_announcements.keys():
                    voice_file = voice_type_dir / f"{action}.wav"
                    if voice_file.exists():
                        print(f"  ✅ {action}.wav")
                    else:
                        print(f"  ❌ {action}.wav (missing)")

def main():
    """Main function to generate voice files."""
    generator = AutoVoiceGenerator()
    
    print("🎤 AUTO VOICE GENERATOR FOR POKER ACTIONS")
    print("=" * 50)
    
    # Check if dependencies are available
    try:
        import pyttsx3
        print("✅ pyttsx3 available")
    except ImportError:
        print("❌ pyttsx3 not available")
        print("💡 Run: pip3 install pyttsx3")
        print("💡 Or run: python3 auto_voice_generator.py --install")
        return
    
    # Generate voice files for all voice types
    generator.generate_voice_files()
    
    # Test the generated voices
    generator.test_generated_voices()
    
    print(f"\n🎉 VOICE GENERATION COMPLETE!")
    print(f"📁 Voice files created in: {generator.voice_dir}")
    print(f"🎮 Launch the app to test the voices!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        generator = AutoVoiceGenerator()
        generator.install_dependencies()
    else:
        main() 
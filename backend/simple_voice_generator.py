#!/usr/bin/env python3
"""
Simple Voice Generator

Creates basic WAV files for poker voice announcements.
"""

import wave
import struct
import math
from pathlib import Path

def create_simple_wav(text: str, output_path: str, duration: float = 1.0, frequency: int = 440):
    """Create a simple WAV file with a tone."""
    # WAV parameters
    sample_rate = 44100
    amplitude = 0.3
    
    # Calculate number of frames
    num_frames = int(sample_rate * duration)
    
    # Create WAV file
    with wave.open(output_path, 'wb') as wav_file:
        # Set parameters: 1 channel, 2 bytes per sample, sample rate
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        # Generate audio data (simple sine wave)
        for i in range(num_frames):
            # Create a simple tone
            value = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
            # Convert to 16-bit integer
            packed_value = struct.pack('<h', int(value * 32767))
            wav_file.writeframes(packed_value)

def main():
    """Generate simple voice files for poker actions."""
    print("🎤 SIMPLE VOICE GENERATOR")
    print("=" * 30)
    
    # Create voice directory
    voice_dir = Path("sounds/voice")
    voice_dir.mkdir(exist_ok=True)
    
    # Voice types
    voice_types = ['dealer_male', 'dealer_female', 'announcer_male', 'announcer_female']
    
    # Poker actions with different frequencies for variety
    actions = {
        'check': 440,    # A4
        'call': 494,     # B4
        'bet': 523,      # C5
        'raise': 587,    # D5
        'fold': 659,     # E5
        'all_in': 698,   # F5
        'winner': 784,   # G5
        'your_turn': 880, # A5
        'dealing': 988,  # B5
        'shuffling': 1047 # C6
    }
    
    for voice_type in voice_types:
        print(f"\n🎤 Generating {voice_type}:")
        voice_type_dir = voice_dir / voice_type
        voice_type_dir.mkdir(exist_ok=True)
        
        for action, frequency in actions.items():
            voice_file = voice_type_dir / f"{action}.wav"
            print(f"  🎤 Creating: {action}.wav (freq: {frequency}Hz)")
            create_simple_wav(action, str(voice_file), duration=0.5, frequency=frequency)
    
    print(f"\n✅ Voice generation complete!")
    print(f"📁 Files created in: {voice_dir}")

if __name__ == "__main__":
    main() 
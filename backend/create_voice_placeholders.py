#!/usr/bin/env python3
"""
Script to create placeholder voice files for testing the voice system.
This creates minimal WAV files that can be used as placeholders.
"""

import os
import struct
import wave

def create_placeholder_wav(filename, duration_ms=1000, sample_rate=22050):
    """Create a placeholder WAV file with a simple tone."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Generate a simple sine wave tone
    sample_rate = 22050
    duration = duration_ms / 1000.0
    num_samples = int(sample_rate * duration)
    
    # Create a simple beep tone (440 Hz)
    frequency = 440.0
    amplitude = 0.3
    
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Generate samples
        for i in range(num_samples):
            t = float(i) / sample_rate
            sample_value = int(32767 * amplitude * (t * frequency * 2 * 3.14159))
            # Clamp to valid range
            sample_value = max(-32767, min(32767, sample_value))
            wav_file.writeframes(struct.pack('h', sample_value))
    
    print(f"✅ Created placeholder: {filename}")

def create_all_voice_placeholders():
    """Create placeholder voice files for all voice categories."""
    voice_categories = [
        "announcer_female",
        "announcer_male", 
        "dealer_female",
        "dealer_male",
        "hostess_female",
        "tournament_female"
    ]
    
    voice_actions = [
        "all_in", "bet", "call", "check", "dealing", 
        "fold", "raise", "shuffling", "winner", "your_turn"
    ]
    
    base_dir = "sounds/voice"
    
    for category in voice_categories:
        for action in voice_actions:
            filename = f"{base_dir}/{category}/{action}.wav"
            create_placeholder_wav(filename, duration_ms=800)
    
    print(f"🎵 Created {len(voice_categories) * len(voice_actions)} voice placeholder files")

if __name__ == "__main__":
    create_all_voice_placeholders()

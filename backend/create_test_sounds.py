#!/usr/bin/env python3
"""
Create test sound files for poker game
"""

import wave
import struct
import math
import os

def create_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.3):
    """Create a simple sine wave sound."""
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        sample = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
        samples.append(int(sample * 32767))
    
    return samples

def save_wav(filename, samples, sample_rate=44100):
    """Save samples as a WAV file."""
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            wav_file.writeframes(struct.pack('<h', sample))

def create_test_sounds():
    """Create basic test sound files."""
    sounds_dir = "sounds"
    os.makedirs(sounds_dir, exist_ok=True)
    
    # Create different sound effects
    sounds = {
        "card_deal": (800, 0.2),      # Higher pitch, short duration
        "chip_bet": (400, 0.3),       # Medium pitch, medium duration
        "player_call": (600, 0.25),   # Medium-high pitch
        "player_fold": (300, 0.4),    # Lower pitch, longer duration
        "player_check": (700, 0.2),   # High pitch, short
        "player_raise": (500, 0.35),  # Medium pitch, medium-long
        "button_move": (900, 0.15),   # Very high pitch, very short
    }
    
    for sound_name, (freq, duration) in sounds.items():
        samples = create_sine_wave(freq, duration)
        filename = os.path.join(sounds_dir, f"{sound_name}.wav")
        save_wav(filename, samples)
        print(f"Created: {filename}")

if __name__ == "__main__":
    create_test_sounds()
    print("✅ Test sound files created successfully!") 
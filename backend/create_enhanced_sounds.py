#!/usr/bin/env python3
"""
Create Enhanced Poker Sound Effects

Generates high-quality sound effects for poker actions with distinct characteristics
for each action type, following modern poker game sound design principles.
"""

import wave
import struct
import math
import os
import random

def create_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.3):
    """Create a simple sine wave sound."""
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        sample = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
        samples.append(int(sample * 32767))
    
    return samples

def create_chip_sound(base_freq, duration, sample_rate=44100):
    """Create a chip stacking sound with multiple frequencies."""
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        # Multiple frequencies to simulate chip stacking
        sample = 0.2 * math.sin(2 * math.pi * base_freq * i / sample_rate)
        sample += 0.1 * math.sin(2 * math.pi * (base_freq * 1.5) * i / sample_rate)
        sample += 0.05 * math.sin(2 * math.pi * (base_freq * 2.2) * i / sample_rate)
        samples.append(int(sample * 32767))
    
    return samples

def create_card_sound(base_freq, duration, sample_rate=44100):
    """Create a card dealing sound with quick attack and decay."""
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        # Quick attack, gentle decay
        envelope = math.exp(-i / (sample_rate * 0.1)) if i < num_samples * 0.3 else 0.3
        sample = envelope * math.sin(2 * math.pi * base_freq * i / sample_rate)
        samples.append(int(sample * 32767))
    
    return samples

def create_fold_sound(base_freq, duration, sample_rate=44100):
    """Create a card folding sound - soft and gentle."""
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        # Soft, gentle sound
        envelope = 0.3 * math.exp(-i / (sample_rate * 0.2))
        sample = envelope * math.sin(2 * math.pi * base_freq * i / sample_rate)
        samples.append(int(sample * 32767))
    
    return samples

def create_winner_sound(base_freq, duration, sample_rate=44100):
    """Create a celebratory winner sound with ascending notes."""
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        # Ascending frequency for celebratory effect
        freq = base_freq + (i / num_samples) * base_freq * 0.5
        envelope = 0.4 * math.exp(-i / (sample_rate * 0.3))
        sample = envelope * math.sin(2 * math.pi * freq * i / sample_rate)
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

def create_enhanced_sounds():
    """Create enhanced poker sound effects with distinct characteristics."""
    sounds_dir = "sounds"
    os.makedirs(sounds_dir, exist_ok=True)
    
    # Define sound characteristics based on modern poker game design
    sounds = {
        "card_deal": (800, 0.15, create_card_sound),      # Quick, sharp card dealing
        "card_fold": (300, 0.4, create_fold_sound),       # Soft, gentle folding
        "player_check": (700, 0.2, create_sine_wave),     # Sharp, distinct tap
        "player_call": (500, 0.25, create_chip_sound),    # Crisp chip placement
        "player_bet": (400, 0.3, create_chip_sound),      # Medium chip stack
        "player_raise": (600, 0.35, create_chip_sound),   # Emphatic chip cascade
        "player_all_in": (200, 0.8, create_winner_sound), # Dramatic all-in sound
        "pot_rake": (350, 0.6, create_chip_sound),        # Satisfying pot collection
        "pot_split": (450, 0.4, create_chip_sound),       # Chip division sound
        "winner_announce": (600, 0.5, create_winner_sound), # Celebratory winner
        "turn_notify": (900, 0.1, create_sine_wave),      # Quick attention chime
        "button_move": (750, 0.12, create_sine_wave),     # Button movement
    }
    
    for sound_name, (freq, duration, generator_func) in sounds.items():
        samples = generator_func(freq, duration)
        filename = os.path.join(sounds_dir, f"{sound_name}.wav")
        save_wav(filename, samples)
    

if __name__ == "__main__":
    create_enhanced_sounds() 
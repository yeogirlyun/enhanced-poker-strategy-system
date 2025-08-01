#!/usr/bin/env python3
"""
Sound Manager for Poker Table

Provides sound effects for the poker table interface.
Works with or without pygame for maximum compatibility.
"""

import os
import time
from typing import Dict, Optional

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️  Pygame not available. Sound effects will be simulated.")


class SoundManager:
    """Manages sound effects for the poker table."""
    
    def __init__(self):
        self.sounds = {}
        self.sound_enabled = True
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self._load_sounds()
            except Exception as e:
                print(f"⚠️  Sound initialization failed: {e}")
                self.sound_enabled = False
        else:
            print("🔊 Using simulated sound effects")
    
    def _load_sounds(self):
        """Load all sound effects from the sounds directory."""
        sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
        if not os.path.isdir(sound_dir):
            print(f"⚠️  'sounds' directory not found at {sound_dir}. Using simulated sounds.")
            self.sound_enabled = False
            return
            
        # Track which sounds are authentic vs generated
        authentic_sounds = []
        generated_sounds = []
        
        for filename in os.listdir(sound_dir):
            if filename.endswith((".wav", ".ogg")):
                name = os.path.splitext(filename)[0]
                path = os.path.join(sound_dir, filename)
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    
                    # Check if this is an authentic sound (larger file size indicates real audio)
                    file_size = os.path.getsize(path)
                    if file_size > 20000:  # Files larger than 20KB are likely authentic
                        authentic_sounds.append(name)
                        print(f"🎵 Loaded AUTHENTIC sound: {name} ({file_size/1024:.1f}KB)")
                    else:
                        generated_sounds.append(name)
                        print(f"✅ Loaded generated sound: {name}")
                        
                except pygame.error as e:
                    print(f"⚠️  Could not load sound '{filename}': {e}")
        
        # Report sound loading summary
        if authentic_sounds:
            print(f"🎧 Authentic sounds loaded: {', '.join(authentic_sounds)}")
        if generated_sounds:
            print(f"🎵 Generated sounds loaded: {len(generated_sounds)}")
    
    def play(self, sound_name: str):
        """Play a sound effect."""
        if not self.sound_enabled:
            return
            
        if sound_name in self.sounds and PYGAME_AVAILABLE:
            try:
                self.sounds[sound_name].play()
                print(f"🔊 Playing: {sound_name}")
            except Exception as e:
                print(f"⚠️  Error playing sound '{sound_name}': {e}")
        else:
            # Simulate sound with console output
            sound_emojis = {
                "card_deal": "🎴", "card_fold": "📄", "player_check": "✅",
                "player_call": "📞", "player_bet": "💰", "player_raise": "📈",
                "player_all_in": "🔥", "pot_rake": "🏦", "winner_announce": "🎉",
                "turn_notify": "🔔", "pot_split": "⚖️", "chip_bet": "💰",
                "button_move": "🎯"
            }
            emoji = sound_emojis.get(sound_name, "🔊")
            print(f"{emoji} Sound (Simulated): {sound_name}")
    
    def enable_sound(self):
        """Enable sound effects."""
        self.sound_enabled = True
        print("🔊 Sound effects enabled")
    
    def disable_sound(self):
        """Disable sound effects."""
        self.sound_enabled = False
        print("🔇 Sound effects disabled")
    
    def get_available_sounds(self) -> list:
        """Get list of available sound names."""
        return list(self.sounds.keys()) if PYGAME_AVAILABLE else []


if __name__ == "__main__":
    # Test the sound manager
    sm = SoundManager()
    sm.play("card_deal")
    sm.play("chip_bet")
    sm.play("player_fold") 
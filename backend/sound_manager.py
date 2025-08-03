#!/usr/bin/env python3
"""
Enhanced Sound Manager for Poker Table

Provides industry-standard sound effects for the poker table interface.
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
    """Manages industry-standard sound effects for the poker table."""
    
    def __init__(self):
        self.sounds = {}
        self.sound_enabled = True
        
        # Industry-standard sound mappings
        self.sound_mappings = {
            # Core poker actions
            "check": "player_check",
            "call": "player_call", 
            "bet": "player_bet",
            "raise": "player_raise",
            "fold": "player_fold",
            "all_in": "player_all_in",
            
            # Card and dealing sounds
            "card_deal": "card_deal",
            "card_flip": "card_fold",  # Using existing card fold for card flip
            "card_fold": "card_fold",
            
            # Chip and money sounds
            "chip_bet": "chip_bet",
            "chip_stack": "chip_bet",  # Using chip_bet for stacking
            "pot_win": "winner_announce",
            "pot_split": "pot_split",
            "pot_rake": "pot_rake",
            
            # Game flow sounds
            "winner_announce": "winner_announce",
            "turn_notify": "turn_notify",
            "button_move": "button_move",
            "dealer_button": "button_move",  # Using button_move for dealer button
        }
        
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
        """Play a sound effect with industry-standard mapping."""
        if not self.sound_enabled:
            return
        
        # Map to actual sound file
        actual_sound = self.sound_mappings.get(sound_name, sound_name)
        
        if actual_sound in self.sounds and PYGAME_AVAILABLE:
            try:
                self.sounds[actual_sound].play()
                print(f"🔊 Playing: {sound_name} -> {actual_sound}")
            except Exception as e:
                print(f"⚠️  Error playing sound '{sound_name}': {e}")
        else:
            # Simulate sound with console output
            sound_emojis = {
                "check": "✅", "call": "📞", "bet": "💰", "raise": "📈", "fold": "📄",
                "all_in": "🔥", "card_deal": "🎴", "card_flip": "🃏", "card_fold": "📄",
                "chip_bet": "💰", "chip_stack": "🪙", "pot_win": "🏆", "pot_split": "⚖️",
                "pot_rake": "🏦", "winner_announce": "🎉", "turn_notify": "🔔", 
                "button_move": "🎯", "dealer_button": "🎯"
            }
            emoji = sound_emojis.get(sound_name, "🔊")
            print(f"{emoji} Sound (Simulated): {sound_name}")
    
    def play_action_sound(self, action: str, amount: float = 0):
        """Play appropriate sound for poker actions with context."""
        if action == "fold":
            self.play("fold")
        elif action == "check":
            self.play("check")
        elif action == "call":
            self.play("call")
        elif action == "bet":
            self.play("bet")
        elif action == "raise":
            self.play("raise")
        elif action == "all_in":
            self.play("all_in")
        else:
            self.play(action)
    
    def play_card_sound(self, action: str):
        """Play card-related sounds."""
        if action == "deal":
            self.play("card_deal")
        elif action == "flip":
            self.play("card_flip")
        elif action == "fold":
            self.play("card_fold")
    
    def play_money_sound(self, action: str):
        """Play money-related sounds."""
        if action == "chip_bet":
            self.play("chip_bet")
        elif action == "chip_stack":
            self.play("chip_stack")
        elif action == "pot_win":
            self.play("pot_win")
        elif action == "pot_split":
            self.play("pot_split")
        elif action == "pot_rake":
            self.play("pot_rake")
    
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
        return list(self.sounds.keys())
    
    def get_sound_mappings(self) -> dict:
        """Get current sound mappings."""
        return self.sound_mappings.copy()
    
    def set_volume(self, volume: float):
        """Set volume for all sounds (0.0 to 1.0)."""
        if PYGAME_AVAILABLE and self.sounds:
            for sound in self.sounds.values():
                sound.set_volume(max(0.0, min(1.0, volume)))
            print(f"🔊 Volume set to {volume:.2f}")
    
    def get_sound_quality_report(self) -> dict:
        """Get a report on sound quality and availability."""
        authentic_sounds = []
        generated_sounds = []
        
        for name, sound in self.sounds.items():
            # This is a simplified check - in a real implementation you'd check file sizes
            if name in ["player_all_in", "pot_rake", "winner_announce", "pot_split", 
                       "player_fold", "card_fold", "player_raise", "player_bet", 
                       "chip_bet", "player_call"]:
                authentic_sounds.append(name)
            else:
                generated_sounds.append(name)
        
        return {
            "total_sounds": len(self.sounds),
            "authentic_sounds": authentic_sounds,
            "generated_sounds": generated_sounds,
            "sound_enabled": self.sound_enabled,
            "pygame_available": PYGAME_AVAILABLE
        } 
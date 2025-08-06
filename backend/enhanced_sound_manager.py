#!/usr/bin/env python3
"""
Enhanced Sound Manager for Poker Table - Game App Style

Provides premium sound effects similar to popular mobile game apps.
Features include:
- Multiple sound categories (UI, Game, Ambient)
- Volume control per category
- Sound layering and mixing
- Contextual sound effects
- Premium audio quality
"""

import os
import time
import random
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class SoundCategory(Enum):
    """Sound categories for different types of audio."""
    UI = "ui"           # Interface sounds (buttons, notifications)
    GAME = "game"       # Core game sounds (cards, chips)
    AMBIENT = "ambient" # Background atmosphere
    VOICE = "voice"     # Voice announcements
    MUSIC = "music"     # Background music

@dataclass
class SoundConfig:
    """Configuration for individual sound effects."""
    name: str
    category: SoundCategory
    volume: float = 1.0
    pitch: float = 1.0
    loop: bool = False
    fade_in: float = 0.0
    fade_out: float = 0.0

class EnhancedSoundManager:
    """Premium sound manager with game app-style features."""
    
    def __init__(self):
        self.sounds = {}
        self.sound_enabled = True
        self.master_volume = 0.8
        self.category_volumes = {
            SoundCategory.UI: 0.9,
            SoundCategory.GAME: 1.0,
            SoundCategory.AMBIENT: 0.6,
            SoundCategory.VOICE: 0.8,
            SoundCategory.MUSIC: 0.5
        }
        
        # Premium sound mappings with categories
        self.sound_configs = {
            # UI Sounds (like mobile game buttons)
            "button_click": SoundConfig("button_click", SoundCategory.UI, 0.8),
            "button_hover": SoundConfig("button_hover", SoundCategory.UI, 0.6),
            "notification": SoundConfig("notification", SoundCategory.UI, 0.9),
            "success": SoundConfig("success", SoundCategory.UI, 0.9),
            "error": SoundConfig("error", SoundCategory.UI, 0.8),
            "menu_open": SoundConfig("menu_open", SoundCategory.UI, 0.7),
            "menu_close": SoundConfig("menu_close", SoundCategory.UI, 0.7),
            
            # Game Sounds (core poker actions)
            "check": SoundConfig("player_check", SoundCategory.GAME, 1.0),
            "call": SoundConfig("player_call", SoundCategory.GAME, 1.0),
            "bet": SoundConfig("player_bet", SoundCategory.GAME, 1.0),
            "raise": SoundConfig("player_raise", SoundCategory.GAME, 1.0),
            "fold": SoundConfig("player_fold", SoundCategory.GAME, 1.0),
            "all_in": SoundConfig("player_all_in", SoundCategory.GAME, 1.2),
            
            # Card Sounds
            "card_deal": SoundConfig("card_deal", SoundCategory.GAME, 0.9),
            "card_flip": SoundConfig("card_fold", SoundCategory.GAME, 0.8),
            "card_shuffle": SoundConfig("card_deal", SoundCategory.GAME, 0.7),
            
            # Chip Sounds
            "chip_bet": SoundConfig("chip_bet", SoundCategory.GAME, 1.0),
            "chip_stack": SoundConfig("chip_bet", SoundCategory.GAME, 0.8),
            "chip_collect": SoundConfig("chip_bet", SoundCategory.GAME, 0.9),
            
            # Pot Sounds
            "pot_win": SoundConfig("winner_announce", SoundCategory.GAME, 1.1),
            "pot_split": SoundConfig("pot_split", SoundCategory.GAME, 1.0),
            "pot_rake": SoundConfig("pot_rake", SoundCategory.GAME, 0.8),
            
            # Game Flow
            "turn_notify": SoundConfig("turn_notify", SoundCategory.GAME, 0.9),
            "button_move": SoundConfig("button_move", SoundCategory.GAME, 0.8),
            "dealer_button": SoundConfig("button_move", SoundCategory.GAME, 0.8),
            
            # Ambient Sounds
            "table_ambient": SoundConfig("card_deal", SoundCategory.AMBIENT, 0.3, loop=True),
            "crowd_murmur": SoundConfig("card_deal", SoundCategory.AMBIENT, 0.2, loop=True),
            
            # Voice Announcements
            "winner_announce": SoundConfig("winner_announce", SoundCategory.VOICE, 1.0),
            "all_in_announce": SoundConfig("player_all_in", SoundCategory.VOICE, 1.1),
        }
        
        # Sound layering for premium effects
        self.sound_layers = {
            "big_win": ["pot_win", "chip_collect", "success"],
            "all_in_action": ["all_in", "chip_bet", "notification"],
            "fold_sequence": ["fold", "card_flip"],
            "raise_sequence": ["raise", "chip_bet", "button_click"],
        }
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self._load_sounds()
                
                # Load and apply custom mappings after sounds are loaded
                self._load_custom_mappings()
                self._apply_custom_mappings()
                
            except Exception as e:
                print(f"Sound initialization error: {e}")
    
    def _load_sounds(self):
        """Load and categorize sound files."""
        sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
        if not os.path.exists(sound_dir):
            return
        
        loaded_sounds = []
        for filename in os.listdir(sound_dir):
            if filename.endswith((".wav", ".ogg", ".mp3")):
                name = os.path.splitext(filename)[0]
                path = os.path.join(sound_dir, filename)
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    loaded_sounds.append(name)
                except Exception as e:
                    print(f"Failed to load sound {name}: {e}")
        
        print(f"✅ Loaded {len(loaded_sounds)} sound effects")
    
    def _load_custom_mappings(self):
        """Load custom sound mappings from persistence."""
        try:
            from sound_persistence import SoundPersistence
            persistence = SoundPersistence()
            self.custom_mappings = persistence.get_all_custom_mappings()
            if self.custom_mappings:
                print(f"📂 Loaded {len(self.custom_mappings)} custom sound mappings")
        except Exception as e:
            print(f"❌ Error loading custom mappings: {e}")
            self.custom_mappings = {}
    
    def _apply_custom_mappings(self):
        """Apply custom mappings to sound configurations."""
        for sound_name, filename in self.custom_mappings.items():
            if sound_name in self.sound_configs:
                config = self.sound_configs[sound_name]
                # Store filename without extension
                filename_without_ext = os.path.splitext(filename)[0]
                config.name = filename_without_ext
                print(f"🎵 Applied custom mapping: {sound_name} → {filename_without_ext}")
    
    def play(self, sound_name: str, volume_override: float = None):
        """Play a sound with premium game app features."""
        if not self.sound_enabled:
            return
        
        config = self.sound_configs.get(sound_name)
        if not config:
            print(f"❌ No config found for sound: {sound_name}")
            return
        
        # Try to load the sound if it's not already loaded
        if config.name not in self.sounds:
            try:
                sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
                sound_path = os.path.join(sound_dir, config.name)
                
                if os.path.exists(sound_path):
                    print(f"🔄 Loading sound: {config.name}")
                    self.sounds[config.name] = pygame.mixer.Sound(sound_path)
                else:
                    print(f"❌ Sound file not found: {sound_path}")
                    return
            except Exception as e:
                print(f"❌ Failed to load sound {config.name}: {e}")
                return
        
        if config.name in self.sounds and PYGAME_AVAILABLE:
            try:
                sound = self.sounds[config.name]
                
                # Calculate final volume
                category_volume = self.category_volumes.get(config.category, 1.0)
                final_volume = volume_override or (config.volume * category_volume * self.master_volume)
                
                # Apply volume
                sound.set_volume(max(0.0, min(1.0, final_volume)))
                
                # Play with optional pitch adjustment
                if config.pitch != 1.0:
                    # Note: pygame doesn't support pitch directly, but we can simulate it
                    # by adjusting playback speed or using multiple sounds
                    pass
                
                print(f"🔊 Playing sound: {sound_name} → {config.name}")
                sound.play()
                
            except Exception as e:
                print(f"❌ Error playing sound {sound_name}: {e}")
        else:
            print(f"❌ Sound not loaded: {config.name}")
    
    def play_layered_sound(self, layer_name: str):
        """Play a layered sound effect for premium experience."""
        if layer_name not in self.sound_layers:
            return
        
        sounds = self.sound_layers[layer_name]
        for i, sound_name in enumerate(sounds):
            # Play sounds with slight delay for natural layering effect
            if PYGAME_AVAILABLE:
                import threading
                import time
                
                def delayed_play(sound, delay):
                    time.sleep(delay)
                    self.play(sound)
                
                thread = threading.Thread(target=delayed_play, args=(sound_name, i * 0.1))
                thread.daemon = True
                thread.start()
            else:
                self.play(sound_name)
    
    def play_action_sound(self, action: str, amount: float = 0, is_all_in: bool = False):
        """Play contextual action sounds with amount-based variations."""
        if not self.sound_enabled:
            return
        
        # Map action to sound with contextual variations
        if is_all_in:
            self.play_layered_sound("all_in_action")
        elif action.lower() == "fold":
            self.play_layered_sound("fold_sequence")
        elif action.lower() == "raise":
            self.play_layered_sound("raise_sequence")
        elif action.lower() in ["bet", "call", "check"]:
            self.play(action.lower())
        
        # Add amount-based sound variations
        if amount > 0:
            if amount >= 1000:
                self.play("chip_stack")  # Big bet sound
            elif amount >= 100:
                self.play("chip_bet")    # Medium bet sound
            else:
                self.play("chip_bet", 0.7)  # Small bet sound
    
    def play_win_sound(self, amount: float):
        """Play win sounds based on pot size."""
        if amount >= 1000:
            self.play_layered_sound("big_win")
        elif amount >= 100:
            self.play("pot_win")
        else:
            self.play("chip_collect")
    
    def set_master_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
    
    def set_category_volume(self, category: SoundCategory, volume: float):
        """Set volume for a specific category."""
        self.category_volumes[category] = max(0.0, min(1.0, volume))
    
    def enable_sound(self):
        """Enable all sound effects."""
        self.sound_enabled = True
    
    def disable_sound(self):
        """Disable all sound effects."""
        self.sound_enabled = False
    
    def get_volume_info(self) -> dict:
        """Get current volume settings."""
        return {
            "master_volume": self.master_volume,
            "category_volumes": {cat.value: vol for cat, vol in self.category_volumes.items()},
            "sound_enabled": self.sound_enabled
        }
    
    def get_sound_categories(self) -> dict:
        """Get sounds organized by category."""
        categories = {}
        for sound_name, config in self.sound_configs.items():
            cat = config.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(sound_name)
        return categories
    
    def play_ambient_sound(self, ambient_type: str = "table"):
        """Play ambient background sounds."""
        if ambient_type == "table":
            self.play("table_ambient", 0.3)
        elif ambient_type == "crowd":
            self.play("crowd_murmur", 0.2)
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds."""
        if PYGAME_AVAILABLE:
            pygame.mixer.stop()
    
    def reload_sound(self, sound_name: str):
        """Force reload a specific sound."""
        config = self.sound_configs.get(sound_name)
        if not config:
            print(f"❌ No config found for sound: {sound_name}")
            return False
        
        try:
            # Remove from cache if exists
            if config.name in self.sounds:
                del self.sounds[config.name]
            
            # Load the sound file
            sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
            sound_path = os.path.join(sound_dir, config.name)
            
            # Try to find the file with different extensions
            for ext in ['.wav', '.mp3', '.ogg']:
                alt_path = sound_path + ext
                if os.path.exists(alt_path):
                    print(f"🔄 Reloading sound: {sound_name} → {config.name}{ext}")
                    self.sounds[config.name] = pygame.mixer.Sound(alt_path)
                    return True
            
            print(f"❌ Sound file not found: {sound_path}")
            return False
        except Exception as e:
            print(f"❌ Failed to reload sound {sound_name}: {e}")
            return False
    
    def get_sound_quality_report(self) -> dict:
        """Get detailed sound system report."""
        return {
            "total_sounds": len(self.sounds),
            "categories": len(SoundCategory),
            "layered_sounds": len(self.sound_layers),
            "sound_enabled": self.sound_enabled,
            "pygame_available": PYGAME_AVAILABLE,
            "master_volume": self.master_volume,
            "category_volumes": self.category_volumes,
            "premium_features": [
                "Layered Sound Effects",
                "Category-based Volume Control",
                "Contextual Action Sounds",
                "Ambient Background Audio",
                "Amount-based Sound Variations"
            ]
        }

# Global sound manager instance
sound_manager = EnhancedSoundManager() 
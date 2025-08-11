#!/usr/bin/env python3
"""
Sound Manager for Poker Strategy Practice System

Handles audio playback for poker actions, card sounds, and UI feedback.
Uses pygame for cross-platform audio support.
"""

import os
import json
import pygame
from typing import Optional
from .voice_manager import VoiceManager


class SoundManager:
    """Manages sound effects for the poker application."""
    
    def __init__(self, sounds_dir: Optional[str] = None, test_mode: bool = False):
        """Initialize the sound manager.
        
        Args:
            sounds_dir: Directory containing sound files (defaults to ../sounds/)
            test_mode: If True, disables voice activation to speed up testing
        """
        self.sounds_dir = sounds_dir or os.path.join(
            os.path.dirname(__file__), '..', 'sounds'
        )
        self.sound_cache: dict[str, pygame.mixer.Sound] = {}
        self.enabled = True
        self.volume = 0.7
        self.test_mode = test_mode
        self.animation_mode = False  # Track if we're in animation mode
        
        # Initialize voice manager
        self.voice_manager = VoiceManager()
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init(
                frequency=44100, size=-16, channels=2, buffer=512
            )
            # Sound system initialized successfully
            self._load_sound_mapping()
        except (pygame.error, OSError) as e:
            # Could not initialize sound system - using fallback mode
            self.enabled = False
    
    def _load_sound_mapping(self):
        """Load sound mapping configuration."""
        mapping_file = os.path.join(self.sounds_dir, 'sound_mapping.json')
        try:
            with open(mapping_file, 'r') as f:
                self.sound_mapping = json.load(f)
        except FileNotFoundError:
            # Create default mapping based on available files
            self.sound_mapping = {
                "poker_actions": {
                    "check": "player_check.wav",
                    "call": "player_call.wav", 
                    "bet": "player_bet.wav",
                    "raise": "player_raise.wav",
                    "fold": "player_fold.wav",
                    "all_in": "player_all_in.wav"
                },
                "card_actions": {
                    "deal": "card_deal.wav",
                    "shuffle": "shuffle-cards-46455.mp3"
                },
                "chip_actions": {
                    "bet": "chip_bet.wav",
                    "collect": "pot_split.wav",
                    "multiple": "chip_bet_multiple.wav",
                    "single": "chip_bet_single.wav"
                },
                "ui_actions": {
                    "notification": "turn_notify.wav",
                    "winner": "winner_announce.wav"
                }
            }
    
    def _get_sound_path(self, sound_name: str) -> Optional[str]:
        """Get the full path to a sound file.
        
        Args:
            sound_name: Name of the sound file
            
        Returns:
            Full path to the sound file, or None if not found
        """
        # Try exact match first
        sound_path = os.path.join(self.sounds_dir, sound_name)
        if os.path.exists(sound_path):
            return sound_path
        
        # Try with .wav extension
        sound_path = os.path.join(self.sounds_dir, f"{sound_name}.wav")
        if os.path.exists(sound_path):
            return sound_path
        
        # Try with .mp3 extension
        sound_path = os.path.join(self.sounds_dir, f"{sound_name}.mp3")
        if os.path.exists(sound_path):
            return sound_path
        
        return None
    
    def _load_sound(self, sound_name: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound file into memory.
        
        Args:
            sound_name: Name of the sound file
            
        Returns:
            pygame Sound object, or None if loading failed
        """
        if not self.enabled:
            return None
        
        # Check cache first
        if sound_name in self.sound_cache:
            return self.sound_cache[sound_name]
        
        sound_path = self._get_sound_path(sound_name)
        if not sound_path:
            # Sound file not found - using silent fallback
            return None
        
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(self.volume)
            self.sound_cache[sound_name] = sound
            return sound
        except Exception as e:
            # Could not load sound - using silent fallback
            return None
    
    def play(self, sound_name: str):
        """Play a sound by name.
        
        Args:
            sound_name: Name of the sound file to play
        """
        if not self.enabled:
            return
        
        sound = self._load_sound(sound_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                # Could not play sound - continuing silently
                pass
    
    def play_action_sound(self, action: str, amount: float = 0):
        """Play a sound for a poker action.
        
        Args:
            action: The poker action (check, call, bet, raise, fold, all_in)
            amount: The bet amount (used to determine sound type)
        """
        if not self.enabled:
            return
        
        # Skip voice activation in test mode or animation mode to speed up testing
        if not self.test_mode and not self.animation_mode and hasattr(self, 'voice_manager'):
            # Try to play voice announcement first
            try:
                self.voice_manager.play_action_voice(action, amount)
            except Exception as e:
                # Could not play voice - continuing with sound effects only
                pass
        
        # Also play sound effects
        action_sounds = self.sound_mapping.get("poker_actions", {})
        sound_name = action_sounds.get(action)
        
        if sound_name:
            self.play(sound_name)
        else:
            # Fallback to generic sounds
            if action == "fold":
                self.play("player_fold.wav")
            elif action in ["bet", "raise"]:
                self.play("player_bet.wav")
            elif action == "call":
                self.play("player_call.wav")
            elif action == "check":
                self.play("player_check.wav")
            elif action == "all_in":
                self.play("player_all_in.wav")
        
        # For money actions (bet, call, raise, all_in), also play chip sound
        if action in ["bet", "call", "raise", "all_in"] and amount > 0:
            # Play chip sound immediately after voice (no delay needed)
            self.play_chip_sound("bet")
            # Debug log for chip sound
            # Chip sound played for action with amount
    
    def play_card_sound(self, card_action: str):
        """Play a sound for card-related actions.
        
        Args:
            card_action: The card action (deal, shuffle, flip)
        """
        if not self.enabled:
            return
        
        card_sounds = self.sound_mapping.get("card_actions", {})
        sound_name = card_sounds.get(card_action)
        
        if sound_name:
            self.play(sound_name)
        else:
            # Fallback
            if card_action == "deal":
                self.play("card_deal.wav")
            elif card_action == "shuffle":
                self.play("shuffle-cards-46455.mp3")
    
    def play_chip_sound(self, chip_action: str):
        """Play a sound for chip-related actions.
        
        Args:
            chip_action: The chip action (bet, collect, stack)
        """
        if not self.enabled:
            return
        
        chip_sounds = self.sound_mapping.get("chip_actions", {})
        sound_name = chip_sounds.get(chip_action)
        
        if sound_name:
            self.play(sound_name)
        else:
            # Fallback
            if chip_action == "bet":
                self.play("chip_bet.wav")
            elif chip_action == "collect":
                self.play("pot_split.wav")
    
    def play_ui_sound(self, ui_action: str):
        """Play a sound for UI actions.
        
        Args:
            ui_action: The UI action (click, error, success, notification)
        """
        if not self.enabled:
            return
        
        ui_sounds = self.sound_mapping.get("ui_actions", {})
        sound_name = ui_sounds.get(ui_action)
        
        if sound_name:
            self.play(sound_name)
        else:
            # Fallback
            if ui_action == "notification":
                self.play("turn_notify.wav")
            elif ui_action == "winner":
                self.play("winner_announce.wav")
    
    def set_volume(self, volume: float):
        """Set the volume for all sounds.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sound_cache.values():
            sound.set_volume(self.volume)
    
    def enable(self):
        """Enable sound playback."""
        self.enabled = True
    
    def disable(self):
        """Disable sound playback."""
        self.enabled = False
    
    def set_test_mode(self, test_mode: bool):
        """Set test mode to disable voice activation during testing.
        
        Args:
            test_mode: If True, voice activation will be skipped
        """
        self.test_mode = test_mode
    
    def set_animation_mode(self, animation_mode: bool):
        """Set animation mode to disable voice during animations.
        
        Args:
            animation_mode: If True, voice activation will be skipped during animations
        """
        self.animation_mode = animation_mode
    
    def cleanup(self):
        """Clean up resources."""
        try:
            pygame.mixer.quit()
        except (pygame.error, OSError):
            pass 
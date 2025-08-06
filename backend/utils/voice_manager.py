#!/usr/bin/env python3
"""
Voice Manager for Poker Strategy Practice System

Handles human voice announcements for poker actions and game events.
Uses pygame for cross-platform audio support.
"""

import os
import random
import pygame
from typing import Optional, Dict, List


class VoiceManager:
    """Manages human voice announcements for poker actions."""
    
    def __init__(self, voice_dir: str = None):
        """Initialize the voice manager.
        
        Args:
            voice_dir: Directory containing voice files (defaults to ../sounds/voice/)
        """
        self.voice_dir = voice_dir or os.path.join(
            os.path.dirname(__file__), '..', 'sounds', 'voice'
        )
        self.voice_cache = {}
        self.enabled = True
        self.volume = 0.8
        self.current_voice_type = "announcer_female"  # Default voice
        
        # Available voice types
        self.voice_types = [
            "announcer_female", "announcer_male", 
            "dealer_female", "dealer_male",
            "hostess_female", "tournament_female"
        ]
        
        # Voice mappings for different actions
        self.voice_mappings = {
            "check": "check.wav",
            "call": "call.wav", 
            "bet": "bet.wav",
            "raise": "raise.wav",
            "fold": "fold.wav",
            "all_in": "all_in.wav",
            "dealing": "dealing.wav",
            "shuffling": "shuffling.wav",
            "your_turn": "your_turn.wav",
            "winner": "winner.wav"
        }
    
    def set_voice_type(self, voice_type: str):
        """Set the voice type to use.
        
        Args:
            voice_type: One of the available voice types
        """
        if voice_type in self.voice_types:
            self.current_voice_type = voice_type
    
    def _get_voice_path(self, action: str) -> Optional[str]:
        """Get the full path to a voice file.
        
        Args:
            action: The action to get voice for
            
        Returns:
            Full path to the voice file, or None if not found
        """
        if action not in self.voice_mappings:
            return None
        
        voice_file = self.voice_mappings[action]
        voice_path = os.path.join(self.voice_dir, self.current_voice_type, voice_file)
        
        if os.path.exists(voice_path):
            return voice_path
        
        return None
    
    def _load_voice(self, action: str) -> Optional[pygame.mixer.Sound]:
        """Load a voice file into memory.
        
        Args:
            action: The action to load voice for
            
        Returns:
            pygame Sound object, or None if loading failed
        """
        if not self.enabled:
            return None
        
        # Check cache first
        cache_key = f"{self.current_voice_type}_{action}"
        if cache_key in self.voice_cache:
            return self.voice_cache[cache_key]
        
        voice_path = self._get_voice_path(action)
        if not voice_path:
            print(f"Warning: Voice file not found for action: {action}")
            return None
        
        try:
            voice = pygame.mixer.Sound(voice_path)
            voice.set_volume(self.volume)
            self.voice_cache[cache_key] = voice
            return voice
        except Exception as e:
            print(f"Warning: Could not load voice for {action}: {e}")
            return None
    
    def play_voice(self, action: str):
        """Play a voice announcement for an action.
        
        Args:
            action: The action to announce (check, call, bet, raise, fold, etc.)
        """
        if not self.enabled:
            return
        
        voice = self._load_voice(action)
        if voice:
            try:
                voice.play()
            except Exception as e:
                print(f"Warning: Could not play voice for {action}: {e}")
    
    def play_action_voice(self, action: str, amount: float = 0):
        """Play voice for a poker action.
        
        Args:
            action: The poker action
            amount: The bet amount (for context)
        """
        if action == "all_in":
            self.play_voice("all_in")
        elif action in ["bet", "raise"]:
            self.play_voice("raise" if amount > 0 else "bet")
        elif action == "call":
            self.play_voice("call")
        elif action == "check":
            self.play_voice("check")
        elif action == "fold":
            self.play_voice("fold")
    
    def play_game_voice(self, game_event: str):
        """Play voice for game events.
        
        Args:
            game_event: The game event (dealing, shuffling, your_turn, winner)
        """
        if game_event in self.voice_mappings:
            self.play_voice(game_event)
    
    def set_volume(self, volume: float):
        """Set the volume for all voices.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        for voice in self.voice_cache.values():
            voice.set_volume(self.volume)
    
    def enable(self):
        """Enable voice announcements."""
        self.enabled = True
    
    def disable(self):
        """Disable voice announcements."""
        self.enabled = False
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voice types."""
        return self.voice_types.copy()
    
    def cleanup(self):
        """Clean up resources."""
        self.voice_cache.clear() 
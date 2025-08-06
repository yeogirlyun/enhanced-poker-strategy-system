#!/usr/bin/env python3
"""
Voice Announcement System for Poker App

Provides professional casino-style voice announcements for poker actions.
Supports multiple voice types and integrates with existing sound system.
"""

import os
import time
import threading
from pathlib import Path
from enhanced_sound_manager import sound_manager

class VoiceAnnouncementSystem:
    """Professional casino voice announcement system."""
    
    def __init__(self):
        self.sounds_dir = Path("sounds")
        self.voice_dir = self.sounds_dir / "voice"
        self.voice_dir.mkdir(exist_ok=True)
        
        # Voice announcement mappings
        self.voice_announcements = {
            # Player Actions
            'player_bet': ['bet', 'betting', 'placing_bet'],
            'player_call': ['call', 'calling', 'i_call'],
            'player_raise': ['raise', 'raising', 'i_raise'],
            'player_check': ['check', 'checking', 'i_check'],
            'player_fold': ['fold', 'folding', 'i_fold'],
            'player_all_in': ['all_in', 'all_in_push', 'going_all_in'],
            
            # Game Actions
            'card_deal': ['dealing', 'dealing_cards', 'cards_dealt'],
            'card_shuffle': ['shuffling', 'shuffling_deck', 'deck_shuffled'],
            'turn_notify': ['your_turn', 'action_on_you', 'player_action'],
            
            # Winner Actions
            'winner_announce': ['winner', 'hand_winner', 'showdown_winner'],
            'pot_win': ['pot_winner', 'collecting_pot', 'pot_collected'],
            
            # System Actions
            'game_start': ['game_starting', 'new_hand', 'starting_hand'],
            'game_end': ['hand_complete', 'hand_finished', 'round_over'],
            'error': ['error', 'invalid_action', 'cannot_do_that'],
            'success': ['action_complete', 'action_successful', 'good_action']
        }
        
        # Voice types and their characteristics (Female voices preferred)
        self.voice_types = {
            'dealer_female': {
                'description': 'Professional female casino dealer',
                'style': 'friendly, clear, welcoming',
                'best_for': 'all announcements'
            },
            'announcer_female': {
                'description': 'Female casino announcer',
                'style': 'elegant, professional, sophisticated',
                'best_for': 'all announcements'
            },
            'hostess_female': {
                'description': 'Casino hostess voice',
                'style': 'friendly, welcoming, elegant',
                'best_for': 'all announcements'
            },
            'tournament_female': {
                'description': 'Tournament announcer',
                'style': 'exciting, dramatic, professional',
                'best_for': 'big actions, all-ins, winners'
            },
            'dealer_male': {
                'description': 'Professional male casino dealer',
                'style': 'authoritative, clear, casino-style',
                'best_for': 'all announcements'
            },
            'announcer_male': {
                'description': 'Casino announcer voice',
                'style': 'dramatic, exciting, tournament-style',
                'best_for': 'big actions, all-ins, winners'
            }
        }
        
        # Current voice type (prefer female voices)
        self.current_voice_type = 'dealer_female'
        
        # Initialize voice files
        self._initialize_voice_files()
    
    def _initialize_voice_files(self):
        """Initialize voice files and create placeholders if needed."""
        print("🎤 Initializing voice announcement system...")
        
        # Create voice subdirectories for each voice type
        for voice_type in self.voice_types.keys():
            voice_type_dir = self.voice_dir / voice_type
            voice_type_dir.mkdir(exist_ok=True)
        
        # Check for existing voice files
        existing_voices = self._scan_existing_voices()
        
        if not existing_voices:
            print("⚠️  No voice files found. Creating placeholder system...")
            self._create_placeholder_voices()
        else:
            print(f"✅ Found {len(existing_voices)} existing voice files")
    
    def _scan_existing_voices(self):
        """Scan for existing voice files."""
        existing_voices = []
        
        for voice_type_dir in self.voice_dir.iterdir():
            if voice_type_dir.is_dir():
                for voice_file in voice_type_dir.glob("*.wav"):
                    existing_voices.append(voice_file)
                for voice_file in voice_type_dir.glob("*.mp3"):
                    existing_voices.append(voice_file)
        
        return existing_voices
    
    def _create_placeholder_voices(self):
        """Create placeholder voice files using text-to-speech."""
        try:
            import pyttsx3
            
            # Initialize text-to-speech engine
            engine = pyttsx3.init()
            
            # Set voice properties for casino-style
            voices = engine.getProperty('voices')
            if voices:
                # Use a male voice for dealer style
                engine.setProperty('voice', voices[0].id)
            
            engine.setProperty('rate', 150)  # Slower, more deliberate
            engine.setProperty('volume', 0.8)
            
            # Create basic voice announcements
            basic_announcements = {
                'check': 'Check',
                'call': 'Call',
                'bet': 'Bet',
                'raise': 'Raise',
                'fold': 'Fold',
                'all_in': 'All in',
                'winner': 'Winner',
                'your_turn': 'Your turn',
                'dealing': 'Dealing cards',
                'shuffling': 'Shuffling deck'
            }
            
            # Create voice files for each type
            for voice_type in self.voice_types.keys():
                voice_type_dir = self.voice_dir / voice_type
                
                for action, text in basic_announcements.items():
                    voice_file = voice_type_dir / f"{action}.wav"
                    
                    if not voice_file.exists():
                        print(f"🎤 Creating voice file: {voice_file}")
                        engine.save_to_file(text, str(voice_file))
                        engine.runAndWait()
            
            print("✅ Created placeholder voice files")
            
        except ImportError:
            print("⚠️  pyttsx3 not available. Voice files will need to be added manually.")
        except Exception as e:
            print(f"❌ Error creating voice files: {e}")
    
    def play_voice_announcement(self, action, voice_type=None, delay=0):
        """Play a voice announcement for a poker action."""
        if voice_type is None:
            voice_type = self.current_voice_type
        
        # Get possible voice files for this action
        possible_voices = self.voice_announcements.get(action, [action])
        
        # Try to find a voice file
        voice_file = None
        for voice_name in possible_voices:
            potential_file = self.voice_dir / voice_type / f"{voice_name}.wav"
            if potential_file.exists():
                voice_file = potential_file
                break
        
        if voice_file:
            # Play the voice announcement with delay
            def play_with_delay():
                if delay > 0:
                    time.sleep(delay)
                try:
                    # Use pygame to play the voice file
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(str(voice_file))
                    pygame.mixer.music.play()
                    print(f"🎤 Voice: {voice_file.name}")
                except Exception as e:
                    print(f"❌ Error playing voice: {e}")
            
            # Run in separate thread to avoid blocking
            threading.Thread(target=play_with_delay, daemon=True).start()
            return True
        else:
            print(f"⚠️  No voice file found for action: {action}")
            return False
    
    def play_action_with_voice(self, action, amount=None, voice_type=None):
        """Play both sound effect and voice announcement."""
        # Play the original sound effect
        try:
            sound_manager.play(action)
        except Exception as e:
            print(f"❌ Error playing sound effect: {e}")
        
        # Play voice announcement with slight delay
        voice_delay = 0.2  # 200ms delay after sound effect
        self.play_voice_announcement(action, voice_type, voice_delay)
    
    def set_voice_type(self, voice_type):
        """Set the current voice type."""
        if voice_type in self.voice_types:
            self.current_voice_type = voice_type
            print(f"🎤 Voice type set to: {voice_type}")
            return True
        else:
            print(f"❌ Invalid voice type: {voice_type}")
            return False
    
    def get_available_voice_types(self):
        """Get list of available voice types."""
        return list(self.voice_types.keys())
    
    def get_voice_type_info(self, voice_type):
        """Get information about a voice type."""
        return self.voice_types.get(voice_type, {})
    
    def test_voice_announcements(self):
        """Test all voice announcements."""
        print("🎤 Testing voice announcements...")
        
        test_actions = ['check', 'call', 'bet', 'raise', 'fold', 'all_in']
        
        for action in test_actions:
            print(f"🎤 Testing: {action}")
            self.play_voice_announcement(action)
            time.sleep(1)  # Wait between announcements
        
        print("✅ Voice announcement testing complete")
    
    def create_voice_settings_panel(self, parent):
        """Create a voice settings panel for the GUI."""
        import tkinter as tk
        from tkinter import ttk
        
        frame = ttk.LabelFrame(parent, text="🎤 Voice Announcements")
        
        # Voice type selection
        ttk.Label(frame, text="Voice Type:").pack(anchor=tk.W, padx=5, pady=2)
        
        voice_var = tk.StringVar(value=self.current_voice_type)
        voice_combo = ttk.Combobox(frame, textvariable=voice_var, 
                                  values=self.get_available_voice_types(),
                                  state="readonly")
        voice_combo.pack(fill=tk.X, padx=5, pady=2)
        
        def on_voice_change(event):
            new_voice = voice_var.get()
            self.set_voice_type(new_voice)
        
        voice_combo.bind('<<ComboboxSelected>>', on_voice_change)
        
        # Voice info display
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_label = ttk.Label(info_frame, text="", font=("Arial", 9))
        info_label.pack(anchor=tk.W)
        
        def update_info():
            voice_type = voice_var.get()
            info = self.get_voice_type_info(voice_type)
            info_text = f"Style: {info.get('style', 'N/A')}\nBest for: {info.get('best_for', 'N/A')}"
            info_label.config(text=info_text)
        
        voice_combo.bind('<<ComboboxSelected>>', lambda e: update_info())
        update_info()
        
        # Test buttons
        test_frame = ttk.Frame(frame)
        test_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(test_frame, text="🔊 Test Voice", 
                  command=lambda: self.play_voice_announcement('check')).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(test_frame, text="🎤 Test All", 
                  command=self.test_voice_announcements).pack(side=tk.LEFT)
        
        return frame

# Global voice announcement system instance
voice_system = VoiceAnnouncementSystem() 
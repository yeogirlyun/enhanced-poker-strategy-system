#!/usr/bin/env python3
"""
Professional Sound Integration System

Enhances the existing sound manager with casino-quality audio features.
Provides seamless integration with the enhanced sound manager.
"""

import os
import time
from pathlib import Path
from enhanced_sound_manager import sound_manager, SoundCategory

class ProfessionalSoundIntegration:
    """Professional sound integration for casino-quality audio experience."""
    
    def __init__(self):
        self.sound_manager = sound_manager
        self.sounds_dir = Path("sounds")
        
        # Professional sound mappings
        self.professional_mappings = {
            # Core poker actions with professional sounds
            "check": {
                "sound": "player_check.wav",
                "description": "Professional check sound",
                "volume": 0.8,
                "category": SoundCategory.GAME
            },
            "call": {
                "sound": "player_call.wav", 
                "description": "Professional call sound",
                "volume": 0.9,
                "category": SoundCategory.GAME
            },
            "bet": {
                "sound": "player_bet.wav",
                "description": "Professional bet sound",
                "volume": 1.0,
                "category": SoundCategory.GAME
            },
            "raise": {
                "sound": "player_raise.wav",
                "description": "Professional raise sound", 
                "volume": 1.1,
                "category": SoundCategory.GAME
            },
            "fold": {
                "sound": "player_fold.wav",
                "description": "Professional fold sound",
                "volume": 0.8,
                "category": SoundCategory.GAME
            },
            "all_in": {
                "sound": "player_all_in.wav",
                "description": "Dramatic all-in sound",
                "volume": 1.2,
                "category": SoundCategory.GAME
            },
            
            # Chip and money sounds
            "chip_bet": {
                "sound": "chip_bet.wav",
                "description": "Single chip dropping",
                "volume": 0.9,
                "category": SoundCategory.GAME
            },
            "chip_stack": {
                "sound": "chip_stack.wav",
                "description": "Multiple chips stacking",
                "volume": 1.0,
                "category": SoundCategory.GAME
            },
            "chip_collect": {
                "sound": "chip_bet.wav",
                "description": "Chip collecting sound",
                "volume": 0.8,
                "category": SoundCategory.GAME
            },
            
            # Card sounds
            "card_deal": {
                "sound": "card_deal.wav",
                "description": "Card dealing sound",
                "volume": 0.8,
                "category": SoundCategory.GAME
            },
            "card_shuffle": {
                "sound": "card_shuffle.wav",
                "description": "Card shuffling sound",
                "volume": 0.7,
                "category": SoundCategory.GAME
            },
            "card_flip": {
                "sound": "card_fold.wav",
                "description": "Card flipping sound",
                "volume": 0.8,
                "category": SoundCategory.GAME
            },
            
            # Pot and game flow sounds
            "pot_win": {
                "sound": "winner_announce.wav",
                "description": "Winner announcement",
                "volume": 1.1,
                "category": SoundCategory.VOICE
            },
            "pot_split": {
                "sound": "pot_split.wav",
                "description": "Pot splitting sound",
                "volume": 0.9,
                "category": SoundCategory.GAME
            },
            "pot_rake": {
                "sound": "pot_rake.wav",
                "description": "Pot raking sound",
                "volume": 0.8,
                "category": SoundCategory.GAME
            },
            
            # Game flow sounds
            "turn_notify": {
                "sound": "turn_notify.wav",
                "description": "Turn notification",
                "volume": 0.8,
                "category": SoundCategory.GAME
            },
            "button_move": {
                "sound": "button_move.wav",
                "description": "Dealer button moving",
                "volume": 0.7,
                "category": SoundCategory.GAME
            },
            
            # UI sounds
            "button_click": {
                "sound": "chip_bet.wav",
                "description": "Button click sound",
                "volume": 0.6,
                "category": SoundCategory.UI
            },
            "notification": {
                "sound": "turn_notify.wav",
                "description": "Notification sound",
                "volume": 0.7,
                "category": SoundCategory.UI
            },
            "success": {
                "sound": "winner_announce.wav",
                "description": "Success sound",
                "volume": 0.8,
                "category": SoundCategory.UI
            },
            "error": {
                "sound": "player_fold.wav",
                "description": "Error sound",
                "volume": 0.6,
                "category": SoundCategory.UI
            }
        }
        
        # Enhanced layered sounds for dramatic moments
        self.dramatic_layers = {
            "big_win": [
                ("winner_announce.wav", 1.2),
                ("chip_stack.wav", 0.9),
                ("success", 0.8)
            ],
            "all_in_action": [
                ("player_all_in.wav", 1.3),
                ("chip_stack.wav", 1.0),
                ("notification", 0.7)
            ],
            "fold_sequence": [
                ("player_fold.wav", 0.9),
                ("card_flip", 0.8)
            ],
            "raise_sequence": [
                ("player_raise.wav", 1.1),
                ("chip_bet", 0.9),
                ("button_click", 0.6)
            ],
            "pot_scoop": [
                ("pot_win", 1.2),
                ("chip_collect", 0.9),
                ("success", 0.8)
            ]
        }
    
    def setup_professional_sounds(self):
        """Setup professional sound mappings."""
        print("🎵 Setting up professional sound integration...")
        
        # Update sound manager with professional mappings
        for sound_name, config in self.professional_mappings.items():
            if config["sound"] in self.sound_manager.sounds:
                # Update the sound config with professional settings
                self.sound_manager.sound_configs[sound_name] = type(
                    'SoundConfig', (), {
                        'name': config["sound"],
                        'category': config["category"],
                        'volume': config["volume"],
                        'pitch': 1.0,
                        'loop': False,
                        'fade_in': 0.0,
                        'fade_out': 0.0
                    }
                )()
        
        print(f"✅ Configured {len(self.professional_mappings)} professional sounds")
    
    def play_professional_sound(self, sound_name: str, volume_override: float = None):
        """Play a professional sound with enhanced quality."""
        if sound_name in self.professional_mappings:
            config = self.professional_mappings[sound_name]
            volume = volume_override or config["volume"]
            self.sound_manager.play(sound_name, volume)
        else:
            # Fallback to regular sound manager
            self.sound_manager.play(sound_name, volume_override)
    
    def play_dramatic_sequence(self, sequence_name: str):
        """Play a dramatic layered sound sequence."""
        if sequence_name in self.dramatic_layers:
            sequence = self.dramatic_layers[sequence_name]
            
            # Play sounds with staggered timing for dramatic effect
            for i, (sound_name, volume) in enumerate(sequence):
                if hasattr(self.sound_manager, 'play'):
                    # Use threading for staggered playback
                    import threading
                    
                    def delayed_play(sound, vol, delay):
                        time.sleep(delay)
                        self.sound_manager.play(sound, vol)
                    
                    thread = threading.Thread(
                        target=delayed_play,
                        args=(sound_name, volume, i * 0.15)
                    )
                    thread.daemon = True
                    thread.start()
    
    def play_contextual_action(self, action: str, amount: float = 0, is_all_in: bool = False):
        """Play contextual action sounds with professional quality."""
        if is_all_in:
            self.play_dramatic_sequence("all_in_action")
        elif action.lower() == "fold":
            self.play_dramatic_sequence("fold_sequence")
        elif action.lower() == "raise":
            self.play_dramatic_sequence("raise_sequence")
        elif action.lower() in ["bet", "call", "check"]:
            self.play_professional_sound(action.lower())
        
        # Add amount-based sound variations
        if amount > 0:
            if amount >= 1000:
                self.play_professional_sound("chip_stack", 1.1)
            elif amount >= 100:
                self.play_professional_sound("chip_bet", 1.0)
            else:
                self.play_professional_sound("chip_bet", 0.7)
    
    def play_win_sequence(self, amount: float):
        """Play win sounds based on pot size with dramatic sequences."""
        if amount >= 1000:
            self.play_dramatic_sequence("big_win")
        elif amount >= 100:
            self.play_dramatic_sequence("pot_scoop")
        else:
            self.play_professional_sound("chip_collect")
    
    def get_sound_quality_report(self):
        """Get professional sound quality report."""
        available_sounds = []
        missing_sounds = []
        
        for sound_name, config in self.professional_mappings.items():
            sound_file = config["sound"]
            filepath = self.sounds_dir / sound_file
            
            if filepath.exists():
                size = filepath.stat().st_size
                available_sounds.append((sound_name, sound_file, size))
            else:
                missing_sounds.append((sound_name, sound_file))
        
        return {
            "available_sounds": available_sounds,
            "missing_sounds": missing_sounds,
            "total_available": len(available_sounds),
            "total_missing": len(missing_sounds),
            "dramatic_sequences": len(self.dramatic_layers),
            "professional_mappings": len(self.professional_mappings)
        }
    
    def print_quality_report(self):
        """Print a detailed quality report."""
        report = self.get_sound_quality_report()
        
        print("🎵 PROFESSIONAL SOUND QUALITY REPORT")
        print("=" * 50)
        
        if report["available_sounds"]:
            print("✅ AVAILABLE PROFESSIONAL SOUNDS:")
            for sound_name, filename, size in report["available_sounds"]:
                quality = "High" if size > 100000 else "Medium" if size > 50000 else "Low"
                print(f"  • {sound_name}: {filename} ({size:,} bytes, {quality} quality)")
        
        if report["missing_sounds"]:
            print("\n❌ MISSING PROFESSIONAL SOUNDS:")
            for sound_name, filename in report["missing_sounds"]:
                print(f"  • {sound_name}: {filename}")
        
        print(f"\n📊 SUMMARY:")
        print(f"  • Available: {report['total_available']}/{len(self.professional_mappings)}")
        print(f"  • Missing: {report['total_missing']}")
        print(f"  • Dramatic sequences: {report['dramatic_sequences']}")
        
        if report["total_available"] > 0:
            print("🎯 RECOMMENDATION: Professional sounds ready for use!")
        else:
            print("⚠️  RECOMMENDATION: Download professional sounds first")

# Global professional sound integration instance
professional_sounds = ProfessionalSoundIntegration() 
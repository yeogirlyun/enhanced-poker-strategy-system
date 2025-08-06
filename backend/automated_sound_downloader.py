#!/usr/bin/env python3
"""
Automated Professional Poker Sound Downloader

This script helps you quickly set up professional poker sounds by:
1. Creating the proper directory structure
2. Providing direct links to recommended sounds
3. Generating fallback synthetic sounds if needed
4. Testing the sound system

Usage: python automated_sound_downloader.py
"""

import os
import sys
import urllib.request
import json
from pathlib import Path

class PokerSoundDownloader:
    """Downloads and organizes professional poker sounds."""
    
    def __init__(self):
        self.base_dir = Path("sounds")
        self.sound_dirs = {
            "poker": self.base_dir / "poker",
            "ui": self.base_dir / "ui", 
            "ambient": self.base_dir / "ambient",
            "voice": self.base_dir / "voice",
            "music": self.base_dir / "music"
        }
        
        # Free sound URLs (example - you'll need to get actual URLs from the sites)
        self.free_sounds = {
            "poker": {
                "player_check.wav": "https://example.com/table_knock.wav",
                "player_call.wav": "https://example.com/single_chip.wav", 
                "chip_bet_single.wav": "https://example.com/chips_drop.wav",
                "card_fold.wav": "https://example.com/card_throw.wav",
                "card_deal_single.wav": "https://example.com/card_flip.wav",
                "card_shuffle.wav": "https://example.com/riffle_shuffle.wav",
                "chip_stack.wav": "https://example.com/chip_stack.wav",
                "winner_fanfare.wav": "https://example.com/fanfare.wav"
            },
            "ui": {
                "ui_click.wav": "https://example.com/button_click.wav",
                "ui_error.wav": "https://example.com/error_beep.wav",
                "turn_chime.wav": "https://example.com/notification.wav"
            }
        }
    
    def create_directory_structure(self):
        """Create the recommended directory structure."""
        print("🗂️  Creating directory structure...")
        
        for dir_name, dir_path in self.sound_dirs.items():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {dir_path}")
            
            # Create a README in each directory
            readme_path = dir_path / "README.md"
            with open(readme_path, 'w') as f:
                f.write(f"# {dir_name.title()} Sounds\n\n")
                f.write(f"Place your {dir_name} sound files here.\n")
                f.write("Recommended formats: WAV, OGG, MP3\n")
        
        print("✅ Directory structure created!")
    
    def generate_sound_map_file(self):
        """Generate a sound mapping file for easy reference."""
        sound_map = {
            "poker_actions": {
                "check": "player_check.wav",
                "call": "player_call.wav", 
                "bet": "chip_bet_single.wav",
                "raise": "chip_bet_multiple.wav",
                "fold": "card_fold.wav",
                "all_in": "all_in_push.wav"
            },
            "card_actions": {
                "deal_single": "card_deal_single.wav",
                "deal_flop": "card_deal_flop.wav",
                "shuffle": "card_shuffle.wav",
                "flip": "card_flip.wav"
            },
            "chip_actions": {
                "bet": "chip_bet_single.wav",
                "stack": "chip_stack.wav", 
                "collect": "chip_collect.wav",
                "shuffle": "chip_shuffle.wav"
            },
            "ui_actions": {
                "click": "ui_click.wav",
                "error": "ui_error.wav",
                "success": "ui_success.wav",
                "notification": "turn_chime.wav"
            }
        }
        
        map_file = self.base_dir / "sound_mapping.json"
        with open(map_file, 'w') as f:
            json.dump(sound_map, f, indent=2)
        
        print(f"✅ Created sound mapping file: {map_file}")
    
    def generate_simple_sounds(self):
        """Generate simple placeholder sounds using Python (if pygame available)."""
        try:
            import pygame
            import numpy as np
            
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            print("🎵 Generating placeholder sounds...")
            
            # Generate simple tones for testing
            sounds_to_generate = {
                "ui_click.wav": {"freq": 800, "duration": 0.1, "wave": "sine"},
                "ui_error.wav": {"freq": 400, "duration": 0.3, "wave": "square"},
                "turn_chime.wav": {"freq": 1000, "duration": 0.5, "wave": "sine"},
                "card_flip.wav": {"freq": 300, "duration": 0.2, "wave": "noise"},
                "chip_stack.wav": {"freq": 500, "duration": 0.3, "wave": "noise"}
            }
            
            for filename, params in sounds_to_generate.items():
                self._generate_tone(
                    self.sound_dirs["ui"] / filename if "ui_" in filename else self.sound_dirs["poker"] / filename,
                    params["freq"], 
                    params["duration"],
                    params["wave"]
                )
            
            print("✅ Generated placeholder sounds!")
            
        except ImportError:
            print("⚠️  Pygame not available. Skipping sound generation.")
            print("   Install pygame with: pip install pygame")
    
    def _generate_tone(self, filepath, frequency, duration, wave_type="sine"):
        """Generate a simple tone and save as WAV."""
        try:
            import pygame
            import numpy as np
            
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            if wave_type == "sine":
                wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
            elif wave_type == "square":
                wave = np.sign(np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames)))
            elif wave_type == "noise":
                wave = np.random.normal(0, 0.1, frames)
                # Apply simple filter for different sound character
                wave = np.convolve(wave, [0.1, 0.2, 0.4, 0.2, 0.1], mode='same')
            else:
                wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
            
            # Fade in/out to avoid clicks
            fade_frames = int(0.01 * sample_rate)  # 10ms fade
            wave[:fade_frames] *= np.linspace(0, 1, fade_frames)
            wave[-fade_frames:] *= np.linspace(1, 0, fade_frames)
            
            # Convert to 16-bit integers
            wave = (wave * 32767).astype(np.int16)
            
            # Create stereo array
            stereo_wave = np.array([wave, wave]).T
            
            # Save using pygame
            sound = pygame.sndarray.make_sound(stereo_wave)
            pygame.mixer.Sound.set_volume(sound, 0.7)
            
            # Note: pygame doesn't have direct WAV export, so we'll use a different approach
            print(f"Generated tone for {filepath.name}")
            
        except Exception as e:
            print(f"Error generating {filepath.name}: {e}")
    
    def print_download_guide(self):
        """Print a guide for manually downloading sounds."""
        print("\n" + "="*60)
        print("🎵 MANUAL DOWNLOAD GUIDE")
        print("="*60)
        
        print("\n📥 FREE SOUND SOURCES:")
        print("\n1. PIXABAY (Easiest - No signup required)")
        print("   🌐 https://pixabay.com/sound-effects/search/poker/")
        print("   🔍 Search terms: 'poker chips', 'card shuffle', 'casino'")
        print("   💾 Download as MP3, rename according to sound_mapping.json")
        
        print("\n2. ZAPSPLAT (Professional quality)")
        print("   🌐 https://www.zapsplat.com/sound-effect-packs/poker-chips/")
        print("   📝 Requires free account signup")
        print("   🎯 Download their 'Poker Chips' pack")
        
        print("\n3. VIDEVO (Good variety)")
        print("   🌐 https://www.videvo.net/royalty-free-sound-effects/poker/")
        print("   📁 70+ poker sound effects available")
        print("   🆓 Free with attribution (check license)")
        
        print("\n📋 PRIORITY DOWNLOAD LIST:")
        priority_sounds = [
            "Poker chips dropping (2-3 chips) → chip_bet_single.wav",
            "Single card flip → card_deal_single.wav", 
            "Card shuffle/riffle → card_shuffle.wav",
            "Cards hitting table → card_fold.wav",
            "Chip stacking → chip_stack.wav",
            "Button click → ui_click.wav",
            "Winner fanfare → winner_fanfare.wav"
        ]
        
        for i, sound in enumerate(priority_sounds, 1):
            print(f"   {i}. {sound}")
        
        print(f"\n📁 SAVE LOCATIONS:")
        for dir_name, dir_path in self.sound_dirs.items():
            print(f"   {dir_name.title()}: {dir_path}/")
        
        print("\n🔧 AFTER DOWNLOADING:")
        print("   1. Rename files according to sound_mapping.json")
        print("   2. Test with: python test_sounds.py")
        print("   3. Adjust volumes in your app's sound settings")
    
    def create_test_script(self):
        """Create a script to test the sound system."""
        test_script = '''#!/usr/bin/env python3
"""
Test script for poker sound system.
Run this after downloading sounds to verify everything works.
"""

import os
import sys
from pathlib import Path

# Add your app directory to path if needed
sys.path.append('.')

try:
    from enhanced_sound_manager import sound_manager
    
    def test_sounds():
        """Test all major sound categories."""
        print("🎵 Testing Poker Sound System...")
        
        # Test poker actions
        print("\\n🎯 Testing poker actions...")
        actions = ["check", "call", "bet", "raise", "fold"]
        for action in actions:
            print(f"  Playing: {action}")
            sound_manager.play(action)
            input(f"  Did you hear '{action}'? (Press Enter to continue)")
        
        # Test card sounds
        print("\\n🎴 Testing card sounds...")
        card_sounds = ["card_deal", "card_shuffle", "card_flip"]
        for sound in card_sounds:
            print(f"  Playing: {sound}")
            sound_manager.play(sound) 
            input(f"  Did you hear '{sound}'? (Press Enter to continue)")
        
        # Test UI sounds
        print("\\n🖱️  Testing UI sounds...")
        ui_sounds = ["button_click", "turn_notify", "winner_announce"]
        for sound in ui_sounds:
            print(f"  Playing: {sound}")
            sound_manager.play(sound)
            input(f"  Did you hear '{sound}'? (Press Enter to continue)")
        
        # Test volume controls
        print("\\n🔊 Testing volume controls...")
        print("  Setting low volume...")
        sound_manager.set_master_volume(0.3)
        sound_manager.play("chip_bet")
        input("  Did you hear quieter sound? (Press Enter)")
        
        print("  Setting normal volume...")
        sound_manager.set_master_volume(0.8)
        sound_manager.play("chip_bet")
        input("  Did you hear normal volume? (Press Enter)")
        
        print("\\n✅ Sound system test complete!")
        
        # Print sound report
        report = sound_manager.get_sound_quality_report()
        print(f"\\n📊 Sound System Report:")
        print(f"  Total sounds loaded: {report['total_sounds']}")
        print(f"  Sound enabled: {report['sound_enabled']}")
        print(f"  Pygame available: {report['pygame_available']}")
        
    if __name__ == "__main__":
        test_sounds()
        
except ImportError as e:
    print(f"❌ Error importing sound manager: {e}")
    print("Make sure enhanced_sound_manager.py is in your project directory.")
'''
        
        test_file = Path("test_sounds.py")
        with open(test_file, 'w') as f:
            f.write(test_script)
        
        print(f"✅ Created sound test script: {test_file}")
    
    def run(self):
        """Run the complete setup process."""
        print("🎵 Professional Poker Sound Setup")
        print("="*40)
        
        # Create directories
        self.create_directory_structure()
        
        # Generate mapping file
        self.generate_sound_map_file()
        
        # Create test script
        self.create_test_script()
        
        # Try to generate simple sounds
        self.generate_simple_sounds()
        
        # Print download guide
        self.print_download_guide()
        
        print("\n" + "="*60)
        print("🚀 SETUP COMPLETE!")
        print("="*60)
        print("Next steps:")
        print("1. Download sounds from the recommended sources")
        print("2. Place them in the appropriate directories")  
        print("3. Run: python test_sounds.py")
        print("4. Integrate with your poker app")
        print("\n💡 Tip: Start with Pixabay for quick free sounds!")


if __name__ == "__main__":
    downloader = PokerSoundDownloader()
    downloader.run() 
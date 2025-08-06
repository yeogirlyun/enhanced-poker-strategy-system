#!/usr/bin/env python3
"""
Professional Poker Sound Downloader

Downloads and organizes professional poker sounds from free sources.
Helps upgrade the poker app's sound system to casino-quality audio.
"""

import os
import requests
import zipfile
import shutil
from pathlib import Path
from urllib.parse import urlparse

class PokerSoundDownloader:
    """Downloads and organizes professional poker sounds."""
    
    def __init__(self):
        self.sounds_dir = Path("sounds")
        self.sounds_dir.mkdir(exist_ok=True)
        
        # Professional sound sources and recommendations
        self.sound_sources = {
            "pixabay": {
                "url": "https://pixabay.com/sound-effects/search/poker/",
                "description": "Free royalty-free poker sounds, no attribution required",
                "recommended_sounds": [
                    "poker chips dropping",
                    "card shuffle",
                    "card dealing",
                    "casino chips stacking",
                    "poker table atmosphere"
                ]
            },
            "zapsplat": {
                "url": "https://www.zapsplat.com/sound-effect-category/poker/",
                "description": "Professional poker chips sound effects pack",
                "recommended_sounds": [
                    "poker chip single drop",
                    "poker chip stack",
                    "card shuffle",
                    "card deal",
                    "poker table background"
                ]
            },
            "videvo": {
                "url": "https://www.videvo.net/search/poker%20sounds/",
                "description": "70 royalty-free poker sound effects",
                "recommended_sounds": [
                    "poker chips",
                    "card sounds",
                    "casino atmosphere",
                    "poker game sounds"
                ]
            }
        }
        
        # Target sound file mapping
        self.target_sounds = {
            "chip_bet.wav": "Single chip dropping sound",
            "chip_stack.wav": "Multiple chips stacking sound", 
            "card_deal.wav": "Card dealing sound",
            "card_shuffle.wav": "Card shuffling sound",
            "card_fold.wav": "Card flipping/folding sound",
            "player_bet.wav": "Player betting sound",
            "player_call.wav": "Player calling sound",
            "player_raise.wav": "Player raising sound",
            "player_fold.wav": "Player folding sound",
            "player_check.wav": "Player checking sound",
            "player_all_in.wav": "All-in dramatic sound",
            "winner_announce.wav": "Winner announcement sound",
            "pot_split.wav": "Pot splitting sound",
            "pot_rake.wav": "Pot raking sound",
            "button_move.wav": "Dealer button moving sound",
            "turn_notify.wav": "Turn notification sound"
        }
    
    def print_download_guide(self):
        """Print a comprehensive download guide."""
        print("🎵 PROFESSIONAL POKER SOUND DOWNLOAD GUIDE")
        print("=" * 60)
        print()
        
        print("📋 RECOMMENDED FREE SOURCES:")
        for source, info in self.sound_sources.items():
            print(f"• {source.upper()}: {info['url']}")
            print(f"  {info['description']}")
            print(f"  Recommended sounds: {', '.join(info['recommended_sounds'])}")
            print()
        
        print("🎯 ESSENTIAL SOUNDS TO DOWNLOAD:")
        for filename, description in self.target_sounds.items():
            print(f"• {filename}: {description}")
        print()
        
        print("📁 DOWNLOAD INSTRUCTIONS:")
        print("1. Visit the recommended sources above")
        print("2. Search for the specific sound types")
        print("3. Download in WAV format (preferred) or MP3")
        print("4. Rename files to match the target filenames")
        print("5. Place all files in the 'sounds' directory")
        print()
        
        print("🔧 INTEGRATION STEPS:")
        print("1. Run: python3 sound_downloader.py --check")
        print("2. Run: python3 sound_downloader.py --organize")
        print("3. Test sounds with: python3 test_enhanced_sound.py")
        print()
        
        print("💡 PRO TIPS:")
        print("• Start with 5-6 core sounds first")
        print("• Ensure consistent volume levels")
        print("• Test timing with visual actions")
        print("• Consider user volume preferences")
        print("• Mobile compatibility testing")
    
    def check_existing_sounds(self):
        """Check what sounds are already available."""
        print("🔍 CHECKING EXISTING SOUNDS")
        print("=" * 40)
        
        existing_sounds = []
        missing_sounds = []
        
        for filename in self.target_sounds.keys():
            filepath = self.sounds_dir / filename
            if filepath.exists():
                size = filepath.stat().st_size
                existing_sounds.append((filename, size))
            else:
                missing_sounds.append(filename)
        
        if existing_sounds:
            print("✅ EXISTING SOUNDS:")
            for filename, size in existing_sounds:
                print(f"  • {filename} ({size:,} bytes)")
        
        if missing_sounds:
            print("\n❌ MISSING SOUNDS:")
            for filename in missing_sounds:
                print(f"  • {filename}")
        
        print(f"\n📊 SUMMARY: {len(existing_sounds)}/{len(self.target_sounds)} sounds available")
        
        return len(existing_sounds), len(missing_sounds)
    
    def organize_sounds(self):
        """Organize and validate downloaded sounds."""
        print("🔧 ORGANIZING SOUNDS")
        print("=" * 30)
        
        # Check for common variations
        variations = {
            "chip_bet": ["chip_bet", "chip_drop", "poker_chip", "single_chip"],
            "chip_stack": ["chip_stack", "chips_stack", "multiple_chips", "chip_pile"],
            "card_deal": ["card_deal", "deal_card", "card_sound", "dealing"],
            "card_shuffle": ["card_shuffle", "shuffle", "shuffling", "cards_shuffle"],
            "card_fold": ["card_fold", "fold_card", "card_flip", "flip_card"],
            "player_bet": ["player_bet", "bet_sound", "betting", "place_bet"],
            "player_call": ["player_call", "call_sound", "calling"],
            "player_raise": ["player_raise", "raise_sound", "raising"],
            "player_fold": ["player_fold", "fold_sound", "folding"],
            "player_check": ["player_check", "check_sound", "checking"],
            "player_all_in": ["player_all_in", "all_in", "allin", "dramatic"],
            "winner_announce": ["winner_announce", "winner", "victory", "win"],
            "pot_split": ["pot_split", "split_pot", "pot_divide"],
            "pot_rake": ["pot_rake", "rake", "house_take"],
            "button_move": ["button_move", "dealer_button", "button"],
            "turn_notify": ["turn_notify", "turn", "notification", "alert"]
        }
        
        # Look for files with similar names
        for target, variations_list in variations.items():
            target_file = self.sounds_dir / f"{target}.wav"
            
            if not target_file.exists():
                # Look for variations
                for variation in variations_list:
                    for ext in [".wav", ".mp3", ".ogg"]:
                        possible_file = self.sounds_dir / f"{variation}{ext}"
                        if possible_file.exists():
                            # Rename to target filename
                            shutil.move(str(possible_file), str(target_file))
                            print(f"✅ Renamed {possible_file.name} → {target_file.name}")
                            break
                    else:
                        continue
                    break
                else:
                    print(f"❌ Missing: {target_file.name}")
            else:
                print(f"✅ Found: {target_file.name}")
    
    def create_sound_quality_report(self):
        """Create a detailed sound quality report."""
        print("📊 SOUND QUALITY REPORT")
        print("=" * 30)
        
        total_size = 0
        sound_details = []
        
        for filename in self.target_sounds.keys():
            filepath = self.sounds_dir / filename
            if filepath.exists():
                size = filepath.stat().st_size
                total_size += size
                
                # Quality assessment
                if size > 100000:  # > 100KB
                    quality = "High"
                elif size > 50000:  # > 50KB
                    quality = "Medium"
                else:
                    quality = "Low"
                
                sound_details.append((filename, size, quality))
        
        if sound_details:
            print("📁 SOUND FILES:")
            for filename, size, quality in sound_details:
                print(f"  • {filename}: {size:,} bytes ({quality} quality)")
            
            print(f"\n📈 TOTAL SIZE: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
            print(f"🎯 AVERAGE QUALITY: {sum(1 for _, _, q in sound_details if q == 'High')}/{len(sound_details)} high quality")
        else:
            print("❌ No sound files found")
    
    def run(self, args=None):
        """Main execution method."""
        if not args:
            import sys
            args = sys.argv[1:]
        
        if "--guide" in args or not args:
            self.print_download_guide()
        elif "--check" in args:
            self.check_existing_sounds()
        elif "--organize" in args:
            self.organize_sounds()
        elif "--report" in args:
            self.create_sound_quality_report()
        elif "--all" in args:
            self.print_download_guide()
            print("\n" + "="*60 + "\n")
            self.check_existing_sounds()
            print("\n" + "="*60 + "\n")
            self.organize_sounds()
            print("\n" + "="*60 + "\n")
            self.create_sound_quality_report()
        else:
            print("Usage: python3 sound_downloader.py [--guide|--check|--organize|--report|--all]")
            print("  --guide    : Show download guide")
            print("  --check    : Check existing sounds")
            print("  --organize : Organize downloaded sounds")
            print("  --report   : Create quality report")
            print("  --all      : Run all operations")

if __name__ == "__main__":
    downloader = PokerSoundDownloader()
    downloader.run() 
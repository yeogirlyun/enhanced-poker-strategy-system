#!/usr/bin/env python3
"""
Sound Detection and Mapping System

Scans existing sound files and maps them to poker actions.
Provides detailed information about current sound usage.
"""

import os
import json
from pathlib import Path
from enhanced_sound_manager import sound_manager

class SoundDetectionSystem:
    """Detects and maps existing sound files to poker actions."""
    
    def __init__(self):
        self.sounds_dir = Path("sounds")
        self.sound_manager = sound_manager
        
        # Sound action mappings
        self.sound_actions = {
            # Card Actions
            'card_deal': ['card_deal.wav', 'card_deal.mp3', 'dealing.wav', 'dealing.mp3'],
            'card_shuffle': ['card_shuffle.wav', 'card_shuffle.mp3', 'shuffle.wav', 'shuffle.mp3', 'cards-shuffling-87543.mp3', 'shuffling-cards-01-86984.mp3'],
            'fold': ['card_fold.wav', 'card_fold.mp3', 'fold.wav', 'fold.mp3'],
            
            # Chip Actions
            'chip_bet': ['chip_bet.wav', 'chip_bet.mp3', 'bet.wav', 'bet.mp3', 'poker_chips1-87592.mp3'],
            'chip_collect': ['chip_collect.wav', 'chip_collect.mp3', 'collect.wav', 'collect.mp3', 'coin-257878.mp3'],
            'chip_stack': ['chip_stack.wav', 'chip_stack.mp3', 'stack.wav', 'stack.mp3', 'money-bag-82960.mp3'],
            
            # Player Actions
            'player_bet': ['player_bet.wav', 'player_bet.mp3', 'bet.wav', 'bet.mp3'],
            'player_call': ['player_call.wav', 'player_call.mp3', 'call.wav', 'call.mp3'],
            'player_raise': ['player_raise.wav', 'player_raise.mp3', 'raise.wav', 'raise.mp3'],
            'player_check': ['player_check.wav', 'player_check.mp3', 'check.wav', 'check.mp3'],
            'player_fold': ['player_fold.wav', 'player_fold.mp3', 'fold.wav', 'fold.mp3'],
            'player_all_in': ['player_all_in.wav', 'player_all_in.mp3', 'all_in.wav', 'all_in.mp3', 'allinpushchips2-39133.mp3'],
            
            # Pot Actions
            'pot_win': ['pot_win.wav', 'pot_win.mp3', 'win.wav', 'win.mp3', 'money-bag-82960.mp3'],
            'pot_split': ['pot_split.wav', 'pot_split.mp3', 'split.wav', 'split.mp3'],
            'pot_rake': ['pot_rake.wav', 'pot_rake.mp3', 'rake.wav', 'rake.mp3'],
            
            # Winner Actions
            'winner_announce': ['winner_announce.wav', 'winner_announce.mp3', 'winner.wav', 'winner.mp3', 'cash-register-kaching-376867.mp3'],
            
            # UI Actions
            'button_click': ['button_click.wav', 'button_click.mp3', 'click.wav', 'click.mp3', 'coin-257878.mp3'],
            'button_hover': ['button_hover.wav', 'button_hover.mp3', 'hover.wav', 'hover.mp3'],
            'button_move': ['button_move.wav', 'button_move.mp3', 'move.wav', 'move.mp3'],
            'turn_notify': ['turn_notify.wav', 'turn_notify.mp3', 'turn.wav', 'turn.mp3'],
            'notification': ['notification.wav', 'notification.mp3', 'notify.wav', 'notify.mp3'],
            
            # System Actions
            'success': ['success.wav', 'success.mp3'],
            'error': ['error.wav', 'error.mp3'],
            'menu_open': ['menu_open.wav', 'menu_open.mp3']
        }
        
        # Scan and map existing sounds
        self.existing_sounds = self._scan_existing_sounds()
        self.sound_mappings = self._create_sound_mappings()
    
    def _scan_existing_sounds(self):
        """Scan all existing sound files in the sounds directory."""
        existing_sounds = {}
        
        if not self.sounds_dir.exists():
            print(f"❌ Sounds directory not found: {self.sounds_dir}")
            return existing_sounds
        
        # Scan all files in sounds directory
        for file_path in self.sounds_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.wav', '.mp3', '.ogg']:
                file_name = file_path.name
                file_size = file_path.stat().st_size
                
                # Determine quality based on file size
                if file_size > 100000:  # > 100KB
                    quality = "High"
                elif file_size > 50000:  # > 50KB
                    quality = "Medium"
                else:
                    quality = "Low"
                
                existing_sounds[file_name] = {
                    'path': str(file_path),
                    'size': file_size,
                    'quality': quality,
                    'type': file_path.suffix.lower()
                }
        
        return existing_sounds
    
    def _create_sound_mappings(self):
        """Create mappings between sound actions and existing files."""
        mappings = {}
        
        for action, possible_files in self.sound_actions.items():
            # Find the best available file for this action
            best_file = None
            best_quality = "Low"
            
            for possible_file in possible_files:
                if possible_file in self.existing_sounds:
                    file_info = self.existing_sounds[possible_file]
                    
                    # Prefer higher quality files
                    if file_info['quality'] == "High" or (best_quality == "Low" and file_info['quality'] == "Medium"):
                        best_file = possible_file
                        best_quality = file_info['quality']
            
            if best_file:
                mappings[action] = {
                    'file': best_file,
                    'quality': best_quality,
                    'size': self.existing_sounds[best_file]['size'],
                    'path': self.existing_sounds[best_file]['path']
                }
        
        return mappings
    
    def print_sound_analysis(self):
        """Print comprehensive analysis of existing sounds."""
        print("🎵 SOUND DETECTION ANALYSIS")
        print("=" * 50)
        
        print(f"\n📁 SOUNDS DIRECTORY: {self.sounds_dir}")
        print(f"📊 TOTAL FILES FOUND: {len(self.existing_sounds)}")
        
        if not self.existing_sounds:
            print("❌ No sound files found!")
            return
        
        # Group by quality
        high_quality = []
        medium_quality = []
        low_quality = []
        unmapped = []
        
        for file_name, file_info in self.existing_sounds.items():
            if file_info['quality'] == "High":
                high_quality.append((file_name, file_info))
            elif file_info['quality'] == "Medium":
                medium_quality.append((file_name, file_info))
            else:
                low_quality.append((file_name, file_info))
        
        # Check which files are mapped
        mapped_files = set()
        for action, mapping in self.sound_mappings.items():
            mapped_files.add(mapping['file'])
        
        # Find unmapped files
        for file_name in self.existing_sounds.keys():
            if file_name not in mapped_files:
                unmapped.append(file_name)
        
        print(f"\n🎯 HIGH QUALITY ({len(high_quality)}):")
        for file_name, file_info in high_quality:
            status = "✅ MAPPED" if file_name in mapped_files else "❌ UNMAPPED"
            print(f"  • {file_name} ({file_info['size']:,} bytes) - {status}")
        
        print(f"\n🎯 MEDIUM QUALITY ({len(medium_quality)}):")
        for file_name, file_info in medium_quality:
            status = "✅ MAPPED" if file_name in mapped_files else "❌ UNMAPPED"
            print(f"  • {file_name} ({file_info['size']:,} bytes) - {status}")
        
        print(f"\n🎯 LOW QUALITY ({len(low_quality)}):")
        for file_name, file_info in low_quality[:10]:  # Show first 10
            status = "✅ MAPPED" if file_name in mapped_files else "❌ UNMAPPED"
            print(f"  • {file_name} ({file_info['size']:,} bytes) - {status}")
        if len(low_quality) > 10:
            print(f"  ... and {len(low_quality) - 10} more")
        
        if unmapped:
            print(f"\n❌ UNMAPPED FILES ({len(unmapped)}):")
            for file_name in unmapped[:10]:
                print(f"  • {file_name}")
            if len(unmapped) > 10:
                print(f"  ... and {len(unmapped) - 10} more")
        
        print(f"\n📊 MAPPING SUMMARY:")
        print(f"  • Total files: {len(self.existing_sounds)}")
        print(f"  • Mapped actions: {len(self.sound_mappings)}")
        print(f"  • Unmapped files: {len(unmapped)}")
        print(f"  • High quality mapped: {sum(1 for m in self.sound_mappings.values() if m['quality'] == 'High')}")
        print(f"  • Medium quality mapped: {sum(1 for m in self.sound_mappings.values() if m['quality'] == 'Medium')}")
    
    def print_action_mappings(self):
        """Print current action-to-file mappings."""
        print("\n🎵 ACTION MAPPINGS")
        print("=" * 30)
        
        for action, mapping in self.sound_mappings.items():
            print(f"  • {action:20s} → {mapping['file']} ({mapping['quality']} quality)")
        
        # Show unmapped actions
        mapped_actions = set(self.sound_mappings.keys())
        all_actions = set(self.sound_actions.keys())
        unmapped_actions = all_actions - mapped_actions
        
        if unmapped_actions:
            print(f"\n❌ UNMAPPED ACTIONS ({len(unmapped_actions)}):")
            for action in sorted(unmapped_actions):
                print(f"  • {action}")
    
    def get_current_mappings(self):
        """Get current sound mappings for GUI display."""
        return self.sound_mappings
    
    def get_unmapped_files(self):
        """Get list of files that aren't mapped to any action."""
        mapped_files = set()
        for action, mapping in self.sound_mappings.items():
            mapped_files.add(mapping['file'])
        
        unmapped = []
        for file_name in self.existing_sounds.keys():
            if file_name not in mapped_files:
                unmapped.append(file_name)
        
        return unmapped
    
    def suggest_mappings(self):
        """Suggest mappings for unmapped files."""
        suggestions = {}
        unmapped_files = self.get_unmapped_files()
        
        for file_name in unmapped_files:
            file_lower = file_name.lower()
            
            # Simple keyword matching
            if 'chip' in file_lower or 'coin' in file_lower:
                suggestions[file_name] = ['chip_bet', 'chip_collect', 'chip_stack']
            elif 'card' in file_lower or 'shuffle' in file_lower:
                suggestions[file_name] = ['card_shuffle', 'card_deal']
            elif 'bet' in file_lower:
                suggestions[file_name] = ['player_bet', 'chip_bet']
            elif 'call' in file_lower:
                suggestions[file_name] = ['player_call']
            elif 'raise' in file_lower:
                suggestions[file_name] = ['player_raise']
            elif 'check' in file_lower:
                suggestions[file_name] = ['player_check']
            elif 'fold' in file_lower:
                suggestions[file_name] = ['player_fold', 'card_fold']
            elif 'all' in file_lower or 'push' in file_lower:
                suggestions[file_name] = ['player_all_in']
            elif 'winner' in file_lower or 'win' in file_lower:
                suggestions[file_name] = ['winner_announce', 'pot_win']
            elif 'cash' in file_lower or 'money' in file_lower:
                suggestions[file_name] = ['winner_announce', 'pot_win', 'chip_collect']
            else:
                suggestions[file_name] = ['unknown']
        
        return suggestions
    
    def update_sound_manager_mappings(self):
        """Update the sound manager with current mappings."""
        if hasattr(self.sound_manager, 'sound_configs'):
            updated_count = 0
            
            for action, mapping in self.sound_mappings.items():
                if action in self.sound_manager.sound_configs:
                    config = self.sound_manager.sound_configs[action]
                    if config.name != mapping['file']:
                        config.name = mapping['file']
                        updated_count += 1
                        print(f"✅ Updated {action} → {mapping['file']}")
            
            print(f"✅ Updated {updated_count} sound manager mappings")
            return updated_count
        else:
            print("❌ Sound manager not properly initialized")
            return 0

# Global sound detection system instance
sound_detector = SoundDetectionSystem() 
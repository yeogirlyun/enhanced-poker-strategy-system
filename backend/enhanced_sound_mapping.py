#!/usr/bin/env python3
"""
Enhanced Sound Mapping System

Analyzes available sounds and creates optimal mappings for the best audio experience.
"""

import os
from pathlib import Path
from enhanced_sound_manager import sound_manager, SoundCategory

class EnhancedSoundMapper:
    """Maps and optimizes sound files for the best poker experience."""
    
    def __init__(self):
        self.sounds_dir = Path("sounds")
        self.sound_manager = sound_manager
        
        # Analyze available sounds and their quality
        self.available_sounds = self._analyze_sounds()
        
        # Create optimal sound mappings
        self.optimal_mappings = self._create_optimal_mappings()
    
    def _analyze_sounds(self):
        """Analyze all available sound files and their quality."""
        sounds = {}
        
        for file_path in self.sounds_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.wav', '.mp3', '.ogg']:
                size = file_path.stat().st_size
                name = file_path.stem
                
                # Quality assessment based on file size and type
                if size > 100000:  # > 100KB
                    quality = "High"
                elif size > 50000:  # > 50KB
                    quality = "Medium"
                else:
                    quality = "Low"
                
                # Categorize sounds based on filename
                category = self._categorize_sound(name)
                
                sounds[name] = {
                    'file': file_path.name,
                    'size': size,
                    'quality': quality,
                    'category': category,
                    'path': str(file_path)
                }
        
        return sounds
    
    def _categorize_sound(self, name):
        """Categorize sounds based on their filename."""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['chip', 'coin', 'money', 'cash']):
            return "chip"
        elif any(word in name_lower for word in ['card', 'shuffle', 'shuffling']):
            return "card"
        elif any(word in name_lower for word in ['all', 'push', 'in']):
            return "all_in"
        elif any(word in name_lower for word in ['winner', 'win', 'announce']):
            return "winner"
        elif any(word in name_lower for word in ['button', 'move', 'turn']):
            return "ui"
        elif any(word in name_lower for word in ['player', 'bet', 'call', 'raise', 'fold', 'check']):
            return "action"
        else:
            return "other"
    
    def _create_optimal_mappings(self):
        """Create optimal sound mappings using the best available sounds."""
        mappings = {}
        
        # Chip sounds - prioritize high quality chip sounds
        chip_sounds = {k: v for k, v in self.available_sounds.items() 
                      if v['category'] == 'chip'}
        
        if chip_sounds:
            # Use the highest quality chip sound for chip_bet
            best_chip = max(chip_sounds.values(), key=lambda x: x['size'])
            mappings['chip_bet'] = best_chip['file']
            
            # Use coin sound for chip_collect if available
            coin_sounds = {k: v for k, v in chip_sounds.items() 
                          if 'coin' in k.lower()}
            if coin_sounds:
                best_coin = max(coin_sounds.values(), key=lambda x: x['size'])
                mappings['chip_collect'] = best_coin['file']
            else:
                mappings['chip_collect'] = best_chip['file']
        
        # Card sounds - prioritize high quality shuffle sounds
        card_sounds = {k: v for k, v in self.available_sounds.items() 
                      if v['category'] == 'card'}
        
        if card_sounds:
            # Use the highest quality shuffle sound
            shuffle_sounds = {k: v for k, v in card_sounds.items() 
                            if 'shuffle' in k.lower()}
            if shuffle_sounds:
                best_shuffle = max(shuffle_sounds.values(), key=lambda x: x['size'])
                mappings['card_shuffle'] = best_shuffle['file']
        
        # All-in sounds - use the new all-in push sound
        all_in_sounds = {k: v for k, v in self.available_sounds.items() 
                        if v['category'] == 'all_in'}
        
        if all_in_sounds:
            best_all_in = max(all_in_sounds.values(), key=lambda x: x['size'])
            mappings['player_all_in'] = best_all_in['file']
        
        # Winner sounds - use cash register sound for big wins
        winner_sounds = {k: v for k, v in self.available_sounds.items() 
                        if 'cash' in k.lower() or 'money' in k.lower()}
        
        if winner_sounds:
            best_winner = max(winner_sounds.values(), key=lambda x: x['size'])
            mappings['winner_announce'] = best_winner['file']
        
        return mappings
    
    def apply_optimal_mappings(self):
        """Apply the optimal sound mappings to the sound manager."""
        print("🎵 Applying optimal sound mappings...")
        
        applied_count = 0
        for sound_name, file_name in self.optimal_mappings.items():
            if file_name in self.available_sounds:
                sound_info = self.available_sounds[file_name.replace('.wav', '').replace('.mp3', '')]
                
                # Update the sound manager's sound configs
                if hasattr(self.sound_manager, 'sound_configs'):
                    # Find the corresponding sound config
                    for config_name, config in self.sound_manager.sound_configs.items():
                        if config_name == sound_name:
                            # Update the sound file
                            config.name = file_name
                            print(f"✅ Mapped {sound_name} → {file_name} ({sound_info['quality']} quality)")
                            applied_count += 1
                            break
        
        print(f"✅ Applied {applied_count} optimal sound mappings")
        return applied_count
    
    def print_sound_analysis(self):
        """Print a detailed analysis of available sounds."""
        print("🎵 SOUND ANALYSIS REPORT")
        print("=" * 50)
        
        # Group sounds by category
        categories = {}
        for name, info in self.available_sounds.items():
            cat = info['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((name, info))
        
        for category, sounds in categories.items():
            print(f"\n📁 {category.upper()} SOUNDS:")
            for name, info in sounds:
                print(f"  • {name}: {info['file']} ({info['size']:,} bytes, {info['quality']} quality)")
        
        print(f"\n📊 SUMMARY:")
        print(f"  • Total sounds: {len(self.available_sounds)}")
        print(f"  • Categories: {len(categories)}")
        print(f"  • High quality: {sum(1 for s in self.available_sounds.values() if s['quality'] == 'High')}")
        print(f"  • Medium quality: {sum(1 for s in self.available_sounds.values() if s['quality'] == 'Medium')}")
        print(f"  • Low quality: {sum(1 for s in self.available_sounds.values() if s['quality'] == 'Low')}")
        
        # Show optimal mappings
        if self.optimal_mappings:
            print(f"\n🎯 OPTIMAL MAPPINGS:")
            for sound_name, file_name in self.optimal_mappings.items():
                info = self.available_sounds.get(file_name.replace('.wav', '').replace('.mp3', ''), {})
                quality = info.get('quality', 'Unknown')
                print(f"  • {sound_name} → {file_name} ({quality} quality)")
    
    def test_enhanced_sounds(self):
        """Test the enhanced sound mappings."""
        print("🎵 Testing enhanced sound mappings...")
        
        # Apply optimal mappings
        self.apply_optimal_mappings()
        
        # Test key sounds
        test_sounds = ['chip_bet', 'card_shuffle', 'player_all_in', 'winner_announce']
        
        for sound in test_sounds:
            if sound in self.optimal_mappings:
                print(f"🎵 Testing {sound}...")
                self.sound_manager.play(sound)
        
        print("✅ Enhanced sound testing complete!")

# Global enhanced sound mapper instance
enhanced_mapper = EnhancedSoundMapper() 
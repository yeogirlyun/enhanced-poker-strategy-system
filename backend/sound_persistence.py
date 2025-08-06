#!/usr/bin/env python3
"""
Sound Persistence System

Saves and loads custom sound replacements between app restarts.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional

class SoundPersistence:
    """Manages persistent sound configurations."""
    
    def __init__(self):
        self.config_file = Path("sound_config.json")
        self.sounds_dir = Path("sounds")
        self.custom_mappings = {}
        self.load_config()
    
    def load_config(self):
        """Load custom sound mappings from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.custom_mappings = json.load(f)
                print(f"📂 Loaded {len(self.custom_mappings)} custom sound mappings")
            except Exception as e:
                print(f"❌ Error loading sound config: {e}")
                self.custom_mappings = {}
        else:
            print(f"📂 No sound config file found, starting fresh")
            self.custom_mappings = {}
    
    def save_config(self):
        """Save custom sound mappings to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.custom_mappings, f, indent=2)
            print(f"💾 Saved {len(self.custom_mappings)} custom sound mappings")
        except Exception as e:
            print(f"❌ Error saving sound config: {e}")
    
    def set_custom_sound(self, sound_name: str, filename: str):
        """Set a custom sound mapping."""
        self.custom_mappings[sound_name] = filename
        self.save_config()
        print(f"🎵 Set custom sound: {sound_name} → {filename}")
    
    def get_custom_sound(self, sound_name: str) -> Optional[str]:
        """Get custom sound filename for a sound."""
        return self.custom_mappings.get(sound_name)
    
    def has_custom_sound(self, sound_name: str) -> bool:
        """Check if a sound has a custom mapping."""
        return sound_name in self.custom_mappings
    
    def remove_custom_sound(self, sound_name: str):
        """Remove a custom sound mapping."""
        if sound_name in self.custom_mappings:
            del self.custom_mappings[sound_name]
            self.save_config()
            print(f"🗑️  Removed custom sound: {sound_name}")
    
    def get_all_custom_mappings(self) -> Dict[str, str]:
        """Get all custom sound mappings."""
        return self.custom_mappings.copy()
    
    def validate_custom_sounds(self):
        """Validate that all custom sound files still exist."""
        valid_mappings = {}
        invalid_mappings = []
        
        for sound_name, filename in self.custom_mappings.items():
            file_path = self.sounds_dir / filename
            if file_path.exists():
                valid_mappings[sound_name] = filename
            else:
                invalid_mappings.append(sound_name)
                print(f"⚠️  Custom sound file not found: {filename}")
        
        # Update mappings with only valid ones
        self.custom_mappings = valid_mappings
        self.save_config()
        
        if invalid_mappings:
            print(f"🗑️  Removed {len(invalid_mappings)} invalid mappings")
        
        return len(invalid_mappings) == 0

def main():
    """Test the sound persistence system."""
    print("💾 TESTING SOUND PERSISTENCE")
    print("=" * 40)
    
    persistence = SoundPersistence()
    
    # Test setting a custom sound
    persistence.set_custom_sound("fold", "fold_custom.wav")
    
    # Test getting the custom sound
    custom_file = persistence.get_custom_sound("fold")
    print(f"📝 Custom sound for 'fold': {custom_file}")
    
    # Test validation
    persistence.validate_custom_sounds()
    
    print(f"📋 All custom mappings: {persistence.get_all_custom_mappings()}")

if __name__ == "__main__":
    main() 
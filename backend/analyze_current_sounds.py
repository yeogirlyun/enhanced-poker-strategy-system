#!/usr/bin/env python3
"""
Analyze Current Sounds

Shows what sound files are currently available and how they're mapped.
"""

from pathlib import Path
from sound_detection_system import sound_detector

def main():
    """Analyze current sound files and mappings."""
    print("🎵 ANALYZING CURRENT SOUNDS")
    print("=" * 50)
    
    # Print comprehensive analysis
    sound_detector.print_sound_analysis()
    
    print("\n" + "=" * 50)
    print("🎯 ACTION MAPPINGS")
    print("=" * 50)
    
    # Print action mappings
    sound_detector.print_action_mappings()
    
    print("\n" + "=" * 50)
    print("🔧 UPDATING SOUND MANAGER")
    print("=" * 50)
    
    # Update sound manager with current mappings
    updated_count = sound_detector.update_sound_manager_mappings()
    
    print(f"\n✅ Analysis complete! Updated {updated_count} sound mappings.")
    print("\n🎯 Next Steps:")
    print("  1. Check the sound analysis above to see what files are available")
    print("  2. Review the action mappings to see what's currently mapped")
    print("  3. Use the GUI to test and replace sounds as needed")

if __name__ == "__main__":
    main() 
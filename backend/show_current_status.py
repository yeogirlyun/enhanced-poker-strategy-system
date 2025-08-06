#!/usr/bin/env python3
"""
Show Current Sound Status

Displays the current status of all sound mappings after the mapping process.
"""

from sound_detection_system import sound_detector

def main():
    """Show current sound status."""
    print("🎵 CURRENT SOUND STATUS")
    print("=" * 50)
    
    # Get current mappings
    mappings = sound_detector.get_current_mappings()
    
    print(f"📊 MAPPED ACTIONS ({len(mappings)}):")
    for action, mapping in mappings.items():
        print(f"  ✅ {action:20s} → {mapping['file']} ({mapping['quality']} quality)")
    
    # Show unmapped actions
    all_actions = set(sound_detector.sound_actions.keys())
    mapped_actions = set(mappings.keys())
    unmapped_actions = all_actions - mapped_actions
    
    if unmapped_actions:
        print(f"\n❌ UNMAPPED ACTIONS ({len(unmapped_actions)}):")
        for action in sorted(unmapped_actions):
            print(f"  • {action}")
    
    # Show unmapped files
    unmapped_files = sound_detector.get_unmapped_files()
    if unmapped_files:
        print(f"\n📁 UNMAPPED FILES ({len(unmapped_files)}):")
        for file_name in unmapped_files[:10]:
            file_info = sound_detector.existing_sounds[file_name]
            print(f"  • {file_name} ({file_info['size']:,} bytes, {file_info['quality']} quality)")
        if len(unmapped_files) > 10:
            print(f"  ... and {len(unmapped_files) - 10} more")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  • Total sound files: {len(sound_detector.existing_sounds)}")
    print(f"  • Mapped actions: {len(mappings)}")
    print(f"  • Unmapped actions: {len(unmapped_actions)}")
    print(f"  • Unmapped files: {len(unmapped_files)}")
    
    # Show quality distribution
    high_quality = sum(1 for m in mappings.values() if m['quality'] == 'High')
    medium_quality = sum(1 for m in mappings.values() if m['quality'] == 'Medium')
    low_quality = sum(1 for m in mappings.values() if m['quality'] == 'Low')
    
    print(f"  • High quality mapped: {high_quality}")
    print(f"  • Medium quality mapped: {medium_quality}")
    print(f"  • Low quality mapped: {low_quality}")

if __name__ == "__main__":
    main() 
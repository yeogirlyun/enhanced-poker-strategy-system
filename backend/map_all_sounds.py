#!/usr/bin/env python3
"""
Map All Sounds

Automatically maps all existing sound files to their appropriate poker actions.
"""

from sound_detection_system import sound_detector
from enhanced_sound_manager import sound_manager

def main():
    """Map all existing sounds to poker actions."""
    print("🎵 MAPPING ALL SOUNDS")
    print("=" * 50)
    
    # Get current mappings
    current_mappings = sound_detector.get_current_mappings()
    unmapped_files = sound_detector.get_unmapped_files()
    
    print(f"📊 Current Status:")
    print(f"  • Mapped actions: {len(current_mappings)}")
    print(f"  • Unmapped files: {len(unmapped_files)}")
    
    # Show unmapped files
    print(f"\n📁 UNMAPPED FILES:")
    for file_name in unmapped_files:
        file_info = sound_detector.existing_sounds[file_name]
        print(f"  • {file_name} ({file_info['size']:,} bytes, {file_info['quality']} quality)")
    
    # Suggest mappings
    suggestions = sound_detector.suggest_mappings()
    
    print(f"\n🎯 SUGGESTED MAPPINGS:")
    for file_name, suggested_actions in suggestions.items():
        if suggested_actions != ['unknown']:
            print(f"  • {file_name} → {', '.join(suggested_actions)}")
    
    # Auto-map based on suggestions
    print(f"\n🔧 AUTO-MAPPING SOUNDS:")
    mapped_count = 0
    
    for file_name, suggested_actions in suggestions.items():
        if suggested_actions != ['unknown']:
            # Use the first suggested action
            action = suggested_actions[0]
            
            # Check if action is already mapped
            if action not in current_mappings:
                # Map the file to this action
                file_info = sound_detector.existing_sounds[file_name]
                sound_detector.sound_mappings[action] = {
                    'file': file_name,
                    'quality': file_info['quality'],
                    'size': file_info['size'],
                    'path': file_info['path']
                }
                print(f"  ✅ {file_name} → {action}")
                mapped_count += 1
            else:
                print(f"  ⚠️  {file_name} → {action} (already mapped)")
    
    # Update sound manager
    print(f"\n🔧 UPDATING SOUND MANAGER:")
    updated_count = sound_detector.update_sound_manager_mappings()
    
    print(f"\n✅ MAPPING COMPLETE!")
    print(f"  • New mappings: {mapped_count}")
    print(f"  • Total mappings: {len(sound_detector.sound_mappings)}")
    print(f"  • Sound manager updates: {updated_count}")
    
    # Show final mappings
    print(f"\n🎵 FINAL MAPPINGS:")
    for action, mapping in sound_detector.sound_mappings.items():
        print(f"  • {action:20s} → {mapping['file']} ({mapping['quality']} quality)")
    
    # Show remaining unmapped files
    remaining_unmapped = sound_detector.get_unmapped_files()
    if remaining_unmapped:
        print(f"\n❌ REMAINING UNMAPPED FILES ({len(remaining_unmapped)}):")
        for file_name in remaining_unmapped[:10]:
            print(f"  • {file_name}")
        if len(remaining_unmapped) > 10:
            print(f"  ... and {len(remaining_unmapped) - 10} more")

if __name__ == "__main__":
    main() 
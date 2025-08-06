#!/usr/bin/env python3
"""
Test New Sounds and Apply Optimal Mappings

Analyzes the new sounds you've added and applies the best ones to the sound system.
"""

from enhanced_sound_mapping import enhanced_mapper
from enhanced_sound_manager import sound_manager

def main():
    """Analyze new sounds and apply optimal mappings."""
    print("🎵 ANALYZING NEW SOUNDS")
    print("=" * 50)
    
    # Print detailed analysis
    enhanced_mapper.print_sound_analysis()
    
    print("\n" + "=" * 50)
    print("🎯 APPLYING OPTIMAL MAPPINGS")
    print("=" * 50)
    
    # Apply optimal mappings
    applied_count = enhanced_mapper.apply_optimal_mappings()
    
    print(f"\n✅ Applied {applied_count} optimal sound mappings!")
    
    print("\n" + "=" * 50)
    print("🎵 TESTING ENHANCED SOUNDS")
    print("=" * 50)
    
    # Test the enhanced sounds
    enhanced_mapper.test_enhanced_sounds()
    
    print("\n🎉 ENHANCED SOUND SYSTEM READY!")
    print("Your poker app now uses the best available sounds!")

if __name__ == "__main__":
    main() 
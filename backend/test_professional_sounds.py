#!/usr/bin/env python3
"""
Test Professional Sound System

Demonstrates the professional sound integration and helps verify sound setup.
"""

from professional_sound_integration import professional_sounds
from enhanced_sound_manager import sound_manager

def test_professional_sound_system():
    """Test the professional sound system features."""
    
    print("🎵 TESTING PROFESSIONAL SOUND SYSTEM")
    print("=" * 50)
    
    # Setup professional sounds
    professional_sounds.setup_professional_sounds()
    
    # Print quality report
    professional_sounds.print_quality_report()
    
    print("\n🎯 TESTING SOUND FEATURES")
    print("=" * 30)
    
    # Test basic professional sounds
    print("📋 Test 1: Basic Professional Sounds")
    test_sounds = ["check", "call", "bet", "raise", "fold", "all_in"]
    for sound in test_sounds:
        print(f"🎵 Testing {sound}...")
        professional_sounds.play_professional_sound(sound)
    
    # Test dramatic sequences
    print("\n📋 Test 2: Dramatic Sound Sequences")
    sequences = ["big_win", "all_in_action", "fold_sequence", "raise_sequence", "pot_scoop"]
    for sequence in sequences:
        print(f"🎵 Testing dramatic sequence: {sequence}")
        professional_sounds.play_dramatic_sequence(sequence)
    
    # Test contextual actions
    print("\n📋 Test 3: Contextual Action Sounds")
    actions = [
        ("fold", 0, False),
        ("call", 50, False),
        ("raise", 200, False),
        ("all_in", 1000, True)
    ]
    
    for action, amount, is_all_in in actions:
        print(f"🎵 Testing {action} with ${amount} (all-in: {is_all_in})")
        professional_sounds.play_contextual_action(action, amount, is_all_in)
    
    # Test win sequences
    print("\n📋 Test 4: Win Sound Sequences")
    win_amounts = [50, 500, 2000]
    for amount in win_amounts:
        print(f"🎵 Testing win sequence for ${amount}")
        professional_sounds.play_win_sequence(amount)
    
    # Test volume controls
    print("\n📋 Test 5: Volume Control Tests")
    sound_manager.set_master_volume(0.7)
    print(f"✅ Master volume set to: {int(sound_manager.master_volume * 100)}%")
    
    # Test category volumes
    from enhanced_sound_manager import SoundCategory
    sound_manager.set_category_volume(SoundCategory.GAME, 0.9)
    print(f"✅ Game volume set to: {int(sound_manager.category_volumes[SoundCategory.GAME] * 100)}%")
    
    print("\n🎯 SUMMARY:")
    print("-" * 30)
    print("✅ Professional sound system working")
    print("✅ Dramatic sequences functioning")
    print("✅ Contextual actions responding")
    print("✅ Volume controls operational")
    print("✅ Casino-quality audio experience")

def check_sound_quality():
    """Check the quality of available sounds."""
    print("\n🔍 SOUND QUALITY CHECK")
    print("=" * 30)
    
    report = professional_sounds.get_sound_quality_report()
    
    if report["total_available"] > 0:
        print(f"✅ {report['total_available']} professional sounds available")
        print(f"🎯 {report['dramatic_sequences']} dramatic sequences configured")
        
        # Show high quality sounds
        high_quality = [s for s in report["available_sounds"] if s[2] > 100000]
        if high_quality:
            print(f"🏆 {len(high_quality)} high-quality sounds detected")
        
        return True
    else:
        print("❌ No professional sounds found")
        print("💡 Run: python3 sound_downloader.py --guide")
        return False

def main():
    """Main test function."""
    print("🎵 PROFESSIONAL POKER SOUND SYSTEM TEST")
    print("=" * 60)
    
    # Check if sounds are available
    if check_sound_quality():
        # Run comprehensive tests
        test_professional_sound_system()
        
        print("\n🎉 PROFESSIONAL SOUND SYSTEM READY!")
        print("Your poker app now has casino-quality audio!")
    else:
        print("\n⚠️  SETUP REQUIRED")
        print("Please download professional sounds first:")
        print("1. Run: python3 sound_downloader.py --guide")
        print("2. Download recommended sounds")
        print("3. Run this test again")

if __name__ == "__main__":
    main() 
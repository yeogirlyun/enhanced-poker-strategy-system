#!/usr/bin/env python3
"""
Verification script for GTO hands loading fix

This verifies that the 'dict' object attribute access errors are fixed
and the GUI should launch correctly.
"""

def test_gto_hands_loading():
    """Test GTO hands loading without errors."""
    print("🔍 Verifying GTO hands loading fix...")
    
    try:
        from ui.tabs.hands_review_tab_ppsm import GTOHandsLoader
        
        # Test the loader
        loader = GTOHandsLoader()
        hands = loader.load_gto_hands()
        
        if not hands:
            print("❌ No hands loaded")
            return False
        
        print(f"✅ Loaded {len(hands)} hands successfully")
        
        # Test accessing Hand object attributes (the ones that were causing errors)
        first_hand = hands[0]
        
        # These should all work now with dictionary access
        hand_id = first_hand.metadata['hand_id']
        small_blind = first_hand.metadata['small_blind']
        big_blind = first_hand.metadata['big_blind']
        
        # Test seat access
        first_seat = first_hand.seats[0]
        seat_no = first_seat['seat_no']
        display_name = first_seat['display_name']
        starting_stack = first_seat['starting_stack']
        
        print(f"✅ Hand access works: {hand_id}")
        print(f"✅ Blinds: {small_blind}/{big_blind}")
        print(f"✅ Seat access works: {seat_no}, {display_name}, ${starting_stack}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_gui_compatibility():
    """Test GUI compatibility."""
    print("\\n🔍 Testing GUI compatibility...")
    
    try:
        import tkinter as tk
        from ui.tabs.hands_review_tab_ppsm import HandsReviewTabPPSM
        from ui.services.event_bus import EventBus
        from ui.services.theme_manager import ThemeManager
        from ui.state.store import Store
        
        # Mock services
        class MockServices:
            def get_app(self, name):
                if name == 'event_bus':
                    return EventBus()
                elif name == 'store':
                    def mock_reducer(state, action): return state
                    return Store({}, mock_reducer)  
                elif name == 'theme':
                    return ThemeManager()
                return None
        
        # Test creating the tab (this was the source of the original error)
        root = tk.Tk()
        root.withdraw()
        
        tab = HandsReviewTabPPSM(root, MockServices())
        
        print("✅ HandsReviewTabPPSM creates without errors")
        print("✅ GTO hands integration working")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI compatibility error: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🎯 GTO Hands Loading Fix Verification")
    print("=" * 50)
    
    tests = [
        ("GTO Hands Loading", test_gto_hands_loading),
        ("GUI Compatibility", test_gui_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\\n🧪 {test_name}:")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\\n" + "=" * 50)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All verification tests passed!")
        print("🚀 GUI should launch correctly now without the 'dict' object errors!")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

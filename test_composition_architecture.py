#!/usr/bin/env python3
"""
Test Composition Architecture

This script tests the new composition-based HandsReviewSessionStateMachine
to verify it works correctly with FPSM as a member variable.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_composition_architecture():
    """Test the composition architecture."""
    print("🧪 Testing Composition Architecture...")
    
    try:
        # Test 1: Import the new composition-based module
        print("✅ Test 1: Importing HandsReviewSessionStateMachine...")
        from core.hands_review_session_state_machine import HandsReviewSessionStateMachine
        print("   ✓ Successfully imported HandsReviewSessionStateMachine")
        
        # Test 2: Check if it uses composition (not inheritance)
        print("✅ Test 2: Checking composition pattern...")
        
        # Check if the class inherits from FlexiblePokerStateMachine
        bases = HandsReviewSessionStateMachine.__bases__
        if FlexiblePokerStateMachine in bases:
            print("   ❌ FAILED: Still using inheritance!")
            return False
        else:
            print("   ✓ SUCCESS: Using composition pattern!")
        
        # Test 3: Check if it has FPSM as a member variable
        print("✅ Test 3: Checking FPSM member variable...")
        
        # Create an instance
        from core.flexible_poker_state_machine import GameConfig
        config = GameConfig(num_players=6)
        session = HandsReviewSessionStateMachine(config)
        
        # Check if it has fpsm as a member variable
        if hasattr(session, 'fpsm'):
            print("   ✓ SUCCESS: Has 'fpsm' member variable")
            print(f"   ✓ FPSM type: {type(session.fpsm).__name__}")
        else:
            print("   ❌ FAILED: No 'fpsm' member variable")
            return False
        
        # Test 4: Check if it can call FPSM methods
        print("✅ Test 4: Testing FPSM method calls...")
        
        # Test calling FPSM method through composition
        try:
            # This should work with composition
            display_state = session.get_display_state()
            print("   ✓ SUCCESS: Can call FPSM methods through composition")
        except Exception as e:
            print(f"   ❌ FAILED: Cannot call FPSM methods: {e}")
            return False
        
        print("\n🎉 ALL TESTS PASSED! Composition architecture is working!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   This suggests the composition module has import issues")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = test_composition_architecture()
    if success:
        print("\n🚀 Ready to integrate with UI!")
    else:
        print("\n💥 Composition architecture test failed!")
        sys.exit(1)

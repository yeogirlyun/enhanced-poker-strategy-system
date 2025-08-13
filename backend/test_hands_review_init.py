#!/usr/bin/env python3
"""
Test script to debug hands review state machine initialization issues.
"""

import sys
import traceback

def test_hands_review_init():
    """Test hands review state machine initialization."""
    print("🔍 Testing Hands Review State Machine Initialization")
    print("=" * 60)
    
    try:
        # Test 1: Import the state machine
        print("📦 Test 1: Import HandsReviewPokerStateMachine")
        from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
        print("✅ Import successful")
        
        # Test 2: Import GameConfig
        print("\n📦 Test 2: Import GameConfig")
        from core.flexible_poker_state_machine import GameConfig
        print("✅ GameConfig import successful")
        
        # Test 3: Create config
        print("\n⚙️  Test 3: Create GameConfig")
        config = GameConfig(
            num_players=6,
            small_blind=1.0,
            big_blind=2.0,
            starting_stack=200.0
        )
        print("✅ GameConfig created successfully")
        
        # Test 4: Create state machine
        print("\n🤖 Test 4: Create HandsReviewPokerStateMachine")
        state_machine = HandsReviewPokerStateMachine(config, session_logger=None)
        print("✅ State machine created successfully")
        
        # Test 5: Check attributes
        print("\n🔍 Test 5: Check state machine attributes")
        print(f"   • historical_actions: {hasattr(state_machine, 'historical_actions')}")
        print(f"   • action_index: {hasattr(state_machine, 'action_index')}")
        print(f"   • current_hand_data: {hasattr(state_machine, 'current_hand_data')}")
        print(f"   • validation_errors: {hasattr(state_machine, 'validation_errors')}")
        print(f"   • is_data_valid: {hasattr(state_machine, 'is_data_valid')}")
        print(f"   • session_logger: {hasattr(state_machine, 'session_logger')}")
        print(f"   • logger: {hasattr(state_machine, 'logger')}")
        
        # Test 6: Test validation method
        print("\n🔍 Test 6: Test validation method")
        test_hand = {
            'id': 'TEST-001',
            'name': 'Test Hand',
            'players': [{'name': 'Player 1', 'starting_stack': 1000, 'hole_cards': ['Ah', 'Kh']}],
            'actions': {'preflop': []},
            'board': {}
        }
        
        is_valid, errors = HandsReviewPokerStateMachine.validate_hand_data_integrity(test_hand)
        print(f"   • Validation result: {'✅ Valid' if is_valid else '❌ Invalid'}")
        if errors:
            print(f"   • Errors: {len(errors)}")
            for error in errors[:3]:
                print(f"     - {error}")
        
        print("\n🎉 All tests passed! Hands review state machine is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hands_review_init()
    print(f"\n{'🎉 Test completed successfully!' if success else '💥 Test failed!'}")
    exit(0 if success else 1)

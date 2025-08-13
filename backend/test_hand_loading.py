#!/usr/bin/env python3
"""
Test script to verify hand loading functionality in hands review.
"""

import json
from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
from core.flexible_poker_state_machine import GameConfig

def test_hand_loading():
    """Test hand loading functionality."""
    print("🔍 Testing Hand Loading Functionality")
    print("=" * 60)
    
    try:
        # Create state machine
        print("🤖 Creating HandsReviewPokerStateMachine...")
        config = GameConfig(
            num_players=6,
            small_blind=1.0,
            big_blind=2.0,
            starting_stack=200.0
        )
        state_machine = HandsReviewPokerStateMachine(config, session_logger=None)
        print("✅ State machine created successfully")
        
        # Load hands data
        print("\n📁 Loading hands data...")
        with open('data/clean_poker_hands_flat.json', 'r') as f:
            data = json.load(f)
        
        hands = data.get('hands', [])
        print(f"✅ Loaded {len(hands)} hands")
        
        # Verify we're using clean data
        if hands and len(hands) > 0:
            first_hand = hands[0]
            print(f"🔍 First hand: {first_hand.get('id', 'Unknown')}")
            print(f"   Source: {first_hand.get('session_id', 'Unknown')}")
            if 'session_id' in first_hand:
                print("✅ Using clean generated data")
            else:
                print("⚠️  Still using old data - check file paths")
        
        # Test validation and filtering
        print("\n🔍 Testing validation and filtering...")
        valid_hands, invalid_hands = HandsReviewPokerStateMachine.filter_valid_hands(hands)
        
        print(f"📊 Results:")
        print(f"   • Total hands: {len(hands)}")
        print(f"   • Valid hands: {len(valid_hands)}")
        print(f"   • Invalid hands: {len(invalid_hands)}")
        
        if len(valid_hands) == 0:
            print("❌ No valid hands found!")
            return False
        
        # Test loading a valid hand
        print(f"\n📥 Testing hand loading with first valid hand...")
        test_hand = valid_hands[0]
        print(f"   • Hand ID: {test_hand.get('id', 'Unknown')}")
        print(f"   • Name: {test_hand.get('name', 'Unknown')}")
        print(f"   • Players: {len(test_hand.get('players', []))}")
        print(f"   • Actions: {sum(len(test_hand.get('actions', {}).get(street, [])) for street in ['preflop', 'flop', 'turn', 'river'])}")
        
        # Load the hand
        success = state_machine.load_hand_for_review(test_hand)
        
        if success:
            print("✅ Hand loaded successfully!")
            
            # Check state machine state
            print(f"\n🔍 State machine state after loading:")
            print(f"   • is_data_valid: {state_machine.is_data_valid}")
            print(f"   • validation_errors: {len(state_machine.validation_errors)}")
            print(f"   • historical_actions: {len(state_machine.historical_actions)}")
            print(f"   • action_index: {state_machine.action_index}")
            print(f"   • current_hand_data: {state_machine.current_hand_data.get('id', 'Unknown')}")
            
            # Test stepping forward
            print(f"\n▶️  Testing step forward...")
            result = state_machine.step_forward()
            print(f"   • Step result: {result}")
            print(f"   • Action index after step: {state_machine.action_index}")
            
            if state_machine.action_index > 0:
                print("✅ Step forward working correctly!")
            else:
                print("⚠️  Step forward may have issues")
            
        else:
            print("❌ Failed to load hand!")
            validation_status = state_machine.get_validation_status()
            print(f"   • Validation status: {validation_status}")
            return False
        
        print(f"\n🎉 Hand loading test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hand_loading()
    print(f"\n{'🎉 Hand loading test passed!' if success else '💥 Hand loading test failed!'}")
    exit(0 if success else 1)

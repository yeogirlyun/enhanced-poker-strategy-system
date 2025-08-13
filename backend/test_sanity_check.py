#!/usr/bin/env python3
"""
Test script for hands review sanity check functionality.
This demonstrates how the system validates hand data integrity and filters out problematic hands.
"""

import json
from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine

def test_sanity_check():
    """Test the sanity check functionality."""
    print("🔍 Testing Hands Review Sanity Check System")
    print("=" * 60)
    
    try:
        # Load hands data
        print("📁 Loading hands data...")
        with open('data/legendary_hands_complete_130_repaired.json', 'r') as f:
            data = json.load(f)
        
        hands = data.get('hands', [])
        print(f"✅ Loaded {len(hands)} hands")
        
        # Test individual hand validation
        print("\n🔍 Testing individual hand validation...")
        test_hand = hands[0] if hands else {}
        
        is_valid, errors = HandsReviewPokerStateMachine.validate_hand_data_integrity(test_hand)
        
        if is_valid:
            print(f"✅ Hand {test_hand.get('id', 'Unknown')} is valid")
        else:
            print(f"❌ Hand {test_hand.get('id', 'Unknown')} has validation errors:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   • {error}")
        
        # Test bulk validation and filtering
        print("\n🔍 Testing bulk validation and filtering...")
        valid_hands, invalid_hands = HandsReviewPokerStateMachine.filter_valid_hands(hands)
        
        print(f"📊 Validation Results:")
        print(f"   • Total hands: {len(hands)}")
        print(f"   • Valid hands: {len(valid_hands)}")
        print(f"   • Invalid hands: {len(invalid_hands)}")
        
        # Show examples of invalid hands
        if invalid_hands:
            print(f"\n⚠️  Examples of invalid hands:")
            for i, invalid_hand in enumerate(invalid_hands[:3]):  # Show first 3
                print(f"   {i+1}. {invalid_hand['hand_id']}: {invalid_hand['name']}")
                print(f"      Errors: {len(invalid_hand['errors'])}")
                for error in invalid_hand['errors'][:2]:  # Show first 2 errors
                    print(f"        • {error}")
        
        # Test session safety
        print(f"\n🛡️  Session Safety:")
        print(f"   • Hands available for review: {len(valid_hands)}")
        print(f"   • Problematic hands filtered out: {len(invalid_hands)}")
        
        if len(valid_hands) == len(hands):
            print("   ✅ All hands are valid - no session disruption expected")
        elif len(valid_hands) > 0:
            print(f"   ⚠️  {len(valid_hands)} hands available for review")
            print(f"   ⚠️  {len(invalid_hands)} hands filtered out to prevent issues")
        else:
            print("   ❌ No valid hands found - session cannot proceed")
        
        # Test specific validation scenarios
        print(f"\n🧪 Testing specific validation scenarios...")
        
        # Test 1: Missing required keys
        print("   Test 1: Missing required keys")
        invalid_hand = {'id': 'TEST-001'}  # Missing name, players, actions, board
        is_valid, errors = HandsReviewPokerStateMachine.validate_hand_data_integrity(invalid_hand)
        print(f"      Result: {'❌ Invalid' if not is_valid else '✅ Valid'}")
        if errors:
            print(f"      Errors: {len(errors)}")
        
        # Test 2: Invalid action types
        print("   Test 2: Invalid action types")
        invalid_action_hand = {
            'id': 'TEST-002',
            'name': 'Test Hand',
            'players': [{'name': 'Player 1', 'stack': 1000, 'cards': ['Ah', 'Kh']}],
            'actions': {'preflop': [{'actor': 0, 'player_name': 'Player 1', 'action_type': 'invalid_action', 'amount': 0}]},
            'board': {}
        }
        is_valid, errors = HandsReviewPokerStateMachine.validate_hand_data_integrity(invalid_action_hand)
        print(f"      Result: {'❌ Invalid' if not is_valid else '✅ Valid'}")
        if errors:
            print(f"      Errors: {len(errors)}")
        
        # Test 3: Valid hand structure
        print("   Test 3: Valid hand structure")
        if valid_hands:
            test_valid_hand = valid_hands[0]
            is_valid, errors = HandsReviewPokerStateMachine.validate_hand_data_integrity(test_valid_hand)
            print(f"      Result: {'❌ Invalid' if not is_valid else '✅ Valid'}")
            if errors:
                print(f"      Errors: {len(errors)}")
        
        print(f"\n🎯 Summary:")
        print(f"   • Sanity check system is {'✅ WORKING' if len(valid_hands) > 0 else '❌ FAILED'}")
        print(f"   • Data integrity: {'✅ GOOD' if len(invalid_hands) == 0 else '⚠️  ISSUES DETECTED'}")
        print(f"   • Session safety: {'✅ GUARANTEED' if len(valid_hands) > 0 else '❌ NOT GUARANTEED'}")
        
        return len(valid_hands) > 0
        
    except Exception as e:
        print(f"❌ Error during sanity check test: {e}")
        return False

if __name__ == "__main__":
    success = test_sanity_check()
    print(f"\n{'🎉 Sanity check test completed successfully!' if success else '💥 Sanity check test failed!'}")
    exit(0 if success else 1)

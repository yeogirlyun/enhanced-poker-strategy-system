#!/usr/bin/env python3
"""Debug validation logic to see why hands are being rejected."""

import json
from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine

def main():
    print("🔍 Debugging validation logic...")
    
    # Load the repaired data
    with open('data/legendary_hands_complete_130_properly_repaired.json', 'r') as f:
        data = json.load(f)
    
    hands = data.get('hands', [])
    print(f"📁 Loaded {len(hands)} hands")
    
    # Test first few hands individually
    for i in range(min(5, len(hands))):
        hand = hands[i]
        hand_id = hand.get('id', f'Unknown-{i}')
        
        print(f"\n🔍 Testing hand {i+1}: {hand_id}")
        
        # Validate individual hand
        is_valid, errors = HandsReviewPokerStateMachine.validate_hand_data_integrity(hand)
        
        print(f"  Valid: {is_valid}")
        if errors:
            print(f"  Errors ({len(errors)}):")
            for j, error in enumerate(errors[:3]):  # Show first 3 errors
                print(f"    {j+1}: {error}")
            if len(errors) > 3:
                print(f"    ... and {len(errors) - 3} more errors")
        else:
            print("  No validation errors")
    
    # Test the filter function
    print(f"\n🔍 Testing filter_valid_hands function...")
    valid, invalid = HandsReviewPokerStateMachine.filter_valid_hands(hands)
    
    print(f"  Total hands: {len(hands)}")
    print(f"  Valid hands: {len(valid)}")
    print(f"  Invalid hands: {len(invalid)}")
    
    if invalid:
        print(f"\n📋 First invalid hand details:")
        first_invalid = invalid[0]
        print(f"  ID: {first_invalid['hand_id']}")
        print(f"  Name: {first_invalid['name']}")
        print(f"  Errors ({len(first_invalid['errors'])}):")
        for i, error in enumerate(first_invalid['errors'][:5]):
            print(f"    {i+1}: {error}")

if __name__ == "__main__":
    main()

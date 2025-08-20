#!/usr/bin/env python3
"""
Simple MVU Test - Just test the store directly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from ui.mvu import MVUStore, Model, NextPressed, LoadHand
from ui.mvu.drivers import create_driver


def main():
    """Test MVU store directly"""
    print("🧪 Testing MVU Store Directly...")
    
    # Create initial model
    initial_model = Model.initial(session_mode="REVIEW")
    
    # Create store
    store = MVUStore(initial_model=initial_model)
    
    # Create sample hand data
    hand_data = {
        "hand_id": "SIMPLE_TEST",
        "seats": {
            0: {
                "player_uid": "hero",
                "name": "Hero", 
                "stack": 1000,
                "chips_in_front": 0,
                "folded": False,
                "all_in": False,
                "cards": ["As", "Kh"],
                "position": 0
            },
            1: {
                "player_uid": "villain",
                "name": "Villain",
                "stack": 1000,
                "chips_in_front": 0,
                "folded": False,
                "all_in": False,
                "cards": ["Qd", "Jc"],
                "position": 1
            }
        },
        "stacks": {0: 1000, 1: 1000},
        "board": [],
        "pot": 0,
        "actions": [
            {"seat": 0, "action": "RAISE", "amount": 30, "street": "PREFLOP"},
            {"seat": 1, "action": "CALL", "amount": 30, "street": "PREFLOP"},
            {"seat": 0, "action": "BET", "amount": 50, "street": "FLOP"},
            {"seat": 1, "action": "FOLD", "amount": None, "street": "FLOP"}
        ],
        "review_len": 4,
        "to_act_seat": 0,
        "legal_actions": ["CHECK", "CALL", "BET", "RAISE", "FOLD"]
    }
    
    # Create and set driver
    driver = create_driver("REVIEW", hand_data=hand_data)
    store.set_session_driver(driver)
    
    # Load hand
    print("\n📋 Loading hand...")
    store.dispatch(LoadHand(hand_data=hand_data))
    
    # Print initial state
    model = store.get_model()
    print(f"\n🎯 Initial state: cursor={model.review_cursor}, len={model.review_len}, to_act={model.to_act_seat}")
    
    # Click Next button 5 times
    for i in range(5):
        print(f"\n🖱️ === BUTTON CLICK #{i+1} ===")
        store.dispatch(NextPressed())
        
        # Print state after click
        model = store.get_model()
        print(f"🎯 After click {i+1}: cursor={model.review_cursor}, len={model.review_len}, to_act={model.to_act_seat}, pot={model.pot}")
        
        # Print seat states
        for seat_num, seat in model.seats.items():
            print(f"  Seat {seat_num}: {seat.name} - Stack: ${seat.stack}, Bet: ${seat.chips_in_front}, Folded: {seat.folded}, Acting: {seat.acting}")
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    main()

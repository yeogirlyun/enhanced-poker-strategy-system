#!/usr/bin/env python3
"""Test multiple hand loading to verify UI cleanup."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
from core.flexible_poker_state_machine import GameConfig
from core.json_hands_database import JSONHandsDatabase, HandCategory

def test_multiple_hand_loading():
    """Test loading multiple hands to verify complete UI cleanup."""
    print("🔍 Testing Multiple Hand Loading for UI Cleanup")
    print("=" * 60)
    
    # Create state machine
    print("🤖 Creating HandsReviewPokerStateMachine...")
    config = GameConfig(
        num_players=6,
        small_blind=1.0,
        big_blind=2.0,
        starting_stack=1000.0,
        test_mode=True
    )
    state_machine = HandsReviewPokerStateMachine(config, session_logger=None)
    
    # Load hands data
    print("📁 Loading hands data...")
    database = JSONHandsDatabase()
    hands_data = database.load_all_hands()
    
    # Extract hands from the category structure
    if isinstance(hands_data, dict):
        # The database returns a dict with HandCategory.LEGENDARY as key
        hands = hands_data.get(HandCategory.LEGENDARY, [])
        if not hands:
            # Try alternative key names
            hands = hands_data.get('hands', [])
    else:
        hands = hands_data
    
    print(f"✅ Loaded {len(hands)} hands")
    
    # Test loading multiple hands
    test_hands = [0, 1, 2, 3]  # Test first 4 hands
    
    for i, hand_index in enumerate(test_hands):
        print(f"\n🔄 Loading Hand {i+1}: {hands[hand_index].metadata.id}")
        
        # Load the hand - use raw_data from ParsedHand
        success = state_machine.load_hand_for_review(hands[hand_index].raw_data)
        if not success:
            print(f"❌ Failed to load hand {hand_index}")
            continue
        
        print(f"✅ Hand {i+1} loaded successfully")
        
        # Check if we can step forward a few times
        print(f"  ▶️  Stepping forward 3 actions...")
        for step in range(3):
            result = state_machine.step_forward()
            if result:
                print(f"    Step {step+1}: ✅")
            else:
                print(f"    Step {step+1}: ❌ (hand may be complete)")
                break
        
        # Verify state is clean
        print(f"  🧹 Checking state cleanliness...")
        if state_machine.game_state.board == []:
            print(f"    Board: ✅ Clean (empty)")
        else:
            print(f"    Board: ❌ Not clean: {state_machine.game_state.board}")
        
        if state_machine.game_state.street == "preflop":
            print(f"    Street: ✅ Clean (preflop)")
        else:
            print(f"    Street: ❌ Not clean: {state_machine.game_state.street}")
        
        print(f"  📊 Action index: {state_machine.action_index}")
        print(f"  🎯 Current state: {state_machine.current_state}")
    
    print("\n🎉 Multiple hand loading test completed!")
    print("✅ If all hands loaded cleanly, UI cleanup is working!")

if __name__ == "__main__":
    test_multiple_hand_loading()

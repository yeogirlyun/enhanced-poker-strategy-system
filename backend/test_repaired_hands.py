#!/usr/bin/env python3
"""
Test the repaired hands data to ensure FPSM natural progression works correctly.
"""

import json
import sys
from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
from core.multi_session_game_director import MultiSessionGameDirector
from core.session_manager import SessionManager
from core.flexible_poker_state_machine import GameConfig

def test_repaired_hands():
    """Test the repaired hands with the hands review system."""
    try:
        print("🧪 Testing repaired hands with hands review system...")
        print("=" * 80)
        
        # Load repaired data
        with open('data/legendary_hands_complete_130_repaired.json', 'r') as f:
            data = json.load(f)
        
        hands = data.get('hands', [])
        print(f"📁 Loaded {len(hands)} repaired hands")
        
        # Test first few hands
        test_hands = hands[:3]  # Test first 3 hands
        
        for i, hand in enumerate(test_hands):
            print(f"\n🎯 Testing Hand {i + 1}: {hand.get('id', 'Unknown')}")
            print(f"   Name: {hand.get('name', 'Unnamed')}")
            
            # Create session manager and game director
            session_manager = SessionManager(num_players=9, big_blind=1000)
            session_manager.start_session()
            session_logger = session_manager.logger
            game_director = MultiSessionGameDirector(session_logger)
            
            # Create hands review state machine
            config = GameConfig(num_players=9, big_blind=1000)
            state_machine = HandsReviewPokerStateMachine(
                config=config,
                session_logger=session_logger
            )
            
            # Load the hand
            success = state_machine.load_hand_for_review(hand)
            if not success:
                print(f"   ❌ Failed to load hand")
                continue
            
            print(f"   ✅ Hand loaded successfully")
            print(f"   📊 Actions: {len(state_machine.historical_actions)}")
            
            # Test stepping through actions
            action_count = 0
            max_actions = min(10, len(state_machine.historical_actions))  # Test first 10 actions
            
            for step in range(max_actions):
                result = state_machine.step_forward()
                if result:
                    action_count += 1
                    current_state = state_machine.current_state
                    board_size = len(state_machine.game_state.board)
                    print(f"   🔄 Step {step + 1}: {current_state} (Board: {board_size})")
                else:
                    print(f"   🏁 Reached end of hand at step {step + 1}")
                    break
            
            print(f"   📈 Processed {action_count} actions")
            print(f"   🎯 Final state: {state_machine.current_state}")
            print(f"   🃏 Final board size: {len(state_machine.game_state.board)}")
            
            # Check if we reached showdown
            if state_machine.current_state.name in ['SHOWDOWN', 'END_HAND']:
                print(f"   🏆 Successfully reached showdown!")
            else:
                print(f"   ⚠️  Hand did not complete naturally")
        
        print("\n" + "=" * 80)
        print("🎉 Testing completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_repaired_hands()
    sys.exit(0 if success else 1)

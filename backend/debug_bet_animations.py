#!/usr/bin/env python3
"""
Debug script to test bet animations in hands review.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
from core.flexible_poker_state_machine import GameConfig
from core.json_hands_database import JSONHandsDatabase

def main():
    print("🔍 Debugging Bet Animations in Hands Review")
    print("=" * 50)
    
    try:
        # Load database
        database = JSONHandsDatabase('data/clean_poker_hands_flat.json')
        hands_data = database.load_all_hands()
        print(f"📊 Database keys: {list(hands_data.keys())}")
        print(f"📊 Hands data types: {[(k, type(v), len(v) if isinstance(v, list) else 'N/A') for k, v in hands_data.items()]}")
        
        # Try different keys
        hands = hands_data.get('LEGENDARY', [])
        if not hands:
            hands = hands_data.get('legendary', [])
        if not hands:
            hands = list(hands_data.values())[0] if hands_data else []
        
        hands = hands[:1]  # Just one hand
        
        if not hands:
            print("❌ No hands found in database")
            return
        
        hand = hands[0]
        print(f"📋 Testing hand: {hand.metadata.id}")
        print(f"📊 Total actions: {len(hand.raw_data.get('actions', []))}")
        
        # Create state machine
        config = GameConfig()
        state_machine = HandsReviewPokerStateMachine(config)
        
        print("\n🔄 Loading hand...")
        state_machine.load_hand_for_review(hand.raw_data)
        
        print(f"✅ Hand loaded")
        print(f"   - Current state: {state_machine.current_state}")
        print(f"   - Board size: {len(state_machine.game_state.board)}")
        print(f"   - Pot: ${state_machine.game_state.pot:.2f}")
        print(f"   - Players: {len(state_machine.game_state.players)}")
        
        # Step through actions to see transitions
        print("\n🎬 Stepping through actions...")
        for i in range(10):  # First 10 actions to see more of the hand
            print(f"\n--- Action {i} ---")
            
            if state_machine.action_index >= len(state_machine.historical_actions):
                print("🏁 End of actions reached")
                break
            
            action = state_machine.historical_actions[state_machine.action_index]
            print(f"   Action: {action.get('player_name')} {action.get('action_type')} ${action.get('amount', 0):.2f}")
            print(f"   Before - State: {state_machine.current_state}, Board: {len(state_machine.game_state.board)}")
            
            result = state_machine.step_forward()
            print(f"   Result: {result}")
            print(f"   After  - State: {state_machine.current_state}, Board: {len(state_machine.game_state.board)}")
            
            if not result:
                print("🏁 Step failed or hand ended")
                break
        
        print("\n🎯 Final state:")
        print(f"   - State: {state_machine.current_state}")
        print(f"   - Board: {state_machine.game_state.board}")
        print(f"   - Pot: ${state_machine.game_state.pot:.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

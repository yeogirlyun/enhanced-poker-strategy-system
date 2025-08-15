#!/usr/bin/env python3
"""
Test the exact GUI flow that's failing.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import json
from backend.core.gto_to_hand_converter import GTOToHandConverter
from backend.core.hand_model_decision_engine import HandModelDecisionEngine
from backend.core.bot_session_state_machine import HandsReviewBotSession
from backend.core.flexible_poker_state_machine import GameConfig

def test_exact_gui_flow():
    """Test the exact same flow that the GUI uses."""
    print("🔍 TESTING EXACT GUI FLOW")
    print("=" * 50)
    
    # Step 1: Load the exact same data as GUI
    with open("/Users/yeogirlyun/Python/Poker/data/clean_gto_hands_generated.json", 'r') as f:
        data = json.load(f)
    
    first_hand = data['hands'][0]
    print(f"📊 Using GUI hand: {first_hand.get('id')}")
    
    # Step 2: Convert exactly like GUI does
    hand_model = GTOToHandConverter.convert_gto_hand(first_hand)
    hand_to_review = {
        'hand_model': hand_model,
        'hand_id': hand_model.metadata.hand_id,
        'id': hand_model.metadata.hand_id,
        'timestamp': hand_model.metadata.hand_id,
        'source': 'GTO Generated (Hand Model)',
        'comments': '',
        'street_comments': {'preflop': '', 'flop': '', 'turn': '', 'river': '', 'overall': ''}
    }
    
    print(f"✅ Hand converted to review format")
    
    # Step 3: Create decision engine exactly like GUI
    decision_engine = HandModelDecisionEngine(hand_to_review['hand_model'])
    print(f"✅ Decision engine created: {decision_engine.total_actions} actions")
    print(f"   Initial completion state: {decision_engine.is_session_complete()}")
    print(f"   Initial action index: {decision_engine.current_action_index}")
    
    # Step 4: Create session exactly like GUI
    game_config = GameConfig(
        num_players=3,
        starting_stack=1000,
        small_blind=5,
        big_blind=10
    )
    
    session = HandsReviewBotSession(
        config=game_config,
        decision_engine=decision_engine
    )
    
    print(f"✅ Session created")
    
    # Step 5: Set preloaded data exactly like GUI
    session.set_preloaded_hand_data(hand_to_review)
    print(f"✅ Preloaded data set")
    
    # Step 6: Check decision engine state before start_session
    print(f"\n🔍 Before start_session:")
    print(f"   Decision engine completion: {session.decision_engine.is_session_complete()}")
    print(f"   Decision engine action index: {session.decision_engine.current_action_index}")
    print(f"   Decision engine total actions: {session.decision_engine.total_actions}")
    
    # Step 7: Start session exactly like GUI
    print(f"\n🚀 Calling start_session...")
    success = session.start_session()
    print(f"   Start session result: {success}")
    
    # Step 8: Check decision engine state after start_session
    print(f"\n🔍 After start_session:")
    print(f"   Decision engine completion: {session.decision_engine.is_session_complete()}")
    print(f"   Decision engine action index: {session.decision_engine.current_action_index}")
    print(f"   Decision engine total actions: {session.decision_engine.total_actions}")
    print(f"   Session active: {session.session_active}")
    
    # Step 9: Try execute_next_bot_action like GUI Next button
    print(f"\n▶️  Simulating Next button click...")
    result = session.execute_next_bot_action()
    print(f"   execute_next_bot_action result: {result}")
    
    if not result:
        print(f"❌ Next button failed!")
        print(f"   Final completion state: {session.decision_engine.is_session_complete()}")
        print(f"   Final action index: {session.decision_engine.current_action_index}")
    else:
        print(f"✅ Next button worked!")

if __name__ == "__main__":
    test_exact_gui_flow()

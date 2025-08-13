#!/usr/bin/env python3
"""
Test winner announcements and hand complete events in hands review.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
from core.multi_session_game_director import MultiSessionGameDirector
from core.session_manager import SessionManager
from core.flexible_poker_state_machine import GameConfig
from core.flexible_poker_state_machine import GameEvent
import json


class TestEventCapture:
    """Capture events emitted by the state machine."""
    
    def __init__(self):
        self.events = []
    
    def on_event(self, event: GameEvent):
        self.events.append({
            'type': event.event_type,
            'data': event.data if hasattr(event, 'data') else None,
            'timestamp': getattr(event, 'timestamp', None)
        })
        
        if event.event_type == "hand_complete":
            print(f"🎉 HAND_COMPLETE EVENT CAPTURED!")
            print(f"   Winner info: {event.data.get('winner_info', 'None')}")
            print(f"   Pot amount: {event.data.get('pot_amount', 'None')}")
            print(f"   Winners: {event.data.get('winners', 'None')}")


def test_winner_announcements():
    """Test if winner announcements work correctly."""
    print("🧪 Testing Winner Announcements and Hand Complete Events")
    print("="*60)
    
    # Setup
    session_manager = SessionManager(num_players=9, big_blind=100.0)
    session_id = session_manager.start_session()
    logger = session_manager.logger
    
    game_director = MultiSessionGameDirector(logger)
    
    config = GameConfig(
        num_players=9,
        big_blind=100.0,
        small_blind=50.0,
        starting_stack=1000000.0,
        test_mode=True
    )
    
    state_machine = HandsReviewPokerStateMachine(config, session_logger=logger)
    state_machine.set_game_director(game_director)
    
    # Setup event capture
    event_capture = TestEventCapture()
    state_machine.add_event_listener(event_capture)
    
    # Register with game director
    game_director.register_session(
        session_id='hands_review',
        state_machine=state_machine,
        ui_renderer=None,
        audio_manager=None,
        session_type='hands_review'
    )
    game_director.activate_session('hands_review')
    
    # Load a hand
    hands_file = os.path.join(os.path.dirname(__file__), 'data', 'legendary_hands_complete_130_fixed.json')
    with open(hands_file, 'r') as f:
        hands_data = json.load(f)
    
    first_hand = hands_data['hands'][0]  # Test first hand
    print(f"🎮 Loading hand: {first_hand.get('description', 'Unknown')}")
    
    if not state_machine.load_hand_for_review(first_hand):
        print("❌ Failed to load hand")
        return
    
    total_actions = len(state_machine.historical_actions)
    print(f"📋 Hand loaded with {total_actions} actions")
    
    # Step through all actions
    print("\n🎯 Stepping through all actions...")
    for step in range(total_actions + 5):  # Extra steps to ensure completion
        success = state_machine.step_forward()
        current_state = state_machine.current_state
        action_index = getattr(state_machine, 'action_index', 0)
        
        print(f"   Step {step+1}: Action {action_index}/{total_actions}, State: {current_state}, Success: {success}")
        
        # Check for hand completion
        if action_index >= total_actions:
            print("✅ All actions completed - checking for events...")
            break
    
    # Report captured events
    print(f"\n📊 EVENTS CAPTURED: {len(event_capture.events)}")
    for i, event in enumerate(event_capture.events):
        print(f"   {i+1}. {event['type']}: {event['data']}")
    
    # Check specifically for hand_complete
    hand_complete_events = [e for e in event_capture.events if e['type'] == 'hand_complete']
    
    if hand_complete_events:
        print(f"\n🎉 SUCCESS: {len(hand_complete_events)} hand_complete event(s) found!")
        for event in hand_complete_events:
            winner_info = event['data'].get('winner_info', {}) if event['data'] else {}
            print(f"   🏆 Winner: {winner_info.get('name', 'Unknown')}")
            print(f"   💰 Pot: ${winner_info.get('amount', 0):,.0f}")
            print(f"   🃏 Hand: {winner_info.get('hand_description', 'Unknown')}")
    else:
        print(f"\n❌ PROBLEM: No hand_complete events captured!")
        print(f"Final state: {state_machine.current_state}")
        print(f"Action index: {getattr(state_machine, 'action_index', 'Unknown')}")


if __name__ == "__main__":
    test_winner_announcements()

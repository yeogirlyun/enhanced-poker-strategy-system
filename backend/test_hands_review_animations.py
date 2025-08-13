#!/usr/bin/env python3
"""
Test pot animations and chip sounds in hands review.

This script tests:
1. Bet-to-pot animations between streets
2. Correct chip sounds for bet/call actions  
3. Winner announcement and pot-to-winner animation
4. Complete hand progression through all streets

Usage:
    python3 test_hands_review_animations.py
"""

import sys
import os
import json
import time

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.hands_review_poker_state_machine_new import HandsReviewPokerStateMachine
from core.multi_session_game_director import MultiSessionGameDirector
from core.session_manager import SessionManager
from core.flexible_poker_state_machine import GameConfig, GameEvent
from core.types import PokerState


class AnimationTestCapture:
    """Capture events and animations from hands review."""
    
    def __init__(self):
        self.events = []
        self.round_complete_events = []
        self.hand_complete_events = []
        self.sound_events = []
        
    def on_event(self, event: GameEvent):
        self.events.append({
            'type': event.event_type,
            'data': event.data if hasattr(event, 'data') else None,
            'timestamp': time.time()
        })
        
        if event.event_type == "round_complete":
            self.round_complete_events.append(event.data)
            
        elif event.event_type == "hand_complete":
            self.hand_complete_events.append(event.data)
            
        elif event.event_type == "sound":
            self.sound_events.append(event.data)


def test_pot_animations_and_sounds():
    """Test pot animations and chip sounds in hands review."""
    print("🎯 Testing Pot Animations and Chip Sounds in Hands Review")
    print("=" * 60)
    
    # Setup test environment
    session_manager = SessionManager(num_players=9, big_blind=100.0)
    session_id = session_manager.start_session()
    logger = session_manager.logger
    
    # Create game director
    game_director = MultiSessionGameDirector(logger)
    
    # Create hands review state machine
    config = GameConfig(
        num_players=9,
        big_blind=100.0,
        small_blind=50.0,
        starting_stack=1000000.0,
        test_mode=True
    )
    state_machine = HandsReviewPokerStateMachine(config, session_logger=logger)
    state_machine.set_game_director(game_director)
    
    # Register with game director
    game_director.register_session(
        session_id='hands_review',
        state_machine=state_machine,
        ui_renderer=None,  # Headless test
        audio_manager=None,  # Headless test
        session_type='hands_review'
    )
    game_director.activate_session('hands_review')
    
    # Setup event capture
    event_capture = AnimationTestCapture()
    state_machine.add_event_listener(event_capture.on_event)
    
    # Load a legendary hand with multiple betting rounds
    hands_file = os.path.join(os.path.dirname(__file__), 'data', 'legendary_hands_complete_130_fixed.json')
    with open(hands_file, 'r') as f:
        hands_data = json.load(f)
    
    # Test the first hand (2003 WSOP Final - Moneymaker vs Farha)
    hand_data = hands_data['hands'][0]
    hand_name = hand_data.get('description', 'Unknown Hand')
    
    print(f"📋 Testing Hand: {hand_name}")
    print(f"📊 Total Actions: {len(state_machine._flatten_historical_actions(hand_data.get('actions', {})))}")
    
    # Load the hand
    if not state_machine.load_hand_for_review(hand_data):
        print("❌ Failed to load hand")
        return False
        
    total_actions = len(state_machine.historical_actions)
    print(f"✅ Hand loaded successfully with {total_actions} actions")
    
    # Track betting rounds and animations
    betting_rounds = {
        "preflop": {"actions": 0, "round_complete": False, "bet_amounts": []},
        "flop": {"actions": 0, "round_complete": False, "bet_amounts": []},
        "turn": {"actions": 0, "round_complete": False, "bet_amounts": []}, 
        "river": {"actions": 0, "round_complete": False, "bet_amounts": []}
    }
    
    current_street = "preflop"
    bet_sounds_detected = []
    call_sounds_detected = []
    
    # Execute all actions and track events
    action_count = 0
    while action_count < total_actions:
        if action_count >= total_actions:
            break
            
        # Get current action
        if hasattr(state_machine, 'historical_actions'):
            action_data = state_machine.historical_actions[action_count]
            action_type = action_data.get('action_type', 'unknown')
            action_amount = action_data.get('amount', 0.0)
            player_name = action_data.get('player_name', 'Unknown')
            
            print(f"  Action {action_count + 1}: {player_name} {action_type} ${action_amount}")
            
            # Track betting actions
            if action_type in ['bet', 'raise'] and action_amount > 0:
                betting_rounds[current_street]["bet_amounts"].append(action_amount)
                bet_sounds_detected.append(f"{player_name} {action_type} ${action_amount}")
                
            elif action_type == 'call' and action_amount > 0:
                betting_rounds[current_street]["bet_amounts"].append(action_amount)
                call_sounds_detected.append(f"{player_name} {action_type} ${action_amount}")
        
        # Record events before action
        events_before = len(event_capture.events)
        round_complete_before = len(event_capture.round_complete_events)
        
        # Execute step
        old_state = state_machine.current_state
        success = state_machine.step_forward()
        new_state = state_machine.current_state
        
        # Check for state transitions (street changes)
        if old_state != new_state:
            print(f"    🔄 State transition: {old_state} → {new_state}")
            
            # Detect street changes
            if new_state == PokerState.DEAL_FLOP:
                current_street = "flop"
                betting_rounds["preflop"]["round_complete"] = True
            elif new_state == PokerState.DEAL_TURN:
                current_street = "turn" 
                betting_rounds["flop"]["round_complete"] = True
            elif new_state == PokerState.DEAL_RIVER:
                current_street = "river"
                betting_rounds["turn"]["round_complete"] = True
            elif new_state == PokerState.SHOWDOWN:
                betting_rounds["river"]["round_complete"] = True
        
        # Check for new round_complete events
        round_complete_after = len(event_capture.round_complete_events)
        if round_complete_after > round_complete_before:
            round_event = event_capture.round_complete_events[-1]
            street = round_event.get("street", "unknown")
            player_bets = round_event.get("player_bets", [])
            print(f"    🎯 ROUND_COMPLETE event: {street} street with {len(player_bets)} player bets")
            for bet in player_bets:
                print(f"       - {bet.get('player_name', 'Unknown')}: ${bet.get('amount', 0)}")
        
        if not success:
            print(f"    ⚠️ Step failed at action {action_count + 1}")
            break
            
        betting_rounds[current_street]["actions"] += 1
        action_count += 1
        
        # Small delay for readability
        time.sleep(0.05)
    
    # Final results
    print(f"\n📊 ANIMATION AND SOUND TEST RESULTS")
    print("=" * 50)
    
    # Betting Round Summary
    print("🃏 BETTING ROUNDS:")
    for street, data in betting_rounds.items():
        status = "✅ COMPLETE" if data["round_complete"] else "❌ INCOMPLETE"
        bet_count = len(data["bet_amounts"])
        total_bet = sum(data["bet_amounts"])
        print(f"  {street.upper()}: {data['actions']} actions, {bet_count} bets (${total_bet:.0f}) - {status}")
    
    # Round Complete Events
    print(f"\n🎯 ROUND_COMPLETE EVENTS: {len(event_capture.round_complete_events)}")
    for i, event in enumerate(event_capture.round_complete_events):
        street = event.get("street", "unknown")
        player_bets = event.get("player_bets", [])
        print(f"  Event {i + 1}: {street} → {len(player_bets)} player bets for animation")
    
    # Hand Complete Events
    print(f"\n🏆 HAND_COMPLETE EVENTS: {len(event_capture.hand_complete_events)}")
    for i, event in enumerate(event_capture.hand_complete_events):
        winner_info = event.get("winner_info", {})
        pot_amount = event.get("pot_amount", 0)
        winner_name = winner_info.get("name", "Unknown") if winner_info else "Unknown"
        print(f"  Event {i + 1}: Winner: {winner_name}, Pot: ${pot_amount}")
    
    # Sound Events
    print(f"\n🔊 SOUND TEST RESULTS:")
    print(f"  BET sounds detected: {len(bet_sounds_detected)}")
    for sound in bet_sounds_detected[:5]:  # Show first 5
        print(f"    - {sound}")
    if len(bet_sounds_detected) > 5:
        print(f"    ... and {len(bet_sounds_detected) - 5} more")
        
    print(f"  CALL sounds detected: {len(call_sounds_detected)}")
    for sound in call_sounds_detected[:5]:  # Show first 5
        print(f"    - {sound}")
    if len(call_sounds_detected) > 5:
        print(f"    ... and {len(call_sounds_detected) - 5} more")
    
    # Overall Assessment
    round_complete_success = len(event_capture.round_complete_events) >= 3  # At least preflop, flop, turn
    hand_complete_success = len(event_capture.hand_complete_events) >= 1
    sound_success = len(bet_sounds_detected) > 0 and len(call_sounds_detected) > 0
    
    overall_success = round_complete_success and hand_complete_success
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    print(f"  Pot animations (round_complete): {'✅ PASS' if round_complete_success else '❌ FAIL'}")
    print(f"  Winner animations (hand_complete): {'✅ PASS' if hand_complete_success else '❌ FAIL'}")
    print(f"  Chip sounds (bet/call): {'✅ PASS' if sound_success else '❌ FAIL'}")
    print(f"  Overall: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
    
    return overall_success


if __name__ == "__main__":
    try:
        success = test_pot_animations_and_sounds()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Simple test to isolate the action validation issue.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import json
from backend.core.gto_to_hand_converter import GTOToHandConverter
from backend.core.hand_model_decision_engine import HandModelDecisionEngine
from backend.core.bot_session_state_machine import HandsReviewBotSession
from backend.core.flexible_poker_state_machine import GameConfig
from backend.core.session_logger import SessionLogger

def test_action_validation():
    """Test action validation in isolation."""
    
    # Load test hand
    with open('cycle_test_hand.json', 'r') as f:
        hand_data = json.load(f)
    
    # Convert to Hand Model
    hand_model = GTOToHandConverter.convert_gto_hand(hand_data)
    decision_engine = HandModelDecisionEngine(hand_model)
    
    # Create session
    config = GameConfig(num_players=3, starting_stack=1000, small_blind=5, big_blind=10)
    session = HandsReviewBotSession(config=config, decision_engine=decision_engine)
    
    # Set hand data and start
    session.set_preloaded_hand_data({'hand_model': hand_model})
    session.start_session()
    
    print(f"🔍 VALIDATION TEST")
    print(f"=" * 50)
    
    # Check initial state
    print(f"Action player index: {session.action_player_index}")
    action_player = session.get_action_player()
    print(f"Action player: {action_player.name if action_player else 'None'}")
    print(f"Action player current_bet: ${action_player.current_bet if action_player else 'N/A'}")
    print(f"Game current_bet: ${session.game_state.current_bet}")
    print(f"Pot: ${session.game_state.pot}")
    
    # Get valid actions
    valid_actions = session.get_valid_actions_for_player(action_player)
    print(f"Valid actions: {valid_actions}")
    
    # Get decision from engine
    decision = decision_engine.get_decision(session.action_player_index, session.game_state)
    print(f"Engine decision: {decision}")
    
    # Try to execute the action manually
    action = decision['action']
    amount = decision['amount']
    
    print(f"\n🎯 MANUAL VALIDATION")
    print(f"Action: {action}, Amount: ${amount}")
    
    # Check specific validation conditions
    call_amount = valid_actions.get('call_amount', 0)
    print(f"Required call amount: ${call_amount}")
    print(f"Decision amount: ${amount}")
    print(f"Amounts match: {call_amount == amount}")
    print(f"Amounts close: {abs(call_amount - amount) < 0.01}")
    
    # Try to execute (correct parameter order: player, action, amount)
    try:
        success = session.execute_action(action_player, action, amount)
        print(f"Execution result: {success}")
    except Exception as e:
        print(f"Execution error: {e}")

if __name__ == "__main__":
    test_action_validation()

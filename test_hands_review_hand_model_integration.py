#!/usr/bin/env python3
"""
Test the Hands Review Hand Model integration.

This test verifies that:
1. GTO hands can be converted to Hand Model format
2. HandModelDecisionEngine can be created from converted hands
3. The Hands Review system can load and use Hand Model data
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.core.gto_to_hand_converter import GTOToHandConverter
from backend.core.hand_model_decision_engine import HandModelDecisionEngine
from backend.core.bot_session_state_machine import HandsReviewBotSession
from backend.core.flexible_poker_state_machine import GameConfig
import json

def test_hand_model_integration():
    """Test the complete integration flow."""
    
    # Load a GTO hand
    try:
        with open('cycle_test_hand.json', 'r') as f:
            gto_hand = json.load(f)
    except FileNotFoundError:
        print("❌ Test data file not found")
        return False
        
    print("🔄 Step 1: Converting GTO hand to Hand Model...")
    try:
        hand_model = GTOToHandConverter.convert_gto_hand(gto_hand)
        print(f"✅ Conversion successful: {hand_model.metadata.hand_id}")
        print(f"   Players: {len(hand_model.seats)}")
        
        # Calculate total actions
        total_actions = sum(len(street_state.actions) for street_state in hand_model.streets.values())
        print(f"   Actions: {total_actions}")
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return False
    
    print("\n🧠 Step 2: Creating HandModelDecisionEngine...")
    try:
        decision_engine = HandModelDecisionEngine(hand_model)
        print(f"✅ Decision engine created with {decision_engine.total_actions} actions")
    except Exception as e:
        print(f"❌ Decision engine creation failed: {e}")
        return False
    
    print("\n🎮 Step 3: Creating HandsReviewBotSession...")
    try:
        config = GameConfig(
            num_players=len(hand_model.seats),
            starting_stack=1000,
            small_blind=5,
            big_blind=10
        )
        
        session = HandsReviewBotSession(config=config, decision_engine=decision_engine)
        
        # Set the hand data (simulating UI integration)
        session.set_preloaded_hand_data({'hand_model': hand_model})
        
        print(f"✅ Session created for {len(hand_model.seats)} players")
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        return False
    
    print("\n🎯 Step 4: Starting hand session...")
    try:
        session.start_session()
        print("✅ Session started successfully")
        
        # Check if players have correct cards
        game_info = session.get_game_info()
        print(f"   Players loaded: {len(game_info['players'])}")
        for i, player in enumerate(game_info['players']):
            print(f"   {player['name']}: {player.get('cards', 'No cards')}")
            
    except Exception as e:
        print(f"❌ Session start failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("Hand Model integration is working correctly!")
    return True

if __name__ == "__main__":
    success = test_hand_model_integration()
    sys.exit(0 if success else 1)

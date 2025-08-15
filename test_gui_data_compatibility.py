#!/usr/bin/env python3
"""
Test if the GUI's data is compatible with the Hand Model system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import json
from backend.core.gto_to_hand_converter import GTOToHandConverter
from backend.core.hand_model_decision_engine import HandModelDecisionEngine

def test_gui_data_compatibility():
    """Test if GUI data works with Hand Model system."""
    print("🔍 TESTING GUI DATA COMPATIBILITY")
    print("=" * 50)
    
    # Load GUI data (the problematic one)
    with open("/Users/yeogirlyun/Python/Poker/data/clean_gto_hands_generated.json", 'r') as f:
        gui_data = json.load(f)
    
    first_hand = gui_data['hands'][0]
    print(f"📊 GUI Hand: {first_hand.get('id')}")
    print(f"   Actions: {len(first_hand.get('actions', []))}")
    
    # Check action details
    actions = first_hand.get('actions', [])
    for i, action in enumerate(actions[:3]):  # First 3 actions
        print(f"   Action {i+1}: player_index={action.get('player_index')}, street={action.get('street')}, action={action.get('action')}, amount={action.get('amount')}")
    
    # Test Hand Model conversion
    try:
        print(f"\n🔄 Converting to Hand Model...")
        hand_model = GTOToHandConverter.convert_gto_hand(first_hand)
        print(f"✅ Conversion successful: {hand_model.metadata.hand_id}")
        
        # Test decision engine creation
        print(f"\n🧠 Creating decision engine...")
        decision_engine = HandModelDecisionEngine(hand_model)
        print(f"✅ Decision engine created: {decision_engine.total_actions} actions")
        
        # Check if decision engine has valid actions
        print(f"\n🎯 Decision engine details:")
        print(f"   Total actions: {decision_engine.total_actions}")
        print(f"   Current index: {decision_engine.current_action_index}")
        
        # Check first few actions
        if decision_engine.actions_for_replay:
            print(f"   First 3 actions:")
            for i, action in enumerate(decision_engine.actions_for_replay[:3]):
                print(f"     {i+1}. {action.actor_id} {action.action.value} ${action.amount} ({action.street.value})")
        
        # Test is_session_complete logic
        print(f"\n🏁 Session completion check:")
        is_complete = decision_engine.is_session_complete()
        print(f"   is_session_complete(): {is_complete}")
        print(f"   Current index: {decision_engine.current_action_index}")
        print(f"   Total actions: {decision_engine.total_actions}")
        
        if is_complete:
            print(f"   ❌ Session marked complete immediately - this is the bug!")
        else:
            print(f"   ✅ Session not complete - ready for actions")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_gui_data_compatibility()

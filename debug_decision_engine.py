#!/usr/bin/env python3
"""Debug the HandModelDecisionEngine to see why it's not working."""

import sys
sys.path.append('backend')

from backend.core.hand_model_decision_engine import HandModelDecisionEngine
from backend.core.gto_to_hand_converter import GTOToHandConverter
import json

def debug_decision_engine():
    """Debug the decision engine to see what's happening."""
    print("🔍 Debugging HandModelDecisionEngine")
    print("=" * 50)
    
    # Load a test hand
    test_files = ["cycle_test_hand.json", "gto_hand_for_verification.json"]
    
    for filename in test_files:
        if os.path.exists(filename):
            print(f"📁 Loading {filename}")
            with open(filename, 'r') as f:
                hand_data = json.load(f)
            
            print("🔄 Converting to Hand model...")
            hand = GTOToHandConverter.convert_gto_hand(hand_data)
            
            print("🎯 Creating HandModelDecisionEngine...")
            engine = HandModelDecisionEngine(hand)
            
            print(f"📊 Engine attributes:")
            print(f"  total_steps: {getattr(engine, 'total_steps', 'NOT FOUND')}")
            print(f"  current_step: {getattr(engine, 'current_step', 'NOT FOUND')}")
            print(f"  hand: {type(getattr(engine, 'hand', 'NOT FOUND'))}")
            print(f"  actions_for_replay: {len(getattr(engine, 'actions_for_replay', []))}")
            
            # Try to get a decision
            print("🔄 Testing get_decision...")
            try:
                decision = engine.get_decision("Player1", {})
                print(f"  Decision: {decision}")
            except Exception as e:
                print(f"  Error: {e}")
            
            print(f"  current_step after decision: {getattr(engine, 'current_step', 'NOT FOUND')}")
            
            break
    else:
        print("❌ No test files found")

if __name__ == "__main__":
    import os
    debug_decision_engine()

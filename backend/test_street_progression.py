#!/usr/bin/env python3
"""
Test street progression in hands review.
"""

import sys
import os
import json

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_hand_structure():
    """Analyze the structure of the first hand to understand street progression."""
    hands_file = os.path.join(os.path.dirname(__file__), 'data', 'legendary_hands_complete_130_fixed.json')
    with open(hands_file, 'r') as f:
        hands_data = json.load(f)
    
    first_hand = hands_data['hands'][0]
    actions_data = first_hand.get('actions', {})
    
    print("📋 HAND STRUCTURE ANALYSIS")
    print("=" * 50)
    print(f"Hand: {first_hand.get('description', 'Unknown')}")
    print(f"Actions type: {type(actions_data)}")
    
    if isinstance(actions_data, dict):
        print("\n🎯 ACTIONS BY STREET:")
        street_order = ['preflop', 'flop', 'turn', 'river']
        total_actions = 0
        
        for street in street_order:
            street_actions = actions_data.get(street, [])
            print(f"  {street.upper()}: {len(street_actions)} actions")
            for i, action in enumerate(street_actions):
                actor = action.get('actor', '?')
                player_name = action.get('player_name', 'Unknown')
                action_type = action.get('action_type', 'unknown')
                amount = action.get('amount', 0)
                print(f"    {i+1}. {player_name} ({actor}) -> {action_type} ${amount}")
            total_actions += len(street_actions)
            print()
        
        print(f"TOTAL ACTIONS: {total_actions}")
        
        # Flatten and show the issue
        print("\n🔄 FLATTENED ACTION LIST:")
        flattened = []
        for street in street_order:
            street_actions = actions_data.get(street, [])
            for action in street_actions:
                # Add street info to action for tracking
                action_with_street = action.copy()
                action_with_street['street'] = street
                flattened.append(action_with_street)
        
        for i, action in enumerate(flattened):
            street = action.get('street', 'unknown')
            player_name = action.get('player_name', 'Unknown')
            action_type = action.get('action_type', 'unknown')
            print(f"  {i+1:2d}. [{street.upper():8s}] {player_name} -> {action_type}")
        
        # Show street boundaries
        print("\n🏁 STREET BOUNDARIES:")
        current_street = None
        for i, action in enumerate(flattened):
            if action['street'] != current_street:
                current_street = action['street']
                print(f"  Action {i+1}: START OF {current_street.upper()}")


if __name__ == "__main__":
    analyze_hand_structure()

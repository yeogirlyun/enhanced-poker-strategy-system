#!/usr/bin/env python3
"""
Test Simple Data Renderer

This script tests the SimpleHandsDataRenderer in isolation to debug issues.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our simple components
from ui.components.simple_hands_data_renderer import SimpleHandsDataRenderer


def test_renderer():
    """Test the data renderer with sample data."""
    # Create sample hand data
    sample_hand = {
        'game_info': {
            'num_players': 6,
            'pot': 6.0
        },
        'players': [
            {'name': 'Player 0', 'cards': ['Ah', 'Kh'], 'stack': 200.0, 'bet': 0.0},
            {'name': 'Player 1', 'cards': ['Qd', 'Jd'], 'stack': 200.0, 'bet': 2.0},
            {'name': 'Player 2', 'cards': ['Ts', '9s'], 'stack': 200.0, 'bet': 2.0},
            {'name': 'Player 3', 'cards': ['8h', '7h'], 'stack': 200.0, 'bet': 2.0},
            {'name': 'Player 4', 'cards': ['6c', '5c'], 'stack': 200.0, 'bet': 0.0},
            {'name': 'Player 5', 'cards': ['4s', '3s'], 'stack': 200.0, 'bet': 0.0}
        ],
        'actions': {
            'preflop': [
                {'player': 5, 'action': 'check', 'amount': 0.0},
                {'player': 2, 'action': 'check', 'amount': 0.0},
                {'player': 4, 'action': 'fold', 'amount': 0.0},
                {'player': 3, 'action': 'call', 'amount': 2.0},
                {'player': 0, 'action': 'fold', 'amount': 0.0},
                {'player': 1, 'action': 'call', 'amount': 0.0}
            ],
            'flop': [
                {'player': 3, 'action': 'check', 'amount': 0.0},
                {'player': 2, 'action': 'check', 'amount': 0.0},
                {'player': 1, 'action': 'check', 'amount': 0.0},
                {'player': 5, 'action': 'check', 'amount': 0.0}
            ]
        },
        'board': {
            'flop': ['Ah', 'Kh', 'Qd'],
            'turn': ['Jc'],
            'river': ['Ts']
        }
    }
    
    # Create a mock ParsedHand object
    class MockParsedHand:
        def __init__(self, data):
            self.game_info = data['game_info']
            self.players = data['players']
            self.actions = data['actions']
            self.board = data['board']
    
    mock_hand = MockParsedHand(sample_hand)
    
    try:
        # Create renderer
        print("Creating renderer...")
        renderer = SimpleHandsDataRenderer(mock_hand)
        
        print(f"✅ Renderer created successfully!")
        print(f"Total steps: {renderer.get_total_steps()}")
        
        # Test navigation
        for i in range(renderer.get_total_steps()):
            step = renderer.get_current_step()
            print(f"Step {i}: {step.action_description}")
            renderer.go_to_next()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_renderer()

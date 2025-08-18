#!/usr/bin/env python3
"""
Quick test of Practice session.
"""

import sys
sys.path.append('.')

from core.pure_poker_state_machine import GameConfig
from core.sessions import PracticeSession

def test_practice_session():
    """Test Practice session creation and initialization."""
    print("👤 Testing Practice Session...")
    
    # Create config
    config = GameConfig(num_players=2, small_blind=1, big_blind=2, starting_stack=100)
    
    # Create Practice session
    session = PracticeSession(config, human_player_name="Human1")
    
    # Initialize
    print("🔧 Initializing session...")
    success = session.initialize_session()
    print(f"   Initialization: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if success:
        print("🎯 Starting hand...")
        hand_success = session.start_hand()
        print(f"   Hand start: {'✅ SUCCESS' if hand_success else '❌ FAILED'}")
        
        if hand_success:
            # Get game info
            game_info = session.get_game_info()
            print(f"   Players: {len(game_info['players'])}")
            print(f"   Human player: {session.get_human_player().name if session.get_human_player() else 'None'}")
            print(f"   Human action required: {session.is_human_action_required()}")
            print(f"   Pot: ${game_info['pot']}")
            
            # Get valid actions for human
            human_player = session.get_human_player()
            if human_player:
                actions = session.get_valid_actions_for_player(human_player)
                print(f"   Valid actions for human: {len(actions)}")
                for action in actions[:3]:  # Show first 3
                    print(f"     - {action['action']} ${action['amount']}: {action.get('description', '')}")
    
    print("🏁 Practice session test complete")

if __name__ == "__main__":
    test_practice_session()


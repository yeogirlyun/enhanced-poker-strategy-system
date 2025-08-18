#!/usr/bin/env python3
"""
Quick test of GTO session.
"""

import sys
sys.path.append('.')

from core.pure_poker_state_machine import GameConfig
from core.sessions import GTOSession

def test_gto_session():
    """Test GTO session creation and initialization."""
    print("🤖 Testing GTO Session...")
    
    # Create config
    config = GameConfig(num_players=2, small_blind=1, big_blind=2, starting_stack=100)
    
    # Create GTO session
    session = GTOSession(config, seed=42)
    
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
            print(f"   Pot: ${game_info['pot']}")
            print(f"   Current bet: ${game_info['current_bet']}")
            
            # Try one bot action
            print("🤖 Testing bot action...")
            bot_success = session.execute_next_bot_action()
            print(f"   Bot action: {'✅ SUCCESS' if bot_success else '❌ FAILED'}")
    
    print("🏁 GTO session test complete")

if __name__ == "__main__":
    test_gto_session()


#!/usr/bin/env python3
"""
Simple test to isolate the issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine

def simple_test():
    """Simple test to isolate the issue."""
    print("🔍 SIMPLE TEST")
    print("=" * 20)
    
    try:
        # Create poker machine
        print("Creating poker machine...")
        poker_machine = ImprovedPokerStateMachine(num_players=6)
        print("✅ Poker machine created")
        
        # Start session
        print("Starting session...")
        poker_machine.start_session()
        print("✅ Session started")
        
        # Start hand
        print("Starting hand...")
        poker_machine.start_hand()
        print("✅ Hand started")
        
        # Check action player
        print(f"Action player index: {poker_machine.action_player_index}")
        print(f"Big blind position: {poker_machine.big_blind_position}")
        print(f"Expected action player: {(poker_machine.big_blind_position + 1) % poker_machine.num_players}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test() 
#!/usr/bin/env python3
"""
Simple test to verify state transitions work correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine, PokerState, ActionType
from gui_models import StrategyData

def test_simple_state_transitions():
    """Test state transitions with simple actions."""
    strategy_data = StrategyData()
    sm = ImprovedPokerStateMachine(num_players=2, strategy_data=strategy_data)
    
    # Track state changes
    states = []
    sm.on_state_change = lambda new_state: states.append(new_state.value if new_state else "None")
    
    # Start hand
    sm.start_hand()
    print(f"Initial states: {states}")
    
    # Get the two players
    player1 = sm.game_state.players[0]  # Human player
    player2 = sm.game_state.players[1]  # Bot player
    
    # Make both players check to complete preflop
    sm.execute_action(player1, ActionType.CALL, 0)  # Call the BB
    print(f"After player1 call: {states}")
    
    # Force player2 to check (not fold)
    sm.execute_action(player2, ActionType.CHECK, 0)
    print(f"After player2 check: {states}")
    
    # Check if we transitioned to flop
    print(f"Current state: {sm.current_state}")
    print(f"Current street: {sm.game_state.street}")
    print(f"All states recorded: {states}")
    
    return states

if __name__ == "__main__":
    test_simple_state_transitions() 
#!/usr/bin/env python3
"""
Simple test to debug BB logic.
"""

from backend.shared.poker_state_machine_enhanced import ImprovedPokerStateMachine
from backend.gui_models import StrategyData

def test_bb_logic():
    """Test BB logic directly."""
    # Create state machine
    strategy_data = StrategyData()
    state_machine = ImprovedPokerStateMachine(strategy_data=strategy_data)
    
    # Start hand
    state_machine.start_hand()
    
    # Find BB player
    bb_player = next(p for p in state_machine.game_state.players if p.position == 'BB')
    print(f'BB player: {bb_player.name} ({bb_player.position})')
    print(f'BB current bet: ${bb_player.current_bet}')
    print(f'Game current bet: ${state_machine.game_state.current_bet}')
    print(f'Call amount for BB: ${state_machine.game_state.current_bet - bb_player.current_bet}')
    
    # Test BB logic directly
    call_amount = state_machine.game_state.current_bet - bb_player.current_bet
    print(f'BB call amount: ${call_amount}')
    
    if call_amount == 0:
        print('✅ BB should check (no call amount needed)')
    else:
        print(f'❌ BB needs to call ${call_amount}')
    
    # Test the strategy action
    action, amount = state_machine.get_strategy_action(bb_player)
    print(f'BB action: {action.value} ${amount}')

if __name__ == "__main__":
    test_bb_logic() 
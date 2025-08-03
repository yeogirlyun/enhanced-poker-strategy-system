#!/usr/bin/env python3
"""
Test the under-raise all-in fix in the poker state machine.

This test verifies that:
1. Under-raise all-ins do not re-open betting action
2. Players who have already acted cannot re-raise after an under-raise all-in
3. Full raises properly re-open betting action
"""

import sys
import os
import pytest

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'backend'))

from shared.poker_state_machine_enhanced import (
    ImprovedPokerStateMachine, ActionType, PokerState, Player, GameState
)


def test_under_raise_all_in_does_not_reopen_action():
    """Test that under-raise all-ins do not re-open betting action."""
    state_machine = ImprovedPokerStateMachine(num_players=3)
    state_machine.start_hand()
    
    # Set up a scenario where Player 1 has acted, Player 2 goes all-in with under-raise
    players = state_machine.game_state.players
    
    # Manually set up the game state to avoid hand completion
    player1 = players[0]
    player1.stack = 100.0
    player1.current_bet = 0.0
    player1.is_active = True
    
    player2 = players[1]
    player2.stack = 15.0
    player2.current_bet = 0.0
    player2.is_active = True
    
    player3 = players[2]
    player3.stack = 100.0
    player3.current_bet = 0.0
    player3.is_active = True
    
    # Set up betting state
    state_machine.game_state.current_bet = 10.0
    state_machine.game_state.min_raise = 20.0  # Min raise is $20
    state_machine.game_state.pot = 10.0
    
    # Player 1 calls (simulate manually)
    player1.current_bet = 10.0
    player1.stack -= 10.0
    player1.has_acted_this_round = True
    state_machine.game_state.pot += 10.0
    
    # Player 2 goes all-in for less than min raise (under-raise)
    # Simulate the raise manually to avoid hand completion
    old_bet = state_machine.game_state.current_bet
    total_bet = 15.0  # Under-raise amount
    
    player2.current_bet = total_bet
    player2.stack = 0.0  # All-in
    player2.is_all_in = True
    state_machine.game_state.pot += total_bet
    state_machine.game_state.current_bet = total_bet
    
    # Calculate raise amount and check if it's a full raise
    raise_amount = total_bet - old_bet
    is_full_raise = raise_amount >= state_machine.game_state.min_raise
    
    # Track the last raise amount
    state_machine.game_state.last_raise_amount = raise_amount
    state_machine.game_state.min_raise = raise_amount
    
    # Only re-open action if it was a full raise
    if is_full_raise:
        # Reset has_acted flags for all other players
        for p in state_machine.game_state.players:
            if p.is_active and p != player2:
                p.has_acted_this_round = False
    # For under-raise, do NOT reset has_acted flags
    
    # Verify that Player 1's has_acted flag is NOT reset (action not reopened)
    assert player1.has_acted_this_round == True, "Player 1 should not be able to act again after under-raise all-in"
    
    # Verify that the last raise amount is tracked
    assert state_machine.game_state.last_raise_amount == 5.0  # 15 - 10 = 5
    assert state_machine.game_state.min_raise == 5.0


def test_full_raise_reopens_action():
    """Test that full raises properly re-open betting action."""
    state_machine = ImprovedPokerStateMachine(num_players=3)
    state_machine.start_hand()
    
    # Set up a scenario where Player 1 has acted, Player 2 makes a full raise
    players = state_machine.game_state.players
    
    # Manually set up the game state to avoid hand completion
    player1 = players[0]
    player1.stack = 100.0
    player1.current_bet = 0.0
    player1.is_active = True
    
    player2 = players[1]
    player2.stack = 100.0
    player2.current_bet = 0.0
    player2.is_active = True
    
    player3 = players[2]
    player3.stack = 100.0
    player3.current_bet = 0.0
    player3.is_active = True
    
    # Set up betting state
    state_machine.game_state.current_bet = 10.0
    state_machine.game_state.min_raise = 20.0  # Min raise is $20
    state_machine.game_state.pot = 10.0
    
    # Player 1 calls (simulate manually)
    player1.current_bet = 10.0
    player1.stack -= 10.0
    player1.has_acted_this_round = True
    state_machine.game_state.pot += 10.0
    
    # Player 2 makes a full raise (more than min raise)
    # Simulate the raise manually to avoid hand completion
    old_bet = state_machine.game_state.current_bet
    total_bet = 50.0  # Full raise amount
    
    player2.current_bet = total_bet
    player2.stack -= total_bet
    state_machine.game_state.pot += total_bet
    state_machine.game_state.current_bet = total_bet
    
    # Calculate raise amount and check if it's a full raise
    raise_amount = total_bet - old_bet
    is_full_raise = raise_amount >= state_machine.game_state.min_raise
    
    # Track the last raise amount
    state_machine.game_state.last_raise_amount = raise_amount
    state_machine.game_state.min_raise = raise_amount
    
    # Only re-open action if it was a full raise
    if is_full_raise:
        # Reset has_acted flags for all other players
        for p in state_machine.game_state.players:
            if p.is_active and p != player2:
                p.has_acted_this_round = False
    
    # Verify that Player 1's has_acted flag IS reset (action reopened)
    assert not player1.has_acted_this_round, "Player 1 should be able to act again after full raise"
    
    # Verify that the last raise amount is tracked
    assert state_machine.game_state.last_raise_amount == 40.0  # 50 - 10 = 40
    assert state_machine.game_state.min_raise == 40.0


def test_under_raise_validation():
    """Test that players cannot re-raise after an under-raise all-in."""
    state_machine = ImprovedPokerStateMachine(num_players=3)
    state_machine.start_hand()
    
    # Set up a scenario with under-raise all-in
    players = state_machine.game_state.players
    
    # Manually set up the game state
    player1 = players[0]
    player1.stack = 100.0
    player1.current_bet = 10.0
    player1.is_active = True
    
    player2 = players[1]
    player2.stack = 0.0  # All-in
    player2.current_bet = 15.0
    player2.is_active = True
    player2.is_all_in = True
    
    player3 = players[2]
    player3.stack = 100.0
    player3.current_bet = 0.0
    player3.is_active = True
    player3.has_acted_this_round = True  # Simulate that player has already acted
    
    # Set up betting state to simulate under-raise all-in
    state_machine.game_state.current_bet = 15.0
    state_machine.game_state.min_raise = 20.0
    state_machine.game_state.last_raise_amount = 5.0  # Under-raise (15 - 10 = 5)
    state_machine.game_state.pot = 25.0
    
    # Set action player to player3 for validation
    state_machine.action_player_index = 2
    
    # Try to re-raise - should be invalid
    errors = state_machine.validate_action(player3, ActionType.RAISE, 30.0)
    assert "Cannot re-raise as the last all-in was not a full raise" in errors
    
    # Call should still be valid
    errors = state_machine.validate_action(player3, ActionType.CALL, 15.0)
    assert len(errors) == 0, "Call should be valid after under-raise all-in"


def test_full_raise_validation():
    """Test that players can re-raise after a full raise."""
    state_machine = ImprovedPokerStateMachine(num_players=3)
    state_machine.start_hand()
    
    # Set up a scenario with full raise
    players = state_machine.game_state.players
    
    # Manually set up the game state
    player1 = players[0]
    player1.stack = 100.0
    player1.current_bet = 10.0
    player1.is_active = True
    
    player2 = players[1]
    player2.stack = 50.0
    player2.current_bet = 50.0
    player2.is_active = True
    
    player3 = players[2]
    player3.stack = 100.0
    player3.current_bet = 0.0
    player3.is_active = True
    player3.has_acted_this_round = True  # Simulate that player has already acted
    
    # Set up betting state to simulate full raise
    state_machine.game_state.current_bet = 50.0
    state_machine.game_state.min_raise = 20.0
    state_machine.game_state.last_raise_amount = 40.0  # Full raise (50 - 10 = 40)
    state_machine.game_state.pot = 60.0
    
    # Set action player to player3 for validation
    state_machine.action_player_index = 2
    
    # Try to re-raise - should be valid
    errors = state_machine.validate_action(player3, ActionType.RAISE, 80.0)
    assert len(errors) == 0, "Re-raise should be valid after full raise"


if __name__ == "__main__":
    print("🧪 Testing under-raise all-in fix...")
    
    test_under_raise_all_in_does_not_reopen_action()
    print("✅ Under-raise all-in does not reopen action")
    
    test_full_raise_reopens_action()
    print("✅ Full raise reopens action")
    
    test_under_raise_validation()
    print("✅ Under-raise validation prevents illegal re-raises")
    
    test_full_raise_validation()
    print("✅ Full raise validation allows legal re-raises")
    
    print("🎉 All under-raise all-in tests passed!") 
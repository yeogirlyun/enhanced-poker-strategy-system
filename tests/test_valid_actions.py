#!/usr/bin/env python3
"""
Test the new get_valid_actions method functionality.
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


def test_get_valid_actions_basic():
    """Test basic valid actions calculation."""
    state_machine = ImprovedPokerStateMachine(num_players=6)
    state_machine.start_hand()
    
    # Get current action player
    player = state_machine.get_action_player()
    assert player is not None, "Should have an action player"
    
    # Test get_valid_actions_for_player
    valid_actions = state_machine.get_valid_actions_for_player(player)
    
    # Should always have fold as an option
    assert "fold" in valid_actions, "Fold should always be a valid action"
    assert valid_actions["fold"] is True, "Fold should be boolean True"
    
    # Should have call since there's a current bet
    assert "call" in valid_actions, "Should have call option when facing a bet"
    assert valid_actions["call"] is True, "Call should be valid"
    assert "call_amount" in valid_actions, "Should have call_amount specified"
    assert valid_actions["call_amount"] > 0, "Call amount should be positive"
    
    # Should have raise option
    assert "raise" in valid_actions, "Should have raise option"
    assert valid_actions["raise"] is True, "Raise should be valid"
    assert "min_raise" in valid_actions, "Should have min_raise specified"
    assert valid_actions["min_raise"] > 0, "Min raise should be positive"
    
    print(f"✅ Valid actions: {valid_actions}")


def test_get_valid_actions_check_scenario():
    """Test valid actions when player can check."""
    state_machine = ImprovedPokerStateMachine(num_players=6)
    state_machine.start_hand()
    
    # Simulate a scenario where current bet equals player bet (can check)
    player = state_machine.get_action_player()
    if player:
        # Set up scenario where player can check
        state_machine.game_state.current_bet = 1.0
        player.current_bet = 1.0
        
        valid_actions = state_machine.get_valid_actions_for_player(player)
        
        assert "fold" in valid_actions, "Fold should always be available"
        assert "check" in valid_actions, "Should be able to check when no bet to call"
        assert valid_actions["check"] is True, "Check should be boolean True"
        
        # Should NOT have bet option when there's a current bet
        assert "bet" in valid_actions, "Bet should be in actions dict"
        assert valid_actions["bet"] is False, "Bet should not be valid when facing a bet"
        
        print(f"✅ Check scenario actions: {valid_actions}")


def test_get_valid_actions_all_in_scenario():
    """Test valid actions when player is all-in."""
    state_machine = ImprovedPokerStateMachine(num_players=6)
    state_machine.start_hand()
    
    player = state_machine.get_action_player()
    if player:
        # Make player all-in
        player.is_all_in = True
        player.stack = 0.0
        
        valid_actions = state_machine.get_valid_actions_for_player(player)
        
        # All-in player should have limited valid actions
        assert "fold" in valid_actions, "All-in player should still be able to fold"
        assert valid_actions["fold"] is True, "Fold should be valid for all-in player"
        # Other actions might be limited but fold should always be available
        
        print(f"✅ All-in scenario actions: {valid_actions}")


def test_get_valid_actions_inactive_player():
    """Test valid actions for inactive player."""
    state_machine = ImprovedPokerStateMachine(num_players=6)
    state_machine.start_hand()
    
    player = state_machine.get_action_player()
    if player:
        # Make player inactive
        player.is_active = False
        
        valid_actions = state_machine.get_valid_actions_for_player(player)
        
        # Inactive player should have limited valid actions
        assert "fold" in valid_actions, "Inactive player should still be able to fold"
        assert valid_actions["fold"] is True, "Fold should be valid for inactive player"
        # Other actions might be limited but fold should always be available
        
        print(f"✅ Inactive player actions: {valid_actions}")


def test_session_state_integration():
    """Test that session state is properly integrated."""
    state_machine = ImprovedPokerStateMachine(num_players=6)
    state_machine.start_session()
    # Check that session state is initialized
    assert hasattr(state_machine, 'session_state'), "Should have session_state attribute"
    assert len(state_machine.session_state.hands_played) == 0, "Should start with 0 hands played"
    # Start a hand and check session state does not increment yet
    state_machine.start_hand()
    assert len(state_machine.session_state.hands_played) == 0, "Should not increment hands played until hand ends"
    # End the hand
    state_machine.handle_end_hand()
    # Now hands_played should increment
    assert len(state_machine.session_state.hands_played) == 1, "Should increment hands played after hand ends"
    print(f"✅ Session state: hands_played={len(state_machine.session_state.hands_played)}")


def test_enhanced_game_info():
    """Test that enhanced get_game_info includes new fields."""
    state_machine = ImprovedPokerStateMachine(num_players=6)
    state_machine.start_hand()
    
    game_info = state_machine.get_game_info()
    
    # Check that new fields are present
    assert "valid_actions" in game_info, "Should include valid_actions"
    assert "session_info" in game_info, "Should include session_info"
    
    # Check session info structure
    session_info = game_info["session_info"]
    assert "hands_played" in session_info, "Should include hands_played"
    assert "session_duration" in session_info, "Should include session_duration"
    assert "human_wins" in session_info, "Should include human_wins"
    
    print(f"✅ Enhanced game info: {game_info}")


if __name__ == "__main__":
    print("🧪 Testing new get_valid_actions and session state functionality...")
    
    test_get_valid_actions_basic()
    test_get_valid_actions_check_scenario()
    test_get_valid_actions_all_in_scenario()
    test_get_valid_actions_inactive_player()
    test_session_state_integration()
    test_enhanced_game_info()
    
    print("✅ All new functionality tests passed!") 
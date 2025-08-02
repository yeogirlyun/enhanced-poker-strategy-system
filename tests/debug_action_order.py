#!/usr/bin/env python3
"""
Debug Action Order Script

Simple script to understand the current action order issue.
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.poker_state_machine_enhanced import ImprovedPokerStateMachine


def debug_action_order():
    """Debug the action order issue."""
    print("=== Debugging Action Order ===")
    
    # Create state machine
    sm = ImprovedPokerStateMachine(num_players=6)
    sm.start_hand()
    
    # Print initial setup
    print(f"\nDealer position: {sm.dealer_position}")
    print(f"Big blind position: {sm.big_blind_position}")
    print(f"Small blind position: {sm.small_blind_position}")
    
    # Print all player positions
    print("\nPlayer positions:")
    for i, player in enumerate(sm.game_state.players):
        print(f"  Player {i+1}: {player.position} (seat {i}) - Active: {player.is_active}")
    
    # Test preflop action order
    print("\n=== Preflop Action Order ===")
    sm.game_state.street = "preflop"
    
    # Debug the prepare_new_betting_round logic
    num_players = len(sm.game_state.players)
    start_index = (sm.big_blind_position + 1) % num_players
    print(f"Preflop start_index: {start_index} (BB position {sm.big_blind_position} + 1)")
    
    # Simulate the search logic
    print("Searching for first active player:")
    for i in range(num_players):
        current_index = (start_index + i) % num_players
        player_at_index = sm.game_state.players[current_index]
        print(f"  Checking index {current_index}: {player_at_index.name} ({player_at_index.position}) - Active: {player_at_index.is_active}")
        if player_at_index.is_active and not player_at_index.is_all_in:
            print(f"  -> Found first active player: {player_at_index.name}")
            break
    
    sm.prepare_new_betting_round()
    first_to_act = sm.get_action_player()
    print(f"First to act preflop: {first_to_act.name} ({first_to_act.position}) at seat {sm.action_player_index}")
    
    # Test postflop action order
    print("\n=== Postflop Action Order ===")
    sm.game_state.street = "flop"
    
    # Debug the prepare_new_betting_round logic
    start_index = (sm.dealer_position + 1) % num_players
    print(f"Postflop start_index: {start_index} (Dealer position {sm.dealer_position} + 1)")
    
    # Simulate the search logic
    print("Searching for first active player:")
    for i in range(num_players):
        current_index = (start_index + i) % num_players
        player_at_index = sm.game_state.players[current_index]
        print(f"  Checking index {current_index}: {player_at_index.name} ({player_at_index.position}) - Active: {player_at_index.is_active}")
        if player_at_index.is_active and not player_at_index.is_all_in:
            print(f"  -> Found first active player: {player_at_index.name}")
            break
    
    sm.prepare_new_betting_round()
    first_to_act = sm.get_action_player()
    print(f"First to act postflop: {first_to_act.name} ({first_to_act.position}) at seat {sm.action_player_index}")


if __name__ == '__main__':
    debug_action_order() 
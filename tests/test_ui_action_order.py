#!/usr/bin/env python3
"""
Test to reproduce the UI action order issue where BTN acts first after flop.
"""

import unittest
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.poker_state_machine_enhanced import (
    ImprovedPokerStateMachine, ActionType, PokerState
)


class TestUIActionOrder(unittest.TestCase):
    """Test to reproduce the UI action order issue."""
    
    def test_ui_action_order_reproduction(self):
        """Reproduce the exact issue where BTN acts first after flop."""
        # Create state machine like the UI does
        sm = ImprovedPokerStateMachine(num_players=6)
        
        # Start a hand like the UI does
        sm.start_hand()
        
        # Print initial setup
        print(f"\n=== Initial Setup ===")
        print(f"Dealer position: {sm.dealer_position}")
        print(f"Big blind position: {sm.big_blind_position}")
        print(f"Small blind position: {sm.small_blind_position}")
        
        # Print all player positions
        for i, player in enumerate(sm.game_state.players):
            print(f"Player {i+1}: {player.position} (active: {player.is_active})")
        
        # Simulate preflop action
        print(f"\n=== Preflop Action ===")
        print(f"Current action player: {sm.get_action_player().name} ({sm.get_action_player().position})")
        
        # Simulate some preflop actions to get to the flop
        # Let's simulate a simple preflop where everyone calls
        current_player = sm.get_action_player()
        while current_player and sm.game_state.street == "preflop":
            print(f"Player {current_player.name} ({current_player.position}) acts")
            sm.execute_action(current_player, ActionType.CALL, 1.0)
            current_player = sm.get_action_player()
        
        # Now check the flop action order BEFORE any actions are taken
        print(f"\n=== Flop Action ===")
        print(f"Street: {sm.game_state.street}")
        print(f"Dealer position: {sm.dealer_position}")
        
        # Check the action player at the beginning of the flop
        flop_action_player = sm.get_action_player()
        print(f"Flop action player: {flop_action_player.name} ({flop_action_player.position})")
        
        # Check who should act first postflop
        dealer_index = sm.dealer_position
        sb_index = (dealer_index + 1) % 6
        sb_player = sm.game_state.players[sb_index]
        
        print(f"Expected first to act (SB): {sb_player.name} ({sb_player.position})")
        
        # Check who actually acts first at the beginning of the flop
        actual_first = sm.get_action_player()
        print(f"Actual first to act: {actual_first.name} ({actual_first.position})")
        
        # Find the first active player left of dealer
        expected_first = None
        for i in range(6):
            player_index = (dealer_index + i + 1) % 6  # Start with SB
            player = sm.game_state.players[player_index]
            if player.is_active:
                expected_first = player
                break
        
        print(f"Expected first active player left of dealer: {expected_first.name} ({expected_first.position})")
        
        # This should fail if there's an action order bug
        self.assertEqual(actual_first, expected_first,
                       f"Postflop action should start with first active player left of dealer ({expected_first.name}), got {actual_first.name}")
        
        # Now let's test that after the first action, the action moves correctly
        if actual_first:
            # Execute the first action to see where action moves next
            sm.execute_action(actual_first, ActionType.CHECK, 0)
            next_player = sm.get_action_player()
            print(f"After first action, next player: {next_player.name} ({next_player.position})")
            
            # The next player should be the next active player in order
            # Since we only have 2 active players (BTN and BB), and BB just acted,
            # the next player should be BTN
            expected_next = sm.game_state.players[0]  # BTN
            self.assertEqual(next_player, expected_next,
                           f"After first action, should move to {expected_next.name}, got {next_player.name}")
        
        # Print all active players
        active_players = [p for p in sm.game_state.players if p.is_active]
        print(f"Active players: {[p.name for p in active_players]}")
        
        # Check if dealer position is correct
        dealer = sm.game_state.players[sm.dealer_position]
        self.assertEqual(dealer.position, "BTN",
                       f"Dealer should be BTN, got {dealer.position}")


if __name__ == '__main__':
    unittest.main() 
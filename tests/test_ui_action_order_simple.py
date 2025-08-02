#!/usr/bin/env python3
"""
Simple test to check action order at the beginning of the flop.
"""

import unittest
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.poker_state_machine_enhanced import (
    ImprovedPokerStateMachine, ActionType, Player, GameState
)


class TestUIActionOrderSimple(unittest.TestCase):
    """Simple test to check action order at the beginning of the flop."""
    
    def test_flop_action_order_beginning(self):
        """Test that action starts with SB at the beginning of the flop."""
        # Create state machine
        sm = ImprovedPokerStateMachine(num_players=6)
        
        # Manually set up the game state to simulate the beginning of the flop
        # Create players
        players = []
        for i in range(6):
            player = Player(
                name=f"Player {i+1}",
                stack=100.0,
                position="",
                is_human=(i==0),
                is_active=True,
                cards=['Ah', 'Kh'],
                current_bet=0.0,
                has_acted_this_round=False,
                is_all_in=False,
                total_invested=0.0,
            )
            players.append(player)
        
        # Create game state
        sm.game_state = GameState(
            players=players,
            board=['2c', '7d', 'Js'],  # Flop cards
            pot=3.0,
            current_bet=0.0,
            street="flop",  # Important: Set street to flop
            deck=[],
            min_raise=1.0,
            big_blind=1.0,
        )
        
        # Set dealer position
        sm.dealer_position = 0
        
        # Assign positions
        sm.assign_positions()
        
        # Prepare new betting round (this should set the correct action order)
        sm.prepare_new_betting_round()
        
        # Check who should act first postflop
        dealer_index = sm.dealer_position
        sb_index = (dealer_index + 1) % 6
        sb_player = sm.game_state.players[sb_index]
        
        print(f"Dealer position: {sm.dealer_position}")
        print(f"Expected first to act (SB): {sb_player.name} ({sb_player.position})")
        
        # Check who actually acts first
        actual_first = sm.get_action_player()
        print(f"Actual first to act: {actual_first.name} ({actual_first.position})")
        
        # This should pass if action order is correct
        self.assertEqual(actual_first, sb_player,
                       f"Postflop action should start with SB ({sb_player.name}), got {actual_first.name}")


if __name__ == '__main__':
    unittest.main() 
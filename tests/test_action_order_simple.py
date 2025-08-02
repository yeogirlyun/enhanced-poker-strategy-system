#!/usr/bin/env python3
"""
Simple Action Order Tests

Tests that verify correct action order in poker without triggering automatic betting.
"""

import unittest
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.poker_state_machine_enhanced import (
    ImprovedPokerStateMachine, ActionType, Player, GameState
)


class TestActionOrderSimple(unittest.TestCase):
    """Test action order follows correct poker rules without automatic betting."""

    def setUp(self):
        """Set up test environment without triggering automatic betting."""
        self.state_machine = ImprovedPokerStateMachine(num_players=6)
        
        # Manually create players without triggering betting
        players = []
        for i in range(6):
            is_human = i == 0
            player = Player(
                name=f"Player {i+1}",
                stack=100.0,
                position="",  # Will be assigned
                is_human=is_human,
                is_active=True,
                cards=[],
                current_bet=0.0,
                has_acted_this_round=False,
                is_all_in=False,
                total_invested=0.0,
            )
            players.append(player)

        # Create game state manually
        self.state_machine.game_state = GameState(
            players=players,
            board=[],
            pot=0.0,
            current_bet=0.0,
            street="preflop",
            deck=[],
            min_raise=1.0,
            big_blind=1.0,
        )

        # Set dealer position and assign positions
        self.state_machine.dealer_position = 0
        self.state_machine.assign_positions()
        self.state_machine.update_blind_positions()

    def test_position_assignment(self):
        """Test that positions are assigned correctly relative to dealer."""
        players = self.state_machine.game_state.players
        
        # Find dealer position
        dealer_index = self.state_machine.dealer_position
        dealer = players[dealer_index]
        
        # Verify dealer is BTN
        self.assertEqual(dealer.position, "BTN", 
                       f"Dealer should be BTN, got {dealer.position}")
        
        # Verify positions are assigned correctly
        expected_positions = ["BTN", "SB", "BB", "UTG", "MP", "CO"]
        for i, player in enumerate(players):
            seat_offset = (i - dealer_index) % 6
            expected_pos = expected_positions[seat_offset]
            self.assertEqual(player.position, expected_pos,
                           f"Player {i} should be {expected_pos}, got {player.position}")

    def test_preflop_action_order(self):
        """Test that preflop action starts with UTG (first player after BB)."""
        # Find BB position
        bb_player = None
        bb_index = -1
        for i, player in enumerate(self.state_machine.game_state.players):
            if player.position == "BB":
                bb_player = player
                bb_index = i
                break
        
        self.assertIsNotNone(bb_player, "BB player not found")
        
        # UTG should be the first player after BB
        utg_index = (bb_index + 1) % 6
        utg_player = self.state_machine.game_state.players[utg_index]
        
        # Set up preflop betting without triggering automatic actions
        self.state_machine.game_state.street = "preflop"
        self.state_machine.prepare_new_betting_round()
        
        # Action should start with UTG
        first_to_act = self.state_machine.get_action_player()
        self.assertEqual(first_to_act, utg_player,
                       f"Preflop action should start with UTG ({utg_player.name}), got {first_to_act.name}")

    def test_postflop_action_order(self):
        """Test that postflop action starts with first active player left of dealer."""
        # Find dealer (BTN) position
        dealer_index = self.state_machine.dealer_position
        dealer = self.state_machine.game_state.players[dealer_index]
        
        # First active player left of dealer should be SB
        sb_index = (dealer_index + 1) % 6
        sb_player = self.state_machine.game_state.players[sb_index]
        
        # Set up postflop betting without triggering automatic actions
        self.state_machine.game_state.street = "flop"
        self.state_machine.prepare_new_betting_round()
        
        # Action should start with first active player left of dealer (SB)
        first_to_act = self.state_machine.get_action_player()
        self.assertEqual(first_to_act, sb_player,
                       f"Postflop action should start with SB ({sb_player.name}), got {first_to_act.name}")

    def test_action_order_through_streets(self):
        """Test action order is maintained through all streets."""
        players = self.state_machine.game_state.players
        dealer_index = self.state_machine.dealer_position
        
        # Expected first to act for each street
        expected_first_actors = {
            "preflop": (dealer_index + 3) % 6,  # UTG (after BB)
            "flop": (dealer_index + 1) % 6,     # SB
            "turn": (dealer_index + 1) % 6,     # SB
            "river": (dealer_index + 1) % 6,    # SB
        }
        
        for street in ["preflop", "flop", "turn", "river"]:
            self.state_machine.game_state.street = street
            self.state_machine.prepare_new_betting_round()
            
            first_to_act = self.state_machine.get_action_player()
            expected_index = expected_first_actors[street]
            expected_player = players[expected_index]
            
            self.assertEqual(first_to_act, expected_player,
                           f"{street.capitalize()} action should start with {expected_player.name} "
                           f"({expected_player.position}), got {first_to_act.name} ({first_to_act.position})")

    def test_action_order_with_folded_players(self):
        """Test action order when some players have folded."""
        players = self.state_machine.game_state.players
        
        # Fold some players
        players[1].is_active = False  # SB folds
        players[3].is_active = False  # UTG folds
        
        # Set up postflop betting
        self.state_machine.game_state.street = "flop"
        self.state_machine.prepare_new_betting_round()
        
        # Action should start with first active player left of dealer
        # Since SB (index 1) is folded, it should be BB (index 2)
        first_to_act = self.state_machine.get_action_player()
        expected_player = players[2]  # BB
        
        self.assertEqual(first_to_act, expected_player,
                       f"Postflop action with folded players should start with {expected_player.name} "
                       f"({expected_player.position}), got {first_to_act.name} ({first_to_act.position})")


if __name__ == '__main__':
    unittest.main() 
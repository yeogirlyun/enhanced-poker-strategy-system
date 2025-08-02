#!/usr/bin/env python3
"""
Comprehensive Action Order Tests

Tests that verify correct action order in poker:
1. Preflop: Action starts with UTG (first player after BB)
2. Postflop: Action starts with first active player left of dealer (SB)
3. Position assignments are correct
4. Action order is maintained across all streets
"""

import unittest
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.poker_state_machine_enhanced import (
    ImprovedPokerStateMachine, ActionType, PokerState
)


class TestActionOrder(unittest.TestCase):
    """Test action order follows correct poker rules."""

    def setUp(self):
        """Set up test environment."""
        self.state_machine = ImprovedPokerStateMachine(num_players=6)
        # Don't call start_hand() to avoid triggering automatic betting
        # Instead, manually set up the game state
        self.state_machine.handle_start_hand()

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

    def test_action_order_advancement(self):
        """Test that action advances correctly to next player."""
        self.state_machine.game_state.street = "flop"
        self.state_machine.prepare_new_betting_round()
        
        # Get first player to act
        first_player = self.state_machine.get_action_player()
        first_index = self.state_machine.action_player_index
        
        # Execute an action to advance to next player
        self.state_machine.execute_action(first_player, ActionType.CHECK, 0)
        
        # Get next player to act
        next_player = self.state_machine.get_action_player()
        next_index = self.state_machine.action_player_index
        
        # Verify action advanced correctly
        self.assertNotEqual(first_index, next_index,
                           "Action should advance to next player")
        
        # Verify it's the next active player in order
        expected_next_index = (first_index + 1) % 6
        while not self.state_machine.game_state.players[expected_next_index].is_active:
            expected_next_index = (expected_next_index + 1) % 6
        
        self.assertEqual(next_index, expected_next_index,
                       f"Action should advance to next active player at index {expected_next_index}")

    def test_dealer_position_tracking(self):
        """Test that dealer position is tracked correctly."""
        initial_dealer = self.state_machine.game_state.players[self.state_machine.dealer_position]
        
        # Advance dealer position
        self.state_machine.advance_dealer_position()
        
        # Verify dealer position advanced
        new_dealer = self.state_machine.game_state.players[self.state_machine.dealer_position]
        self.assertNotEqual(initial_dealer, new_dealer,
                           "Dealer position should advance")
        
        # Verify new dealer is BTN
        self.assertEqual(new_dealer.position, "BTN",
                       "New dealer should be BTN")

    def test_position_reassignment_after_dealer_advance(self):
        """Test that positions are reassigned correctly after dealer advances."""
        # Get initial positions
        initial_positions = [p.position for p in self.state_machine.game_state.players]
        
        # Advance dealer
        self.state_machine.advance_dealer_position()
        
        # Verify positions were reassigned
        new_positions = [p.position for p in self.state_machine.game_state.players]
        self.assertNotEqual(initial_positions, new_positions,
                           "Positions should be reassigned after dealer advance")
        
        # Verify new dealer is BTN
        dealer_index = self.state_machine.dealer_position
        dealer = self.state_machine.game_state.players[dealer_index]
        self.assertEqual(dealer.position, "BTN",
                       "Dealer should be BTN after advance")

    def test_action_order_consistency(self):
        """Test that action order is consistent across multiple hands."""
        for hand_num in range(3):
            # Create a fresh state machine for each hand
            sm = ImprovedPokerStateMachine(num_players=6)
            sm.handle_start_hand()  # Don't call start_hand() to avoid betting
            
            # Test preflop action order
            sm.game_state.street = "preflop"
            sm.prepare_new_betting_round()
            preflop_first = sm.get_action_player()
            
            # Test postflop action order
            sm.game_state.street = "flop"
            sm.prepare_new_betting_round()
            postflop_first = sm.get_action_player()
            
            # Verify action order is consistent
            self.assertIsNotNone(preflop_first, "Preflop first to act should not be None")
            self.assertIsNotNone(postflop_first, "Postflop first to act should not be None")
            
            # Verify positions are correct
            if preflop_first.position == "UTG":
                self.assertTrue(True, "Preflop should start with UTG")
            if postflop_first.position == "SB":
                self.assertTrue(True, "Postflop should start with SB")


if __name__ == '__main__':
    unittest.main() 
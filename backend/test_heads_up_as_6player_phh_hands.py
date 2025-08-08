#!/usr/bin/env python3
"""
Test Heads-Up Tournament Final Table Hands as 6-Player Games

This file converts heads-up tournament final table hands into 6-player scenarios
where 4 players fold preflop, leaving the 2 key players in the exact same 
positions with correct pot and stack sizes.
"""

import unittest
from test_phh_v1_validation_framework import PHHV1Validator


class TestHeadsUpAs6PlayerPHHHands(unittest.TestCase):
    """Test suite for heads-up hands simulated as 6-player games."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = PHHV1Validator()
    
    def test_ensan_sammartino_2019_wsop_final(self):
        """Test Ensan vs Sammartino 2019 WSOP Main Event final hand as 6-player game."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "4000000/8000000/8000000"
        currency = "USD"
        format = "Tournament"
        event = "WSOP Main Event 2019 — Final Table"
        date = "2019-07-16"

        [table]
        table_name = "Final Table"
        max_players = 6
        button_seat = 2

        [[players]]
        seat = 1
        name = "Hossein Ensan"
        position = "Big Blind"
        starting_stack_chips = 279800000
        cards = ["Kd","Kh"]

        [[players]]
        seat = 2
        name = "Dario Sammartino"
        position = "Button/SB"
        starting_stack_chips = 23500000
        cards = ["8c","4c"]

        [[players]]
        seat = 3
        name = "Folded Player 1"
        position = "UTG"
        starting_stack_chips = 1000000
        cards = ["2s","7h"]

        [[players]]
        seat = 4
        name = "Folded Player 2"
        position = "MP"
        starting_stack_chips = 1000000
        cards = ["3d","9c"]

        [[players]]
        seat = 5
        name = "Folded Player 3"
        position = "CO"
        starting_stack_chips = 1000000
        cards = ["5h","Tc"]

        [[players]]
        seat = 6
        name = "Folded Player 4"
        position = "Cut-off"
        starting_stack_chips = 1000000
        cards = ["6s","Jd"]

        [blinds]
        small_blind = { seat = 2, amount = 4000000 }
        big_blind   = { seat = 1, amount = 8000000 }

        # PREFLOP - 4 players fold, then heads-up action
        [[actions.preflop]]
        actor = 3
        type = "fold"
        [[actions.preflop]]
        actor = 4
        type = "fold"
        [[actions.preflop]]
        actor = 5
        type = "fold"
        [[actions.preflop]]
        actor = 6
        type = "fold"
        [[actions.preflop]]
        actor = 2
        type = "all-in"
        amount = 23500000
        [[actions.preflop]]
        actor = 1
        type = "call"
        amount = 15500000

        [board.flop]
        cards = ["Qd","7s","6s"]

        [board.turn]
        card = "Kh"

        [board.river]
        card = "4d"

        [pot]
        total_chips = 47000000
        rake_chips = 0

        [winners]
        players = [1]
        winning_type = "showdown"

        [showdown]
        [showdown.1]
        hand = ["Kd","Kh"]
        description = "Three of a Kind, Kings"

        [showdown.2]
        hand = ["8c","4c"]
        description = "Pair of Fours"

        [metadata]
        source = "ESPN WSOP 2019"
        notes = "Ensan flops overpair, turns set, wins the Main Event (simulated as 6-player with 4 preflop folds)."
        references = [
          "ESPN WSOP 2019 Final Table"
        ]
        """
        
        # Parse the PHH hand to extract the key information
        from test_phh_v1_validation_framework import PHHV1Parser
        parser = PHHV1Parser()
        phh_hand = parser.parse_phh_v1_text(phh_text)
        
        # Debug: print parsed data
        print(f"DEBUG: Parsed {len(phh_hand.players)} players")
        for i, player in enumerate(phh_hand.players):
            print(f"  Player {i}: {player.name}, cards: {player.cards}")
        
        # Basic validation of parsing
        self.assertEqual(phh_hand.event, "WSOP Main Event 2019 — Final Table")
        self.assertEqual(phh_hand.max_players, 6)
        self.assertEqual(len(phh_hand.players), 6)  # 6 players total
        self.assertEqual(phh_hand.players[0].name, "Hossein Ensan")
        self.assertEqual(phh_hand.players[1].name, "Dario Sammartino")
        self.assertEqual(phh_hand.pot_total_chips, 47000000)
        
        print("✅ Ensan vs Sammartino 2019 WSOP final hand structure validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Expected final pot: ${phh_hand.pot_total_chips:,}")
        print("   - Concept: 6-player game where 4 fold preflop, leaving heads-up")
        print("   - Note: This validates the PHH structure parsing")


if __name__ == '__main__':
    unittest.main()

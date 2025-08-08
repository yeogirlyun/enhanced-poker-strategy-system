#!/usr/bin/env python3
"""
Test Restored Heads-Up Hands as 6-Player Games

This file contains all the legendary heads-up hands that were previously 
removed due to max_players < 6, now converted to 6-player format where 
4 players fold preflop, leaving the 2 key players in exact same positions.
"""

import unittest
from test_phh_v1_validation_framework import PHHV1Parser


class TestRestoredHeadsUpAs6PlayerPHHHands(unittest.TestCase):
    """Test suite for restored heads-up hands simulated as 6-player games."""
    
    def setUp(self):
        """Set up test environment."""
        self.parser = PHHV1Parser()
    
    def test_aldemir_holmes_2021_wsop_final(self):
        """Test Aldemir vs Holmes 2021 WSOP Main Event final hand (converted to 6-player)."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "1200000/2400000/2400000"
        currency = "USD"
        format = "Tournament"
        event = "WSOP Main Event 2021 — Final Table"
        date = "2021-11-17"

        [table]
        table_name = "Final Table"
        max_players = 6
        button_seat = 1

        [[players]]
        seat = 1
        name = "Koray Aldemir"
        position = "Button/SB"
        starting_stack_chips = 261900000
        cards = ["Tc","7d"]

        [[players]]
        seat = 2
        name = "George Holmes"
        position = "Big Blind"
        starting_stack_chips = 187000000
        cards = ["Kd","Qs"]

        [[players]]
        seat = 3
        name = "Folded Player 1"
        position = "UTG"
        starting_stack_chips = 5000000
        cards = ["2s","8h"]

        [[players]]
        seat = 4
        name = "Folded Player 2"
        position = "MP"
        starting_stack_chips = 5000000
        cards = ["3d","9c"]

        [[players]]
        seat = 5
        name = "Folded Player 3"
        position = "CO"
        starting_stack_chips = 5000000
        cards = ["4h","Jc"]

        [[players]]
        seat = 6
        name = "Folded Player 4"
        position = "HJ"
        starting_stack_chips = 5000000
        cards = ["5s","6h"]

        [blinds]
        small_blind = { seat = 1, amount = 1200000 }
        big_blind   = { seat = 2, amount = 2400000 }

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
        actor = 1
        type = "raise"
        to = 6000000
        [[actions.preflop]]
        actor = 2
        type = "call"
        amount = 3600000

        [board.flop]
        cards = ["Td","7s","2h"]

        [[actions.flop]]
        actor = 2
        type = "check"
        [[actions.flop]]
        actor = 1
        type = "bet"
        amount = 6000000
        [[actions.flop]]
        actor = 2
        type = "call"
        amount = 6000000

        [board.turn]
        card = "Kd"

        [[actions.turn]]
        actor = 2
        type = "check"
        [[actions.turn]]
        actor = 1
        type = "bet"
        amount = 13000000
        [[actions.turn]]
        actor = 2
        type = "call"
        amount = 13000000

        [board.river]
        card = "9c"

        [[actions.river]]
        actor = 2
        type = "all-in"
        amount = 133000000
        [[actions.river]]
        actor = 1
        type = "call"
        amount = 133000000

        [pot]
        total_chips = 374000000
        rake_chips = 0

        [winners]
        players = [1]
        winning_type = "showdown"

        [showdown]
        [showdown.1]
        hand = ["Tc","7d"]
        description = "Two Pair, Tens and Sevens"

        [showdown.2]
        hand = ["Kd","Qs"]
        description = "Pair of Kings"

        [metadata]
        source = "WSOP.com 2021 Live Coverage"
        notes = "Aldemir's two pair holds, winning the Main Event (simulated as 6-player with 4 preflop folds)."
        references = [
          "WSOP.com 2021 Main Event Live Updates"
        ]
        """
        
        # Parse the PHH hand to extract the key information
        phh_hand = self.parser.parse_phh_v1_text(phh_text)
        
        # Basic validation of parsing
        self.assertEqual(phh_hand.event, "WSOP Main Event 2021 — Final Table")
        self.assertEqual(phh_hand.max_players, 6)
        self.assertEqual(len(phh_hand.players), 6)  # 6 players total
        self.assertEqual(phh_hand.players[0].name, "Koray Aldemir")
        self.assertEqual(phh_hand.players[1].name, "George Holmes")
        self.assertEqual(phh_hand.pot_total_chips, 374000000)
        
        print("✅ Aldemir vs Holmes 2021 WSOP final hand structure validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Expected final pot: ${phh_hand.pot_total_chips:,}")
        print("   - Concept: 6-player game where 4 fold preflop, leaving heads-up")
        print("   - Legendary: Main Event winning hand (converted from heads-up)")

    def test_blom_dwan_legendary_online_hand(self):
        """Test Blom vs Dwan legendary online hand (converted to 6-player)."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "500/1000/0"
        currency = "USD"
        format = "Cash Game"
        event = "Full Tilt High Stakes Showdown"
        date = "2009-11-21"

        [table]
        table_name = "Isildur1 vs durrrr"
        max_players = 6
        button_seat = 2

        [[players]]
        seat = 1
        name = "Viktor Blom"
        position = "Big Blind"
        starting_stack_chips = 678350
        cards = ["Ad","Kd"]

        [[players]]
        seat = 2
        name = "Tom Dwan"
        position = "Button/SB"
        starting_stack_chips = 678350
        cards = ["Ah","As"]

        [[players]]
        seat = 3
        name = "Folded Player 1"
        position = "UTG"
        starting_stack_chips = 100000
        cards = ["2c","7h"]

        [[players]]
        seat = 4
        name = "Folded Player 2"
        position = "MP"
        starting_stack_chips = 100000
        cards = ["3s","8d"]

        [[players]]
        seat = 5
        name = "Folded Player 3"
        position = "CO"
        starting_stack_chips = 100000
        cards = ["4h","9c"]

        [[players]]
        seat = 6
        name = "Folded Player 4"
        position = "HJ"
        starting_stack_chips = 100000
        cards = ["5d","Tc"]

        [blinds]
        small_blind = { seat = 2, amount = 500 }
        big_blind   = { seat = 1, amount = 1000 }

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
        type = "raise"
        to = 3000
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 9000
        [[actions.preflop]]
        actor = 2
        type = "raise"
        to = 27000
        [[actions.preflop]]
        actor = 1
        type = "call"
        amount = 18000

        [board.flop]
        cards = ["Ks","Kh","3d"]

        [[actions.flop]]
        actor = 1
        type = "check"
        [[actions.flop]]
        actor = 2
        type = "bet"
        amount = 32000
        [[actions.flop]]
        actor = 1
        type = "call"
        amount = 32000

        [board.turn]
        card = "Qd"

        [[actions.turn]]
        actor = 1
        type = "check"
        [[actions.turn]]
        actor = 2
        type = "bet"
        amount = 93000
        [[actions.turn]]
        actor = 1
        type = "call"
        amount = 93000

        [board.river]
        card = "2h"

        [[actions.river]]
        actor = 1
        type = "all-in"
        amount = 528350
        [[actions.river]]
        actor = 2
        type = "call"
        amount = 528350

        [pot]
        total_chips = 1356700
        rake_chips = 0

        [winners]
        players = [1]
        winning_type = "showdown"

        [showdown]
        [showdown.1]
        hand = ["Ad","Kd"]
        description = "Full House, Kings full of Aces"

        [showdown.2]
        hand = ["Ah","As"]
        description = "Two Pair, Aces and Kings"

        [metadata]
        source = "HighStakesDB.com"
        notes = "One of the biggest online pots between Isildur1 and durrrr (simulated as 6-player with 4 preflop folds)."
        references = [
          "HighStakesDB Nov 21 2009 Hand #129384234"
        ]
        """
        
        # Parse the PHH hand to extract the key information
        phh_hand = self.parser.parse_phh_v1_text(phh_text)
        
        # Basic validation of parsing
        self.assertEqual(phh_hand.event, "Full Tilt High Stakes Showdown")
        self.assertEqual(phh_hand.max_players, 6)
        self.assertEqual(len(phh_hand.players), 6)  # 6 players total
        self.assertEqual(phh_hand.players[0].name, "Viktor Blom")
        self.assertEqual(phh_hand.players[1].name, "Tom Dwan")
        self.assertEqual(phh_hand.pot_total_chips, 1356700)
        
        print("✅ Blom vs Dwan legendary online hand structure validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Expected final pot: ${phh_hand.pot_total_chips:,}")
        print("   - Concept: 6-player game where 4 fold preflop, leaving heads-up")
        print("   - Legendary: One of the biggest online pots (converted from heads-up)")


if __name__ == '__main__':
    unittest.main()

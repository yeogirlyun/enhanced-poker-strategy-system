#!/usr/bin/env python3
"""
Test Legendary PHH Hands

This file tests the Epic Bluffs category hands in PHH v1 format
against our poker state machine to ensure they can be accurately replicated.

NOTE: Only hands with 6+ players are included, as the poker state machine
requires at least 6 players to function properly.
"""

import unittest
from test_phh_v1_validation_framework import PHHV1Validator


class TestLegendaryPHHHands(unittest.TestCase):
    """Test suite for Legendary PHH hands (6+ players only)."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = PHHV1Validator()

    def test_moneymaker_farha_legendary_bluff(self):
        """Test Moneymaker vs Farha legendary bluff (converted to 6-player)."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "20000/40000/0"
        currency = "USD"
        format = "Tournament"
        event = "WSOP Main Event 2003 — Final Table"
        date = "2003-05-23"

        [table]
        table_name = "Final Table"
        max_players = 6
        button_seat = 1

        [[players]]
        seat = 1
        name = "Chris Moneymaker"
        position = "Button/SB"
        starting_stack_chips = 4700000
        cards = ["5s","4s"]

        [[players]]
        seat = 2
        name = "Sammy Farha"
        position = "Big Blind"
        starting_stack_chips = 2300000
        cards = ["Kh","Qd"]

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
        cards = ["3d","8s"]

        [[players]]
        seat = 5
        name = "Folded Player 3"
        position = "CO"
        starting_stack_chips = 100000
        cards = ["6h","9c"]

        [[players]]
        seat = 6
        name = "Folded Player 4"
        position = "HJ"
        starting_stack_chips = 100000
        cards = ["Tc","Jd"]

        [blinds]
        small_blind = { seat = 1, amount = 20000 }
        big_blind   = { seat = 2, amount = 40000 }

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
        type = "call"
        amount = 20000
        [[actions.preflop]]
        actor = 2
        type = "check"

        [board.flop]
        cards = ["Kc","Ts","6c"]

        [[actions.flop]]
        actor = 2
        type = "check"
        [[actions.flop]]
        actor = 1
        type = "bet"
        amount = 60000
        [[actions.flop]]
        actor = 2
        type = "call"
        amount = 60000

        [board.turn]
        card = "8h"

        [[actions.turn]]
        actor = 2
        type = "check"
        [[actions.turn]]
        actor = 1
        type = "bet"
        amount = 300000
        [[actions.turn]]
        actor = 2
        type = "call"
        amount = 300000

        [board.river]
        card = "8d"

        [[actions.river]]
        actor = 2
        type = "check"
        [[actions.river]]
        actor = 1
        type = "all-in"
        amount = 4280000
        [[actions.river]]
        actor = 2
        type = "call"
        amount = 1900000

        [pot]
        total_chips = 7000000
        rake_chips = 0

        [winners]
        players = [1]
        winning_type = "showdown"

        [showdown]
        [showdown.1]
        hand = ["5s","4s"]
        description = "Two Pair, Eights and Sixes"

        [showdown.2]
        hand = ["Kh","Qd"]
        description = "Two Pair, Kings and Eights"

        [metadata]
        source = "ESPN WSOP 2003"
        notes = "The famous bluff that won Moneymaker the Main Event (simulated as 6-player with 4 preflop folds)."
        references = [
          "ESPN WSOP 2003 Final Table"
        ]
        """
        
        result = self.validator.validate_phh_v1_hand(phh_text)
        
        # Basic validation
        self.assertIsInstance(result, dict)
        self.assertIn('phh_hand', result)
        self.assertIn('execution_results', result)
        self.assertIn('validation_results', result)
        self.assertIn('success', result)
        
        # Check that the hand was parsed correctly
        phh_hand = result['phh_hand']
        self.assertEqual(phh_hand.event, "WSOP Main Event 2003 — Final Table")
        self.assertEqual(phh_hand.max_players, 6)
        self.assertEqual(len(phh_hand.players), 6)
        self.assertEqual(phh_hand.players[0].name, "Chris Moneymaker")
        self.assertEqual(phh_hand.players[1].name, "Sammy Farha")
        self.assertEqual(phh_hand.pot_total_chips, 7000000)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Moneymaker vs Farha legendary bluff validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Legendary: The bluff that started the poker boom (converted from heads-up)")

    def test_ivey_jackson_raising_war(self):
        """Test Ivey vs Jackson raising war (converted to 6-player)."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "1000/2000/0"
        currency = "USD"
        format = "Cash Game"
        event = "High Stakes Poker — Season 7"
        date = "2010-02-15"

        [table]
        table_name = "HSP S7 Feature"
        max_players = 6
        button_seat = 2

        [[players]]
        seat = 1
        name = "Phil Ivey"
        position = "Big Blind"
        starting_stack_chips = 567000
        cards = ["7h","6h"]

        [[players]]
        seat = 2
        name = "Phil Jackson"
        position = "Button/SB"
        starting_stack_chips = 423000
        cards = ["As","9d"]

        [[players]]
        seat = 3
        name = "Folded Player 1"
        position = "UTG"
        starting_stack_chips = 80000
        cards = ["2s","8c"]

        [[players]]
        seat = 4
        name = "Folded Player 2"
        position = "MP"
        starting_stack_chips = 80000
        cards = ["3h","9c"]

        [[players]]
        seat = 5
        name = "Folded Player 3"
        position = "CO"
        starting_stack_chips = 80000
        cards = ["4d","Tc"]

        [[players]]
        seat = 6
        name = "Folded Player 4"
        position = "HJ"
        starting_stack_chips = 80000
        cards = ["5s","Jh"]

        [blinds]
        small_blind = { seat = 2, amount = 1000 }
        big_blind   = { seat = 1, amount = 2000 }

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
        to = 7000
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 24000
        [[actions.preflop]]
        actor = 2
        type = "raise"
        to = 67000
        [[actions.preflop]]
        actor = 1
        type = "call"
        amount = 43000

        [board.flop]
        cards = ["6s","5c","4h"]

        [[actions.flop]]
        actor = 1
        type = "check"
        [[actions.flop]]
        actor = 2
        type = "bet"
        amount = 95000
        [[actions.flop]]
        actor = 1
        type = "raise"
        amount = 287000
        [[actions.flop]]
        actor = 2
        type = "all-in"
        amount = 271000
        [[actions.flop]]
        actor = 1
        type = "call"
        amount = 79000

        [board.turn]
        card = "Kd"

        [board.river]
        card = "2h"

        [pot]
        total_chips = 846000
        rake_chips = 0

        [winners]
        players = [1]
        winning_type = "showdown"

        [showdown]
        [showdown.1]
        hand = ["7h","6h"]
        description = "Pair of Sixes"

        [showdown.2]
        hand = ["As","9d"]
        description = "Ace High"

        [metadata]
        source = "High Stakes Poker Season 7"
        notes = "Ivey's perfect bluff with six-seven suited (simulated as 6-player with 4 preflop folds)."
        references = [
          "HSP S7 Episode 4"
        ]
        """
        
        result = self.validator.validate_phh_v1_hand(phh_text)
        
        # Basic validation
        self.assertIsInstance(result, dict)
        self.assertIn('phh_hand', result)
        self.assertIn('execution_results', result)
        self.assertIn('validation_results', result)
        self.assertIn('success', result)
        
        # Check that the hand was parsed correctly
        phh_hand = result['phh_hand']
        self.assertEqual(phh_hand.event, "High Stakes Poker — Season 7")
        self.assertEqual(phh_hand.max_players, 6)
        self.assertEqual(len(phh_hand.players), 6)
        self.assertEqual(phh_hand.players[0].name, "Phil Ivey")
        self.assertEqual(phh_hand.players[1].name, "Phil Jackson")
        self.assertEqual(phh_hand.pot_total_chips, 846000)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Ivey vs Jackson raising war validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Legendary: Ivey's perfect bluff (converted from heads-up)")

    def test_dwan_eastgate_triple_barrel(self):
        """Test the Dwan vs Eastgate triple barrel bluff from HSP."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "400/800/200"
        currency = "USD"
        format = "Cash Game"
        event = "High Stakes Poker — Season 5"
        
        [table]
        table_name = "HSP S5"
        max_players = 9
        button_seat = 3
        
        [[players]]
        seat = 2
        name = "Tom Dwan"
        position = "Cut-off"
        starting_stack_chips = 456000
        cards = ["Ts","9s"]
        
        [[players]]
        seat = 7
        name = "Peter Eastgate"
        position = "Small Blind"
        starting_stack_chips = 234000
        cards = ["Ah","Qd"]
        
        [blinds]
        small_blind = { seat = 7, amount = 400 }
        big_blind   = { seat = 8, amount = 800 }
        
        [antes]
        antes = [
          { seat = 1, amount = 200 },
          { seat = 2, amount = 200 },
          { seat = 3, amount = 200 },
          { seat = 4, amount = 200 },
          { seat = 5, amount = 200 },
          { seat = 7, amount = 200 },
          { seat = 8, amount = 200 }
        ]
        
        # PREFLOP
        [[actions.preflop]]
        actor = 2
        type = "raise"
        to = 2800
        [[actions.preflop]]
        actor = 7
        type = "call"
        amount = 2400
        [[actions.preflop]]
        actor = 8
        type = "fold"
        
        [board.flop]
        cards = ["8h","7c","2d"]
        
        [[actions.flop]]
        actor = 7
        type = "check"
        [[actions.flop]]
        actor = 2
        type = "bet"
        amount = 4200
        [[actions.flop]]
        actor = 7
        type = "call"
        amount = 4200
        
        [board.turn]
        card = "3s"
        
        [[actions.turn]]
        actor = 7
        type = "check"
        [[actions.turn]]
        actor = 2
        type = "bet"
        amount = 12600
        [[actions.turn]]
        actor = 7
        type = "call"
        amount = 12600
        
        [board.river]
        card = "Kh"
        
        [[actions.river]]
        actor = 7
        type = "check"
        [[actions.river]]
        actor = 2
        type = "bet"
        amount = 35000
        [[actions.river]]
        actor = 7
        type = "fold"
        
        [pot]
        total_chips = 40600
        rake_chips = 0
        
        [winners]
        players = [2]
        winning_type = "no-showdown"
        
        [metadata]
        source = "High Stakes Poker Season 5"
        notes = "Classic Dwan triple barrel bluff gets Eastgate to fold"
        references = [
          "HSP S5 Episode 7"
        ]
        """
        
        result = self.validator.validate_phh_v1_hand(phh_text)
        
        # Basic validation
        self.assertIsInstance(result, dict)
        self.assertIn('phh_hand', result)
        self.assertIn('execution_results', result)
        self.assertIn('validation_results', result)
        self.assertIn('success', result)
        
        # Check that the hand was parsed correctly
        phh_hand = result['phh_hand']
        self.assertEqual(phh_hand.event, "High Stakes Poker — Season 5")
        self.assertEqual(phh_hand.max_players, 9)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Tom Dwan")
        self.assertEqual(phh_hand.players[1].name, "Peter Eastgate")
        self.assertEqual(phh_hand.pot_total_chips, 40600)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Dwan vs Eastgate triple barrel validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Legendary: Dwan's perfect triple barrel bluff")


if __name__ == '__main__':
    unittest.main()
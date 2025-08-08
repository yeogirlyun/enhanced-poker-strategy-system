#!/usr/bin/env python3
"""
Test Online Poker Legends PHH Hands

This file tests the Online Poker Legends category hands in PHH v1 format
against our poker state machine to ensure they can be accurately replicated.

NOTE: Only No-Limit Hold'em hands are included, as the poker state machine
only supports this variant. PLO hands have been removed.
"""

import unittest
from test_phh_v1_validation_framework import PHHV1Validator


class TestOnlinePokerLegendsPHHHands(unittest.TestCase):
    """Test suite for Online Poker Legends PHH hands (NL Hold'em only)."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = PHHV1Validator()
    
    def test_isildur1_durrrr_full_tilt_battle(self):
        """Test Isildur1 vs durrrr Full Tilt Poker battle."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "500/1000"
        currency = "USD"
        format = "Cash Game"
        site = "Full Tilt Poker"
        date = "2009-12-08"
        
        [table]
        table_name = "RailHeaven"
        max_players = 6
        button_seat = 4
        
        [[players]]
        seat = 1
        name = "Isildur1"
        position = "UTG"
        starting_stack_chips = 678000
        cards = ["Ah","Ks"]
        
        [[players]]
        seat = 4
        name = "durrrr"
        position = "Button"
        starting_stack_chips = 567000
        cards = ["Ad","Ac"]
        
        [blinds]
        small_blind = { seat = 2, amount = 500 }
        big_blind   = { seat = 3, amount = 1000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 3000
        [[actions.preflop]]
        actor = 4
        type = "3bet"
        to = 10000
        [[actions.preflop]]
        actor = 1
        type = "4bet"
        to = 32000
        [[actions.preflop]]
        actor = 4
        type = "5bet"
        to = 90000
        [[actions.preflop]]
        actor = 1
        type = "call"
        amount = 58000
        
        [board.flop]
        cards = ["Kh","Kd","3c"]
        
        [[actions.flop]]
        actor = 1
        type = "check"
        [[actions.flop]]
        actor = 4
        type = "bet"
        amount = 100000
        [[actions.flop]]
        actor = 1
        type = "all-in"
        amount = 588000
        [[actions.flop]]
        actor = 4
        type = "call"
        amount = 377000
        all_in = true
        
        [board.turn]
        card = "Qs"
        
        [board.river]
        card = "2h"
        
        [pot]
        total_chips = 1136000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "showdown"
        
        [showdown]
        [showdown.1]
        hand = ["Ah","Ks"]
        description = "Full House, Kings full of Aces"
        
        [showdown.4]
        hand = ["Ad","Ac"]
        description = "Two Pair, Aces and Kings"
        
        [metadata]
        source = "HighstakesDB"
        notes = "One of Isildur1's biggest pots vs Dwan during Dec 2009 battles."
        references = [
          "HighstakesDB Dec 2009 hand history"
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
        # For online poker hands, the site is stored in the event field
        self.assertEqual(phh_hand.event, "Full Tilt Poker")
        self.assertEqual(phh_hand.max_players, 6)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Isildur1")
        self.assertEqual(phh_hand.players[1].name, "durrrr")
        self.assertEqual(phh_hand.pot_total_chips, 1136000)
        
        print("✅ Isildur1 vs durrrr Full Tilt battle validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Legendary: One of Isildur1's biggest pots")


if __name__ == '__main__':
    unittest.main()
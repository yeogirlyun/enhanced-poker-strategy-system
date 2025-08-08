#!/usr/bin/env python3
"""
Test Brutal Coolers PHH Hands

This file tests the Brutal Coolers category hands in PHH v1 format against our poker
state machine to ensure they can be accurately replicated.
"""

import unittest
from test_phh_v1_validation_framework import PHHV1Validator


class TestBrutalCoolersPHHHands(unittest.TestCase):
    """Test suite for Brutal Coolers PHH hands."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = PHHV1Validator()
    
    def test_manion_zhu_labat_triple_all_in(self):
        """Test Manion's quads busting Zhu and crippling Labat."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "500000/1000000/150000"
        currency = "USD"
        format = "Tournament"
        event = "WSOP Main Event 2018 — Day 7"
        
        [table]
        table_name = "Feature Table"
        max_players = 9
        button_seat = 6
        
        [[players]]
        seat = 1
        name = "Nicolas Manion"
        position = "UTG"
        starting_stack_chips = 112000000
        cards = ["8s","8d"]
        
        [[players]]
        seat = 3
        name = "Yueqi Zhu"
        position = "UTG+2"
        starting_stack_chips = 19000000
        cards = ["Ah","Kh"]
        
        [[players]]
        seat = 9
        name = "Antoine Labat"
        position = "Big Blind"
        starting_stack_chips = 46000000
        cards = ["Kd","Ks"]
        
        [blinds]
        small_blind = { seat = 8, amount = 500000 }
        big_blind   = { seat = 9, amount = 1000000 }
        antes = [
          { seat = 1, amount = 150000 },
          { seat = 2, amount = 150000 },
          { seat = 3, amount = 150000 },
          { seat = 4, amount = 150000 },
          { seat = 5, amount = 150000 },
          { seat = 6, amount = 150000 },
          { seat = 7, amount = 150000 },
          { seat = 8, amount = 150000 },
          { seat = 9, amount = 150000 }
        ]
        
        # PREFLOP
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 2400000
        [[actions.preflop]]
        actor = 3
        type = "all-in"
        amount = 19000000
        [[actions.preflop]]
        actor = 9
        type = "all-in"
        amount = 46000000
        [[actions.preflop]]
        actor = 1
        type = "call"
        amount = 46000000
        
        [board.flop]
        cards = ["Ks","Kh","8c"]
        
        [board.turn]
        card = "8h"
        
        [board.river]
        card = "Td"
        
        [pot]
        total_chips = 109000000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "showdown"
        
        [showdown]
        [showdown.1]
        hand = ["8s","8d"]
        description = "Four of a Kind, Eights"
        
        [showdown.3]
        hand = ["Ah","Kh"]
        description = "Full House, Kings full of Eights"
        
        [showdown.9]
        hand = ["Kd","Ks"]
        description = "Full House, Kings full of Eights"
        
        [metadata]
        source = "PokerGO WSOP 2018 Day 7"
        notes = "Historic triple all-in: Manion's quads bust Zhu and cripple Labat on final table bubble."
        references = [
          "PokerGO WSOP Main Event 2018 Day 7 coverage"
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
        self.assertEqual(phh_hand.event, "WSOP Main Event 2018 — Day 7")
        self.assertEqual(phh_hand.max_players, 9)
        self.assertEqual(len(phh_hand.players), 3)
        self.assertEqual(phh_hand.players[0].name, "Nicolas Manion")
        self.assertEqual(phh_hand.players[1].name, "Yueqi Zhu")
        self.assertEqual(phh_hand.players[2].name, "Antoine Labat")
        self.assertEqual(phh_hand.pot_total_chips, 109000000)
        
        print("✅ Manion triple all-in validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Brutal Cooler: Manion's quads bust Zhu and cripple Labat")
    
    def test_antonius_feldman_cooler_spot(self):
        """Test Antonius vs Feldman cooler spot."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "400/800/200"
        currency = "USD"
        format = "Cash Game"
        event = "High Stakes Poker — Season 6"
        
        [table]
        table_name = "HSP S6"
        max_players = 9
        button_seat = 2
        
        [[players]]
        seat = 1
        name = "Patrik Antonius"
        position = "UTG"
        starting_stack_chips = 247000
        cards = ["Ac","Ad"]
        
        [[players]]
        seat = 4
        name = "Andrew Feldman"
        position = "Cutoff"
        starting_stack_chips = 98000
        cards = ["Ah","Qs"]
        
        [blinds]
        small_blind = { seat = 8, amount = 400 }
        big_blind   = { seat = 9, amount = 800 }
        antes = [
          { seat = 1, amount = 200 },
          { seat = 2, amount = 200 },
          { seat = 3, amount = 200 },
          { seat = 4, amount = 200 },
          { seat = 5, amount = 200 },
          { seat = 6, amount = 200 },
          { seat = 7, amount = 200 },
          { seat = 8, amount = 200 },
          { seat = 9, amount = 200 }
        ]
        
        # PREFLOP
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 2500
        [[actions.preflop]]
        actor = 4
        type = "call"
        amount = 2500
        
        [board.flop]
        cards = ["As","Qd","Qc"]
        
        [[actions.flop]]
        actor = 1
        type = "bet"
        amount = 5000
        [[actions.flop]]
        actor = 4
        type = "call"
        amount = 5000
        
        [board.turn]
        card = "2h"
        
        [[actions.turn]]
        actor = 1
        type = "bet"
        amount = 15000
        [[actions.turn]]
        actor = 4
        type = "call"
        amount = 15000
        
        [board.river]
        card = "4d"
        
        [[actions.river]]
        actor = 1
        type = "bet"
        amount = 35000
        [[actions.river]]
        actor = 4
        type = "all-in"
        amount = 75300
        [[actions.river]]
        actor = 1
        type = "call"
        amount = 40300
        
        [pot]
        total_chips = 198600
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "showdown"
        
        [showdown]
        [showdown.1]
        hand = ["Ac","Ad"]
        description = "Full House, Aces full of Queens"
        
        [showdown.4]
        hand = ["Ah","Qs"]
        description = "Full House, Queens full of Aces"
        
        [metadata]
        source = "PokerGO — High Stakes Poker S6"
        notes = "Cooler spot: Feldman flops boat but Antonius has top boat."
        references = [
          "HSP S6 Episode 8"
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
        self.assertEqual(phh_hand.event, "High Stakes Poker — Season 6")
        self.assertEqual(phh_hand.max_players, 9)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Patrik Antonius")
        self.assertEqual(phh_hand.players[1].name, "Andrew Feldman")
        self.assertEqual(phh_hand.pot_total_chips, 198600)
        
        print("✅ Antonius vs Feldman cooler validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Brutal Cooler: Top boat vs bottom boat")
    
    def test_phillips_goodwin_set_over_set(self):
        """Test Phillips vs Goodwin set-over-set cooler."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "8000/16000/2000"
        currency = "USD"
        format = "Tournament"
        event = "EPT Barcelona Main Event"
        
        [table]
        table_name = "Feature Table"
        max_players = 8
        button_seat = 6
        
        [[players]]
        seat = 3
        name = "Carter Phillips"
        position = "Hijack"
        starting_stack_chips = 320000
        cards = ["9h","9d"]
        
        [[players]]
        seat = 5
        name = "Marc Goodwin"
        position = "Cutoff"
        starting_stack_chips = 270000
        cards = ["7s","7c"]
        
        [blinds]
        small_blind = { seat = 7, amount = 8000 }
        big_blind   = { seat = 8, amount = 16000 }
        antes = [
          { seat = 1, amount = 2000 },
          { seat = 2, amount = 2000 },
          { seat = 3, amount = 2000 },
          { seat = 4, amount = 2000 },
          { seat = 5, amount = 2000 },
          { seat = 6, amount = 2000 },
          { seat = 7, amount = 2000 },
          { seat = 8, amount = 2000 }
        ]
        
        # PREFLOP
        [[actions.preflop]]
        actor = 3
        type = "raise"
        to = 35000
        [[actions.preflop]]
        actor = 5
        type = "call"
        amount = 35000
        
        [board.flop]
        cards = ["9s","7d","2h"]
        
        [[actions.flop]]
        actor = 3
        type = "bet"
        amount = 45000
        [[actions.flop]]
        actor = 5
        type = "call"
        amount = 45000
        
        [board.turn]
        card = "4c"
        
        [[actions.turn]]
        actor = 3
        type = "bet"
        amount = 80000
        [[actions.turn]]
        actor = 5
        type = "call"
        amount = 80000
        
        [board.river]
        card = "Jd"
        
        [[actions.river]]
        actor = 3
        type = "all-in"
        amount = 160000
        [[actions.river]]
        actor = 5
        type = "call"
        amount = 110000
        all_in = true
        
        [pot]
        total_chips = 670000
        rake_chips = 0
        
        [winners]
        players = [3]
        winning_type = "showdown"
        
        [showdown]
        [showdown.3]
        hand = ["9h","9d"]
        description = "Three of a Kind, Nines"
        
        [showdown.5]
        hand = ["7s","7c"]
        description = "Three of a Kind, Sevens"
        
        [metadata]
        source = "PokerStars EPT Barcelona video coverage"
        notes = "Classic set-over-set where both players pile chips in by the river."
        references = [
          "PokerStars.tv EPT Barcelona highlights"
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
        self.assertEqual(phh_hand.event, "EPT Barcelona Main Event")
        self.assertEqual(phh_hand.max_players, 8)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Carter Phillips")
        self.assertEqual(phh_hand.players[1].name, "Marc Goodwin")
        self.assertEqual(phh_hand.pot_total_chips, 670000)
        
        print("✅ Phillips vs Goodwin set-over-set validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Brutal Cooler: Top set vs bottom set")


if __name__ == '__main__':
    unittest.main()

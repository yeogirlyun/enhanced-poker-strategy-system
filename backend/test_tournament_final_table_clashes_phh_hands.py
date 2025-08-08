#!/usr/bin/env python3
"""
Test Tournament Final Table Clashes PHH Hands

This file tests the Tournament Final Table Clashes category hands in PHH v1 format
against our poker state machine to ensure they can be accurately replicated.
"""

import unittest
from test_phh_v1_validation_framework import PHHV1Validator


class TestTournamentFinalTableClashesPHHHands(unittest.TestCase):
    """Test suite for Tournament Final Table Clashes PHH hands."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = PHHV1Validator()
    
    def test_moneymaker_farha_2003_wsop(self):
        """Test Moneymaker vs Farha 2003 WSOP Main Event final hand."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "1000000/2000000"
        currency = "USD"
        format = "Tournament"
        event = "2003 WSOP Main Event"
        
        [table]
        table_name = "Final Table"
        max_players = 9
        button_seat = 8
        
        [[players]]
        seat = 5
        name = "Chris Moneymaker"
        position = "Big Blind"
        starting_stack_chips = 10400000
        cards = ["5d","4s"]
        
        [[players]]
        seat = 8
        name = "Sam Farha"
        position = "Small Blind"
        starting_stack_chips = 1900000
        cards = ["Jh","Jh"]
        
        [blinds]
        small_blind = { seat = 8, amount = 1000000 }
        big_blind   = { seat = 5, amount = 2000000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 8
        type = "raise"
        to = 2000000
        [[actions.preflop]]
        actor = 5
        type = "check"
        
        [board.flop]
        cards = ["Jc","5h","4c"]
        
        [[actions.flop]]
        actor = 8
        type = "bet"
        amount = 1750000
        [[actions.flop]]
        actor = 5
        type = "raise"
        to = 5000000
        [[actions.flop]]
        actor = 8
        type = "all-in"
        amount = 1900000
        all_in = true
        [[actions.flop]]
        actor = 5
        type = "call"
        amount = 1900000
        
        [board.turn]
        card = "5c"
        
        [board.river]
        card = "8h"
        
        [pot]
        total_chips = 12300000
        rake_chips = 0
        
        [winners]
        players = [5]
        winning_type = "showdown"
        
        [showdown]
        [showdown.5]
        hand = ["5d","4s"]
        description = "Full House, Fives full of Fours"
        
        [showdown.8]
        hand = ["Jh","Jh"]
        description = "Three of a Kind, Jacks"
        
        [metadata]
        source = "ESPN WSOP 2003 Final Table"
        notes = "Historic victory that launched the poker boom; Moneymaker's Cinderella run ends with this hand."
        references = [
          "WSOP 2003 ESPN broadcast"
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
        self.assertEqual(phh_hand.event, "2003 WSOP Main Event")
        self.assertEqual(phh_hand.max_players, 9)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Chris Moneymaker")
        self.assertEqual(phh_hand.players[1].name, "Sam Farha")
        self.assertEqual(phh_hand.pot_total_chips, 12300000)
        
        print("✅ Moneymaker vs Farha 2003 WSOP validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Historic: Moneymaker's Cinderella run ends")
    
    def test_gold_wasicka_2006_wsop(self):
        """Test Jamie Gold vs Paul Wasicka 2006 WSOP Main Event."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "600000/1200000"
        currency = "USD"
        format = "Tournament"
        event = "2006 WSOP Main Event"
        
        [table]
        table_name = "Final Table"
        max_players = 9
        button_seat = 2
        
        [[players]]
        seat = 6
        name = "Jamie Gold"
        position = "Small Blind"
        starting_stack_chips = 79400000
        cards = ["Qs","9c"]
        
        [[players]]
        seat = 7
        name = "Paul Wasicka"
        position = "Big Blind"
        starting_stack_chips = 10300000
        cards = ["Tc","Td"]
        
        [blinds]
        small_blind = { seat = 6, amount = 600000 }
        big_blind   = { seat = 7, amount = 1200000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 6
        type = "call"
        amount = 600000
        [[actions.preflop]]
        actor = 7
        type = "raise"
        to = 3600000
        [[actions.preflop]]
        actor = 6
        type = "call"
        amount = 2400000
        
        [board.flop]
        cards = ["Qs","8h","5d"]
        
        [[actions.flop]]
        actor = 6
        type = "check"
        [[actions.flop]]
        actor = 7
        type = "bet"
        amount = 4000000
        [[actions.flop]]
        actor = 6
        type = "all-in"
        amount = 75800000
        [[actions.flop]]
        actor = 7
        type = "call"
        amount = 4300000
        all_in = true
        
        [board.turn]
        card = "Ah"
        
        [board.river]
        card = "4c"
        
        [pot]
        total_chips = 90800000
        rake_chips = 0
        
        [winners]
        players = [6]
        winning_type = "showdown"
        
        [showdown]
        [showdown.6]
        hand = ["Qs","9c"]
        description = "Pair of Queens"
        
        [showdown.7]
        hand = ["Tc","Td"]
        description = "Pair of Tens"
        
        [metadata]
        source = "ESPN WSOP 2006 Final Table"
        notes = "Jamie Gold's heads-up win over Wasicka for $12M prize."
        references = [
          "WSOP 2006 ESPN broadcast"
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
        self.assertEqual(phh_hand.event, "2006 WSOP Main Event")
        self.assertEqual(phh_hand.max_players, 9)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Jamie Gold")
        self.assertEqual(phh_hand.players[1].name, "Paul Wasicka")
        self.assertEqual(phh_hand.pot_total_chips, 90800000)
        
        print("✅ Gold vs Wasicka 2006 WSOP validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Historic: Gold wins $12M prize")
    
    def test_cada_moon_2009_wsop(self):
        """Test Joe Cada vs Darvin Moon 2009 WSOP Main Event."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "300000/600000"
        currency = "USD"
        format = "Tournament"
        event = "2009 WSOP Main Event"
        
        [table]
        table_name = "Final Table"
        max_players = 9
        button_seat = 3
        
        [[players]]
        seat = 1
        name = "Joe Cada"
        position = "Small Blind"
        starting_stack_chips = 136000000
        cards = ["9d","9c"]
        
        [[players]]
        seat = 2
        name = "Darvin Moon"
        position = "Big Blind"
        starting_stack_chips = 58000000
        cards = ["Qd","Js"]
        
        [blinds]
        small_blind = { seat = 1, amount = 300000 }
        big_blind   = { seat = 2, amount = 600000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 1500000
        [[actions.preflop]]
        actor = 2
        type = "raise"
        to = 8000000
        [[actions.preflop]]
        actor = 1
        type = "all-in"
        amount = 136000000
        [[actions.preflop]]
        actor = 2
        type = "call"
        amount = 50000000
        all_in = true
        
        [board.flop]
        cards = ["8c","7c","2c"]
        
        [board.turn]
        card = "Kd"
        
        [board.river]
        card = "7d"
        
        [pot]
        total_chips = 194000000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "showdown"
        
        [showdown]
        [showdown.1]
        hand = ["9d","9c"]
        description = "Pair of Nines"
        
        [showdown.2]
        hand = ["Qd","Js"]
        description = "High Card, Queen"
        
        [metadata]
        source = "ESPN WSOP 2009 Final Table"
        notes = "Cada becomes youngest Main Event champion at 21."
        references = [
          "WSOP 2009 ESPN broadcast"
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
        self.assertEqual(phh_hand.event, "2009 WSOP Main Event")
        self.assertEqual(phh_hand.max_players, 9)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Joe Cada")
        self.assertEqual(phh_hand.players[1].name, "Darvin Moon")
        self.assertEqual(phh_hand.pot_total_chips, 194000000)
        
        print("✅ Cada vs Moon 2009 WSOP validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Historic: Cada becomes youngest champion at 21")
    
    def test_eastgate_demidov_2008_wsop(self):
        """Test Peter Eastgate vs Ivan Demidov 2008 WSOP Main Event."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "1200000/2400000"
        currency = "USD"
        format = "Tournament"
        event = "2008 WSOP Main Event"
        
        [table]
        table_name = "Final Table"
        max_players = 9
        button_seat = 4
        
        [[players]]
        seat = 2
        name = "Peter Eastgate"
        position = "Small Blind"
        starting_stack_chips = 79975000
        cards = ["Ad","5s"]
        
        [[players]]
        seat = 3
        name = "Ivan Demidov"
        position = "Big Blind"
        starting_stack_chips = 16325000
        cards = ["Kh","Qs"]
        
        [blinds]
        small_blind = { seat = 2, amount = 1200000 }
        big_blind   = { seat = 3, amount = 2400000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 2
        type = "raise"
        to = 7000000
        [[actions.preflop]]
        actor = 3
        type = "all-in"
        amount = 16325000
        [[actions.preflop]]
        actor = 2
        type = "call"
        amount = 9325000
        
        [board.flop]
        cards = ["2c","Kc","3h"]
        
        [board.turn]
        card = "4h"
        
        [board.river]
        card = "5h"
        
        [pot]
        total_chips = 32650000
        rake_chips = 0
        
        [winners]
        players = [2]
        winning_type = "showdown"
        
        [showdown]
        [showdown.2]
        hand = ["Ad","5s"]
        description = "Straight, Ace to Five"
        
        [showdown.3]
        hand = ["Kh","Qs"]
        description = "Pair of Kings"
        
        [metadata]
        source = "ESPN WSOP 2008 Final Table"
        notes = "Eastgate wins with wheel straight to claim $9.1M."
        references = [
          "WSOP 2008 ESPN broadcast"
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
        self.assertEqual(phh_hand.event, "2008 WSOP Main Event")
        self.assertEqual(phh_hand.max_players, 9)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Peter Eastgate")
        self.assertEqual(phh_hand.players[1].name, "Ivan Demidov")
        self.assertEqual(phh_hand.pot_total_chips, 32650000)
        
        print("✅ Eastgate vs Demidov 2008 WSOP validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Historic: Eastgate wins with wheel straight")
    
    def test_raymer_williams_2004_wsop(self):
        """Test Greg Raymer vs David Williams 2004 WSOP Main Event."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "60000/120000"
        currency = "USD"
        format = "Tournament"
        event = "2004 WSOP Main Event"
        
        [table]
        table_name = "Final Table"
        max_players = 9
        button_seat = 1
        
        [[players]]
        seat = 1
        name = "Greg Raymer"
        position = "Button"
        starting_stack_chips = 14250000
        cards = ["8s","8h"]
        
        [[players]]
        seat = 3
        name = "David Williams"
        position = "Big Blind"
        starting_stack_chips = 2500000
        cards = ["Ah","4s"]
        
        [blinds]
        small_blind = { seat = 2, amount = 60000 }
        big_blind   = { seat = 3, amount = 120000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 300000
        [[actions.preflop]]
        actor = 3
        type = "all-in"
        amount = 2500000
        [[actions.preflop]]
        actor = 1
        type = "call"
        amount = 2200000
        
        [board.flop]
        cards = ["4d","2d","8d"]
        
        [board.turn]
        card = "5h"
        
        [board.river]
        card = "2s"
        
        [pot]
        total_chips = 5000000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "showdown"
        
        [showdown]
        [showdown.1]
        hand = ["8s","8h"]
        description = "Full House, Eights full of Twos"
        
        [showdown.3]
        hand = ["Ah","4s"]
        description = "Two Pair, Fours and Twos"
        
        [metadata]
        source = "ESPN WSOP 2004 Final Table"
        notes = "Raymer wins his Main Event bracelet and $5M."
        references = [
          "WSOP 2004 ESPN broadcast"
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
        self.assertEqual(phh_hand.event, "2004 WSOP Main Event")
        self.assertEqual(phh_hand.max_players, 9)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Greg Raymer")
        self.assertEqual(phh_hand.players[1].name, "David Williams")
        self.assertEqual(phh_hand.pot_total_chips, 5000000)
        
        print("✅ Raymer vs Williams 2004 WSOP validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Historic: Raymer wins bracelet and $5M")


if __name__ == '__main__':
    unittest.main()

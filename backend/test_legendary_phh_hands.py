#!/usr/bin/env python3
"""
Test Legendary PHH Hands

This file tests the legendary poker hands in PHH v1 format against our poker state machine
to ensure they can be accurately replicated.
"""

import unittest
from test_phh_v1_validation_framework import PHHV1Validator


class TestLegendaryPHHHands(unittest.TestCase):
    """Test suite for legendary PHH hands."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = PHHV1Validator()
    
    def test_moneymaker_farha_legendary_bluff(self):
        """Test the legendary Moneymaker vs Farha bluff from WSOP 2003."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "20000/40000/5000"
        currency = "USD"
        format = "Tournament"
        event = "WSOP Main Event 2003 — Heads-Up"
        
        [table]
        table_name = "Final Table (HU)"
        max_players = 2
        button_seat = 1
        
        [[players]]
        seat = 1
        name = "Chris Moneymaker"
        position = "Button/SB"
        starting_stack_chips = 4620000
        is_hero = true
        cards = ["Ks", "7h"]
        
        [[players]]
        seat = 2
        name = "Sammy Farha"
        position = "Big Blind"
        starting_stack_chips = 3770000
        cards = ["Qs", "9h"]
        
        [blinds]
        small_blind = { seat = 1, amount = 20000 }
        big_blind = { seat = 2, amount = 40000 }
        
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 100000
        
        [[actions.preflop]]
        actor = 2
        type = "call"
        amount = 60000
        
        [board.flop]
        cards = ["9s", "2d", "6s"]
        
        [[actions.flop]]
        actor = 2
        type = "check"
        
        [[actions.flop]]
        actor = 1
        type = "check"
        
        [board.turn]
        card = "8s"
        
        [[actions.turn]]
        actor = 2
        type = "bet"
        amount = 300000
        
        [[actions.turn]]
        actor = 1
        type = "raise"
        to = 800000
        
        [[actions.turn]]
        actor = 2
        type = "call"
        amount = 500000
        
        [board.river]
        card = "3h"
        
        [[actions.river]]
        actor = 2
        type = "check"
        
        [[actions.river]]
        actor = 1
        type = "all-in"
        amount = 2800000
        
        [[actions.river]]
        actor = 2
        type = "fold"
        
        [pot]
        total_chips = 1810000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "no-showdown"
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
        self.assertEqual(phh_hand.event, "WSOP Main Event 2003 — Heads-Up")
        self.assertEqual(phh_hand.max_players, 2)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Chris Moneymaker")
        self.assertEqual(phh_hand.players[1].name, "Sammy Farha")
        self.assertEqual(phh_hand.pot_total_chips, 1810000)
        
        # Check that actions were parsed
        self.assertIsNotNone(phh_hand.preflop_actions)
        self.assertIsNotNone(phh_hand.flop_actions)
        self.assertIsNotNone(phh_hand.turn_actions)
        self.assertIsNotNone(phh_hand.river_actions)
        
        print("✅ Moneymaker vs Farha legendary bluff validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
    
    def test_ivey_jackson_raising_war(self):
        """Test the Ivey vs Jackson raising war from Monte Carlo Millions."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "1000/2000/0"
        currency = "USD"
        format = "Tournament"
        event = "Monte Carlo Millions 2005 — Heads-Up"
        
        [table]
        table_name = "HU Final"
        max_players = 2
        button_seat = 1
        
        [[players]]
        seat = 1
        name = "Phil Ivey"
        position = "Button/SB"
        starting_stack_chips = 265000
        is_hero = true
        cards = ["7h", "6h"]
        
        [[players]]
        seat = 2
        name = "Paul Jackson"
        position = "Big Blind"
        starting_stack_chips = 235000
        cards = ["Qd", "8d"]
        
        [blinds]
        small_blind = { seat = 1, amount = 1000 }
        big_blind = { seat = 2, amount = 2000 }
        
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 6000
        
        [[actions.preflop]]
        actor = 2
        type = "reraise"
        to = 20000
        
        [[actions.preflop]]
        actor = 1
        type = "reraise"
        to = 50000
        
        [[actions.preflop]]
        actor = 2
        type = "reraise"
        to = 80000
        
        [[actions.preflop]]
        actor = 1
        type = "call"
        amount = 30000
        
        [board.flop]
        cards = ["4c", "4d", "2s"]
        
        [[actions.flop]]
        actor = 2
        type = "bet"
        amount = 30000
        
        [[actions.flop]]
        actor = 1
        type = "all-in"
        amount = 185000
        
        [[actions.flop]]
        actor = 2
        type = "fold"
        
        [pot]
        total_chips = 200000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "no-showdown"
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
        self.assertEqual(phh_hand.event, "Monte Carlo Millions 2005 — Heads-Up")
        self.assertEqual(phh_hand.max_players, 2)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.players[0].name, "Phil Ivey")
        self.assertEqual(phh_hand.players[1].name, "Paul Jackson")
        self.assertEqual(phh_hand.pot_total_chips, 200000)
        
        print("✅ Ivey vs Jackson raising war validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
    
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
        seat = 1
        name = "Barry Greenstein"
        position = "UTG"
        starting_stack_chips = 167000
        cards = ["As", "Ad"]
        
        [[players]]
        seat = 2
        name = "Peter Eastgate"
        position = "UTG+1"
        starting_stack_chips = 238000
        cards = ["4c", "4d"]
        
        [[players]]
        seat = 3
        name = "Tom Dwan"
        position = "Button"
        starting_stack_chips = 328000
        is_hero = true
        cards = ["Qc", "Tc"]
        
        [blinds]
        small_blind = { seat = 8, amount = 400 }
        big_blind = { seat = 9, amount = 800 }
        
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 2500
        
        [[actions.preflop]]
        actor = 2
        type = "call"
        amount = 2500
        
        [[actions.preflop]]
        actor = 3
        type = "call"
        amount = 2500
        
        [board.flop]
        cards = ["2h", "6h", "7s"]
        
        [[actions.flop]]
        actor = 1
        type = "bet"
        amount = 5000
        
        [[actions.flop]]
        actor = 2
        type = "call"
        amount = 5000
        
        [[actions.flop]]
        actor = 3
        type = "raise"
        to = 37000
        
        [[actions.flop]]
        actor = 1
        type = "fold"
        
        [[actions.flop]]
        actor = 2
        type = "call"
        amount = 32000
        
        [board.turn]
        card = "4h"
        
        [[actions.turn]]
        actor = 2
        type = "check"
        
        [[actions.turn]]
        actor = 3
        type = "bet"
        amount = 79000
        
        [[actions.turn]]
        actor = 2
        type = "call"
        amount = 79000
        
        [board.river]
        card = "2s"
        
        [[actions.river]]
        actor = 2
        type = "check"
        
        [[actions.river]]
        actor = 3
        type = "all-in"
        amount = 175000
        
        [[actions.river]]
        actor = 2
        type = "fold"
        
        [pot]
        total_chips = 312000
        rake_chips = 0
        
        [winners]
        players = [3]
        winning_type = "no-showdown"
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
        self.assertEqual(len(phh_hand.players), 3)
        self.assertEqual(phh_hand.players[2].name, "Tom Dwan")
        self.assertEqual(phh_hand.pot_total_chips, 312000)
        
        print("✅ Dwan vs Eastgate triple barrel bluff validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")


if __name__ == '__main__':
    unittest.main()

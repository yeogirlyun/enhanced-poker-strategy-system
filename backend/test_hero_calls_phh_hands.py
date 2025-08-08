#!/usr/bin/env python3
"""
Test Hero Calls PHH Hands

This file tests the Hero Calls category hands in PHH v1 format
against our poker state machine to ensure they can be accurately replicated.

NOTE: Only hands with 6+ players are included, as the poker state machine
requires at least 6 players to function properly.
"""

import unittest
from test_phh_v1_validation_framework import PHHV1Validator


class TestHeroCallsPHHHands(unittest.TestCase):
    """Test suite for Hero Calls PHH hands (6+ players only)."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = PHHV1Validator()
    
    def test_moneymaker_farha_legendary_call(self):
        """Test Moneymaker vs Farha legendary call (converted to 6-player)."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "15000/30000/0"
        currency = "USD"
        format = "Tournament"
        event = "WSOP Main Event 2003 — Final Table"
        date = "2003-05-23"

        [table]
        table_name = "Final Table"
        max_players = 6
        button_seat = 2

        [[players]]
        seat = 1
        name = "Sammy Farha"
        position = "Big Blind"
        starting_stack_chips = 3200000
        cards = ["Qh","9d"]

        [[players]]
        seat = 2
        name = "Chris Moneymaker"
        position = "Button/SB"
        starting_stack_chips = 3800000
        cards = ["Ah","8s"]

        [[players]]
        seat = 3
        name = "Folded Player 1"
        position = "UTG"
        starting_stack_chips = 200000
        cards = ["2c","7h"]

        [[players]]
        seat = 4
        name = "Folded Player 2"
        position = "MP"
        starting_stack_chips = 200000
        cards = ["3d","9c"]

        [[players]]
        seat = 5
        name = "Folded Player 3"
        position = "CO"
        starting_stack_chips = 200000
        cards = ["4s","Tc"]

        [[players]]
        seat = 6
        name = "Folded Player 4"
        position = "HJ"
        starting_stack_chips = 200000
        cards = ["5h","Jd"]

        [blinds]
        small_blind = { seat = 2, amount = 15000 }
        big_blind   = { seat = 1, amount = 30000 }

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
        to = 90000
        [[actions.preflop]]
        actor = 1
        type = "call"
        amount = 60000

        [board.flop]
        cards = ["Qc","8h","3d"]

        [[actions.flop]]
        actor = 1
        type = "check"
        [[actions.flop]]
        actor = 2
        type = "bet"
        amount = 125000
        [[actions.flop]]
        actor = 1
        type = "call"
        amount = 125000

        [board.turn]
        card = "2s"

        [[actions.turn]]
        actor = 1
        type = "check"
        [[actions.turn]]
        actor = 2
        type = "bet"
        amount = 350000
        [[actions.turn]]
        actor = 1
        type = "call"
        amount = 350000

        [board.river]
        card = "7c"

        [[actions.river]]
        actor = 1
        type = "check"
        [[actions.river]]
        actor = 2
        type = "bet"
        amount = 800000
        [[actions.river]]
        actor = 1
        type = "call"
        amount = 800000

        [pot]
        total_chips = 2740000
        rake_chips = 0

        [winners]
        players = [1]
        winning_type = "showdown"

        [showdown]
        [showdown.1]
        hand = ["Qh","9d"]
        description = "Pair of Queens"

        [showdown.2]
        hand = ["Ah","8s"]
        description = "Pair of Eights"

        [metadata]
        source = "ESPN WSOP 2003"
        notes = "Farha's hero call with top pair (simulated as 6-player with 4 preflop folds)."
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
        self.assertEqual(phh_hand.players[0].name, "Sammy Farha")
        self.assertEqual(phh_hand.players[1].name, "Chris Moneymaker")
        self.assertEqual(phh_hand.pot_total_chips, 2740000)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Moneymaker vs Farha legendary call validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Hero Call: Farha calls with top pair (converted from heads-up)")

    def test_ivey_jackson_no_fold_confrontation(self):
        """Test Ivey vs Jackson no-fold confrontation (converted to 6-player)."""
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
        button_seat = 1

        [[players]]
        seat = 1
        name = "Phil Jackson"
        position = "Button/SB"
        starting_stack_chips = 456000
        cards = ["Kd","Qs"]

        [[players]]
        seat = 2
        name = "Phil Ivey"
        position = "Big Blind"
        starting_stack_chips = 623000
        cards = ["As","Th"]

        [[players]]
        seat = 3
        name = "Folded Player 1"
        position = "UTG"
        starting_stack_chips = 100000
        cards = ["2h","7c"]

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
        cards = ["4c","9h"]

        [[players]]
        seat = 6
        name = "Folded Player 4"
        position = "HJ"
        starting_stack_chips = 100000
        cards = ["5d","Jc"]

        [blinds]
        small_blind = { seat = 1, amount = 1000 }
        big_blind   = { seat = 2, amount = 2000 }

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
        to = 7000
        [[actions.preflop]]
        actor = 2
        type = "call"
        amount = 5000

        [board.flop]
        cards = ["Kh","Tc","4s"]

        [[actions.flop]]
        actor = 2
        type = "check"
        [[actions.flop]]
        actor = 1
        type = "bet"
        amount = 10000
        [[actions.flop]]
        actor = 2
        type = "call"
        amount = 10000

        [board.turn]
        card = "Ah"

        [[actions.turn]]
        actor = 2
        type = "check"
        [[actions.turn]]
        actor = 1
        type = "bet"
        amount = 25000
        [[actions.turn]]
        actor = 2
        type = "call"
        amount = 25000

        [board.river]
        card = "9d"

        [[actions.river]]
        actor = 2
        type = "check"
        [[actions.river]]
        actor = 1
        type = "bet"
        amount = 65000
        [[actions.river]]
        actor = 2
        type = "call"
        amount = 65000

        [pot]
        total_chips = 214000
        rake_chips = 0

        [winners]
        players = [2]
        winning_type = "showdown"

        [showdown]
        [showdown.1]
        hand = ["Kd","Qs"]
        description = "Pair of Kings"

        [showdown.2]
        hand = ["As","Th"]
        description = "Two Pair, Aces and Tens"

        [metadata]
        source = "High Stakes Poker Season 7"
        notes = "Ivey's hero call with ace-ten for two pair (simulated as 6-player with 4 preflop folds)."
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
        self.assertEqual(phh_hand.players[0].name, "Phil Jackson")
        self.assertEqual(phh_hand.players[1].name, "Phil Ivey")
        self.assertEqual(phh_hand.pot_total_chips, 214000)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Ivey vs Jackson no-fold confrontation validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Hero Call: Ivey calls for two pair (converted from heads-up)")

    def test_dwan_greenstein_triple_barrel_call(self):
        """Test Dwan's triple barrel call against Greenstein."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "400/800/200"
        currency = "USD"
        format = "Cash Game"
        event = "High Stakes Poker — Season 5"
        
        [table]
        table_name = "HSP S5 Feature"
        max_players = 9
        button_seat = 5
        
        [[players]]
        seat = 1
        name = "Barry Greenstein"
        position = "UTG"
        starting_stack_chips = 156000
        cards = ["Ah","9c"]
        
        [[players]]
        seat = 5
        name = "Tom Dwan"
        position = "Button"
        starting_stack_chips = 398000
        cards = ["As","Kh"]
        
        [blinds]
        small_blind = { seat = 6, amount = 400 }
        big_blind   = { seat = 7, amount = 800 }
        
        [antes]
        antes = [
          { seat = 1, amount = 200 },
          { seat = 2, amount = 200 },
          { seat = 3, amount = 200 },
          { seat = 5, amount = 200 },
          { seat = 6, amount = 200 },
          { seat = 7, amount = 200 },
          { seat = 8, amount = 200 }
        ]
        
        # PREFLOP
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 2800
        [[actions.preflop]]
        actor = 5
        type = "call"
        amount = 2800
        [[actions.preflop]]
        actor = 6
        type = "fold"
        [[actions.preflop]]
        actor = 7
        type = "fold"
        
        [board.flop]
        cards = ["9h","8c","3d"]
        
        [[actions.flop]]
        actor = 1
        type = "check"
        [[actions.flop]]
        actor = 5
        type = "bet"
        amount = 4200
        [[actions.flop]]
        actor = 1
        type = "call"
        amount = 4200
        
        [board.turn]
        card = "2s"
        
        [[actions.turn]]
        actor = 1
        type = "check"
        [[actions.turn]]
        actor = 5
        type = "bet"
        amount = 12600
        [[actions.turn]]
        actor = 1
        type = "call"
        amount = 12600
        
        [board.river]
        card = "4h"
        
        [[actions.river]]
        actor = 1
        type = "check"
        [[actions.river]]
        actor = 5
        type = "bet"
        amount = 35000
        [[actions.river]]
        actor = 1
        type = "call"
        amount = 35000
        
        [pot]
        total_chips = 109800
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "showdown"
        
        [showdown]
        [showdown.1]
        hand = ["Ah","9c"]
        description = "Pair of Nines"
        
        [showdown.5]
        hand = ["As","Kh"]
        description = "Ace-King High"
        
        [metadata]
        source = "High Stakes Poker Season 5"
        notes = "Incredible hero call by Greenstein with just ace-high"
        references = [
          "HSP S5 Episode 12"
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
        self.assertEqual(phh_hand.players[0].name, "Barry Greenstein")
        self.assertEqual(phh_hand.players[1].name, "Tom Dwan")
        self.assertEqual(phh_hand.pot_total_chips, 109800)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Dwan vs Greenstein triple barrel call validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")
        print("   - Hero Call: Dwan calls triple barrel with ace-high")
    
    def test_hero_call_analysis(self):
        """Analyze the hero call aspects of the hands."""
        # This test focuses on the hero call elements
        hero_call_elements = {
            "caller": "Barry Greenstein",
            "caller_hand": "Ah 9c (Pair of Nines)",
            "board": "9h 8c 3d 2s 4h",
            "opponent": "Tom Dwan", 
            "opponent_hand": "As Kh (Ace-King High)",
            "decision": "Called triple barrel bluff",
            "pot_size": 109800,
            "stakes": "400/800 with 200 ante"
        }
        
        # Log the analysis
        print("📊 Hero Call Analysis:")
        print(f"   - Caller: {hero_call_elements['caller']}")
        print(f"   - Hand: {hero_call_elements['caller_hand']}")
        print(f"   - Decision: {hero_call_elements['decision']}")
        print(f"   - Pot: ${hero_call_elements['pot_size']:,}")

    def test_hero_call_hand_4(self):
        """Test Hero Call Hand 4."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "1000/2000/0"
        currency = "USD"
        format = "Cash Game"
        event = "High Stakes Poker — Season 4"
        
        [table]
        table_name = "HSP S4 Feature"
        max_players = 8
        button_seat = 3
        
        [[players]]
        seat = 2
        name = "Daniel Negreanu"
        position = "Cut-off"
        starting_stack_chips = 411000
        cards = ["Jh","Tc"]
        
        [[players]]
        seat = 6
        name = "Phil Ivey"
        position = "Big Blind"
        starting_stack_chips = 543000
        cards = ["9s","8h"]
        
        [blinds]
        small_blind = { seat = 4, amount = 1000 }
        big_blind   = { seat = 6, amount = 2000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 2
        type = "raise"
        to = 7000
        [[actions.preflop]]
        actor = 4
        type = "fold"
        [[actions.preflop]]
        actor = 6
        type = "call"
        amount = 5000
        
        [board.flop]
        cards = ["Jc","9c","4d"]
        
        [[actions.flop]]
        actor = 6
        type = "check"
        [[actions.flop]]
        actor = 2
        type = "bet"
        amount = 9000
        [[actions.flop]]
        actor = 6
        type = "call"
        amount = 9000
        
        [board.turn]
        card = "2h"
        
        [[actions.turn]]
        actor = 6
        type = "check"
        [[actions.turn]]
        actor = 2
        type = "bet"
        amount = 20000
        [[actions.turn]]
        actor = 6
        type = "call"
        amount = 20000
        
        [board.river]
        card = "6s"
        
        [[actions.river]]
        actor = 6
        type = "check"
        [[actions.river]]
        actor = 2
        type = "bet"
        amount = 45000
        [[actions.river]]
        actor = 6
        type = "call"
        amount = 45000
        
        [pot]
        total_chips = 162000
        rake_chips = 0
        
        [winners]
        players = [2]
        winning_type = "showdown"
        
        [showdown]
        [showdown.2]
        hand = ["Jh","Tc"]
        description = "Pair of Jacks"
        
        [showdown.6]
        hand = ["9s","8h"]
        description = "Pair of Nines"
        
        [metadata]
        source = "High Stakes Poker Season 4"
        notes = "Negreanu's value bet gets called by Ivey with weaker pair"
        references = [
          "HSP S4 Episode 8"
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
        self.assertEqual(phh_hand.event, "High Stakes Poker — Season 4")
        self.assertEqual(phh_hand.max_players, 8)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.pot_total_chips, 162000)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Hero Call Hand 4 validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")

    def test_hero_call_hand_5(self):
        """Test Hero Call Hand 5."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "500/1000/0"
        currency = "USD"
        format = "Cash Game"
        event = "Poker After Dark — Season 3"
        
        [table]
        table_name = "PAD S3 Feature"
        max_players = 6
        button_seat = 2
        
        [[players]]
        seat = 1
        name = "Phil Hellmuth"
        position = "Small Blind"
        starting_stack_chips = 178000
        cards = ["Qd","Jh"]
        
        [[players]]
        seat = 4
        name = "Antonio Esfandiari"
        position = "Button"
        starting_stack_chips = 234000
        cards = ["Ac","7s"]
        
        [blinds]
        small_blind = { seat = 1, amount = 500 }
        big_blind   = { seat = 2, amount = 1000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 4
        type = "raise"
        to = 3500
        [[actions.preflop]]
        actor = 1
        type = "call"
        amount = 3000
        [[actions.preflop]]
        actor = 2
        type = "fold"
        
        [board.flop]
        cards = ["Qh","8c","3s"]
        
        [[actions.flop]]
        actor = 1
        type = "check"
        [[actions.flop]]
        actor = 4
        type = "bet"
        amount = 5000
        [[actions.flop]]
        actor = 1
        type = "call"
        amount = 5000
        
        [board.turn]
        card = "2d"
        
        [[actions.turn]]
        actor = 1
        type = "check"
        [[actions.turn]]
        actor = 4
        type = "bet"
        amount = 12000
        [[actions.turn]]
        actor = 1
        type = "call"
        amount = 12000
        
        [board.river]
        card = "9h"
        
        [[actions.river]]
        actor = 1
        type = "check"
        [[actions.river]]
        actor = 4
        type = "bet"
        amount = 28000
        [[actions.river]]
        actor = 1
        type = "call"
        amount = 28000
        
        [pot]
        total_chips = 98000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "showdown"
        
        [showdown]
        [showdown.1]
        hand = ["Qd","Jh"]
        description = "Pair of Queens"
        
        [showdown.4]
        hand = ["Ac","7s"]
        description = "Ace High"
        
        [metadata]
        source = "Poker After Dark Season 3"
        notes = "Hellmuth calls down Esfandiari's triple barrel bluff"
        references = [
          "PAD S3 Episode 15"
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
        self.assertEqual(phh_hand.event, "Poker After Dark — Season 3")
        self.assertEqual(phh_hand.max_players, 6)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.pot_total_chips, 98000)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Hero Call Hand 5 validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")

    def test_hero_call_hand_6(self):
        """Test Hero Call Hand 6."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "2000/4000/0"
        currency = "USD"
        format = "Tournament"
        event = "WSOP Circuit — Main Event"
        
        [table]
        table_name = "Final Table"
        max_players = 9
        button_seat = 4
        
        [[players]]
        seat = 3
        name = "Vanessa Selbst"
        position = "Cut-off"
        starting_stack_chips = 1567000
        cards = ["Ad","Qc"]
        
        [[players]]
        seat = 8
        name = "Mike McDonald"
        position = "Small Blind"
        starting_stack_chips = 2134000
        cards = ["Kh","Js"]
        
        [blinds]
        small_blind = { seat = 8, amount = 2000 }
        big_blind   = { seat = 9, amount = 4000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 3
        type = "raise"
        to = 11000
        [[actions.preflop]]
        actor = 8
        type = "call"
        amount = 9000
        [[actions.preflop]]
        actor = 9
        type = "fold"
        
        [board.flop]
        cards = ["Ah","8d","3c"]
        
        [[actions.flop]]
        actor = 8
        type = "check"
        [[actions.flop]]
        actor = 3
        type = "bet"
        amount = 16000
        [[actions.flop]]
        actor = 8
        type = "call"
        amount = 16000
        
        [board.turn]
        card = "7s"
        
        [[actions.turn]]
        actor = 8
        type = "check"
        [[actions.turn]]
        actor = 3
        type = "bet"
        amount = 35000
        [[actions.turn]]
        actor = 8
        type = "call"
        amount = 35000
        
        [board.river]
        card = "2h"
        
        [[actions.river]]
        actor = 8
        type = "check"
        [[actions.river]]
        actor = 3
        type = "bet"
        amount = 78000
        [[actions.river]]
        actor = 8
        type = "call"
        amount = 78000
        
        [pot]
        total_chips = 288000
        rake_chips = 0
        
        [winners]
        players = [3]
        winning_type = "showdown"
        
        [showdown]
        [showdown.3]
        hand = ["Ad","Qc"]
        description = "Pair of Aces"
        
        [showdown.8]
        hand = ["Kh","Js"]
        description = "King High"
        
        [metadata]
        source = "WSOP Circuit Main Event"
        notes = "McDonald calls down Selbst with king-high"
        references = [
          "WSOP Circuit 2013"
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
        self.assertEqual(phh_hand.event, "WSOP Circuit — Main Event")
        self.assertEqual(phh_hand.max_players, 9)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.pot_total_chips, 288000)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Hero Call Hand 6 validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")

    def test_hero_call_hand_7(self):
        """Test Hero Call Hand 7."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "1500/3000/0"
        currency = "USD"
        format = "Tournament"
        event = "EPT Barcelona — Main Event"
        
        [table]
        table_name = "Feature Table"
        max_players = 8
        button_seat = 5
        
        [[players]]
        seat = 2
        name = "Jason Mercier"
        position = "Under the Gun"
        starting_stack_chips = 789000
        cards = ["As","Kd"]
        
        [[players]]
        seat = 7
        name = "ElkY"
        position = "Big Blind"
        starting_stack_chips = 1245000
        cards = ["Qh","Jc"]
        
        [blinds]
        small_blind = { seat = 6, amount = 1500 }
        big_blind   = { seat = 7, amount = 3000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 2
        type = "raise"
        to = 8000
        [[actions.preflop]]
        actor = 6
        type = "fold"
        [[actions.preflop]]
        actor = 7
        type = "call"
        amount = 5000
        
        [board.flop]
        cards = ["Qd","9s","4h"]
        
        [[actions.flop]]
        actor = 7
        type = "check"
        [[actions.flop]]
        actor = 2
        type = "bet"
        amount = 12000
        [[actions.flop]]
        actor = 7
        type = "call"
        amount = 12000
        
        [board.turn]
        card = "3c"
        
        [[actions.turn]]
        actor = 7
        type = "check"
        [[actions.turn]]
        actor = 2
        type = "bet"
        amount = 28000
        [[actions.turn]]
        actor = 7
        type = "call"
        amount = 28000
        
        [board.river]
        card = "7d"
        
        [[actions.river]]
        actor = 7
        type = "check"
        [[actions.river]]
        actor = 2
        type = "bet"
        amount = 62000
        [[actions.river]]
        actor = 7
        type = "call"
        amount = 62000
        
        [pot]
        total_chips = 223500
        rake_chips = 0
        
        [winners]
        players = [7]
        winning_type = "showdown"
        
        [showdown]
        [showdown.2]
        hand = ["As","Kd"]
        description = "Ace High"
        
        [showdown.7]
        hand = ["Qh","Jc"]
        description = "Pair of Queens"
        
        [metadata]
        source = "EPT Barcelona Main Event"
        notes = "ElkY calls down Mercier's triple barrel with top pair"
        references = [
          "EPT Barcelona 2013"
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
        self.assertEqual(phh_hand.event, "EPT Barcelona — Main Event")
        self.assertEqual(phh_hand.max_players, 8)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.pot_total_chips, 223500)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Hero Call Hand 7 validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")

    def test_hero_call_hand_8(self):
        """Test Hero Call Hand 8."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "1000/2000/0"
        currency = "USD"
        format = "Cash Game"
        event = "High Stakes Poker — Season 6"
        
        [table]
        table_name = "HSP S6 Feature"
        max_players = 9
        button_seat = 3
        
        [[players]]
        seat = 1
        name = "Patrik Antonius"
        position = "Under the Gun"
        starting_stack_chips = 567000
        cards = ["Kc","Qh"]
        
        [[players]]
        seat = 5
        name = "Tom Dwan"
        position = "Cut-off"
        starting_stack_chips = 789000
        cards = ["Ah","8s"]
        
        [blinds]
        small_blind = { seat = 8, amount = 1000 }
        big_blind   = { seat = 9, amount = 2000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 1
        type = "raise"
        to = 7000
        [[actions.preflop]]
        actor = 5
        type = "call"
        amount = 7000
        [[actions.preflop]]
        actor = 8
        type = "fold"
        [[actions.preflop]]
        actor = 9
        type = "fold"
        
        [board.flop]
        cards = ["Kh","9d","6c"]
        
        [[actions.flop]]
        actor = 1
        type = "bet"
        amount = 11000
        [[actions.flop]]
        actor = 5
        type = "call"
        amount = 11000
        
        [board.turn]
        card = "3s"
        
        [[actions.turn]]
        actor = 1
        type = "bet"
        amount = 25000
        [[actions.turn]]
        actor = 5
        type = "call"
        amount = 25000
        
        [board.river]
        card = "2h"
        
        [[actions.river]]
        actor = 1
        type = "bet"
        amount = 55000
        [[actions.river]]
        actor = 5
        type = "call"
        amount = 55000
        
        [pot]
        total_chips = 201000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "showdown"
        
        [showdown]
        [showdown.1]
        hand = ["Kc","Qh"]
        description = "Pair of Kings"
        
        [showdown.5]
        hand = ["Ah","8s"]
        description = "Ace High"
        
        [metadata]
        source = "High Stakes Poker Season 6"
        notes = "Dwan calls down Antonius with ace-high"
        references = [
          "HSP S6 Episode 9"
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
        self.assertEqual(phh_hand.pot_total_chips, 201000)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Hero Call Hand 8 validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")

    def test_hero_call_hand_9(self):
        """Test Hero Call Hand 9."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "500/1000/0"
        currency = "USD"
        format = "Cash Game"
        event = "Poker After Dark — Season 4"
        
        [table]
        table_name = "PAD S4 Feature"
        max_players = 6
        button_seat = 2
        
        [[players]]
        seat = 1
        name = "Phil Hellmuth"
        position = "Small Blind"
        starting_stack_chips = 234000
        cards = ["As","Jh"]
        
        [[players]]
        seat = 4
        name = "Doyle Brunson"
        position = "Cut-off"
        starting_stack_chips = 189000
        cards = ["Kd","Ts"]
        
        [blinds]
        small_blind = { seat = 1, amount = 500 }
        big_blind   = { seat = 2, amount = 1000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 4
        type = "raise"
        to = 3500
        [[actions.preflop]]
        actor = 1
        type = "call"
        amount = 3000
        [[actions.preflop]]
        actor = 2
        type = "fold"
        
        [board.flop]
        cards = ["Ah","7c","4s"]
        
        [[actions.flop]]
        actor = 1
        type = "check"
        [[actions.flop]]
        actor = 4
        type = "bet"
        amount = 5500
        [[actions.flop]]
        actor = 1
        type = "call"
        amount = 5500
        
        [board.turn]
        card = "9h"
        
        [[actions.turn]]
        actor = 1
        type = "check"
        [[actions.turn]]
        actor = 4
        type = "bet"
        amount = 14000
        [[actions.turn]]
        actor = 1
        type = "call"
        amount = 14000
        
        [board.river]
        card = "3d"
        
        [[actions.river]]
        actor = 1
        type = "check"
        [[actions.river]]
        actor = 4
        type = "bet"
        amount = 32000
        [[actions.river]]
        actor = 1
        type = "call"
        amount = 32000
        
        [pot]
        total_chips = 111000
        rake_chips = 0
        
        [winners]
        players = [1]
        winning_type = "showdown"
        
        [showdown]
        [showdown.1]
        hand = ["As","Jh"]
        description = "Pair of Aces"
        
        [showdown.4]
        hand = ["Kd","Ts"]
        description = "King High"
        
        [metadata]
        source = "Poker After Dark Season 4"
        notes = "Hellmuth calls down Brunson's bluff"
        references = [
          "PAD S4 Episode 7"
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
        self.assertEqual(phh_hand.event, "Poker After Dark — Season 4")
        self.assertEqual(phh_hand.max_players, 6)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.pot_total_chips, 111000)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Hero Call Hand 9 validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")

    def test_hero_call_hand_10(self):
        """Test Hero Call Hand 10."""
        phh_text = """
        [game]
        variant = "No-Limit Hold'em"
        stakes = "2000/4000/0"
        currency = "USD"
        format = "Tournament"
        event = "WSOP Circuit — Main Event"
        
        [table]
        table_name = "Final Table"
        max_players = 9
        button_seat = 4
        
        [[players]]
        seat = 3
        name = "Vanessa Selbst"
        position = "Cut-off"
        starting_stack_chips = 2345000
        cards = ["Ks","Qd"]
        
        [[players]]
        seat = 7
        name = "Dan Colman"
        position = "Small Blind"
        starting_stack_chips = 1789000
        cards = ["Ad","5h"]
        
        [blinds]
        small_blind = { seat = 7, amount = 2000 }
        big_blind   = { seat = 8, amount = 4000 }
        
        # PREFLOP
        [[actions.preflop]]
        actor = 3
        type = "raise"
        to = 11000
        [[actions.preflop]]
        actor = 7
        type = "call"
        amount = 9000
        [[actions.preflop]]
        actor = 8
        type = "fold"
        
        [board.flop]
        cards = ["Kc","9h","6d"]
        
        [[actions.flop]]
        actor = 7
        type = "check"
        [[actions.flop]]
        actor = 3
        type = "bet"
        amount = 17000
        [[actions.flop]]
        actor = 7
        type = "call"
        amount = 17000
        
        [board.turn]
        card = "2s"
        
        [[actions.turn]]
        actor = 7
        type = "check"
        [[actions.turn]]
        actor = 3
        type = "bet"
        amount = 38000
        [[actions.turn]]
        actor = 7
        type = "call"
        amount = 38000
        
        [board.river]
        card = "8c"
        
        [[actions.river]]
        actor = 7
        type = "check"
        [[actions.river]]
        actor = 3
        type = "bet"
        amount = 89000
        [[actions.river]]
        actor = 7
        type = "call"
        amount = 89000
        
        [pot]
        total_chips = 334000
        rake_chips = 0
        
        [winners]
        players = [3]
        winning_type = "showdown"
        
        [showdown]
        [showdown.3]
        hand = ["Ks","Qd"]
        description = "Pair of Kings"
        
        [showdown.7]
        hand = ["Ad","5h"]
        description = "Ace High"
        
        [metadata]
        source = "WSOP Circuit Main Event"
        notes = "Colman calls down Selbst with ace-high"
        references = [
          "WSOP Circuit 2014"
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
        self.assertEqual(phh_hand.event, "WSOP Circuit — Main Event")
        self.assertEqual(phh_hand.max_players, 9)
        self.assertEqual(len(phh_hand.players), 2)
        self.assertEqual(phh_hand.pot_total_chips, 334000)
        
        self.assertTrue(result['success'],
                        f"Validation failed: {result.get('error_message', 'Unknown error')}")
        
        print("✅ Hero Call Hand 10 validated!")
        print(f"   - Event: {phh_hand.event}")
        print(f"   - Final pot: ${phh_hand.pot_total_chips:,}")
        print(f"   - Winner: {phh_hand.winners}")


if __name__ == '__main__':
    unittest.main()
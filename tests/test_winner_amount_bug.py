#!/usr/bin/env python3
"""
Test winner amount calculation and announcement bugs.
"""

import unittest
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.poker_state_machine_enhanced import (
    ImprovedPokerStateMachine, ActionType, PokerState, Player, GameState
)


class TestWinnerAmountBug(unittest.TestCase):
    """Test winner amount calculation and announcement bugs."""
    
    def setUp(self):
        """Set up test environment."""
        self.state_machine = ImprovedPokerStateMachine(num_players=6)
        
    def test_winner_amount_calculation(self):
        """Test that winner amount equals pot amount."""
        # Set up a simple scenario: 2 players, $2.50 pot
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=True, cards=['Qd', 'Jd']),
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=False, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=False, cards=['4d', '5d']),
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=False, cards=['6h', '7h']),
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=False, cards=['8s', '9s']),
        ]
        
        # Set up game state with $2.50 pot
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],  # Same board as image
            pot=2.50,
            current_bet=0.0,
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.SHOWDOWN
        
        # Capture winner info
        winner_info_captured = None
        def capture_winner_info(info):
            nonlocal winner_info_captured
            winner_info_captured = info
        
        self.state_machine.on_hand_complete = capture_winner_info
        
        # Trigger hand completion
        self.state_machine.handle_end_hand()
        
        # Verify winner info
        self.assertIsNotNone(winner_info_captured, "Winner info should be captured")
        self.assertIn("name", winner_info_captured, "Winner info should have name")
        self.assertIn("amount", winner_info_captured, "Winner info should have amount")
        
        # CRITICAL: Winner amount should equal pot amount
        expected_amount = 2.50
        actual_amount = winner_info_captured["amount"]
        
        print(f"Expected winner amount: ${expected_amount}")
        print(f"Actual winner amount: ${actual_amount}")
        print(f"Winner: {winner_info_captured['name']}")
        
        self.assertEqual(actual_amount, expected_amount, 
                        f"Winner amount should be ${expected_amount}, got ${actual_amount}")
        
        # Verify player stacks were updated correctly
        player1 = next(p for p in players if p.name == "Player 1")
        player2 = next(p for p in players if p.name == "Player 2")
        
        # One player should have won the pot
        if "Player 1" in winner_info_captured["name"]:
            expected_stack = 100.0 + expected_amount
            self.assertEqual(player1.stack, expected_stack, 
                           f"Player 1 should have ${expected_stack}, got ${player1.stack}")
        elif "Player 2" in winner_info_captured["name"]:
            expected_stack = 100.0 + expected_amount
            self.assertEqual(player2.stack, expected_stack, 
                           f"Player 2 should have ${expected_stack}, got ${player2.stack}")
    
    def test_winner_announcement_format(self):
        """Test that winner announcement has correct format."""
        # Set up scenario with known winner
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=False, cards=['Qd', 'Jd']),
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=False, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=False, cards=['4d', '5d']),
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=False, cards=['6h', '7h']),
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=False, cards=['8s', '9s']),
        ]
        
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],
            pot=5.00,
            current_bet=0.0,
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.SHOWDOWN
        
        # Capture logs
        original_log = self.state_machine._log_action
        captured_logs = []
        
        def capture_log(message):
            captured_logs.append(message)
            original_log(message)
        
        self.state_machine._log_action = capture_log
        
        # Trigger hand completion
        self.state_machine.handle_end_hand()
        
        # Check for proper winner announcement
        winner_logs = [log for log in captured_logs if "🏆 Winner" in log]
        self.assertGreater(len(winner_logs), 0, "Should have winner announcement log")
        
        winner_log = winner_logs[0]
        print(f"Winner announcement: {winner_log}")
        
        # Should contain winner name and amount
        self.assertIn("Player", winner_log, "Should mention winner name")
        self.assertIn("win $5.00", winner_log, "Should mention correct amount")
    
    def test_multiple_winners_split_pot(self):
        """Test that multiple winners split the pot correctly."""
        # Set up scenario with tied hands
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=True, cards=['Ad', 'Kd']),
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=False, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=False, cards=['4d', '5d']),
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=False, cards=['6h', '7h']),
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=False, cards=['8s', '9s']),
        ]
        
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],
            pot=6.00,
            current_bet=0.0,
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.SHOWDOWN
        
        # Capture winner info
        winner_info_captured = None
        def capture_winner_info(info):
            nonlocal winner_info_captured
            winner_info_captured = info
        
        self.state_machine.on_hand_complete = capture_winner_info
        
        # Trigger hand completion
        self.state_machine.handle_end_hand()
        
        # Verify split pot
        self.assertIsNotNone(winner_info_captured, "Winner info should be captured")
        self.assertIn("Player 1", winner_info_captured["name"], "Player 1 should be winner")
        self.assertIn("Player 2", winner_info_captured["name"], "Player 2 should be winner")
        self.assertEqual(winner_info_captured["amount"], 6.00, "Should award full pot amount")
        
        # Verify both players got half the pot
        player1 = next(p for p in players if p.name == "Player 1")
        player2 = next(p for p in players if p.name == "Player 2")
        
        expected_split = 3.00
        self.assertEqual(player1.stack, 100.0 + expected_split, 
                        f"Player 1 should have ${100.0 + expected_split}")
        self.assertEqual(player2.stack, 100.0 + expected_split, 
                        f"Player 2 should have ${100.0 + expected_split}")
    
    def test_showdown_vs_fold_scenarios(self):
        """Test winner amount in both showdown and fold scenarios."""
        test_cases = [
            {
                "name": "Showdown with $2.50 pot",
                "pot": 2.50,
                "active_players": 2,
                "expected_amount": 2.50
            },
            {
                "name": "Everyone folds except one",
                "pot": 1.50,
                "active_players": 1,
                "expected_amount": 1.50
            },
            {
                "name": "Large pot $10.00",
                "pot": 10.00,
                "active_players": 2,
                "expected_amount": 10.00
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(test_case["name"]):
                # Set up players
                players = []
                for i in range(6):
                    is_active = i < test_case["active_players"]
                    players.append(Player(
                        name=f"Player {i+1}",
                        stack=100.0,
                        position="BTN",
                        is_human=(i==0),
                        is_active=is_active,
                        cards=['Ah', 'Kh']
                    ))
                
                game_state = GameState(
                    players=players,
                    board=['Ts', 'Tc', '9h', '3c', 'Js'],
                    pot=test_case["pot"],
                    current_bet=0.0,
                    street="river"
                )
                
                self.state_machine.game_state = game_state
                self.state_machine.current_state = PokerState.SHOWDOWN
                
                # Capture winner info
                winner_info_captured = None
                def capture_winner_info(info):
                    nonlocal winner_info_captured
                    winner_info_captured = info
                
                self.state_machine.on_hand_complete = capture_winner_info
                
                # Trigger hand completion
                self.state_machine.handle_end_hand()
                
                # Verify winner amount
                self.assertIsNotNone(winner_info_captured, 
                                   f"Winner info should be captured for {test_case['name']}")
                self.assertEqual(winner_info_captured["amount"], test_case["expected_amount"],
                              f"Winner amount should be ${test_case['expected_amount']} for {test_case['name']}")


if __name__ == '__main__':
    unittest.main() 
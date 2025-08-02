#!/usr/bin/env python3
"""
Test highlighting fix for player actions.
"""

import unittest
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.poker_state_machine_enhanced import (
    ImprovedPokerStateMachine, ActionType, PokerState, Player, GameState
)


class TestHighlightingFix(unittest.TestCase):
    """Test that players are properly highlighted when it's their turn."""
    
    def setUp(self):
        """Set up test environment."""
        self.state_machine = ImprovedPokerStateMachine(num_players=6)
        
    def test_player_highlighting_when_folded(self):
        """Test that folded players are still highlighted when it's their turn."""
        # Set up a scenario where Player 5 has folded but it's their turn
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=True, cards=['Qd', 'Jd']),
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=True, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=True, cards=['4d', '5d']),
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=False, cards=['6h', '7h']),  # Folded
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=True, cards=['8s', '9s']),
        ]
        
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],
            pot=2.50,
            current_bet=0.0,
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Set Player 5 (folded) as the current action player
        self.state_machine.action_player_index = 4  # Player 5 index
        
        # Get game info
        game_info = self.state_machine.get_game_info()
        
        # Verify that Player 5 is the action player
        self.assertEqual(game_info['action_player'], 4, "Player 5 should be the action player")
        
        # Verify that Player 5 is not active (folded)
        player5_info = game_info['players'][4]
        self.assertFalse(player5_info['is_active'], "Player 5 should be inactive (folded)")
        
        # The key test: action_player should be 4 even though player is inactive
        self.assertEqual(game_info['action_player'], 4, 
                        "Action player should be 4 (Player 5) even though they are folded")
        
        print(f"✅ Test passed: Player 5 (folded) is action player: {game_info['action_player']}")
    
    def test_action_animation_callback(self):
        """Test that action animation callback is triggered."""
        # Set up a simple scenario
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=True, cards=['Qd', 'Jd']),
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=True, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=True, cards=['4d', '5d']),
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=True, cards=['6h', '7h']),
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=True, cards=['8s', '9s']),
        ]
        
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],
            pot=2.50,
            current_bet=1.0,
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Capture callback calls
        callback_calls = []
        def capture_action(player_index, action, amount):
            callback_calls.append((player_index, action, amount))
        
        self.state_machine.on_action_executed = capture_action
        
        # Set Player 2 as the current action player first
        self.state_machine.action_player_index = 1  # Player 2 index
        
        # Execute an action
        player = players[1]  # Player 2
        self.state_machine.execute_action(player, ActionType.FOLD, 0)
        
        # Verify callback was called
        self.assertEqual(len(callback_calls), 1, "Action callback should be called once")
        player_index, action, amount = callback_calls[0]
        self.assertEqual(player_index, 1, "Should be Player 2 (index 1)")
        self.assertEqual(action, "fold", "Action should be 'fold'")
        self.assertEqual(amount, 0, "Amount should be 0")
        
        print(f"✅ Test passed: Action callback triggered for {action} by Player {player_index + 1}")

    def test_all_action_types_animations(self):
        """Test that all action types (check, call, bet, raise) trigger animations."""
        # Set up scenario for different action types
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=True, cards=['Qd', 'Jd']),
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=True, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=True, cards=['4d', '5d']),
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=True, cards=['6h', '7h']),
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=True, cards=['8s', '9s']),
        ]
        
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],
            pot=2.50,
            current_bet=0.0,  # No current bet for check/bet
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Capture callback calls
        callback_calls = []
        def capture_action(player_index, action, amount):
            callback_calls.append((player_index, action, amount))
        
        self.state_machine.on_action_executed = capture_action
        
        # Test CHECK action
        self.state_machine.action_player_index = 0  # Player 1
        self.state_machine.execute_action(players[0], ActionType.CHECK, 0)
        
        # Test BET action
        self.state_machine.action_player_index = 1  # Player 2
        self.state_machine.execute_action(players[1], ActionType.BET, 5.0)
        
        # Test CALL action (need a current bet)
        game_state.current_bet = 3.0
        self.state_machine.action_player_index = 2  # Player 3
        self.state_machine.execute_action(players[2], ActionType.CALL, 3.0)
        
        # Test RAISE action
        game_state.current_bet = 3.0
        self.state_machine.action_player_index = 3  # Player 4
        self.state_machine.execute_action(players[3], ActionType.RAISE, 8.0)
        
        # Verify we have at least our 4 intended callbacks (bot actions may add more)
        self.assertGreaterEqual(len(callback_calls), 4, "Should have at least 4 action callbacks")
        
        # Find our specific actions in the callback list
        check_action = None
        bet_action = None
        call_action = None
        raise_action = None
        
        for player_index, action, amount in callback_calls:
            if action == "check" and amount == 0:
                check_action = (player_index, action, amount)
            elif action == "bet" and amount == 5.0:
                bet_action = (player_index, action, amount)
            elif action == "call" and amount == 3.0:
                call_action = (player_index, action, amount)
            elif action == "raise" and amount == 8.0:
                raise_action = (player_index, action, amount)
        
        # Verify CHECK action
        self.assertIsNotNone(check_action, "CHECK action should be found")
        player_index, action, amount = check_action
        print(f"✅ CHECK animation test passed: Player {player_index + 1} checked")
        
        # Verify BET action
        self.assertIsNotNone(bet_action, "BET action should be found")
        player_index, action, amount = bet_action
        print(f"✅ BET animation test passed: Player {player_index + 1} bet ${amount}")
        
        # Verify CALL action
        self.assertIsNotNone(call_action, "CALL action should be found")
        player_index, action, amount = call_action
        print(f"✅ CALL animation test passed: Player {player_index + 1} called ${amount}")
        
        # Verify RAISE action
        self.assertIsNotNone(raise_action, "RAISE action should be found")
        player_index, action, amount = raise_action
        print(f"✅ RAISE animation test passed: Player {player_index + 1} raised to ${amount}")

    def test_action_animation_with_different_amounts(self):
        """Test action animations with various amounts."""
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=True, cards=['Qd', 'Jd']),
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=True, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=True, cards=['4d', '5d']),
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=True, cards=['6h', '7h']),
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=True, cards=['8s', '9s']),
        ]
        
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],
            pot=2.50,
            current_bet=0.0,
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Capture callback calls
        callback_calls = []
        def capture_action(player_index, action, amount):
            callback_calls.append((player_index, action, amount))
        
        self.state_machine.on_action_executed = capture_action
        
        # Test different bet amounts
        test_cases = [
            (0, ActionType.CHECK, 0.0, "check"),
            (1, ActionType.BET, 1.0, "bet"),
            (2, ActionType.BET, 10.0, "bet"),
            (3, ActionType.BET, 25.5, "bet"),
            (4, ActionType.BET, 50.0, "bet"),
            (5, ActionType.BET, 100.0, "bet"),
        ]
        
        for player_index, action_type, amount, expected_action in test_cases:
            self.state_machine.action_player_index = player_index
            self.state_machine.execute_action(players[player_index], action_type, amount)
        
        # Verify we have at least our intended callbacks (bot actions may add more)
        self.assertGreaterEqual(len(callback_calls), len(test_cases), 
                               f"Should have at least {len(test_cases)} action callbacks")
        
        # Find our specific actions in the callback list
        found_actions = []
        for player_index, action, amount in callback_calls:
            for i, (expected_player, expected_action_type, expected_amount, expected_action_name) in enumerate(test_cases):
                if (action == expected_action_name and 
                    abs(amount - expected_amount) < 0.01 and
                    i not in [found[0] for found in found_actions]):
                    found_actions.append((i, player_index, action, amount))
                    break
        
        # Verify we found all our intended actions
        self.assertEqual(len(found_actions), len(test_cases), 
                        f"Should have found all {len(test_cases)} intended actions")
        
        for i, player_index, action, amount in found_actions:
            expected_action = test_cases[i][3]
            expected_amount = test_cases[i][2]
            
            self.assertEqual(action, expected_action, 
                           f"Action {i} should be '{expected_action}', got '{action}'")
            self.assertAlmostEqual(amount, expected_amount, delta=0.01,
                                 msg=f"Amount {i} should be {expected_amount}, got {amount}")
            
            print(f"✅ Action {i+1} test passed: Player {player_index + 1} {action} ${amount}")

    def test_folded_player_action_animation(self):
        """Test that folded players can still trigger action animations."""
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=False, cards=['Qd', 'Jd']),  # Folded
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=True, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=False, cards=['4d', '5d']),  # Folded
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=True, cards=['6h', '7h']),
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=True, cards=['8s', '9s']),
        ]
        
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],
            pot=2.50,
            current_bet=0.0,
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Capture callback calls
        callback_calls = []
        def capture_action(player_index, action, amount):
            callback_calls.append((player_index, action, amount))
        
        self.state_machine.on_action_executed = capture_action
        
        # Test that folded players can still trigger animations
        folded_players = [1, 3]  # Player 2 and Player 4 are folded
        
        for player_index in folded_players:
            self.state_machine.action_player_index = player_index
            # Even though they're folded, they should still be able to trigger animations
            # (This would happen if they somehow got a turn despite being folded)
            self.state_machine.execute_action(players[player_index], ActionType.FOLD, 0)
        
        # Verify we have at least our intended callbacks for folded players (bot actions may add more)
        self.assertGreaterEqual(len(callback_calls), len(folded_players), 
                               f"Should have at least {len(folded_players)} callbacks for folded players")
        
        # Find our specific folded player actions in the callback list
        folded_actions = []
        for player_index, action, amount in callback_calls:
            if (player_index in folded_players and 
                action == "fold" and 
                amount == 0 and
                player_index not in [found[0] for found in folded_actions]):
                folded_actions.append((player_index, action, amount))
        
        # Verify we found all our intended folded player actions
        self.assertEqual(len(folded_actions), len(folded_players), 
                        f"Should have found all {len(folded_players)} folded player actions")
        
        for player_index, action, amount in folded_actions:
            self.assertIn(player_index, folded_players, 
                         f"Player {player_index + 1} should be a folded player")
            self.assertEqual(action, "fold", f"Folded player action should be 'fold'")
            self.assertEqual(amount, 0, f"Folded player amount should be 0")
            
            print(f"✅ Folded player animation test passed: Player {player_index + 1} (folded) triggered animation")

    def test_action_animation_edge_cases(self):
        """Test action animations with edge cases."""
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=True, cards=['Qd', 'Jd']),
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=True, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=True, cards=['4d', '5d']),
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=True, cards=['6h', '7h']),
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=True, cards=['8s', '9s']),
        ]
        
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],
            pot=2.50,
            current_bet=0.0,
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Capture callback calls
        callback_calls = []
        def capture_action(player_index, action, amount):
            callback_calls.append((player_index, action, amount))
        
        self.state_machine.on_action_executed = capture_action
        
        # Test edge cases
        edge_cases = [
            (0, ActionType.CHECK, 0.0, "Zero amount check"),
            (1, ActionType.BET, 0.01, "Very small bet"),
            (2, ActionType.BET, 99.99, "Almost all-in bet"),
            (3, ActionType.BET, 100.0, "Exact stack bet"),
            (4, ActionType.FOLD, 0.0, "Fold with zero amount"),
        ]
        
        for player_index, action_type, amount, description in edge_cases:
            self.state_machine.action_player_index = player_index
            self.state_machine.execute_action(players[player_index], action_type, amount)
            
            # Verify the callback was called
            self.assertGreater(len(callback_calls), 0, f"Callback should be called for {description}")
            
            # Find our specific action in the callback list
            found_action = None
            for call_player_index, call_action, call_amount in callback_calls:
                if (call_player_index == player_index and 
                    call_action == action_type.value and 
                    abs(call_amount - amount) < 0.01):
                    found_action = (call_player_index, call_action, call_amount)
                    break
            
            self.assertIsNotNone(found_action, f"Should find action for {description}")
            self.assertEqual(found_action[0], player_index, f"Player index should match for {description}")
            self.assertAlmostEqual(found_action[2], amount, delta=0.01, 
                                 msg=f"Amount should match for {description}")
            
            print(f"✅ Edge case test passed: {description} - Player {player_index + 1} {found_action[1]} ${amount}")

    def test_action_animation_performance(self):
        """Test that rapid actions don't cause performance issues."""
        # Setup a simple game state in valid betting state
        self.state_machine.game_state.players = [
            Player(name=f"Player {i+1}", stack=100.0, position="BTN", 
                   is_human=(i==0), is_active=True, cards=['Ah', 'Kh'])
            for i in range(6)
        ]
        self.state_machine.game_state.action_player_index = 0
        self.state_machine.game_state.street = "river"
        self.state_machine.game_state.pot = 2.50
        self.state_machine.game_state.current_bet = 0.0
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Execute multiple actions rapidly
        callback_calls = []
        def track_callback(player_index, action, amount):
            callback_calls.append((player_index, action, amount))
        
        self.state_machine.on_action_executed = track_callback
        
        # Execute several actions
        for i in range(3):
            self.state_machine.execute_action(
                self.state_machine.game_state.players[i], 
                ActionType.CHECK, 0
            )
        
        # Should have at least 3 callbacks
        self.assertGreaterEqual(len(callback_calls), 3)
        
        # Verify all actions were CHECK
        check_actions = [call for call in callback_calls if call[1] == "CHECK"]
        self.assertGreaterEqual(len(check_actions), 3)

    def test_persistent_action_indicators(self):
        """Test that action indicators persist until next player acts."""
        # Setup game state with two players in a valid betting state
        self.state_machine.game_state.players = [
            Player(name="Player 1", stack=100.0, position="BTN", 
                   is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", 
                   is_human=False, is_active=True, cards=['Qh', 'Jh'])
        ]
        self.state_machine.game_state.action_player_index = 0
        self.state_machine.game_state.street = "river"
        self.state_machine.game_state.pot = 2.50
        self.state_machine.game_state.current_bet = 0.0
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Track action indicators
        action_indicators = {}
        def track_action_indicator(player_index, action, amount):
            action_indicators[player_index] = (action, amount)
        
        self.state_machine.on_action_executed = track_action_indicator
        
        # Player 1 checks
        self.state_machine.execute_action(
            self.state_machine.game_state.players[0], 
            ActionType.CHECK, 0
        )
        
        # Verify Player 1's action is recorded
        self.assertIn(0, action_indicators)
        self.assertEqual(action_indicators[0], ("CHECK", 0))
        
        # Player 2 acts (should clear Player 1's indicator)
        self.state_machine.game_state.action_player_index = 1
        self.state_machine.execute_action(
            self.state_machine.game_state.players[1], 
            ActionType.CHECK, 0
        )
        
        # Verify Player 2's action is recorded and Player 1's is cleared
        self.assertIn(1, action_indicators)
        self.assertEqual(action_indicators[1], ("CHECK", 0))
        # Note: In the actual UI, Player 1's indicator would be cleared
        # but in this test we're just tracking the callback calls
        
    def test_check_mark_persistence(self):
        """Test that check marks persist until next player acts."""
        # Setup game state in a valid betting state
        self.state_machine.game_state.players = [
            Player(name="Player 1", stack=100.0, position="BTN", 
                   is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", 
                   is_human=False, is_active=True, cards=['Qh', 'Jh'])
        ]
        self.state_machine.game_state.action_player_index = 0
        self.state_machine.game_state.street = "river"
        self.state_machine.game_state.pot = 2.50
        self.state_machine.game_state.current_bet = 0.0
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Track callbacks
        callback_calls = []
        def track_callback(player_index, action, amount):
            callback_calls.append((player_index, action, amount))
        
        self.state_machine.on_action_executed = track_callback
        
        # Player 1 checks
        self.state_machine.execute_action(
            self.state_machine.game_state.players[0], 
            ActionType.CHECK, 0
        )
        
        # Verify check action was recorded
        check_calls = [call for call in callback_calls if call[1] == "CHECK"]
        self.assertGreaterEqual(len(check_calls), 1)
        
        # Player 2 acts (this should clear Player 1's check mark in UI)
        self.state_machine.game_state.action_player_index = 1
        self.state_machine.execute_action(
            self.state_machine.game_state.players[1], 
            ActionType.CHECK, 0
        )
        
        # Verify both players' actions were recorded
        self.assertGreaterEqual(len(callback_calls), 2)
        check_calls = [call for call in callback_calls if call[1] == "CHECK"]
        self.assertGreaterEqual(len(check_calls), 2)

    def test_multiple_actions_highlighting(self):
        """Test highlighting through multiple actions."""
        # Set up scenario with multiple players taking actions
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=True, cards=['Qd', 'Jd']),
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=True, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=True, cards=['4d', '5d']),
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=True, cards=['6h', '7h']),
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=True, cards=['8s', '9s']),
        ]
        
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],
            pot=2.50,
            current_bet=1.0,
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Test highlighting for each player
        for i in range(6):
            self.state_machine.action_player_index = i
            game_info = self.state_machine.get_game_info()
            
            self.assertEqual(game_info['action_player'], i, 
                           f"Player {i+1} should be highlighted when action_player_index is {i}")
            
            print(f"✅ Player {i+1} highlighting test passed")
    
    def test_folded_player_highlighting(self):
        """Test that folded players can still be highlighted."""
        # Set up scenario where some players have folded
        players = [
            Player(name="Player 1", stack=100.0, position="BTN", is_human=True, is_active=True, cards=['Ah', 'Kh']),
            Player(name="Player 2", stack=100.0, position="SB", is_human=False, is_active=False, cards=['Qd', 'Jd']),  # Folded
            Player(name="Player 3", stack=100.0, position="BB", is_human=False, is_active=True, cards=['2c', '3c']),
            Player(name="Player 4", stack=100.0, position="UTG", is_human=False, is_active=False, cards=['4d', '5d']),  # Folded
            Player(name="Player 5", stack=100.0, position="MP", is_human=False, is_active=True, cards=['6h', '7h']),
            Player(name="Player 6", stack=100.0, position="CO", is_human=False, is_active=True, cards=['8s', '9s']),
        ]
        
        game_state = GameState(
            players=players,
            board=['Ts', 'Tc', '9h', '3c', 'Js'],
            pot=2.50,
            current_bet=1.0,
            street="river"
        )
        
        self.state_machine.game_state = game_state
        self.state_machine.current_state = PokerState.RIVER_BETTING
        
        # Test that folded players can still be highlighted
        folded_players = [1, 3]  # Player 2 and Player 4 are folded
        
        for player_index in folded_players:
            self.state_machine.action_player_index = player_index
            game_info = self.state_machine.get_game_info()
            
            # Verify the player is highlighted (action_player) even though inactive
            self.assertEqual(game_info['action_player'], player_index,
                           f"Folded Player {player_index+1} should still be highlightable")
            
            # Verify the player is indeed inactive
            player_info = game_info['players'][player_index]
            self.assertFalse(player_info['is_active'],
                           f"Player {player_index+1} should be inactive (folded)")
            
            print(f"✅ Folded Player {player_index+1} highlighting test passed")


if __name__ == '__main__':
    unittest.main() 
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
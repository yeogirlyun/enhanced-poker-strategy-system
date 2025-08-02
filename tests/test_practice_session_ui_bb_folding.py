#!/usr/bin/env python3
"""
Test BB folding behavior in practice_session_ui.
"""

import unittest
import sys
import os
import tkinter as tk
from unittest.mock import Mock, MagicMock, patch

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from practice_session_ui import PracticeSessionUI
from shared.poker_state_machine_enhanced import Player, ActionType, GameState, PokerState


class TestPracticeSessionUIBBFolding(unittest.TestCase):
    """Test BB folding behavior in the practice_session_ui."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a real Tkinter root
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window
        
        # Create mock strategy data
        self.strategy_data = Mock()
        
        # Create the UI
        self.ui = PracticeSessionUI(self.root, self.strategy_data)
        
        # Mock the state machine
        self.mock_state_machine = MagicMock()
        self.mock_state_machine.game_state = MagicMock()
        self.mock_state_machine.game_state.big_blind = 1.0
        self.ui.state_machine = self.mock_state_machine
        
        # Mock human action controls
        self.ui.human_action_controls = {
            'fold': Mock(),
            'check': Mock(),
            'call': Mock(),
            'bet_raise': Mock(),
        }
        
        # Mock pot label
        self.ui.pot_label = Mock()
        
        # Mock add_game_message to capture messages
        self.ui.add_game_message = Mock()
        
    def tearDown(self):
        """Clean up after test."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_bb_can_fold_when_facing_bet(self):
        """Test that BB can fold when facing a bet in the UI."""
        # Set up game info where BB is facing a bet
        game_info = {
            "state": PokerState.TURN_BETTING.value,
            "pot": 3.50,
            "current_bet": 1.0,  # Someone has bet $1
            "min_raise": 2.0,
            "board": ["9c", "Jh", "2h", "3d"],
            "players": [
                {"name": "Player 1", "position": "BTN", "stack": 98.0, "current_bet": 1.0, "is_active": True},
                {"name": "Player 2", "position": "SB", "stack": 99.5, "current_bet": 0.0, "is_active": False},
                {"name": "Player 3", "position": "BB", "stack": 99.0, "current_bet": 0.0, "is_active": True},
                {"name": "Player 4", "position": "UTG", "stack": 100.0, "current_bet": 0.0, "is_active": False},
                {"name": "Player 5", "position": "MP", "stack": 100.0, "current_bet": 0.0, "is_active": False},
                {"name": "Player 6", "position": "CO", "stack": 100.0, "current_bet": 0.0, "is_active": False},
            ],
            "action_player": 2,  # BB's turn
        }
        
        # Mock get_game_info to return our test data
        self.mock_state_machine.get_game_info.return_value = game_info
        
        # Create a BB player
        bb_player = Player(
            name="Player 3",
            stack=99.0,
            position="BB",
            is_human=False,
            is_active=True,
            cards=['Qd', 'Tc'],
            current_bet=0.0,  # BB has already posted blind
            has_acted_this_round=False,
            is_all_in=False,
            total_invested=0.0,
        )
        
        # Call prompt_human_action with BB player
        self.ui.prompt_human_action(bb_player)
        
        # Check that fold button is enabled (not disabled)
        fold_button = self.ui.human_action_controls['fold']
        
        # Get all calls to config method
        config_calls = fold_button.config.call_args_list
        
        # Find calls that enable the fold button
        enabled_calls = [call for call in config_calls 
                        if 'state' in call[1] and call[1]['state'] == 'normal']
        
        # Find calls that disable the fold button
        disabled_calls = [call for call in config_calls 
                         if 'state' in call[1] and call[1]['state'] == 'disabled']
        
        print(f"Fold button config calls: {config_calls}")
        print(f"Enabled calls: {enabled_calls}")
        print(f"Disabled calls: {disabled_calls}")
        
        # BB should be able to fold when facing a bet
        self.assertGreater(len(enabled_calls), 0, 
                          "Fold button should be enabled for BB when facing a bet")
        
        # BB should not be disabled
        self.assertEqual(len(disabled_calls), 0,
                        "Fold button should not be disabled for BB when facing a bet")
        
        # Check that no error message was added
        self.ui.add_game_message.assert_not_called()
    
    def test_bb_cannot_fold_when_no_bet(self):
        """Test that BB cannot fold when no bet has been made."""
        # Set up game info where BB doesn't face a bet
        game_info = {
            "state": PokerState.TURN_BETTING.value,
            "pot": 1.50,
            "current_bet": 1.0,  # Only blinds
            "min_raise": 2.0,
            "board": ["9c", "Jh", "2h", "3d"],
            "players": [
                {"name": "Player 1", "position": "BTN", "stack": 100.0, "current_bet": 0.0, "is_active": True},
                {"name": "Player 2", "position": "SB", "stack": 99.5, "current_bet": 0.5, "is_active": True},
                {"name": "Player 3", "position": "BB", "stack": 99.0, "current_bet": 1.0, "is_active": True},
                {"name": "Player 4", "position": "UTG", "stack": 100.0, "current_bet": 0.0, "is_active": False},
                {"name": "Player 5", "position": "MP", "stack": 100.0, "current_bet": 0.0, "is_active": False},
                {"name": "Player 6", "position": "CO", "stack": 100.0, "current_bet": 0.0, "is_active": False},
            ],
            "action_player": 2,  # BB's turn
        }
        
        # Mock get_game_info to return our test data
        self.mock_state_machine.get_game_info.return_value = game_info
        
        # Create a BB player
        bb_player = Player(
            name="Player 3",
            stack=99.0,
            position="BB",
            is_human=False,
            is_active=True,
            cards=['Qd', 'Tc'],
            current_bet=1.0,  # BB has posted their blind
            has_acted_this_round=False,
            is_all_in=False,
            total_invested=0.0,
        )
        
        # Call prompt_human_action with BB player
        self.ui.prompt_human_action(bb_player)
        
        # Check that fold button is disabled
        fold_button = self.ui.human_action_controls['fold']
        
        # Get all calls to config method
        config_calls = fold_button.config.call_args_list
        
        # Find calls that disable the fold button
        disabled_calls = [call for call in config_calls 
                         if 'state' in call[1] and call[1]['state'] == 'disabled']
        
        print(f"Fold button config calls: {config_calls}")
        print(f"Disabled calls: {disabled_calls}")
        
        # BB should not be able to fold when no bet has been made
        self.assertGreater(len(disabled_calls), 0,
                          "Fold button should be disabled for BB when no bet has been made")
        
        # Check that error message was added
        self.ui.add_game_message.assert_called_with("⚠️ Big Blind cannot fold when no raise has been made")


if __name__ == '__main__':
    unittest.main() 
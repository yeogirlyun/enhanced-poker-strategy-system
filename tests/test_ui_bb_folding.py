#!/usr/bin/env python3
"""
Test to reproduce the BB folding issue in practice_session_ui.
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from practice_session_ui import PracticeSessionUI
from shared.poker_state_machine_enhanced import Player, ActionType, GameState, PokerState


class TestUIBBFolding(unittest.TestCase):
    """Test BB folding behavior in the UI."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a real Tkinter root
        import tkinter as tk
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window
        
        # Create mock strategy data
        self.strategy_data = Mock()
        
        # Create the UI
        self.ui = PracticeSessionUI(self.root, self.strategy_data)
        
        # Mock the state machine
        self.mock_state_machine = MagicMock()
        self.mock_state_machine.game_state = MagicMock()
        self.mock_state_machine.game_state.big_blind = 1.0  # Set big blind value
        self.ui.state_machine = self.mock_state_machine
        
        # Set up mock game info
        self.game_info = {
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
        self.mock_state_machine.get_game_info.return_value = self.game_info
        
        # Create a mock BB player
        self.bb_player = Player(
            name="Player 3",
            stack=99.0,
            position="BB",
            is_human=False,
            is_active=True,
            cards=['Qd', 'Tc'],
            current_bet=0.0,
            has_acted_this_round=False,
            is_all_in=False,
            total_invested=0.0,
        )
        
        # Mock get_action_player to return BB
        self.mock_state_machine.get_action_player.return_value = self.bb_player
        
        # Mock human action controls
        self.ui.human_action_controls = {
            'fold': Mock(),
            'check': Mock(),
            'call': Mock(),
            'bet_raise': Mock(),
        }
        
        # Mock pot label
        self.ui.pot_label = Mock()
        
    def test_bb_can_fold_when_facing_bet(self):
        """Test that BB can fold when facing a bet in the UI."""
        # Call prompt_human_action with BB player
        self.ui.prompt_human_action(self.bb_player)
        
        # Check that fold button is enabled (not disabled)
        fold_button = self.ui.human_action_controls['fold']
        
        # The fold button should be enabled when BB is facing a bet
        # We need to check if config was called with 'normal' state
        fold_button.config.assert_called()
        
        # Get all calls to config method
        config_calls = [call for call in fold_button.config.call_args_list if 'state' in call[1]]
        
        # Should have at least one call to enable the fold button
        enabled_calls = [call for call in config_calls if call[1]['state'] == 'normal']
        
        print(f"Fold button config calls: {config_calls}")
        print(f"Enabled calls: {enabled_calls}")
        
        # BB should be able to fold when facing a bet
        self.assertGreater(len(enabled_calls), 0, 
                          "Fold button should be enabled for BB when facing a bet")
        
    def test_bb_fold_button_text_correct(self):
        """Test that BB fold button text is correct when facing a bet."""
        # Call prompt_human_action with BB player
        self.ui.prompt_human_action(self.bb_player)
        
        # Check that fold button text is set correctly
        fold_button = self.ui.human_action_controls['fold']
        
        # Get all calls to config method for text
        text_calls = [call for call in fold_button.config.call_args_list if 'text' in call[1]]
        
        print(f"Fold button text calls: {text_calls}")
        
        # Should have a call to set text to "Fold" (not "Fold (BB)")
        fold_text_calls = [call for call in text_calls if call[1]['text'] == 'Fold']
        
        self.assertGreater(len(fold_text_calls), 0,
                          "Fold button text should be 'Fold' when BB can fold")

    def tearDown(self):
        """Clean up after test."""
        if hasattr(self, 'root'):
            self.root.destroy()


if __name__ == '__main__':
    unittest.main() 
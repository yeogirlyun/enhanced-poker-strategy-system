import unittest
from unittest.mock import MagicMock
import tkinter as tk
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from shared.poker_state_machine_enhanced import (
    ImprovedPokerStateMachine, ActionType
)
from practice_session_ui import PracticeSessionUI


class TestBBFoldingBug(unittest.TestCase):
    """
    Comprehensive test suite to identify and fix the BB folding bug.
    This bug violates fundamental poker rules where BB should never fold 
    when it's their turn.
    """

    def setUp(self):
        """Set up test environment."""
        self.state_machine = ImprovedPokerStateMachine(num_players=6)
        
        # Create a real Tk root for UI tests
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        
        # Mock strategy data
        self.mock_strategy_data = {
            "preflop": {},
            "postflop": {}
        }
        
        # Create UI with real state machine
        self.ui = PracticeSessionUI(self.root, self.mock_strategy_data)

    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()

    def test_bb_should_never_fold_preflop(self):
        """
        Test that BB (Big Blind) should never fold during preflop betting
        when it's their turn to act.
        """
        # Start a new hand
        self.state_machine.start_hand()
        
        # Find the BB player
        bb_player = None
        for player in self.state_machine.game_state.players:
            if player.position == "BB":
                bb_player = player
                break
        
        self.assertIsNotNone(bb_player, "BB player should exist")
        
        # Set BB as the current action player
        self.state_machine.action_player_index = \
            self.state_machine.game_state.players.index(bb_player)
        
        # Simulate BB's turn with weak hand
        bb_player.cards = ["2c", "7d"]  # Weak hand
        
        # Execute bot action for BB
        action, amount = self.state_machine.get_basic_bot_action(bb_player)
        
        # BB should NEVER fold - this is the core bug
        self.assertNotEqual(action, ActionType.FOLD, 
                           f"BB should never fold! Got {action} with cards "
                           f"{bb_player.cards}")
        
        # BB should either call, check, or raise
        valid_actions = [ActionType.CALL, ActionType.CHECK, ActionType.RAISE]
        self.assertIn(action, valid_actions, 
                     f"BB should call, check, or raise, not {action}")

    def test_bb_fold_validation_should_fail(self):
        """
        Test that the validation system should prevent BB from folding
        when it's their turn to act.
        """
        # Start a new hand
        self.state_machine.start_hand()
        
        # Find the BB player
        bb_player = None
        for player in self.state_machine.game_state.players:
            if player.position == "BB":
                bb_player = player
                break
        
        # Set BB as the current action player
        self.state_machine.action_player_index = self.state_machine.game_state.players.index(bb_player)
        
        # Try to execute a fold action for BB
        errors = self.state_machine.validate_action(bb_player, ActionType.FOLD, 0)
        
        # The validation should catch this invalid action
        self.assertGreater(len(errors), 0, 
                          "Validation should prevent BB from folding")
        
        # Check that the error message is appropriate
        error_messages = [error.lower() for error in errors]
        self.assertTrue(any("bb" in msg or "big blind" in msg or "fold" in msg 
                           for msg in error_messages),
                       f"Error should mention BB folding issue: {errors}")

    def test_bb_action_logic_with_weak_hand(self):
        """
        Test BB action logic specifically with weak hands to ensure
        they don't fold inappropriately.
        """
        # Start a new hand
        self.state_machine.start_hand()
        
        # Find the BB player
        bb_player = None
        for player in self.state_machine.game_state.players:
            if player.position == "BB":
                bb_player = player
                break
        
        # Test with various weak hands
        weak_hands = [
            ["2c", "3d"],  # 23o - very weak
            ["7c", "2d"],  # 72o - weak
            ["9c", "4d"],  # 94o - weak
            ["Tc", "2d"],  # T2o - weak
        ]
        
        for hand in weak_hands:
            bb_player.cards = hand
            self.state_machine.action_player_index = self.state_machine.game_state.players.index(bb_player)
            
            # Get bot action
            action, amount = self.state_machine.get_basic_bot_action(bb_player)
            
            # BB should never fold, even with weak hands
            self.assertNotEqual(action, ActionType.FOLD,
                               f"BB folded with {hand} - should not happen!")
            
            # Should call, check, or raise
            valid_actions = [ActionType.CALL, ActionType.CHECK, ActionType.RAISE]
            self.assertIn(action, valid_actions,
                         f"BB should call/check/raise with {hand}, not {action}")

    def test_bb_action_logic_with_strong_hand(self):
        """
        Test BB action logic with strong hands to ensure they
        play appropriately.
        """
        # Start a new hand
        self.state_machine.start_hand()
        
        # Find the BB player
        bb_player = None
        for player in self.state_machine.game_state.players:
            if player.position == "BB":
                bb_player = player
                break
        
        # Test with strong hands
        strong_hands = [
            ["Ah", "Kh"],  # AKs - very strong
            ["As", "Ad"],  # AA - very strong
            ["Kh", "Qh"],  # KQs - strong
            ["Jc", "Jd"],  # JJ - strong
        ]
        
        for hand in strong_hands:
            bb_player.cards = hand
            self.state_machine.action_player_index = self.state_machine.game_state.players.index(bb_player)
            
            # Get bot action
            action, amount = self.state_machine.get_basic_bot_action(bb_player)
            
            # BB should never fold with strong hands
            self.assertNotEqual(action, ActionType.FOLD,
                               f"BB folded with {hand} - should not happen!")
            
            # With strong hands, should raise or call
            valid_actions = [ActionType.CALL, ActionType.RAISE]
            self.assertIn(action, valid_actions,
                         f"BB should call/raise with {hand}, not {action}")

    def test_bb_fold_in_ui_should_be_prevented(self):
        """
        Test that the UI should prevent BB from folding when it's their turn.
        """
        # Mock the pot_label to avoid UI setup issues
        self.ui.pot_label = MagicMock()
        
        # Start a new hand
        self.ui.state_machine.start_hand()
        
        # Find the BB player
        bb_player = None
        for player in self.ui.state_machine.game_state.players:
            if player.position == "BB":
                bb_player = player
                break
        
        # Set BB as the current action player
        self.ui.state_machine.action_player_index = self.ui.state_machine.game_state.players.index(bb_player)
        
        # Mock the state machine methods for testing
        self.ui.state_machine.execute_action = MagicMock()
        self.ui.state_machine.validate_action = MagicMock(return_value=["BB cannot fold"])
        
        # Try to submit a fold action for BB
        self.ui._submit_human_action("fold")
        
        # The execute_action should not be called due to validation error
        self.ui.state_machine.execute_action.assert_not_called()

    def test_bb_fold_button_should_be_disabled(self):
        """
        Test that the fold button should be disabled for BB in the UI.
        """
        # Mock the pot_label to avoid UI setup issues
        self.ui.pot_label = MagicMock()
        
        # Start a new hand
        self.ui.state_machine.start_hand()
        
        # Find the BB player
        bb_player = None
        for player in self.ui.state_machine.game_state.players:
            if player.position == "BB":
                bb_player = player
                break
        
        # Set BB as the current action player
        self.ui.state_machine.action_player_index = self.ui.state_machine.game_state.players.index(bb_player)
        
        # Prompt for BB action
        self.ui.prompt_human_action(bb_player)
        
        # Check that fold button is disabled or not present
        if 'fold' in self.ui.human_action_controls:
            fold_button = self.ui.human_action_controls['fold']
            # The fold button should be disabled for BB
            self.assertEqual(fold_button['state'], 'disabled',
                           "Fold button should be disabled for BB")

    def test_bb_action_validation_in_state_machine(self):
        """
        Test that the state machine properly validates BB actions
        and prevents invalid folds.
        """
        # Start a new hand
        self.state_machine.start_hand()
        
        # Find the BB player
        bb_player = None
        for player in self.state_machine.game_state.players:
            if player.position == "BB":
                bb_player = player
                break
        
        # Set BB as the current action player
        self.state_machine.action_player_index = self.state_machine.game_state.players.index(bb_player)
        
        # Try to execute a fold action
        initial_pot = self.state_machine.game_state.pot
        initial_active_players = sum(1 for p in self.state_machine.game_state.players if p.is_active)
        
        # Execute the fold action
        self.state_machine.execute_action(bb_player, ActionType.FOLD, 0)
        
        # Check that the action was properly handled
        # If BB folds, it should be logged as an error
        # We can check the hand history for this
        hand_history = self.state_machine.get_hand_history()
        
        # Look for error messages about BB folding
        error_found = False
        for entry in hand_history:
            if "BB" in entry.player_name and entry.action == ActionType.FOLD:
                error_found = True
                break
        
        # If BB did fold, it should have been logged as an error
        if error_found:
            # Check that there was an error logged
            self.assertTrue(any("error" in str(entry).lower() for entry in hand_history),
                          "BB fold should be logged as an error")

    def test_bb_action_with_different_game_states(self):
        """
        Test BB actions in different game states to ensure
        they never fold inappropriately.
        """
        # Start a new hand
        self.state_machine.start_hand()
        
        # Find the BB player
        bb_player = None
        for player in self.state_machine.game_state.players:
            if player.position == "BB":
                bb_player = player
                break
        
        # Test different game states
        test_scenarios = [
            {"current_bet": 0, "description": "No bet to call"},
            {"current_bet": 1, "description": "Small bet to call"},
            {"current_bet": 5, "description": "Medium bet to call"},
            {"current_bet": 10, "description": "Large bet to call"},
        ]
        
        for scenario in test_scenarios:
            # Set up the scenario
            self.state_machine.game_state.current_bet = scenario["current_bet"]
            self.state_machine.action_player_index = self.state_machine.game_state.players.index(bb_player)
            
            # Test with weak hand
            bb_player.cards = ["2c", "7d"]
            action, amount = self.state_machine.get_basic_bot_action(bb_player)
            
            # BB should never fold
            self.assertNotEqual(action, ActionType.FOLD,
                               f"BB folded in scenario: {scenario['description']}")
            
            # Test with strong hand
            bb_player.cards = ["Ah", "Kh"]
            action, amount = self.state_machine.get_basic_bot_action(bb_player)
            
            # BB should never fold
            self.assertNotEqual(action, ActionType.FOLD,
                               f"BB folded with strong hand in scenario: {scenario['description']}")

    def test_bb_action_consistency(self):
        """
        Test that BB actions are consistent and don't randomly fold.
        """
        # Start a new hand
        self.state_machine.start_hand()
        
        # Find the BB player
        bb_player = None
        for player in self.state_machine.game_state.players:
            if player.position == "BB":
                bb_player = player
                break
        
        # Set BB as the current action player
        self.state_machine.action_player_index = self.state_machine.game_state.players.index(bb_player)
        
        # Test the same scenario multiple times
        bb_player.cards = ["2c", "7d"]  # Weak hand
        actions = []
        
        for _ in range(10):
            action, amount = self.state_machine.get_basic_bot_action(bb_player)
            actions.append(action)
        
        # BB should never fold in any iteration
        self.assertNotIn(ActionType.FOLD, actions,
                        "BB should never fold, even with weak hands")
        
        # All actions should be valid
        valid_actions = [ActionType.CALL, ActionType.CHECK, ActionType.RAISE]
        for action in actions:
            self.assertIn(action, valid_actions,
                         f"BB action {action} should be valid")


if __name__ == '__main__':
    unittest.main() 
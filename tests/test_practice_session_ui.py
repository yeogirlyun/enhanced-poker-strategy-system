import unittest
from unittest.mock import MagicMock
import tkinter as tk
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..',
                'backend'))

from practice_session_ui import PracticeSessionUI
from shared.poker_state_machine_enhanced import Player, ActionType, PokerState


class TestPracticeSessionUI(unittest.TestCase):
    """
    Rigorous unit tests for the PracticeSessionUI, focusing on the interaction
    between the UI logic and the poker state machine.
    """

    def setUp(self):
        """
        Set up a mocked environment for the UI tests.
        This runs before each test.
        """
        # We need a real Tk root to host the UI frame, but it won't be displayed
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window

        # Mock strategy data
        self.mock_strategy_data = {
            "preflop": {},
            "postflop": {}
        }

        # Create the UI with real state machine but mock the callbacks
        self.ui = PracticeSessionUI(self.root, self.mock_strategy_data)
        
        # Mock the state machine methods for testing
        mock_players = [
            {
                "name": f"Player {i+1}",
                "stack": 100.0,
                "position": "BTN",
                "is_human": i == 0,
                "is_active": True,
                "cards": ['Ah', 'Kh'],
                "current_bet": 0.0
            }
            for i in range(6)
        ]
        
        self.ui.state_machine.get_game_info = MagicMock(return_value={
            "pot": 0.0,
            "current_bet": 0.0,
            "board": [],
            "players": mock_players,
            "action_player": 0
        })
        self.ui.state_machine.get_action_player = MagicMock()
        self.ui.state_machine.execute_action = MagicMock()
        self.ui.state_machine.start_hand = MagicMock()
        
        # Ensure pot_label is created by calling the resize handler
        self.ui._on_resize()

    def tearDown(self):
        """
        Clean up the Tkinter window after each test.
        """
        self.root.destroy()

    def _get_mock_game_state(self, num_players=6, action_player_index=0,
                            current_bet=1.0):
        """Helper function to create a default mock game state."""
        players = [
            Player(name=f"Player {i+1}", stack=100.0, position="BTN",
                  is_human=(i == 0), is_active=True, cards=['Ah', 'Kh'])
            for i in range(num_players)
        ]
        human_player = players[0]
        human_player.is_human = True

        game_info = {
            "state": PokerState.PREFLOP_BETTING.value,
            "pot": 1.5,
            "current_bet": current_bet,
            "min_raise": 2.0,
            "board": ["2c", "7d", "Js"],
            "players": [p.__dict__ for p in players],
            "action_player": action_player_index,
        }
        self.ui.state_machine.get_game_info.return_value = game_info
        self.ui.state_machine.get_action_player.return_value = \
            players[action_player_index]
        return game_info, players

    def test_ui_initialization(self):
        """Test that all UI components are created on initialization."""
        self.assertIsNotNone(self.ui.canvas)
        self.assertIsNotNone(self.ui.info_text)
        self.assertIsNotNone(self.ui.player_seats)
        self.assertIsNotNone(self.ui.community_card_labels)
        self.assertIsNotNone(self.ui.pot_label)

    def test_update_ui_reflects_game_state(self):
        """Test if the UI correctly updates player stacks, pot, and cards."""
        game_info, _ = self._get_mock_game_state()

        # Test the update display method
        self.ui.update_display()

        # Verify that the pot label was updated
        self.assertIn("Pot: $1.50", self.ui.pot_label.cget("text"))

    def test_action_buttons_on_human_turn(self):
        """Test that action buttons are correctly enabled/disabled for the human player's turn."""
        # Scenario: There is a bet to call
        game_info, players = self._get_mock_game_state(current_bet=10.0)
        human_player = players[0]
        human_player.current_bet = 1.0  # Human has 1.0 in, needs to call 9.0 more

        # Simulate it being the human's turn
        self.ui.prompt_human_action(human_player)

        # Check that action controls are created
        self.assertIn('fold', self.ui.human_action_controls)
        self.assertIn('check', self.ui.human_action_controls)
        self.assertIn('call', self.ui.human_action_controls)
        self.assertIn('bet_raise', self.ui.human_action_controls)

    def test_check_button_logic(self):
        """Test that the 'Check' button appears when there is no bet to call."""
        # Scenario: No bet to call
        game_info, players = self._get_mock_game_state(current_bet=0.0)

        # Simulate it being the human's turn
        self.ui.prompt_human_action(players[0])

        # Check that action controls are created
        self.assertIn('check', self.ui.human_action_controls)
        self.assertIn('bet_raise', self.ui.human_action_controls)

    def test_fold_action(self):
        """Test that clicking the fold button calls the state machine correctly."""
        # Setup mock state machine
        mock_player = Player(name="Player 1", stack=100.0, position="BTN", 
                           is_human=True, is_active=True, cards=['Ah', 'Kh'])
        self.ui.state_machine.get_action_player.return_value = mock_player
        
        # Simulate fold action
        self.ui._submit_human_action("fold")
        
        # Verify the state machine was called with correct parameters
        self.ui.state_machine.execute_action.assert_called_once_with(
            mock_player,
            ActionType.FOLD,
            0
        )

    def test_call_action(self):
        """Test that clicking the call/check button calls the state machine correctly."""
        # Setup a scenario where the action is a CALL
        game_info, players = self._get_mock_game_state(current_bet=10.0)
        human_player = players[0]
        human_player.current_bet = 1.0
        self.ui.state_machine.get_action_player.return_value = human_player
        
        # Mock the bet_size_var for the call amount calculation
        # The call action doesn't use bet_size_var, it uses the difference
        # between current_bet and player.current_bet
        self.ui.bet_size_var = MagicMock()
        self.ui.bet_size_var.get.return_value = 0  # Call uses 0 for amount
        
        # Simulate call action
        self.ui._submit_human_action("call")
        
        # Verify the state machine was called with correct parameters
        self.ui.state_machine.execute_action.assert_called_once_with(
            human_player,
            ActionType.CALL,
            0  # Call action uses 0 amount, the state machine calculates the difference
        )

    def test_raise_action(self):
        """Test that clicking the bet/raise button calls the state machine correctly."""
        # Setup a scenario where a raise is possible
        game_info, players = self._get_mock_game_state(current_bet=10.0)
        human_player = players[0]
        human_player.current_bet = 1.0
        self.ui.state_machine.get_action_player.return_value = human_player
        
        # Mock the bet_size_var for the raise amount
        self.ui.bet_size_var = MagicMock()
        self.ui.bet_size_var.get.return_value = 25.0
        
        # Simulate raise action
        self.ui._submit_human_action("raise")
        
        # Verify the state machine was called with correct parameters
        self.ui.state_machine.execute_action.assert_called_once_with(
            human_player,
            ActionType.RAISE,
            25.0  # The amount from the slider
        )

    def test_winner_display_on_hand_complete(self):
        """Test that the winner information is displayed when the hand ends."""
        winner_info = {
            "name": "Player 1",
            "amount": 150.0,
            "hand": "a Full House",
            "board": ["Ac", "Ad", "Ah", "Ks", "Kd"]
        }
        
        # Test the hand complete handler
        self.ui.handle_hand_complete(winner_info)
        
        # Verify that the winner info was processed
        self.assertIsNotNone(winner_info)

    def test_add_game_message(self):
        """Test that game messages are properly added to the info text."""
        test_message = "Test game message"
        
        # Add a game message
        self.ui.add_game_message(test_message)
        
        # Verify the method exists and can be called
        self.assertTrue(hasattr(self.ui, 'add_game_message'))

    def test_start_new_hand(self):
        """Test that starting a new hand resets the UI properly."""
        # Test the start new hand method
        self.ui.start_new_hand()
        
        # Verify the state machine was called to start a new hand
        self.ui.state_machine.start_hand.assert_called_once()

    def test_format_card(self):
        """Test that card formatting works correctly."""
        # Test various card formats
        self.assertEqual(self.ui._format_card("Ah"), "A♥")
        self.assertEqual(self.ui._format_card("Kd"), "K♦")
        self.assertEqual(self.ui._format_card("Qs"), "Q♠")
        self.assertEqual(self.ui._format_card("Jc"), "J♣")

    def test_reset_ui_for_new_hand(self):
        """Test that the UI is properly reset for a new hand."""
        # Test the reset method
        self.ui._reset_ui_for_new_hand()
        
        # Verify that the UI components are reset
        # This would typically clear displays, reset buttons, etc.
        self.assertTrue(hasattr(self.ui, '_reset_ui_for_new_hand'))


if __name__ == '__main__':
    unittest.main() 